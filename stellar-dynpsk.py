#!/usr/bin/env python3

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#
# This script is meant to change the PSK of a given SSID whenever it is called (e.g. via cron)
#

# TODO
# - Ensure that .gitignore is set up :)
# - Figure out a good way to log the outcome (logger module maybe)
# - Send a mail when done (also read details from config file)
# - Find out if any other user than "admin" can use the RESTful API of OmniVista v4.2.2 in read-only mode to get APs
# - Don't forget to leverage the http/https choice for contacting the APs!
# - Generate QR code for mail
# - Potentially support multiple AP-Groups, but it would be simpler to just run the script for each group

#
# Imports
#
import sys
try:
    import requests
except ImportError as ie:
    print(ie)
    sys.exit("Please install python-requests!")
try:
    import pyqrcode
except ImportError as ie:
    sys.exit("Please install pyqrcode!")
import json
import random
import urllib3

print("\nStellar DynPSK - a simple PSK changer for Stellar Wireless SSIDs")
print("Written by Benny Eggerstedt in 2018")
print("This is free software not provided/shipped by Alcatel-Lucent Enterprise. Use it at your own risk!\n")

# Load settings from settings.json file
print("[+] Reading settings.json file")
try:
    with open("settings.json", "r") as json_data:
        settings = json.load(json_data)
        ov_hostname = settings["ov_hostname"]
        ov_username = settings["ov_username"]
        ov_password = settings["ov_password"]
        validate_https_certificate = settings["validate_https_certificate"]
        ap_group = settings["ap_group"]
        ssid = settings["ssid"]
        psk_length = settings["psk_length"]
except IOError as ioe:
    print(ioe)
    sys.exit("ERROR: Couldn't find/open settings.json file!")
except TypeError as te:
    print(te)
    sys.exit("ERROR: Couldn't read json format!")

# Try to initialise a random seed. If urandom() is not available on the system, this script will fail
# If we don't fail, this will generate the new PSK
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"
try:
    r = random.SystemRandom()
except NotImplementedError as nie:
    print(nie)
    sys.exit("Your system doesn't provide a secure random generator!")

# Generate a PSK
new_psk = "".join(r.choice(letters) for _ in range(psk_length))

# Validate that setting.json is configured and not using the default
if ov_hostname == "omnivista.example.com":
    sys.exit("ERROR: Can't work with default template value for OmniVista hostname!")

# Validate that the hostname is a hostname, not URL
if "https://" in ov_hostname:
    print("[!] Found \"https://\" in ov_hostname, removing it!")
    ov_hostname = ov_hostname.lstrip("https://")

# Validate that the hostname doesn't contain a "/"
if "/" in ov_hostname:
    print("[!] Found \"/\" in hostname, removing it!")
    ov_hostname = ov_hostname.strip("/")


# Figure out if HTTPS certificates should be validated
# That should actually be the default, so we'll warn if disabled.

if(validate_https_certificate.lower() == "yes"):
    check_certs = True
else:
    # This is needed to get rid of a warning coming from urllib3 on self-signed certificates
    print("[!] Ignoring certificate warnings or self-signed certificates!")
    print("[!] You should really fix this!")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    check_certs = False    

# Test connection to OmniVista
print("[*] Attempting to connect to OmniVista server @ https://{0}".format(ov_hostname))

req = requests.Session()

# Use the ca-certificate store managed via Debian
# This is just for development, should be commented out for production.
req.verify = "/etc/ssl/certs/"

# Check if we die on the HTTPS certificate
try:
    ov = req.get("https://{0}".format(ov_hostname), verify=check_certs)
except requests.exceptions.SSLError as sslerror:
    print(sslerror)
    sys.exit("[!] Caught issues on certificate, try to change \"validate_https_certificate\" to \"no\" in settings.json. Exiting!")

if ov.status_code == 200:
    print("[*] Connection to {0} successful!".format(ov_hostname))
else:
    sys.exit("[!] Connection to {0} failed, exiting!".format(ov_hostname))

ov_login_data = {"userName" : ov_username, "password" : ov_password}
ov_header = {"Content-Type": "application/json"}

