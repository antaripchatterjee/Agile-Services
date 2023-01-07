from typing import Set, Dict
from typing import Optional, Callable
from pydantic import BaseModel

class HTTPRequestBodyModel(BaseModel):
    pass

class HTTPRequestQueryModel(BaseModel):
    pass

class HTTPRequiredHeader(BaseModel):
    header_key : str
    error_code : int = 400
    def __hash__(self):
        return hash(self.header_key)
    def __eq__(self, other):
        if isinstance(other, HTTPRequiredHeader):
            return self.header_key == other.header_key
        return False
    
class HTTPRequiredHeaders(BaseModel):
    headers : Set[HTTPRequiredHeader]

    def iter_items(self):
        for header in self.headers:
            yield header.header_key, header.error_code

class HTTPRequestDataModel(BaseModel):
    body: HTTPRequestBodyModel
    query : HTTPRequestQueryModel
    headers : Dict[str, str]

class HTTPRequestHeaders(object):
    __instance = None
    def __new__(cls, get_header : Optional[Callable[[str], str]] = None):
        if cls.__instance is None:
            cls.__instance = super(HTTPRequestHeaders, cls).__new__(cls)
            cls.__instance.__get_header__ = get_header
        return cls.__instance
    def __call__(self, header_key : str) -> str:
        return self.__get_header__(header_key)
    