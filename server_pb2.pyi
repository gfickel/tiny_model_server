from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmptyArgs(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TextArgs(_message.Message):
    __slots__ = ("text", "model", "args")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    text: str
    model: str
    args: str
    def __init__(self, text: _Optional[str] = ..., model: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...

class ImageArgs(_message.Message):
    __slots__ = ("image", "model", "args")
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    image: NumpyImage
    model: str
    args: str
    def __init__(self, image: _Optional[_Union[NumpyImage, _Mapping]] = ..., model: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...

class BatchTextArgs(_message.Message):
    __slots__ = ("texts", "model", "args")
    TEXTS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    texts: _containers.RepeatedScalarFieldContainer[str]
    model: str
    args: str
    def __init__(self, texts: _Optional[_Iterable[str]] = ..., model: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...

class BatchImageArgs(_message.Message):
    __slots__ = ("images", "model", "args")
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    images: _containers.RepeatedCompositeFieldContainer[NumpyImage]
    model: str
    args: str
    def __init__(self, images: _Optional[_Iterable[_Union[NumpyImage, _Mapping]]] = ..., model: _Optional[str] = ..., args: _Optional[str] = ...) -> None: ...

class NumpyImage(_message.Message):
    __slots__ = ("height", "width", "channels", "data", "dtype")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    channels: int
    data: bytes
    dtype: str
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., channels: _Optional[int] = ..., data: _Optional[bytes] = ..., dtype: _Optional[str] = ...) -> None: ...

class StringArg(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("data", "image")
    DATA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    data: str
    image: NumpyImage
    def __init__(self, data: _Optional[str] = ..., image: _Optional[_Union[NumpyImage, _Mapping]] = ...) -> None: ...

class Shape(_message.Message):
    __slots__ = ("height", "width", "channels")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    channels: int
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., channels: _Optional[int] = ...) -> None: ...
