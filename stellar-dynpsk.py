#!/usr/bin/env python3

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#
# This script is meant to change the PSK of a given SSID whenever it is called (e.g. via cron)
#

# TODO
# - Figure out a good way to log the outcome (logger module maybe)
# - Find out if any other user than "admin" can use the RESTful API of OmniVista v4.2.2 in read-only mode to get APs
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

#
# Functions
#

def send_mail(email_from, email_to, ssid_name, new_psk, language,
                smtp_server, smtp_auth, smtp_port, smtp_password):

    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.

    #from email.MIMEMultipart import MIMEMultipart
    #from email.MIMEText import MIMEText
    #from email.MIMEImage import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage

    # Define these once; use them twice!
    strFrom = email_from
    strTo = email_to

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    if language == "de":
        msgRoot['Subject'] = "Neuer Pre-Shared Key (PSK) fuer SSID: {0}".format(ssid_name)
    else:
        msgRoot['Subject'] = "New pre-shared key (PSK) for SSID: {0}".format(ssid_name)
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    if language == "de":
        msgText = MIMEText("""
Hallo,

soeben hat sich der Pre-Shared Key (PSK) fuer das WLAN \"{0}\" geaendert.
Der neue PSK lautet: {1}

Bis bald!
        """.format(ssid_name, new_psk))
    else:
        msgText = MIMEText("""
Hi,

we just changed our pre-shared key (PSK) for SSID \"{0}\".
The new PSK for this network is: {1}

Cheers!
        """.format(ssid_name, new_psk))

    msgAlternative.attach(msgText)

    if language == "de":
        mail_content = """
<!DOCTYPE html>
<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style>
body {{
background-color: #ebebeb;
width: 800px;
margin: 0 auto;
padding-top: 20px;
padding-bottom: 60px;
font-family: "HelveticaNeueLight", "HelveticaNeue-Light", "Helvetica Neue Light", "HelveticaNeue", "Helvetica Neue", 'TeXGyreHerosRegular', "Helvetica", "Tahoma", "Geneva", "Arial", sans-serif; font-weight:300; font-stretch:normal;
}}

a {{
color: #2e9ec9;
}}

h2 {{
font-family: Georgia;
font-weight: normal;
font-size: 80px;
margin-bottom: 20px;
}}

li b {{
font-weight: bold;
}}

h2 a {{
text-decoration: none;
color: #444444;
text-shadow: 1px 1px 0px white;
}}

h3 {{
font-family: Georgia;
font-size: 24px;
color: #444444;
text-shadow: 1px 1px 0px white;
}}

ul {{
margin-left: 0px;
margin-bottom: 40px;
padding-left: 0px;
}}

ul>li {{
font-size: 16px;
line-height: 1.4em;
list-style-type: none;
position: relative;
margin-bottom: 20px;
padding-left: 40px;
padding-top: 40px;
padding-right: 40px;
padding-bottom: 60px;
background: #fff;
color: #444444;
-webkit-box-shadow:0 1px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 0, 0, 0.1) inset;
-moz-box-shadow:0 1px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 0, 0, 0.1) inset;
box-shadow:0 1px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 0, 0, 0.1) inset;
}}

li li {{
padding: 10px 10px 0px 5px;
font-size: 16px;
margin-bottom: 0px;
margin-left: 25px;
list-style-type: disc;
list-style-position: outside;
-webkit-box-shadow: none;
-moz-box-shadow: none;
box-shadow: none;
}}

ul>li:before, ul>li:after {{
content:"";
position:absolute;
z-index:-2;
}}

body > ul > li > a:first-child {{
position: absolute;
bottom: 30px;
right: 40px;
font-family: Georgia;
font-size: 12px;
}}

body > ul > li > a:first-child::before {{
font-size: 100%;
content: "Permalink: ";
}}

blockquote {{
font-family: Georgia;
font-style: italic;
padding-left: 10px;
margin-left: 20px;
}}

/* For Screens smaller than 800px width. Smaller margins on boxes and flexible widths */

@media only screen and (max-width: 800px){{
body {{
padding: 5px;
width: 93%;
margin: 0 auto;
}}

h2 {{
font-size: 50px;
margin-bottom: 20px;
}}
               
ul {{
margin-left: 0px;
margin-bottom: 20px;
padding-left: 0px;
}}
                          
ul>li {{
margin-bottom: 15px;
padding: 25px 25px 50px 25px;
}}

blockquote {{
padding-left: 0;
margin-left: 15px;
}}
}}
</style>
</head><body>

<p></p>

<ul>
<li>
<p><a href="https://www.al-enterprise.com/"><img src="cid:image1" height="60px"></a>
<a href="https://www.al-enterprise.com/"><img src="cid:image3" height="75px"></a>
</p>
<p>Hallo,</p>

<p>der Pre-Shared Key (PSK) f&uuml;r das WLAN <b>{0}</b> hat sich soeben ge&auml;ndert.</p>

<p>Mit dem folgenden QR Code f&auml;llt die Verbindung mit dem WLAN leichter:</p>
<p><img src="cid:image2_{1}" height="120px"></p>

<p>Der neue PSK lautet: <b>{1}</b></p>
<p>
Danke und Gru&szlig;,<br>
Ihr ALE Stellar Wireless Team
</p>
</li>
</ul>
</body></html>
    """.format(ssid_name, new_psk)
    else:
        mail_content = """
<!DOCTYPE html>
<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style>
body {{
background-color: #ebebeb;
width: 800px;
margin: 0 auto;
padding-top: 20px;
padding-bottom: 60px;
font-family: "HelveticaNeueLight", "HelveticaNeue-Light", "Helvetica Neue Light", "HelveticaNeue", "Helvetica Neue", 'TeXGyreHerosRegular', "Helvetica", "Tahoma", "Geneva", "Arial", sans-serif; font-weight:300; font-stretch:normal;
}}

a {{
color: #2e9ec9;
}}

h2 {{
font-family: Georgia;
font-weight: normal;
font-size: 80px;
margin-bottom: 20px;
}}

li b {{
font-weight: bold;
}}

h2 a {{
text-decoration: none;
color: #444444;
text-shadow: 1px 1px 0px white;
}}

h3 {{
font-family: Georgia;
font-size: 24px;
color: #444444;
text-shadow: 1px 1px 0px white;
}}

ul {{
margin-left: 0px;
margin-bottom: 40px;
padding-left: 0px;
}}

ul>li {{
font-size: 16px;
line-height: 1.4em;
list-style-type: none;
position: relative;
margin-bottom: 20px;
padding-left: 40px;
padding-top: 40px;
padding-right: 40px;
padding-bottom: 60px;
background: #fff;
color: #444444;
-webkit-box-shadow:0 1px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 0, 0, 0.1) inset;
-moz-box-shadow:0 1px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 0, 0, 0.1) inset;
box-shadow:0 1px 4px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 0, 0, 0.1) inset;
}}

li li {{
padding: 10px 10px 0px 5px;
font-size: 16px;
margin-bottom: 0px;
margin-left: 25px;
list-style-type: disc;
list-style-position: outside;
-webkit-box-shadow: none;
-moz-box-shadow: none;
box-shadow: none;
}}

ul>li:before, ul>li:after {{
content:"";
position:absolute;
z-index:-2;
}}

body > ul > li > a:first-child {{
position: absolute;
bottom: 30px;
right: 40px;
font-family: Georgia;
font-size: 12px;
}}

body > ul > li > a:first-child::before {{
font-size: 100%;
content: "Permalink: ";
}}

blockquote {{
font-family: Georgia;
font-style: italic;
padding-left: 10px;
margin-left: 20px;
}}

/* For Screens smaller than 800px width. Smaller margins on boxes and flexible widths */

@media only screen and (max-width: 800px){{
body {{
padding: 5px;
width: 93%;
margin: 0 auto;
}}

h2 {{
font-size: 50px;
margin-bottom: 20px;
}}
               
ul {{
margin-left: 0px;
margin-bottom: 20px;
padding-left: 0px;
}}
                          
ul>li {{
margin-bottom: 15px;
padding: 25px 25px 50px 25px;
}}

blockquote {{
padding-left: 0;
margin-left: 15px;
}}
}}
</style>
</head><body>

<p></p>

<ul>
<li>
<p><a href="https://www.al-enterprise.com/"><img src="cid:image1" height="60px"></a>
<a href="https://www.al-enterprise.com/"><img src="cid:image3" height="75px"></a>
</p>
<p>Hi,</p>

<p>the pre-shared key (PSK) for the SSID <b>{0}</b> has just been changed.</p>

<p>You may scan the following QR code with your mobile phone to ease the connection process:</p>
<p><img src="cid:image2_{1}" height="120px"></p>

<p>This is the new PSK: <b>{1}</b></p>
<p>
Thanks,
Regards,<br>
The ALE Stellar Wireless Team
</p>
</li>
</ul>
</body></html>
    """.format(ssid_name, new_psk)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(mail_content, 'html')
    msgAlternative.attach(msgText)

    # ALE Logo
    fp = open('logos/al_enterprise_bk_50mm.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    # QR Code
    fp = open('logos/qrcode.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    # Avoid that the mail client can cache a previous QR code by giving a custom name
    msgImage.add_header('Content-ID', '<image2_{0}>'.format(new_psk))
    msgRoot.attach(msgImage)

    # Stellar Logo
    fp = open('logos/stellar-logo.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image3>')
    msgRoot.attach(msgImage)

    # Send the email
    import smtplib
    smtp = smtplib.SMTP()
    smtp.set_debuglevel(0)
    smtp.connect("{0}:{1}".format(smtp_server, smtp_port))

    if smtp_auth == "yes":
        smtp.ehlo()
        smtp.starttls()
        smtp.login(email_from, smtp_password)
        result = smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    else:
        result = smtp.sendmail(strFrom, strTo, msgRoot.as_string())

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
        encr = settings["encryption"]
        psk_length = settings["psk_length"]
        send_psk_via_mail = settings["send_psk_via_mail"]
        email_from = settings["email_from"]
        smtp_server = settings["smtp_server"]
        smtp_auth = settings["smtp_auth"]
        smtp_port = settings["smtp_port"]
        smtp_password = settings["smtp_password"]
        language = settings["language"]
        email_to = settings["email_to"]
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
pskqr = pyqrcode.create("WIFI:T:{0};S:{1};P:{2};;".format(encr, ssid, new_psk))
if send_psk_via_mail == "yes":
    pskqr.png("logos/qrcode.png", scale=8)
    send_mail(email_from, email_to, ssid, new_psk, language,
            smtp_server, smtp_auth, smtp_port, smtp_password)
    print("[+] Scan the QR Code sent via mail with your mobile phone and login to the network!")
else:
    print(pskqr.terminal())
    print("[+] Scan the above QR Code with your mobile phone and login to the network!")
