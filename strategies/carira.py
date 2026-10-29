from edge_sim_py import *
import pandas as pd
from random import seed
import numpy as np
from lab_utils import get_results as get_results
from lab_utils import helper_methods as helper_methods
from lab_utils import get_info

## path
import os
#abspath = os.path.abspath(os.path.join('..'))
abspath = os.getcwd()
algo_name = "carira"
helper_methods.create_default_folders("reports")
helper_methods.create_default_folders("results")

#Paramethers
max_delay = 70
max_cpu = 32
max_memory = 32768

# Sorting applications according to their sla deadline
def my_algorithm(parameters):
    print(f"[STEP {parameters['current_step']}]")

    sla_list = list()

    for app in Application.all():
        # print('>>>>>>>>>>>>>>>>>>>>>>> 1. Scheduling' + str(app))
        # print(app.services)
        user = app.users[0]
        delay = user.delays
        # print(user.making_requests)

        if delay.get(list(delay)[0]) == None:
            d_aux = 0
        else:
            d_aux = delay.get(list(delay)[0])

        sla = user.delay_slas
        s_aux = sla.get(list(sla)[0])

        sla_deadline = s_aux - d_aux

        sla_list.append(sla_deadline)

    dt_sla = pd.DataFrame(sla_list, columns=['sla_deadline']).reset_index().rename(
        columns={'index': 'user'}).sort_values(by='sla_deadline')
    dt_sla['user'] = dt_sla['user'] + 1
    # print(dt_sla)

    # Iterate over every app in sorted list
    for app_id in dt_sla['user']:
        app = Application.find_by_id(app_id)
        services = sorted(app.services, key=lambda s: (-s.privacy_requirement, -s.cpu_demand))

        # print('>>>>>>>>>>>>>>>>>>>>>>> 2. Placement ' + str(app))

        # Iterating over the list of services that compose the application
        for ser in app.services:
            # print('>>>>>>>>>>>>>>>>>>>>>>> 2.1 Placement ' + str(service))

            # print(ser, "being provisioned:", ser.being_provisioned)

            #if not ser.being_provisioned:  # If service needs to be migrated
            if ser.allocated_in_server == -1:


                #edge_servers = sorted(
                #    EdgeServer.all(),
                #    key=lambda s: ((s.cpu - s.cpu_demand) * (s.memory - s.memory_demand) * (
                #                s.disk - s.disk_demand)) ** (1 / 3),
                #    reverse=False,
                #)

                #for ed in EdgeServer.all():
                #    print(helper_methods.min_max_norm(helper_methods.get_delay(app.users[0], ed), 0, max_delay))
                #    print(get_info.get_future_app_availability_score(app, ed.id))

                edge_servers = sorted(
                    EdgeServer.all(),
                    key=lambda s: 0.9 * ( 1 - helper_methods.min_max_norm(helper_methods.get_delay(app.users[0], s), 0,
                                                              max_delay)) + 0.1 * (get_info.get_future_app_availability_score(app, s.id))
                    ,reverse=True
                )

                #for s in edge_servers:
                #    print("DELAY")
                #    print(helper_methods.min_max_norm(helper_methods.get_delay(app.users[0], s), 0, max_delay))
                #    print("AVAILABILITY")
                #    print(get_info.get_future_app_availability_score(app, s.id))

                for edge_server in edge_servers:
                    # Check if the edge server has resources to host the service
                    ser.drop = True
                    if edge_server.has_capacity_to_host(service=ser):
                        # We just need to migrate the service if it's not already in the least occupied edge server
                        ser.drop = False
                        if ser.server != edge_server:
                            # print(f"Migrating {ser} From {ser.server} to {edge_server}")
                            ser.provision(target_server=edge_server)
                            ser.allocated_in_server = edge_server.id
                            # After start migrating the service we can move on to the next service
                            break
                    # else:
                    # print(str(edge_server) + " has no capacity to host " + str(service))
                        # Setting the application as provisioned once all of its services have been provisioned
        if all([service.server != None for service in app.services]):
            app.provisioned = True
    #Report in each step
    #get_info.servers_report("deap", "test_allocation", {parameters['current_step']})
    #get_results.get_results_each_seed(simulator, algo_name, "sce", 1, {parameters['current_step']})


def stopping_criterion(model: object):
    # As EdgeSimPy will halt the simulation whenever this function returns True,
    # its output will be a boolean expression that checks if the current time step is 600
    return model.schedule.steps == 10


def run(steps, scenario_list, seed_list, change_slas, abspath, mu=1, sigma=1):
    # run the experiment many times
    global num_steps
    num_steps = steps
    print(f">>>>>> [{algo_name}] <<<<<<")

    # Simulation execution
    for scenario in scenario_list:
        print(f"====== [SEED {scenario}] ======")

        ## 4 different scenarios that will be executed by 10 different seeds
        for seed_value in seed_list:
            print(f"====== [SEED {seed_value}] ======")
            seed(seed_value)
            # torch.manual_seed(seed_value)
            np.random.seed(seed_value)
            # start the simulation
            simulator = Simulator(
                tick_duration=1,
                tick_unit="seconds",
                stopping_criterion=helper_methods.stopping_criterion_services,
                resource_management_algorithm=my_algorithm,
                logs_directory=f"logs/algorithm={algo_name}/seed={seed_value}/scenario={scenario}",
            )

            # Loading a sample dataset
            ## change the slas
            path = f"{abspath}/datasets/dataset_{scenario}.json"
            change_slas(path, mu, sigma)
            ##Initalize
            simulator.initialize(input_file=f"{abspath}/datasets/dataset_{scenario}.json")

            #Loading customized attributes
            for app in Application.all():
                app.provisioned = False
                # Service
            for s in Service.all():
                s.allocated_in_server = -1

            # Assigning the custom collect methods
            User.collect = helper_methods.user_custom_collect_method

            # Executing the simulation
            simulator.run_model()

            # Results -------------------------------------------------------------------------------------------------------------------------------------
            get_results.get_results(simulator, algo_name, scenario, seed_value)
            get_info.get_all_reports(algo_name, scenario, seed_value)