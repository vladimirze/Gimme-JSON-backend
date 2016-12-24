from app.endpoint import api
from flask import Blueprint


blueprint = Blueprint('endpoint', __name__)

blueprint.add_url_rule('/endpoint/', view_func=api.get_list, methods=['GET'])
blueprint.add_url_rule('/endpoint/', view_func=api.create, methods=['POST'])
blueprint.add_url_rule('/endpoint/<string:endpoint_id>/', view_func=api.get, methods=['GET'])
blueprint.add_url_rule('/endpoint/<string:endpoint_id>/', view_func=api.delete, methods=['DELETE'])
blueprint.add_url_rule('/endpoint/<string:endpoint_id>/', view_func=api.partial_update, methods=['PATCH'])
blueprint.add_url_rule('/endpoint/<string:endpoint_id>/', view_func=api.save, methods=['PUT'])
