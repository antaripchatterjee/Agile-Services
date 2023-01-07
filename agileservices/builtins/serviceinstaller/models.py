from typing import Optional

from agileservices.servicemanager import ServiceModels
from agileservices.responsemodels import HTTPResponseDataModel
from agileservices.requestmodels import HTTPRequestBodyModel
from agileservices.requestmodels import HTTPRequestQueryModel


class ServiceInstallerResponseModel(HTTPResponseDataModel):
    authentication : bool
    id : int


class ServiceInstallerRequestBody(HTTPRequestBodyModel):
    # token : str
    pass


class ServiceInstallerRequestQueries(HTTPRequestQueryModel):
    id : Optional[int] = 1


class ServiceInstallerModels(ServiceModels):
    ResponseDataModel = ServiceInstallerResponseModel
    RequestBodyModel = ServiceInstallerRequestBody
    RequestQueriesModel = ServiceInstallerRequestQueries