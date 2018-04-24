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
        self.doLogging = False

    def setLogging(self, val):
        self.doLogging = val

    def log(self, *args, end="\n"):
        if self.doLogging:
            print(*args, end=end)

    def logHeader(self, header):
            self.log("\tFLAGS", end="")
            self.log(" QR", header.qr, end=";")
            self.log(" OPCODE", header.opcode, end=";")
            self.log(" AA", header.aa, end=";")
            self.log(" TC", header.tc, end=";")
            self.log(" RD", header.rd, end=";")
            self.log(" RA", header.ra, end=";")
            self.log(" Z", header.z, end=";")
            self.log(" RCODE", header.rcode, end=";\n")

    def send_request(self, ip, name):

            #create socket and request
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
            self.log("\nRESOLVING REQUEST", hostname, "at:", ip)
            answers, authorities, additionals = self.send_request(ip, hostname)

            # Process data
            namelist = []
            ipaddrlist = []
            if len(answers) != 0:
                self.log("\n\tGOT RESPONSE")
                for answer in answers:
                    if answer.type_ == Type.A:
                        ipaddrlist.append(answer.rdata.address)
                        self.log("\t\t", answer.type_, answer.rdata.address)
                    if answer.type_ == Type.CNAME:
                        namelist.append(hostname)
                        self.log("\t\t", answer.type_, answer.rdata.cname)
                return True, ipaddrlist, namelist
            else:

                if len(additionals) != 0:
                    self.log("\n\tGOT ADDITIONALS")
                    for answer in additionals:
                        if answer.type_ == Type.A:
                            ipaddrlist.append(answer.rdata.address)
                            self.log('\t\t', answer.type_, answer.rdata.address)

                if len(authorities) != 0:
                    self.log("\n\tGOT AUTHORITIES")
                    for answer in authorities:
                        namelist.append(answer.rdata.nsdname)
                        self.log('\t\t', answer.type_, answer.rdata.nsdname)

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

        hostname = Name(hostname)
        self.log("NEW QUERY:", hostname)
        rootserverip = "198.41.0.4"
        serveriplist = [rootserverip]

        while len(serveriplist) != 0:
            res, iplist, namelist = self.resolve_request(serveriplist[0], hostname)
            if res:
                self.log("END OF QUERY:", hostname)
                return hostname, namelist, iplist
            elif len(iplist) == 0 and not len(namelist) == 0:
                newlist = []
                for x in namelist:
                    newhostname, newaliases, newips= self.gethostbyname(str(x))
                    newlist.extend(newips)
                newlist.extend(serveriplist)
                serveriplist = newlist
            else:
                iplist.extend(serveriplist[1:])
                serveriplist = iplist
        self.log("FAILURE")
        return hostname, [], []
