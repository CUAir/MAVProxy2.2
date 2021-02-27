import json

import MAVProxy.mavproxy_logging
import MAVProxy.modules.server.views.decorators as decs
from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data
from MAVProxy.modules.mavproxy_param import get_param_mod
import MAVProxy.modules.server.views.schemas as schemas


logger = MAVProxy.mavproxy_logging.create_logger("Parameters")


@app.route('/ground/api/v3/params')
@decs.trace_errors(logger, 'Failed to get parameter data')
def get_params():
    return json.dumps(Data.params)


@app.route('/ground/api/v3/params/max')
@decs.trace_errors(logger, 'Failed to get param max')
def get_params_max():
    return str(Data.max_param_num)


# USAGE: Post JSON  {'pname': parameter_name, 'value': value}
# See schemas.py for full details.
@app.route('/ground/api/v3/params', methods=['POST'])
@decs.trace_errors(logger, 'update_param failed')
@decs.require_headers({'token': Data.password})
@decs.validate_json(logger, schemas.parameters)
def update_param(parameter):
    if not parameter['pname'].upper() in get_param_mod().mav_param:
        return "Unable to find parameter {0}".format(parameter['pname']), 400

    get_param_mod().set_param(str(parameter['pname']), str(parameter['value']))
    return "Successfully changed parameter: {}".format(parameter['pname']), 200
