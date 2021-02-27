import json
import MAVProxy.mavproxy_logging
from MAVProxy.modules.server.urls import app
import MAVProxy.modules.server.views.decorators as decs
from MAVProxy.modules.mavproxy_simcoverage import get_simcoverage_mod

logger = MAVProxy.mavproxy_logging.create_logger("Simulated Coverage")

@app.route('/ground/api/v3/simcoverage', methods=['GET'])
@decs.trace_errors(logger, 'Simulating Coverage')
def get_simulated_coverage():
    get_simcoverage_mod().simulate()
    return json.dumps(True)


