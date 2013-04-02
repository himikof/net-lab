# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='sessions/server/ServerReplication.proto',
  package='ru.kt15.net.labs.sessions',
  serialized_pb='\n\'sessions/server/ServerReplication.proto\x12\x19ru.kt15.net.labs.sessions\"1\n\nSessionKey\x12\x11\n\tsessionId\x18\x01 \x02(\t\x12\x10\n\x08serverId\x18\x02 \x02(\t\"\xa0\x01\n\x07Session\x12\x32\n\x03key\x18\x01 \x02(\x0b\x32%.ru.kt15.net.labs.sessions.SessionKey\x12\x11\n\ttimestamp\x18\x02 \x02(\x04\x12\x15\n\rsessionSource\x18\x03 \x01(\t\x12\x13\n\x0bsessionDest\x18\x04 \x01(\t\x12\x12\n\nvalidUntil\x18\x05 \x01(\x04\x12\x0e\n\x06remove\x18\x06 \x01(\x08\"\x1a\n\x07HostKey\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x02(\t\"w\n\x04Host\x12/\n\x03key\x18\x01 \x02(\x0b\x32\".ru.kt15.net.labs.sessions.HostKey\x12\x11\n\ttimestamp\x18\x02 \x02(\x04\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\r\n\x05valid\x18\x04 \x01(\x08\x12\x0e\n\x06remove\x18\x05 \x01(\x08\"l\n\x04List\x12\x34\n\x08sessions\x18\x01 \x03(\x0b\x32\".ru.kt15.net.labs.sessions.Session\x12.\n\x05hosts\x18\x02 \x03(\x0b\x32\x1f.ru.kt15.net.labs.sessions.Host')




_SESSIONKEY = descriptor.Descriptor(
  name='SessionKey',
  full_name='ru.kt15.net.labs.sessions.SessionKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='sessionId', full_name='ru.kt15.net.labs.sessions.SessionKey.sessionId', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='serverId', full_name='ru.kt15.net.labs.sessions.SessionKey.serverId', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=70,
  serialized_end=119,
)


_SESSION = descriptor.Descriptor(
  name='Session',
  full_name='ru.kt15.net.labs.sessions.Session',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='key', full_name='ru.kt15.net.labs.sessions.Session.key', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='timestamp', full_name='ru.kt15.net.labs.sessions.Session.timestamp', index=1,
      number=2, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='sessionSource', full_name='ru.kt15.net.labs.sessions.Session.sessionSource', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='sessionDest', full_name='ru.kt15.net.labs.sessions.Session.sessionDest', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='validUntil', full_name='ru.kt15.net.labs.sessions.Session.validUntil', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='remove', full_name='ru.kt15.net.labs.sessions.Session.remove', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=122,
  serialized_end=282,
)


_HOSTKEY = descriptor.Descriptor(
  name='HostKey',
  full_name='ru.kt15.net.labs.sessions.HostKey',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='address', full_name='ru.kt15.net.labs.sessions.HostKey.address', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=284,
  serialized_end=310,
)


_HOST = descriptor.Descriptor(
  name='Host',
  full_name='ru.kt15.net.labs.sessions.Host',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='key', full_name='ru.kt15.net.labs.sessions.Host.key', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='timestamp', full_name='ru.kt15.net.labs.sessions.Host.timestamp', index=1,
      number=2, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='name', full_name='ru.kt15.net.labs.sessions.Host.name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='valid', full_name='ru.kt15.net.labs.sessions.Host.valid', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='remove', full_name='ru.kt15.net.labs.sessions.Host.remove', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=312,
  serialized_end=431,
)


_LIST = descriptor.Descriptor(
  name='List',
  full_name='ru.kt15.net.labs.sessions.List',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='sessions', full_name='ru.kt15.net.labs.sessions.List.sessions', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='hosts', full_name='ru.kt15.net.labs.sessions.List.hosts', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=433,
  serialized_end=541,
)

_SESSION.fields_by_name['key'].message_type = _SESSIONKEY
_HOST.fields_by_name['key'].message_type = _HOSTKEY
_LIST.fields_by_name['sessions'].message_type = _SESSION
_LIST.fields_by_name['hosts'].message_type = _HOST
DESCRIPTOR.message_types_by_name['SessionKey'] = _SESSIONKEY
DESCRIPTOR.message_types_by_name['Session'] = _SESSION
DESCRIPTOR.message_types_by_name['HostKey'] = _HOSTKEY
DESCRIPTOR.message_types_by_name['Host'] = _HOST
DESCRIPTOR.message_types_by_name['List'] = _LIST

class SessionKey(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _SESSIONKEY
  
  # @@protoc_insertion_point(class_scope:ru.kt15.net.labs.sessions.SessionKey)

class Session(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _SESSION
  
  # @@protoc_insertion_point(class_scope:ru.kt15.net.labs.sessions.Session)

class HostKey(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _HOSTKEY
  
  # @@protoc_insertion_point(class_scope:ru.kt15.net.labs.sessions.HostKey)

class Host(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _HOST
  
  # @@protoc_insertion_point(class_scope:ru.kt15.net.labs.sessions.Host)

class List(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _LIST
  
  # @@protoc_insertion_point(class_scope:ru.kt15.net.labs.sessions.List)

# @@protoc_insertion_point(module_scope)