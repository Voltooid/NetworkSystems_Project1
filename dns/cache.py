#!/usr/bin/env python3

"""A cache for resource records

This module contains a class which implements a cache for DNS resource records,
you still have to do most of the implementation. The module also provides a
class and a function for converting ResourceRecords from and to JSON strings.
It is highly recommended to use these.
"""


import json
import time

from dns.resource import ResourceRecord


class RecordCache:
    """Cache for ResourceRecords"""

    def __init__(self, ttl):
        """Initialize the RecordCache

        Args:
            ttl (int): TTL of cached entries (if > 0)
        """
        self.records = {}
        self.ttl = ttl

    def lookup(self, dname, type_, class_):
        """Lookup resource records in cache

        Lookup for the resource records for a domain name with a specific type
        and class.

        Args:
            dname (str): domain name
            type_ (Type): type
            class_ (Class): class
        """

        res = []
        for r in self.records:
            if r.name == dname and r.type_ == type_ and r.class_ == class_:
                if r.ttl < time.time():
                    r = None
                else:
                    res.append(r)

        self.records = [x for x in self.records if not x == None]

        return res

    def dump_cache(self):
        for r in self.records:
            print(r.to_dict())

    def add_record(self, record):
        """Add a new Record to the cache

        Args:
            record (ResourceRecord): the record added to the cache
        """
        record.ttl = record.ttl + time.time()
        for x in self.records:
            if x.name == record.name and x.type_ == record.type_ and x.class_ == record.class_:
                key = list(x.rdata.to_dict().keys())[0]
                if x.rdata.to_dict()[key] == record.rdata.to_dict()[key]:
                    x = record
                    return
        self.records.append(record)

    def read_cache_file(self):
        """Read the cache file from disk"""
        dcts = []
        try:
            with open("cache", "r") as file_:
                dcts = json.load(file_)
        except:
            print("could not read cache")
        self.records = [ResourceRecord.from_dict(dct) for dct in dcts]

    def write_cache_file(self):
        """Write the cache file to disk"""
        dcts = [record.to_dict() for record in self.records]
        try:
            with open("cache", "w") as file_:
                json.dump(dcts, file_, indent=2)
        except:
            print("could not write cache")
