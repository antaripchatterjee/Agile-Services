from pydantic import BaseModel

class BaseServiceInformation(BaseModel):
    service_name : str
    service_version : str
    service_method : str
    http_method : str

class BaseHTTPResponseModel(BaseModel):
    information : BaseServiceInformation
    
    class Config:
        fields = {'ack' : '_ack'}


class BasicHTTPErroredResponse(BaseHTTPResponseModel):
    ack : bool = False
    detail : str


class HTTPResponseDataModel(BaseModel):
    pass


class BasicHTTPOkayResponse(BaseHTTPResponseModel):
    ack : bool = True
    data : HTTPResponseDataModel

