from flask import Flask, Blueprint
from flask import jsonify, request
from agileservices.servicemanager import ServiceManager
from agileservices.servicemanager import HTTPRequestHeaders

def get_header(header_key : str) -> str:
    return request.headers.get(header_key)

def register_flask_app(app: Flask, pkg: str):
    ServiceManager.install_builtins()
    blueprint = Blueprint('agileservices', __name__)
    HTTPRequestHeaders(get_header=get_header)

    @blueprint.route('/<string:name>/<string:version>/<string:service_method>',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    @blueprint.route('/<string:name>/<string:version>',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def handle_service(name, version, service_method='run'):
        manager = ServiceManager()
        http_method = request.method.upper()
        content_type = request.content_type.lower()
        if content_type != 'application/json':
            return jsonify({'message' : f'Unsupported content-type {content_type}'}), 400
        body = request.get_json(force=True)
        query = request.args.to_dict(flat=True)
        response, status_code = manager.exec_service(
            name, version,
            service_method,
            http_method,
            content_type,
            body=body,
            query=query
        )
        
        return jsonify(response.dict()), status_code
        
    app.register_blueprint(blueprint, url_prefix=f'/{pkg}')
