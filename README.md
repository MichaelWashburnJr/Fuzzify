# Fuzzify
SWEN-331 Fuzzer Project

Python Version: 3.*

Install Instructions:
=====================

1. Make sure Pip is installed: https://pip.pypa.io/en/latest/installing.html
2. In the fuzzer directory, execute the command `pip install -r requirements.txt`

Usage:
======

Discover
--------
To use the Fuzzer's discover functionality, issue the command:

`python fuzz.py discover http://url.to/fuzzify --common-words=file.txt [--custom-auth dvwa]`

Test
--------
To use the Fuzzer's test functionality, issue the command:

`python fuzz.py test http://url.to/fuzzify --common-words=file.txt [--custom-auth dvwa] [--slow 100] [--vectors vectors.txt] [--sensitive sensitive.txt]`

Help
-----
For help using the program or a list of more advanced options, execute the 
command `python fuzz.py -h` or `python fuzz.py --help`
