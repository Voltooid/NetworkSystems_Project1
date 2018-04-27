#!/usr/bin/env python3

"""A recursive DNS server

This module provides a recursive DNS server. You will have to implement this
server using the algorithm described in section 4.3.2 of RFC 1034.
"""


from threading import Thread
from dns.zone import Zone
from dns.name import Name
from dns.message import Message, Header
from dns.cache import RecordCache
from dns.resource import ResourceRecord, ARecordData, CNAMERecordData
from dns.types import Type
from dns.name import Name
from dns.classes import Class
from dns.resolver import Resolver
import socket
import struct

class RequestHandler(Thread):
    """A handler for requests to the DNS server"""

    def __init__(self):
        """Initialize the handler thread"""
        super().__init__()
        self.daemon = True

    def run(self):
        """ Run the handler thread"""
        pass


class Server:
    """A recursive DNS server"""

    def __init__(self, port, caching, ttl):
        """Initialize the server

        Args:
            port (int): port that server is listening on
            caching (bool): server uses resolver with caching if true
            ttl (int): ttl for records (if > 0) of cache
        """
        self.caching = caching
        self.ttl = ttl
        self.port = port
        self.done = False
        self.zone = Zone()
        self.zone.read_master_file('zone')
        self.cache = RecordCache(ttl)
        if self.caching:
            self.cache.read_cache_file()
        self.doLogging = True

    def log(self, *args, end="\n"):
        if self.doLogging:
            print(*args, end=end)

    def search_zone(self, question):
        tests = str(question).split('.')
        for i in range(len(tests)):
            test = '.'.join(tests[i:])
            if test == '':
                test = '.'
            r = self.zone.records.get(test, None)
            if not r == None:
                if test == str(question):
                    return True, r
                return False, r
        return False, []

    def zone_resolution(self, questions):
        for q in questions:
            self.log("\tRESOLVING:", q.qname)
            res, rlist = self.search_zone(q.qname)
            answers = []
            authorities = []
            additionals = []
            for r in rlist:
                if r.type_ == Type.A and res:
                    answers.append(r)
                if r.type_ == Type.NS:
                    res, a = self.search_zone(r.rdata.nsdname)
                    authorities.append(r)
                    if res:
                        additionals.append(a[0])
        return answers, authorities, additionals

    def check_cache(self, hostname):
        iplist = self.cache.lookup(hostname, Type.A, Class.IN)
        namelist = self.cache.lookup(hostname, Type.CNAME, Class.IN)
        if not (iplist == [] and namelist == []):
            iplist = [x.rdata.address for x in iplist]
            namelist = [x.rdata.cname for x in namelist]
            return True, iplist, namelist
        return False, [], []

    def consult_cache(self, questions):
        answers = []
        for q in questions:
            res, iplist, namelist = self.check_cache(q.qname)
            if res:
                for ip in iplist:
                    answers.append(ResourceRecord(q.qname, Type.A, Class.IN, self.ttl, ARecordData(ip)))
                for n in namelist:
                    answers.append(ResourceRecord(q.qname, Type.CNAME, Class.IN, self.ttl, CNAMERecordData(n)))
        return answers

    def build_message(self,id, rd, aa, rcode, questions, answers, authorities, additionals):
        header = Header(id, 0, len(questions), len(answers), len(authorities), len(additionals))
        header.qr = 1
        header.opcode = 0
        header.rd = rd
        header.ra = 1
        header.aa = aa
        header.rcode = rcode
        return Message(header, questions=questions, answers=answers, authorities=authorities, additionals=additionals)


    def serve(self):
        """Start serving requests"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.port))

        while not self.done:
            data, address = sock.recvfrom(65565)
            message = Message.from_bytes(data)

            rd = message.header.rd
            rcode = 0
            aa = 1

            self.log("REQUEST RECIEVED:", address)
            answers, authorities, additionals = self.zone_resolution(message.questions)

            if answers == []:
                if authorities == [] and additionals == []:
                    self.log("\tZONE RESOLUTION FAILED")
                    answers = self.consult_cache(message.questions)

                    if answers == []:
                        self.log("\tCACHE LOOKUP FAILED")
                        rcode = 3
                    else:
                        aa = 0

                if rcode == 3 and rd == 1:
                    rcode = 0
                    self.log("\tCALLING RESOLVER")
                    resolver = Resolver(5, True, 0)
                    resolver.rd = 0
                    resolver.rootip = "198.41.0.4"
                    for q in message.questions:
                        self.log("\t\tRESOLVING:", q.qname)

                        hostname, namelist, iplist = resolver.gethostbyname(str(q.qname))
                        if hostname == str(q.qname):
                            for ip in iplist:
                                answers.append(ResourceRecord(q.qname, Type.A, Class.IN, self.ttl, ARecordData(ip)))
                            for n in namelist:
                                answers.append(ResourceRecord(q.qname, Type.CNAME, Class.IN, self.ttl, CNAMERecordData(n)))

            self.log("SENDING RESPONSE:", rcode, "\n")
            mess = self.build_message(message.header.ident, rd, aa, rcode, message.questions, answers, authorities, additionals)
            sock.sendto(mess.to_bytes(), address)

    def shutdown(self):
        """Shut the server down"""
        self.done = True

