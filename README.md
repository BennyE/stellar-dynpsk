# stellar-dynpsk
stellar-dynpsk is a small tool to generate a new PSK for a given SSID on Stellar Wireless (Enterprise mode)

## Dependencies
- requests (Thanks to Kenneth Reitz - http://www.python-requests.org/)
- pyqrcode (Thanks to Michael Nooner - https://github.com/mnooner256/pyqrcode)
- Python3.5 (This is what comes with my Debian release, no support for Python 2.x)
- A separate system to run this code, as you can host this on Alcatel-Lucent Enterprise OmniVista 2500 today
 
## Example

```python
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

## Things to consider
- Introduce some data structure to generate the PSK & send information a few days before the PSK is actually changed
- Implement a function to send this as mail to a given address
- Expand this kind of functionality to Stellar Wireless Express mode
