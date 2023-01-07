import abc
import importlib
from functools import wraps
from typing import Optional
from pydantic import BaseModel

from .builtins import allow_install

from .requestmodels import HTTPRequestHeaders
from .requestmodels import HTTPRequestDataModel
from .requestmodels import HTTPRequestBodyModel
from .requestmodels import HTTPRequestQueryModel

from .responsemodels import HTTPResponseDataModel
from .responsemodels import BasicHTTPOkayResponse
from .responsemodels import BasicHTTPErroredResponse
from .responsemodels import BaseServiceInformation

from .exceptionmanager import WrongStatusCodeByServiceError
from .exceptionmanager import WrongResponseModelByServiceError


class ServiceInstallRecord(BaseModel):
    ack : bool
    service : str
    version : str
    message : str

class ServiceRequestInfo(BaseServiceInformation):
    content_type : Optional[str]

    def getabstractinfo(self):
        return BaseServiceInformation(**self.dict())


class Service(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def run(cls, *, info: BaseServiceInformation, req : HTTPRequestDataModel):
        pass


class ServiceModels:
    ResponseDataModel = HTTPResponseDataModel
    RequestBodyModel = HTTPRequestBodyModel
    RequestQueriesModel = HTTPRequestQueryModel

class ServiceManager(object):
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(ServiceManager, cls).__new__(cls)
            cls.__instance.__services__ = dict()
            cls.__instance.__builtins_responses__ = []
        return cls.__instance

    @classmethod
    def install_builtins(cls):
        base_module_name = f'agileservices.builtins'
        manager = cls()
        for service_name, service_version in allow_install.fget().items():
            status_code, msg = manager.install_service(
                base_module_name, service_name, service_version
            )
            manager.__builtins_responses__.append(
                ServiceInstallRecord(
                    ack=status_code==200,
                    service=service_name,
                    version=service_version,
                    message=msg
                )
            )

    def is_installed(self, service_name, service_version):
        return f'{service_name}/{service_version}' in self.__services__.keys()

    def install_service(self, pkg, service_name, service_version):
        if self.is_installed(service_name, service_version):
            return 403, 'Service is already installed'
        try:
            module_name = f'{pkg}.{service_name}.versions'
            module = importlib.import_module(module_name)
            service = module.Version.get_service(service_version)
            self.add_service(service_name, service_version, service)
            return 200, 'Installed successfully'
        except ImportError as e:
            return 400, f'{type(e).__name__} : {e}'
        except NotImplementedError as e:
            return 501, f'{type(e).__name__} : {e}'
        # except AttributeError as e:
        #     return 417, f'{type(e).__name__} : {e}'

    def add_service(self, service_name, service_version, service):
        service_id = f'{service_name}/{service_version}'
        if service_id not in self.__services__.keys():
            self.__services__[service_id] = service

    def exec_service(self, service_name, service_version, service_method, http_method, content_type, *, query, body):
        info = ServiceRequestInfo(
            http_method=http_method,
            service_version=service_version,
            service_name=service_name,
            service_method=service_method,
            content_type=content_type
        )
        if not self.is_installed(service_name, service_version):
            return BasicHTTPErroredResponse(
                information=info,
                detail='Could not find the service'
            ), 400
        service_id = f'{service_name}/{service_version}'
        service = self.__services__.get(service_id)
        try:
            if service is None:
                raise AttributeError()
            method = getattr(service, service_method)
        except AttributeError:
            return BasicHTTPErroredResponse(
                information=info,
                detail='Failed to call the service method'
            ), 404
        try:
            response, status_code = method(info=info, req={
                'body' : body,
                'query' : query,
                'header_o' : HTTPRequestHeaders()
            })

            success_status_codes = (*range(200, 209), 226)
            if status_code in success_status_codes:
                if not isinstance(response, BasicHTTPOkayResponse):
                    raise WrongStatusCodeByServiceError(
                        f'Invalid status code {status_code}, returned response is error type'
                    )
            elif not isinstance(response, BasicHTTPErroredResponse):
                raise WrongResponseModelByServiceError(
                    f'Invalid status code {status_code}, returned response should be error type'
                )
            return response, status_code
        except Exception as e:
            return BasicHTTPErroredResponse(
                information=info.getabstractinfo(),
                detail=f'Fatal: {type(e).__name__} occurred. More: {e}'
            ), 500

