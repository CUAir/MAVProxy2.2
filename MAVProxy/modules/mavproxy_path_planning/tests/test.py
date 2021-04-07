import os
import sys
import json
import numpy as np
import shapely.geometry as sg
import matplotlib.pyplot as plt

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from algorithms import potential_flow, gradient_based

def run(json_filename):
	with open(json_filename) as json_file:
		data = json.load(json_file)

		start = np.asarray(data["start"])
		end = np.asarray(data["end"])
		obstacles = np.asarray(data["obstacles"])
		geofence = sg.Polygon(np.asarray(data["geofence"]))
		spline_param = data["spline_params"]

		algo_list = []
		for algo_json in data["algorithms"]:
			algo_list.append(init_algo(algo_json, start, end, obstacles, geofence, spline_param))

		path_list = [planner.plan(start, end) for planner in algo_list]
		metric_list = [planner.metric() for planner in algo_list]

		print(metric_list)

		plot_list = [planner.plot() for planner in algo_list]


def init_algo(algo_json, start, end, obstacles, geofence, spline_param):
	algo_dict = {
		1 : potential_flow.PotentialFlow,
		2 : gradient_based.GradientBased
	}

	parameters = algo_json["params"]
	parameters["obstacles"] = obstacles
	parameters["geofence"] = geofence
	parameters["spline_params"] = spline_param

	if "initializer" in parameters.keys():
		parameters["initializer"] = init_algo(parameters["initializer"], start, end, obstacles, geofence, spline_param).plan(start, end)
	
	planner = algo_dict[algo_json["type"]](**parameters)
	return planner


if __name__ == "__main__":
	run("/Users/arpitkalla/Desktop/CUAir/MAVProxy/MAVProxy/modules/mavproxy_path_planning/tests/test.json")