from fnmatch import fnmatch
from functools import wraps
from collections.abc import Mapping
from typing import List, Optional, Type
from pydantic import ValidationError, BaseModel

from .servicemanager import ServiceModels
from .servicemanager import ServiceRequestInfo
from .servicemanager import HTTPRequestDataModel

from .requestmodels import HTTPRequiredHeaders

from .responsemodels import BasicHTTPOkayResponse
from .responsemodels import BasicHTTPErroredResponse

from .exceptionmanager import WrongResponseModelByServiceError
from .exceptionmanager import HTTPRequestError

class RequestValidationProps(BaseModel):
    methods: List[str]
    required_headers: Optional[HTTPRequiredHeaders] = None
    models : Type[ServiceModels] = ServiceModels
    accept_only : str = 'application/json'

def validate_request(*, reqValProps: RequestValidationProps):
    _required_headers = reqValProps.required_headers or HTTPRequiredHeaders(headers=set())
    def wrapper(fn):
        @wraps(fn)
        def inner(cls, *, info: ServiceRequestInfo, req: HTTPRequestDataModel):
            def raise_header_error(hkey, code):
                raise HTTPRequestError(
                    status_code=code,
                    message=f"Missing required header '{hkey}'"
                )
            if info.http_method in reqValProps.methods:
                if info.content_type and fnmatch(info.content_type, reqValProps.accept_only):
                    try:
                        header_o = req.pop('header_o')
                        headers = {
                            hkey : header_o(hkey) or raise_header_error(hkey, code) \
                                for hkey, code in _required_headers.iter_items()
                        }
                        req = HTTPRequestDataModel(
                            body = reqValProps.models.RequestBodyModel(
                                **req.get('body')
                            ),
                            query = reqValProps.models.RequestQueriesModel(
                                **req.get('query')
                            ),
                            headers=headers
                        )
                        _data, status_code = (*[fn(cls, info=info.getabstractinfo(), req=req)], 200)[:2]
                        if isinstance(_data, Mapping):
                            data = reqValProps.models.ResponseDataModel(**_data)
                        else:
                            data = _data
                        if not isinstance(data, reqValProps.models.ResponseDataModel):
                            raise WrongResponseModelByServiceError(
                                f'Invalid status code {status_code}, returned response is error type'
                            )
                        response = BasicHTTPOkayResponse(
                            information=info.getabstractinfo(),
                            data=data
                        )
                    except ValidationError as e:
                        status_code = 422
                        response = BasicHTTPErroredResponse(
                            information=info.getabstractinfo(),
                            detail=f'{type(e).__name__} : {e}'
                        )
                    except HTTPRequestError as e:
                        status_code = e.status_code
                        response = BasicHTTPErroredResponse(
                            information=info.getabstractinfo(),
                            detail=e.message
                        )
                else:
                    status_code = 415
                    response = BasicHTTPErroredResponse(
                        information=info.getabstractinfo(),
                        detail=f'Unsupported content-type `{info.content_type}`'
                    )
            else:
                status_code = 405 
                response = BasicHTTPErroredResponse(
                    information=info.getabstractinfo(),
                    detail=f'HTTP {info.http_method} is not allowed'
                )
            return response, status_code
        return inner
    return wrapper