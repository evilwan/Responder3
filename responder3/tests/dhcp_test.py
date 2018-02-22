from responder3.protocols.DHCP import *

data = bytes.fromhex('010106000000155c0000800000000000000000000000000000000000cc000ac400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000063825363350101390204803d1b00636973636f2d636330302e306163342e303030302d4661302f300c025230370801060f2c0321962bff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
msg = DHCPMessage.from_bytes(data)
print(repr(msg))

data2 = bytes.fromhex('020106000000155c0000800000000000c0a800030000000000000000cc000ac4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501023604c0a8000133040000003c3a040000001e3b04000000340104ffffff000304c0a800010608c0a80001c0a80101ff00000000000000000000')
msg2 = DHCPMessage.from_bytes(data2)
print(repr(msg2))

data3 = bytes.fromhex('010106000000155c0000800000000000000000000000000000000000cc000ac400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000063825363350103390204803d1b00636973636f2d636330302e306163342e303030302d4661302f303604c0a800013204c0a8000333040000003c0c025230370801060f2c0321962bff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
msg3 = DHCPMessage.from_bytes(data3)
print(repr(msg3))

data3 = bytes.fromhex('020106000000155c0000800000000000c0a800030000000000000000cc000ac4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501053604c0a8000133040000003c3a040000001e3b04000000340c0252300104ffffff000304c0a800010608c0a80001c0a80101ff000000000000')
msg3 = DHCPMessage.from_bytes(data3)
print(repr(msg3))

data3 = bytes.fromhex('010106000000155c00000000c0a80003000000000000000000000000cc000ac400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000063825363350103390204803d1b00636973636f2d636330302e306163342e303030302d4661302f3033040000003c0c025230370801060f2c0321962bff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
msg3 = DHCPMessage.from_bytes(data3)
print(repr(msg3))

data3 = bytes.fromhex('020106000000155c00000000c0a80003c0a800030000000000000000cc000ac4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501053604c0a8000133040000003c3a040000001e3b04000000340c0252300104ffffff000304c0a800010608c0a80001c0a80101ff000000000000')
msg3 = DHCPMessage.from_bytes(data3)
print(repr(msg3))

data3 = bytes.fromhex('010106000000155c00000000c0a80003000000000000000000000000cc000ac400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000063825363350103390204803d1b00636973636f2d636330302e306163342e303030302d4661302f3033040000003c0c025230370801060f2c0321962bff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
msg3 = DHCPMessage.from_bytes(data3)
print(repr(msg3))