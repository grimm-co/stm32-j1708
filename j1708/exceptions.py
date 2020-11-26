# Custom exception classes to make it easy to differentiate msg decoding errors 
# from logic errors

class J1708Error(ValueError): pass
class J1708LogParseError(J1708Error): pass
class J1708EncodeError(J1708Error): pass
class J1708DecodeError(J1708Error): pass
class J1708ChecksumError(J1708DecodeError): pass
class J1708MultisectionError(J1708DecodeError): pass
