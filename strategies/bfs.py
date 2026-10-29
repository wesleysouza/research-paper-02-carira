from edge_sim_py import *
from random import seed
import numpy as np
from lab_utils import get_results as get_results
from lab_utils import helper_methods as helper_methods
from lab_utils import get_info

algo_name = "bfs"

def my_algorithm(parameters):
    """Adapted version of [1], that focuses on finding host servers for microservice-based applications on
    Edge Computing scenarios with multiple infrastructure providers. This heuristic was originally designed to define
    service's deployment (i.e., initial placement). The code below is an adapted version that uses the heuristic's
    original reasoning to perform service migration when it detects application's SLA are violated.

    References:
        [1] Faticanti, Francescomaria, et al. "Deployment of Application Microservices in Multi-Domain Federated
        Fog Environments." International Conference on Omni-layer Intelligent Systems (COINS). IEEE, 2020.
    """

    # Based on Faticanti's idea, we sort services based on their positions in their application's service chain and
    # according to their applications's network demand (services from applications with lower demand come first).
    services = sorted(
        Service.all(),
        key=lambda service: (service.application.services.index(service), service.application.network_demand),
    )

    for service in services:
        # Faticanti's heuristic was originally designed to define initial service placement. As we perform migrations
        # based on users mobility_model, we modify the heuristic to just relocate services when their application's SLA is
        # violated so that the heuristic avoids performing unnecessary migrations. Without such modification, the
        # heuristic would try to migrate services in all time steps, which would lead to poor results in our scenario.

        # Sorting edge servers by: trustworthiness, distance from user (in terms of delay), and free resources.
        edge_servers = sorted(
            EdgeServer.all(),
            key=lambda s: (
                helper_methods.get_delay(service.application.users[0], s),
                s.cpu - s.cpu_demand, s.memory - s.memory_demand,
            ),
         )

        # Greedily iterating over the list of EdgeNode
        # candidates to find the best node to host the service
        for edge_server in edge_servers:
            if service.server == edge_server:
                break

            elif edge_server.has_capacity_to_host(service):
                #service.migrate(target_server=edge_server)
                service.provision(target_server=edge_server)
                service.allocated_in_server = edge_server.id
                #user.set_communication_path(app=app)
                break

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
                stopping_criterion=stopping_criterion,
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