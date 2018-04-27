#!/usr/bin/env python3

"""Zones of domain name space

See section 6.1.2 of RFC 1035 and section 4.2 of RFC 1034.
Instead of tree structures we simply use dictionaries from domain names to
zones or record sets.

These classes are merely a suggestion, feel free to use something else.
"""

from dns.resource import *
from dns.types import Type
from dns.classes import Class
import json

class Catalog:
    """A catalog of zones"""

    def __init__(self):
        """Initialize the catalog"""
        self.zones = {}

    def add_zone(self, name, zone):
        """Add a new zone to the catalog

        Args:
            name (str): root domain name
            zone (Zone): zone
        """
        self.zones[name] = zone


class Zone:
    """A zone in the domain name space"""

    def __init__(self):
        """Initialize the Zone """
        self.records = {}

    def add_node(self, name, record_set):
        """Add a record set to the zone

        Args:
            name (str): domain name
            record_set ([ResourceRecord]): resource records
        """
        self.records[name] = record_set

    def read_master_file(self, filename):
        """Read the zone from a master file

        See section 5 of RFC 1035.

        Args:
            filename (str): the filename of the master file
        """
        with open(filename) as file:
            lines = file.readlines()
        dct = {}
        for line in lines:
            if line[0] != ";":
                data = line.split()
                if data[2] == 'NS':
                    t  = Type.NS
                    rdata = NSRecordData(Name(data[3]))
                elif data[2] == 'A':
                    t  = Type.A
                    rdata = ARecordData(data[3])

                elif data[2] == 'CNAME':
                    t  = Type.CNAME
                    rdata = CNAMERecordData(Name(data[3]))
                else:
                    continue
                RR = ResourceRecord(Name(data[0]), t, Class.IN, int(data[1]), rdata)
                if data[0] in dct.keys() :
                    dct[data[0]].append(RR)
                else:
                    dct[data[0]] = [RR]
        
        for key, value in dct.items():
            self.add_node(key, value)

                
            
