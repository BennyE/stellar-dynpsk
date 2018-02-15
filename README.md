# stellar-dynpsk
stellar-dynpsk is a small tool to generate a new PSK for a given SSID on Stellar Wireless (Enterprise mode)

## Dependencies
- requests (Thanks to Kenneth Reitz - http://www.python-requests.org/)
- pyqrcode (Thanks to Michael Nooner - https://github.com/mnooner256/pyqrcode)
- pypng (Thanks to David Jones - https://pythonhosted.org/pypng/)
- Python3.5 (This is what comes with my Debian release, no support for Python 2.x)
- A separate system to run this code, as you can't host this on Alcatel-Lucent Enterprise OmniVista 2500 today
 
## Example

```
$ python stellar-dynpsk.py 

Stellar DynPSK - a simple PSK changer for Stellar Wireless SSIDs
Written by Benny Eggerstedt in 2018
This is free software not provided/shipped by Alcatel-Lucent Enterprise. Use it at your own risk!

[+] Reading settings.json file
[*] Attempting to connect to OmniVista server @ https://omnivista.home
[*] Connection to omnivista.home successful!
[*] Found instanceID 59ab1cb7e4b010f83b3d47f0 for AP group Home
[*] Found deviceId 5a7d02b6e4b0582ec054a882 for SSID dynpsk
[+] Changed the PSK of SSID dynpsk to: 6nVjc9xJXtHn

(Here comes some QR CODE)

[+] Scan the above QR Code with your mobile phone and login to the network!
```

## Demo Video
[![Demo Video](https://img.youtube.com/vi/cx0n13rECW0/0.jpg)](https://www.youtube.com/watch?v=cx0n13rECW0)

## Usage

Edit the **settings.json.template** and save it as **settings.json**
```
{
        "ov_hostname": "omnivista.example.com",		# The OmniVista 2500 server to connect to
        "ov_username": "admin",				# Username
        "ov_password": "switch",			# Password
        "validate_https_certificate": "yes",		# Validate the HTTPS certificate?
        "ap_group": "ap-group-name-case-sensitive",	# AP-Group of APs that you want to update (case-sensitive!)
        "ssid": "ssid-name",				# Name of the SSID on which you want to update the PSK
        "psk_length": 12				# The length of the PSK to generate
        "send_psk_via_mail": "yes",			# If you want to send a mail with the PSK/QR Code
        "email_from": "FROMaddress@mailprovider.com",	# mailFrom
        "smtp_server": "smtp.gmail.com",		# SMTP server
        "smtp_auth": "yes",				# Please specifiy if you need authentication
        "smtp_port": 587,				# If "auth" is set, we currently always do TLS
        "smtp_password": "passwordforsmtp",		# SMTP password
        "language": "de",				# Language for the mail (de, en) 
        "email_to": "TOaddress@mailprovider.com"	# mailTo
}
```

## Things to consider for the future
- Introduce some data structure to generate the PSK & send information a few days before the PSK is actually changed
- Expand this kind of functionality to Stellar Wireless Express mode