# requests.post with json=payload was introduced in version 2.4.2
# otherwise it would need to be "data=json.dumps(ov_login_data),"

ov = req.post("https://{0}/api/login".format(ov_hostname),
              headers=ov_header,
              json=ov_login_data,
              verify=check_certs)

if ov.status_code == 200:
    token = ov.json()
    token = token["accessToken"]
    ov_header["Authorization"] = "Bearer {0}".format(token)
else:
    sys.exit("[!] The connection to OmniVista was not successful! Exiting!")

# As we want to change the configuraton LIVE, we need to work on "device config" and not the "template" in OmniVista.
# To do that we first POST to the following URL and retrieve a bunch of instance IDs with the goal to find our AP group
# https://omnivista.home/api/ag/deviceconfig/devices

dc_post = {"AGRequestObject":{"objectType":"WLANService","others":{"deviceType":"AP_GROUP"}}}

dc_list = req.post("https://{0}/api/ag/deviceconfig/devices".format(ov_hostname),
                  headers=ov_header,
                  json=dc_post,
                  verify=check_certs)

if dc_list.status_code == 200:
    instanceid = None
    for devicegroup in dc_list.json()["response"]:
        if devicegroup["apGroupId"] == ap_group:
            instanceid = devicegroup["instanceid"]
            print("[*] Found instanceID {0} for AP group {1}".format(instanceid, ap_group))
            break
    if instanceid is None:
        sys.exit("[!] Your AP Group couldn't be found! Keep in mind that it is case-sensitive!")
else:
    sys.exit("[!] Couldn't get device config from OmniVista! Exiting!")

# In this step we obtain the current configuration from the AP Group (with the previously obtained instanceid)
# We'll look for our SSID now to modify the PSK afterwards.

# TODO - There was a smarter way to do this, but I forgot
dc_instance = "[\"{0}\"]".format(instanceid)
#dc_instance.append(instanceid)

dc_config = req.post("https://{0}/api/ag/uadeviceconfig/WLANService".format(ov_hostname),
                  headers=ov_header,
                  data=dc_instance,
                  #data=instanceid,
                  #json=instanceid,
                  verify=check_certs)

if dc_config.status_code == 200:
    ssid_instance = None
    for ssid_nbr in dc_config.json()["response"]:
        if ssid_nbr["uniqueValue"] == ssid:
            ssid_instance = ssid_nbr["instanceid"]
            profileinfo = ssid_nbr["profileInfo"]
            print("[*] Found deviceId {0} for SSID {1}".format(ssid_instance, ssid))
            break
    if ssid_instance is None:
        sys.exit("[!] Your SSID couldn't be found! Exiting!")
else:
    sys.exit("[!] Couldn't get device config (SSIDs) from OmniVista! Exiting!")

# In this step we build the json object that will update the PSK

ua_update = {
        
        "UnifiedProfileRequestObject": {
            "deviceRequests": [
                {
                    "deviceConfigId": ssid_instance,
                    "deviceType": "AP_GROUP",
                    "updateAttrs": {
                        }
                }
                ]
        }
}

ua_update["UnifiedProfileRequestObject"]["deviceRequests"][0]["updateAttrs"] = profileinfo
ua_update["UnifiedProfileRequestObject"]["deviceRequests"][0]["updateAttrs"]["passphrase"] = new_psk

dc_update = req.put("https://{0}/api/ag/uadeviceconfig/update/WLANService".format(ov_hostname),
                  headers=ov_header,
                  json=ua_update,
                  verify=check_certs)

# BUG: OmniVista v4.2.2 Build 115
# The above API responds with a faulty JSON object, thus I can't really validate the result

if dc_update.status_code == 200:
    print("[+] Changed the PSK of SSID {0} to: {1}".format(ssid, new_psk))
else:
    sys.exit("[!] Something went wrong while updating the PSK!")

# Generate a QR code to login to this SSID
# QR format: "WIFI:T:WPA;S:SSID;P:PSK;;"
pskqr = pyqrcode.create("WIFI:T:WPA/WPA2;S:{0};P:{1};;".format(ssid, new_psk))
print(pskqr.terminal())

print("[+] Scan the above QR Code with your mobile phone and login to the network!")

