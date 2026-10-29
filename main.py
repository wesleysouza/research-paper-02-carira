import os
from lab_utils import helper_methods
from strategies import argos
from strategies import bfs
from strategies import thea
from strategies import carira

scenario_name = "in-depth_analysis"
steps = 10

abspath = os.getcwd()
helper_methods.create_default_folders("reports")
helper_methods.create_default_folders("results")

##LOAD SCENARIOS DEFINITIONS
dict_definitions = helper_methods.get_experiment_definitions(scenario_name, abspath)
scenario_list = dict_definitions['datasets']
seed_list = dict_definitions['seeds']

argos.run(steps, scenario_list, seed_list, helper_methods.change_slas_static, abspath)
bfs.run(steps, scenario_list, seed_list, helper_methods.change_slas_static, abspath)
thea.run(steps, scenario_list, seed_list, helper_methods.change_slas_static, abspath)
carira.run(steps, scenario_list, seed_list, helper_methods.change_slas_static, abspath)

