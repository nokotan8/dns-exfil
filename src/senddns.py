import struct
import socket

# Sources: 
#   https://gist.github.com/mrpapercut/92422ecf06b5ab8e64e502da5e33b9f7
#   https://datatracker.ietf.org/doc/html/rfc1035

QDCOUNT = 1 # Number of questions          
ANCOUNT = 0 # Number of answers            
NSCOUNT = 0 # Number of authority records  
ARCOUNT = 0 # Number of additional records 

TYPE_A = 1
TYPE_NS = 2
TYPE_CNAME = 5

CLASS_IN = 1


def sendQuery(addr, record_type, dns_server):
    """
    Args:
        addr (string): URL to resolve.
        record_type (int): The type of DNS query. For exfiltration, use TYPE_A (1)
        dns_server (string): What DNS server to use.
    """
    # Header section format:
    #                                 1  1  1  1  1  1
    #   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                      ID                       |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    QDCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    ANCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    NSCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                    ARCOUNT                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    id = 43690
    RECURSION = 1 << 8 # Only field in the second row that matters
    # All arguments to big-endian unsigned short, or network-byte order
    header = struct.pack('!HHHHHH', id, RECURSION, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)
    
    # Question section format:
    #                                 1  1  1  1  1  1
    #   0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                                               |
    # /                     QNAME                     /
    # /                                               /
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                     QTYPE                     |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # |                     QCLASS                    |
    # +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    
    # Construct the question, i.e. what domain to resolve
    question = b''
    addr_parts = addr.split('.')
    for part in addr_parts:
        question += bytes([len(part)]) + part.encode('ascii')
    question += b'\x00'
    question += struct.pack('!HH', record_type, CLASS_IN)
    
    query = header + question
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send it to DNS Server, which accepts requests on port 53
    sock.sendto(query, (dns_server, 53))