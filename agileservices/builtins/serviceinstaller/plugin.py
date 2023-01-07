from collections import OrderedDict

from agileservices.helper import validate_request
from agileservices.helper import RequestValidationProps
from agileservices.servicemanager import Service
from agileservices.servicemanager import BaseServiceInformation
from agileservices.servicemanager import HTTPRequestDataModel
from agileservices.requestmodels import HTTPRequiredHeader
from agileservices.requestmodels import HTTPRequiredHeaders
from agileservices.exceptionmanager import HTTPRequestError

from .models import ServiceInstallerModels

fake_db = OrderedDict([
    (1, 'nI7pW5ZhxAGi9M11mCrtYDG5cuscAKUJZLaD4xT541Q')
])

required_headers = HTTPRequiredHeaders(
    headers={
        HTTPRequiredHeader(
            header_key='X-Service-Token',
            error_code=401
        )
    }
)
reqValProps = RequestValidationProps(
    methods=['POST'],
    required_headers=required_headers,
    models=ServiceInstallerModels
)

middlewares = []


class ServiceInstaller(Service):
    @classmethod
    @validate_request(reqValProps=reqValProps)
    def run(cls, *, info : BaseServiceInformation, req: HTTPRequestDataModel):
        try:
            assert fake_db[req.query.id] == req.headers.get('X-Service-Token')
            return dict(
                authentication=True, id=req.query.id
            )
        except AssertionError:
            raise HTTPRequestError(status_code=401, message='Invalid token')

