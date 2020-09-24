# Custom exception classes to make it easy to differentiate msg decoding errors 
# from logic errors

class J1708ChecksumError(ValueError): pass
class J1708DecodeError(ValueError): pass
class J1708EncodeError(ValueError): pass
class J1708LogParseError(ValueError): pass
