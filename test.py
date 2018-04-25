from dns.resource import ResourceRecord, NSRecordData, ARecordData
from dns.name import Name
from dns.types import Type
from dns.classes import Class

b = Name('a.').to_bytes(0)
x, y = Name.from_bytes(b, 0)
print(b, x)
b = Name('b.').to_bytes(0)
x, y = Name.from_bytes(b, 0)
print(b, x)
b = Name('.').to_bytes(0)
x, y = Name.from_bytes(b, 0)
print(b, x)