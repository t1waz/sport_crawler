from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class WebsiteFetchRequest(_message.Message):
    __slots__ = ["id", "url"]
    ID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    url: str
    def __init__(self, id: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class WebsiteFetchResponse(_message.Message):
    __slots__ = ["id", "content"]
    ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    id: str
    content: bytes
    def __init__(
        self, id: _Optional[str] = ..., content: _Optional[bytes] = ...
    ) -> None: ...
