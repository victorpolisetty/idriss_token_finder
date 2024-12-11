# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
"""Generated protocol buffer code."""
# pylint: disable=line-too-long,C0121,W0212
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\nnttp.proto\x12\x17\x61\x65\x61.fetchai.http.v1_0_0"\x93\x03\n\x0bHttpMessage\x12L\n\x07request\x18\x05 \x01(\x0b\x32\x39.aea.fetchai.http.v1_0_0.HttpMessage.Request_PerformativeH\x00\x12N\n\x08response\x18\x06 \x01(\x0b\x32:.aea.fetchai.http.v1_0_0.HttpMessage.Response_PerformativeH\x00\x1a\x63\n\x14Request_Performative\x12\x0e\n\x06method\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x12\x0f\n\x07headers\x18\x04 \x01(\t\x12\x0c\n\x04\x62ody\x18\x05 \x01(\x0c\x1aq\n\x15Response_Performative\x12\x0f\n\x07version\x18\x01 \x01(\t\x12\x13\n\x0bstatus_code\x18\x02 \x01(\x05\x12\x13\n\x0bstatus_text\x18\x03 \x01(\t\x12\x0f\n\x07headers\x18\x04 \x01(\t\x12\x0c\n\x04\x62ody\x18\x05 \x01(\x0c\x42\x0e\n\x0cperformativeb\x06proto3'
)


_HTTPMESSAGE = DESCRIPTOR.message_types_by_name["HttpMessage"]
_HTTPMESSAGE_REQUEST_PERFORMATIVE = _HTTPMESSAGE.nested_types_by_name[
    "Request_Performative"
]
_HTTPMESSAGE_RESPONSE_PERFORMATIVE = _HTTPMESSAGE.nested_types_by_name[
    "Response_Performative"
]
HttpMessage = _reflection.GeneratedProtocolMessageType(
    "HttpMessage",
    (_message.Message,),
    {
        "Request_Performative": _reflection.GeneratedProtocolMessageType(
            "Request_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _HTTPMESSAGE_REQUEST_PERFORMATIVE,
                "__module__": "http_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.http.v1_0_0.HttpMessage.Request_Performative)
            },
        ),
        "Response_Performative": _reflection.GeneratedProtocolMessageType(
            "Response_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _HTTPMESSAGE_RESPONSE_PERFORMATIVE,
                "__module__": "http_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.http.v1_0_0.HttpMessage.Response_Performative)
            },
        ),
        "DESCRIPTOR": _HTTPMESSAGE,
        "__module__": "http_pb2"
        # @@protoc_insertion_point(class_scope:aea.fetchai.http.v1_0_0.HttpMessage)
    },
)
_sym_db.RegisterMessage(HttpMessage)
_sym_db.RegisterMessage(HttpMessage.Request_Performative)
_sym_db.RegisterMessage(HttpMessage.Response_Performative)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _HTTPMESSAGE._serialized_start = 40
    _HTTPMESSAGE._serialized_end = 443
    _HTTPMESSAGE_REQUEST_PERFORMATIVE._serialized_start = 213
    _HTTPMESSAGE_REQUEST_PERFORMATIVE._serialized_end = 312
    _HTTPMESSAGE_RESPONSE_PERFORMATIVE._serialized_start = 314
    _HTTPMESSAGE_RESPONSE_PERFORMATIVE._serialized_end = 427
# @@protoc_insertion_point(module_scope)