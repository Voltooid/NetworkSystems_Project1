#!/usr/bin/env python3

"""DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""


import socket

from dns.classes import Class
from dns.message import Message, Question, Header
from dns.name import Name
from dns.types import Type


class Resolver:
    """DNS resolver"""

    def __init__(self, timeout, caching, ttl):
        """Initialize the resolver

        Args:
            caching (bool): caching is enabled if True
            ttl (int): ttl of cache entries (if > 0)
        """
        self.timeout = timeout
        self.caching = caching
        self.ttl = ttl

    def logHeader(self, header):
            print("\tFLAGS", end="")
            print(" QR", header.qr, end=";")
            print(" OPCODE", header.opcode, end=";")
            print(" AA", header.aa, end=";")
            print(" TC", header.tc, end=";")
            print(" RD", header.rd, end=";")
            print(" RA", header.ra, end=";")
            print(" Z", header.z, end=";")
            print(" RCODE", header.rcode, end=";\n")

    def send_request(self, ip, name):

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            question = Question(name, Type.A, Class.IN)
            header = Header(9001, 0, 1, 0, 0, 0)
            header.qr = 0
            header.opcode = 0
            header.rd = 0
            query = Message(header, [question])

            sock.sendto(query.to_bytes(), (ip, 53))

            # Receive response
            data = sock.recv(512)
            response = Message.from_bytes(data)
            self.logHeader(response.header)
            return response.answers, response.authorities, response.additionals

    def resolve_request(self, ip, hostname):
            print("\nRESOLVING REQUEST", hostname, "at:", ip)
            answers, authorities, additionals = self.send_request(ip, hostname)

            # Process data
            namelist = []
            ipaddrlist = []
            if len(answers) != 0:
                print("\n\tGOT RESPONSE")
                for answer in answers:
                    if answer.type_ == Type.A:
                        ipaddrlist.append(answer.rdata.address)
                        print("\t\t", answer.type_, answer.rdata.address)
                    if answer.type_ == Type.CNAME:
                        namelist.append(hostname)
                        print("\t\t", answer.type_, answer.rdata.cname)
                return True, ipaddrlist, namelist
            else:

                if len(additionals) != 0:
                    print("\n\tGOT ADDITIONALS")
                    for answer in additionals:
                        if answer.type_ == Type.A:
                            ipaddrlist.append(answer.rdata.address)
                            print('\t\t', answer.type_, answer.rdata.address)

                if len(authorities) != 0:
                    print("\n\tGOT AUTHORITIES")
                    for answer in authorities:
                        namelist.append(answer.rdata.nsdname)
                        print('\t\t', answer.type_, answer.rdata.nsdname)

                return False, ipaddrlist, namelist

    def gethostbyname(self, hostname):
        """Translate a host name to IPv4 address.

        Currently this method contains an example. You will have to replace
        this example with the algorithm described in section 5.3.3 in RFC 1034.

        Args:
            hostname (str): the hostname to resolve

        Returns:
            (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
        """
        # check cache
        # pick nameserver


        # build iterative dns request
        # send request over UDP

        hostname = Name(hostname)
        print("NEW QUERY:", hostname)
        rootserverip = "198.41.0.4"
        serveriplist = [rootserverip]

        while len(serveriplist) != 0:
            res, iplist, namelist = self.resolve_request(serveriplist[0], hostname)
            if res:
                print("END OF QUERY:", hostname)
                return hostname, namelist, iplist
            elif len(iplist) == 0 and not len(namelist) == 0:
                newlist = []
                for x in namelist:
                    newhostname, newaliases, newips= self.gethostbyname(str(x))
                    print("newIPS", newips)
                    newlist.extend(newips)
                newlist.extend(serveriplist)
                serveriplist = newlist
            else:
                iplist.extend(serveriplist[1:])
                serveriplist = iplist
            print(serveriplist)
        print("FAILURE")
