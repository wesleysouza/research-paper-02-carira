from edge_sim_py import *

from random import seed
import numpy as np
from lab_utils import get_results as get_results
from lab_utils import helper_methods as helper_methods
from lab_utils import get_info

algo_name = "argos"

def my_algorithm(parameters: dict = {}):
    """Privacy-aware service provisioning strategy for edge computing environments proposed in [1].

    [1] Souza, P.; Crestani, Â.; Rubin, F.; Ferreto, T. and Rossi, F. (2022). Latency-aware Privacy-preserving
    Service Migration in Federated Edges. In International Conference on Cloud Computing and Services Science (CLOSER),
    pages 288-295. DOI: 10.5220/0011084500003200.

    Args:
        parameters (dict, optional): Algorithm parameters. Defaults to {}.
    """

    print(f"[STEP {parameters['current_step']}]")

    apps = sorted(Application.all(), key=lambda app: app.users[0].delay_slas[str(app.id)])

    for app in apps:
        user = app.users[0]
        services = sorted(app.services, key=lambda s: (-s.privacy_requirement, -s.cpu_demand))

        # FUNCTION: get_host_candidates(user=user)
        user_switch = user.base_station.network_switch
        host_candidates = []
        for edge_server in EdgeServer.all():
            topology = user_switch.model.topology
            path = find_shortest_path(origin_network_switch=user_switch,
                                      target_network_switch=edge_server.network_switch)
            delay = topology.calculate_path_delay(path=path)

            host_candidates.append(
                {
                    "object": edge_server,
                    "delay": delay,
                    "trust_degree": user.providers_trust[str(edge_server.infrastructure_provider)],
                }
            )

        edge_servers = sorted(host_candidates, key=lambda s: (-s["trust_degree"], s["delay"]))

        for service in services:
            # Greedily iterating over the list of edge servers to find a host for the service
            for edge_server_metadata in edge_servers:
                edge_server = edge_server_metadata["object"]
                # Check if the edge server has resources to host the service
                if edge_server.has_capacity_to_host(service=service):
                    # We just need to migrate the service if it's not already in the least occupied edge server
                    service.drop = False
                    if service.server != edge_server:
                        # print(f"Migrating {service} From {service.server} to {edge_server}")
                        service.provision(target_server=edge_server)
                        service.allocated_in_server = edge_server.id

                        # After start migrating the service we can move on to the next service
                        break


def find_shortest_path(origin_network_switch: object, target_network_switch: object) -> int:
    import networkx as nx

    """Finds the shortest path (delay used as weight) between two network switches (origin and target).

    Args:
        origin_network_switch (object): Origin network switch.
        target_network_switch (object): Target network switch.

    Returns:
        path (list): Shortest path between the origin and target network switches.
    """
    topology = origin_network_switch.model.topology
    path = []

    if not hasattr(topology, "delay_shortest_paths"):
        topology.delay_shortest_paths = {}

    key = (origin_network_switch, target_network_switch)

    if key in topology.delay_shortest_paths.keys():
        path = topology.delay_shortest_paths[key]
    else:
        path = nx.shortest_path(G=topology, source=origin_network_switch, target=target_network_switch, weight="delay")
        topology.delay_shortest_paths[key] = path

    return path


def stopping_criterion(model: object):
    # As EdgeSimPy will halt the simulation whenever this function returns True,
    return model.schedule.steps == num_steps


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