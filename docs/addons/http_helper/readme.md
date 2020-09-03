## HTTP parse 

## Flow 的元素 


```python 
class ReqeustData:
     def __init__(
            self,
            host: str,
            port: int,
            method: bytes,
            scheme: bytes,
            authority: bytes,
            path: bytes,
            http_version: bytes,
            headers: Union[Headers, Tuple[Tuple[bytes, bytes], ...]],
            content: Optional[bytes],
            trailers: Union[None, Headers, Tuple[Tuple[bytes, bytes], ...]],
            timestamp_start: float,
            timestamp_end: Optional[float],
    )
        pass 


class ResponseData:
    def __init__(
            self,
            http_version: bytes,
            status_code: int,
            reason: bytes,
            headers: Union[Headers, Tuple[Tuple[bytes, bytes], ...]],
            content: Optional[bytes],
            trailers: Union[None, Headers, Tuple[Tuple[bytes, bytes], ...]],
            timestamp_start: float,
            timestamp_end: Optional[float],
    ):
        pass 

```