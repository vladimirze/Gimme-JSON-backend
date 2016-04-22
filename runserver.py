import json
import flask
from flask import Response, request
from app import blueprints
from app.resource.model import ResourceModel


def assign(source, destination):
    for k in source.keys():
        destination[k] = source[k]
    return destination

def endpoint_handler_wrapper(response, query_params):
    def endpoint_handler(*args, **kwargs):
        # handle query params
        response_dict = json.loads(response)
        for param in request.args:
            if query_params.has_key(param):
                response_dict = assign(json.loads(query_params[param]), response_dict)
        return Response(response=json.dumps(response_dict), status=200, mimetype='application/json')
    return endpoint_handler

def register_many_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

application = flask.Flask(__name__)
register_many_blueprints(application, blueprints)

# register all resources
resource_model = ResourceModel()
all_resources = resource_model.get_all_resources().original()
for i, res in enumerate(all_resources):
    query_params_as_dict = {}
    for param in res['queryParams']:
        query_params_as_dict[param['param']] = param['response']
    application.add_url_rule(res['endpoint'], 'resource-' + str(i), endpoint_handler_wrapper(res['response'], query_params_as_dict), methods=res['methods'])

if __name__ == '__main__':
    application.run(debug=True)
