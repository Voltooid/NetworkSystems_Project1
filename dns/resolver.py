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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        rootserverip = "198.41.0.4"
        serveriplist = [rootserverip]
        servernamelist = [hostname]

        while len(serveriplist) != 0 or len(servernamelist) != 0:
            # Create and send query
            ip = serveriplist[0]
            if not (len(servernamelist) > 1):
                del serveriplist[0]
            servername = servernamelist[0]
            if not (len(serveriplist) > 1):
                del servernamelist[0]

            print("\nREQUEST", servername, "FROM:", ip)
            question = Question(servername, Type.A, Class.IN)
            header = Header(9001, 0, 1, 0, 0, 0)
            header.qr = 0
            header.opcode = 0
            header.rd = 0
            query = Message(header, [question])

            sock.sendto(query.to_bytes(), (ip, 53))

            # Receive response
            data = sock.recv(512)
            response = Message.from_bytes(data)

            # Get data
            aliaslist = []
            ipaddrlist = []
            print("\tFLAGS", end="")
            print(" QR", response.header.qr, end=";")
            print(" OPCODE", response.header.opcode, end=";")
            print(" AA", response.header.aa, end=";")
            print(" TC", response.header.tc, end=";")
            print(" RD", response.header.rd, end=";")
            print(" RA", response.header.ra, end=";")
            print(" Z", response.header.z, end=";")
            print(" RCODE", response.header.rcode, end=";\n")

            if len(response.answers) != 0:
                print("\n\tGOT RESPONSE")
                servernamelist = []
                serveriplist = []
                for answer in response.answers:
                    if answer.type_ == Type.A:
                        if servername == hostname:
                            ipaddrlist.append(answer.rdata.address)
                        else:
                            serveriplist = [answer.rdata.address]
                            servernamelist = [hostname]
                        print("\t\t", answer.type_, answer.rdata.address)
                    if answer.type_ == Type.CNAME:
                        aliaslist.append(hostname)
                        hostname = str(answer.rdata.cname)
                        print("\t\t", answer.type_, answer.rdata.cname)

            if len(response.additionals) != 0: 
                print("\n\tGOT ADDITIONALS")
                serveriplist = []
                servernamelist = [servername]
                for answer in response.additionals:
                    if answer.type_ == Type.A:
                        serveriplist.append(answer.rdata.address)
                        print('\t\t', answer.type_, answer.rdata.address)

            elif len(response.authorities) != 0:
                print("\n\tGOT AUTHORITIES")
                serveriplist = [rootserverip]
                servernamelist = []
                for answer in response.authorities:
                    servernamelist.append(answer.rdata.nsdname)
                    print('\t\t', answer.type_, answer.rdata.nsdname)
            print("END")


        print("END OF QUERY:", hostname)
        return hostname, aliaslist, ipaddrlist
