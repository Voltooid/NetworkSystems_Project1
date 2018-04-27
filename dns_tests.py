#!/usr/bin/env python3

"""Tests for your DNS resolver and server"""


import sys
import unittest
import time
from unittest import TestCase
from argparse import ArgumentParser
from dns.resolver import Resolver
from dns.resource import ResourceRecord, ARecordData, CNAMERecordData
from dns.types import Type
from dns.name import Name
from dns.classes import Class
from dns.server import Server


PORT = 5001
SERVER = "localhost"


class TestResolver(TestCase):
    """Resolver tests"""
    def setUp(self):
        self.resolver = Resolver(5, True, 0)

    def test_testOne(self):
        RR = ResourceRecord(Name("invalid_address.asdas"), Type.A, Class.IN, 2, ARecordData("1.4.1"))
        self.resolver.cache.add_record(RR)
        hostname, aliaslist, ipaddrlist = self.resolver.gethostbyname("invalid_address.asdas")
        self.assertEqual(ipaddrlist[0], "1.4.1")

    def test_testTwo(self):
        time.sleep(4)
        hostname, aliaslist, ipaddrlist = self.resolver.gethostbyname("invalid_address.asdas")
        self.assertEqual(ipaddrlist, [])
        
class TestServer(TestCase):
    def setUp(self):
        self.resolver = Resolver(5, False, 0, "127.0.0.1")

    def test_testOne(self):
        hostname, aliaslist, ipaddrlist = self.resolver.gethostbyname("kaas.lol")
        self.assertEqual("1.1.1.1", ipaddrlist[0])

    def test_testTwo(self):
        hostname, aliaslist, ipaddrlist = self.resolver.gethostbyname("ru.nl")
        self.assertEqual("131.174.78.60", ipaddrlist[0])

    def test_testThree(self):
        hostname, aliaslist, ipaddrlist = self.resolver.gethostbyname("google.com")
        self.assertEqual([], ipaddrlist)

def run_tests():
    """Run the DNS resolver and server tests"""
    parser = ArgumentParser(description="DNS Tests")
    parser.add_argument("-s", "--server", type=str, default="localhost",
                        help="the address of the server")
    parser.add_argument("-p", "--port", type=int, default=5001,
                        help="the port of the server")
    args, extra = parser.parse_known_args()
    global PORT, SERVER
    PORT = args.port
    SERVER = args.server

    # Pass the extra arguments to unittest
    sys.argv[1:] = extra

    # Start test suite
    unittest.main()


if __name__ == "__main__":
    run_tests()
