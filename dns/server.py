#!/usr/bin/env python3

"""A recursive DNS server

This module provides a recursive DNS server. You will have to implement this
server using the algorithm described in section 4.3.2 of RFC 1034.
"""


from threading import Thread
from dns.zone import Zone
from dns.name import Name
from dns.message import Message, Header
from dns.types import Type
from dns.classes import Class
from dns.resource import ResourceRecord, NSRecordData, ARecordData
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
                return r
        return None

    def serve(self):
        """Start serving requests"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 53))

        while not self.done:
            data, address = sock.recvfrom(65565)
            message = Message.from_bytes(data)
            recursion = message.header.rd
            for q in message.questions:
                rlist = self.search_zone(q.qname)
                answers = []
                authorities = []
                additionals = []
                if rlist:
                    for r in rlist: 
                        if r.type_ == Type.A:
                            answers.append(r)
                        if r.type_ == Type.NS:
                            a = self.search_zone(r.rdata.nsdname)
                            authorities.append(r)
                            additionals.append(a[0])
                
                header = Header(message.header.ident, 0,len(message.questions),len(answers),len(authorities),len(additionals))
                header.qr = 1
                header.opcode = 0
                header.rd = recursion
                header.ra = 1
                header.aa = 1
                mess = Message(header, questions=message.questions, answers=answers, authorities=authorities, additionals=additionals)
                sock.sendto(mess.to_bytes(), address) 



    def shutdown(self):
        """Shut the server down"""
        self.done = True

