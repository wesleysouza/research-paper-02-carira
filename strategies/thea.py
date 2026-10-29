# Packages, seed and path
## packages
from edge_sim_py import *
import json
import numpy as np
from random import seed
from lab_utils import get_results as get_results
from lab_utils import helper_methods as helper_methods
from lab_utils import get_info

## path
import os
#abspath = os.path.abspath(os.path.join('..'))
abspath = os.getcwd()
algo_name = "thea"
scenario_name = "in-depth_analysis"
helper_methods.create_default_folders("reports")
helper_methods.create_default_folders("results")


# change the slas
def change_slas(path, mu, sigma):
    # Opening JSON file
    f = open(path)

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    # sla values from probabilistic distribution
    n = len(data['User'])
    sla_values = np.around(np.random.normal(mu, sigma, n), decimals=0)
    # list
    for i in range(len(data['User'])):
        print('>>> user', i, "<<<")
        print('before:', data['User'][i].get('attributes').get('delay_slas'))
        data['User'][i].get('attributes').get('delay_slas').update({str(i + 1): sla_values[i]})
        print('after:', data['User'][i].get('attributes').get('delay_slas'))

    # Closing file
    f.close()

    # Serializing json
    json_object = json.dumps(data, indent=4)

    # Writing to sample.json
    with open(path, "w") as outfile:
        outfile.write(json_object)


# change the network delays
def change_network(path, link_delay, wireless_delay):
    # Opening JSON file
    f = open(path)

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json - networklink
    for i in range(len(data['NetworkLink'])):
        print('>>> network link', i, "<<<")
        print('before:', data['NetworkLink'][i].get('attributes').get('delay'))
        data['NetworkLink'][i].get('attributes').update({'delay': link_delay})
        print('after:', data['NetworkLink'][i].get('attributes').get('delay'))

    # Iterating through the json - wireless
    for i in range(len(data['BaseStation'])):
        print('>>> base station', i, "<<<")
        print('before:', data['BaseStation'][i].get('attributes').get('wireless_delay'))
        data['BaseStation'][i].get('attributes').update({'wireless_delay': wireless_delay})
        print('after:', data['BaseStation'][i].get('attributes').get('wireless_delay'))
    # Closing file
    f.close()

    # Serializing json
    json_object = json.dumps(data, indent=4)

    # Writing to sample.json
    with open(path, "w") as outfile:
        outfile.write(json_object)


# Custom collect method to measure users
def user_custom_collect_method(self) -> dict:
    # Python libraries
    import copy
    """Method that collects a set of metrics for the object.

    Returns:
        metrics (dict): Object metrics.
    """
    access_history = {}
    for app in self.applications:
        access_history[str(app.id)] = self.access_patterns[str(app.id)].history

    try:
        delay_sla_deadlines = self.delay_slas.get(str(self.id)) - self.delays.get(str(self.id))
    except:
         delay_sla_deadlines = None

    metrics = {
        "Instance ID": self.id,
        "Coordinates": self.coordinates,
        "Base Station": f"{self.base_station} ({self.base_station.coordinates})" if self.base_station else None,
        "Delays": self.delays.get(str(self.id)), #copy.deepcopy(self.delays),
        "Delay slas": self.delay_slas.get(str(self.id)),#copy.deepcopy(self.delay_slas),
        "Delay sla deadlines": delay_sla_deadlines,
        "Communication Paths": copy.deepcopy(self.communication_paths),
        "Making Requests": copy.deepcopy(self.making_requests),
        "Access History": copy.deepcopy(access_history)
    }
    return metrics


# Functions

def get_application_delay_score(app: object) -> float:
    """Calculates the application delay score considering the number application's SLA and the number of edge servers close enough
    to the application's user that could be used to host the application's services without violating the delay SLA.

    Args:
        app (object): Application whose delay score will be calculated.

    Returns:
        app_delay_score (float): Application's delay score.
    """
    # Gathering information about the application
    delay_sla = app.users[0].delay_slas[str(app.id)]
    user_switch = app.users[0].base_station.network_switch

    # Gathering the list of hosts close enough to the user that could be used to host the services without violating the delay SLA
    edge_servers_that_dont_violate_delay_sla = 0
    for edge_server in EdgeServer.all():
        topology = user_switch.model.topology
        path = find_shortest_path(origin_network_switch=user_switch, target_network_switch=edge_server.network_switch)
        delay = topology.calculate_path_delay(path=path)
        if delay <= delay_sla:
            edge_servers_that_dont_violate_delay_sla += 1

    if edge_servers_that_dont_violate_delay_sla == 0:
        app_delay_score = 0
    else:
        app_delay_score = 1 / ((edge_servers_that_dont_violate_delay_sla * delay_sla) ** (1 / 2))

    app_delay_score = app_delay_score * len(app.services)

    return app_delay_score


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


def normalize_cpu_and_memory(cpu, memory) -> float:
    """Normalizes the CPU and memory values.

    Args:
        cpu (float): CPU value.
        memory (float): Memory value.

    Returns:
        normalized_value (float): Normalized value.
    """
    normalized_value = (cpu * memory) ** (1 / 2)
    return normalized_value


def find_minimum_and_maximum(metadata: list):
    """Finds the minimum and maximum values of a list of dictionaries.

    Args:
        metadata (list): List of dictionaries that contains the analyzed metadata.

    Returns:
        min_and_max (dict): Dictionary that contains the minimum and maximum values of the attributes.
    """
    min_and_max = {
        "minimum": {},
        "maximum": {},
    }

    for metadata_item in metadata:
        for attr_name, attr_value in metadata_item.items():
            if attr_name != "object":
                # Updating the attribute's minimum value
                if (
                        attr_name not in min_and_max["minimum"]
                        or attr_name in min_and_max["minimum"]
                        and attr_value < min_and_max["minimum"][attr_name]
                ):
                    min_and_max["minimum"][attr_name] = attr_value

                # Updating the attribute's maximum value
                if (
                        attr_name not in min_and_max["maximum"]
                        or attr_name in min_and_max["maximum"]
                        and attr_value > min_and_max["maximum"][attr_name]
                ):
                    min_and_max["maximum"][attr_name] = attr_value

    return min_and_max


def min_max_norm(x, min, max):
    """Normalizes a given value (x) using the Min-Max Normalization method.

    Args:
        x (any): Value that must be normalized.
        min (any): Minimum value known.
        max (any): Maximum value known.

    Returns:
        (any): Normalized value.
    """
    if min == max:
        return 1
    return (x - min) / (max - min)


def get_norm(metadata: dict, attr_name: str, min: dict, max: dict) -> float:
    """Wrapper to normalize a value using the Min-Max Normalization method.

    Args:
        metadata (dict): Dictionary that contains the metadata of the object whose values are being normalized.
        attr_name (str): Name of the attribute that must be normalized.
        min (dict): Dictionary that contains the minimum values of the attributes.
        max (dict): Dictionary that contains the maximum values of the attributes.

    Returns:
        normalized_value (float): Normalized value.
    """
    normalized_value = min_max_norm(x=metadata[attr_name], min=min[attr_name], max=max[attr_name])
    return normalized_value


def calculate_path_delay(origin_network_switch: object, target_network_switch: object) -> int:
    """Gets the distance (in terms of delay) between two network switches (origin and target).

    Args:
        origin_network_switch (object): Origin network switch.
        target_network_switch (object): Target network switch.

    Returns:
        delay (int): Delay between the origin and target network switches.
    """
    topology = origin_network_switch.model.topology

    path = find_shortest_path(origin_network_switch=origin_network_switch, target_network_switch=target_network_switch)
    # print(path)
    delay = topology.calculate_path_delay(path=path)

    return delay


def sign(value: int):
    """Calculates the sign of a real number using the well-known "sign" function (https://wikipedia.org/wiki/Sign_function).

    Args:
        value (int): Value whose sign must be calculated.

    Returns:
        (int): Sign of the passed value.
    """
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def get_application_privacy_score(app: object):
    """Calculates the application privacy score considering the demand and privacy requirements of its services.

    Args:
        app (object): Application whose privacy score will be calculated.

    Returns:
        app_privacy_score (float): Application's privacy score.
    """
    app_privacy_score = 0

    for service in app.services:
        normalized_demand = normalize_cpu_and_memory(cpu=service.cpu_demand, memory=service.memory_demand)
        privacy_requirement = service.privacy_requirement
        service_privacy_score = normalized_demand * (1 + privacy_requirement)
        app_privacy_score += service_privacy_score

    return app_privacy_score


def get_host_candidates(user: object, service: object) -> list:
    """Get list of host candidates for hosting services of a given user.
    Args:
        user (object): User object.
    Returns:
        host_candidates (list): List of host candidates.
    """
    chain = list([service.application.users[0]] + [service])
    prev_item = chain[chain.index(service) - 1]
    switch_of_previous_item_in_chain = (
        prev_item.base_station.network_switch if chain.index(service) - 1 == 0 else prev_item.server.network_switch
    )
    app_delay = user.delays[str(service.application.id)] if user.delays[str(service.application.id)] is not None else 0

    host_candidates = []

    for edge_server in EdgeServer.all():
        additional_delay = calculate_path_delay(
            origin_network_switch=switch_of_previous_item_in_chain, target_network_switch=edge_server.network_switch
        )
        overall_delay = app_delay + additional_delay
        delay_cost = additional_delay if service == service.application.services[-1] else 0

        # Checking if any of the SLAs (delay or privacy) would be violated by hosting the service on the edge server
        violates_privacy_sla = 1 if user.providers_trust[
                                        str(edge_server.infrastructure_provider)] < service.privacy_requirement else 0
        violates_delay_sla = 1 if overall_delay > user.delay_slas[str(service.application.id)] else 0
        sla_violations = violates_delay_sla + violates_privacy_sla

        # Gathering the edge server's power consumption cost based on its CPU usage
        static_power_consumption = edge_server.power_model_parameters["static_power_percentage"]
        consumption_per_core = edge_server.power_model_parameters["max_power_consumption"] / edge_server.cpu
        power_consumption = consumption_per_core + static_power_consumption * (1 - sign(edge_server.cpu_demand))

        # Gathering the list of non-provisioned services that could possibly rely on the edge server regarding its trust degree
        affected_services = []
        for affected_service in Service.all():
            affected_user = affected_service.application.users[0]
            trust_on_the_edge_server = affected_user.providers_trust[str(edge_server.infrastructure_provider)]
            relies_on_the_edge_server = trust_on_the_edge_server >= affected_service.privacy_requirement

            if affected_service.server is None and affected_service != service and relies_on_the_edge_server:
                distance_to_affected_user = calculate_path_delay(
                    origin_network_switch=affected_user.base_station.network_switch,
                    target_network_switch=edge_server.network_switch
                )
                distance_cost = 1 / max(1, distance_to_affected_user)
                affected_services.append(distance_cost)

        affected_services_cost = sum(affected_services) if service == service.application.services[-1] else 0

        host_candidates.append(
            {
                "object": edge_server,
                "sla_violations": sla_violations,
                "affected_services_cost": affected_services_cost,
                "power_consumption": power_consumption,
                "delay_cost": delay_cost,
            }
        )

    return host_candidates


# algorithm
def my_algorithm(parameters: dict = {}):
    print(f"[STEP {parameters['current_step']}]")
    """Heuristic algorithm that provisions composite applications on federated edge infrastructures taking into account the delay
    and privacy requirements of applications, the trust degree between application users and infrastructure providers, and the
    power consumption of edge servers.

    Args:
        parameters (dict, optional): Algorithm parameters. Defaults to {}.
    """
    # Sorting applications according to their delay and privacy scores
    apps_metadata = []
    # for app in [app for app in Application.all() if not app.provisioned]:
    for app in Application.all():
        app_attrs = {
            "object": app,
            "number_of_services": len(app.services),
            "delay_sla": app.users[0].delay_slas[str(app.id)],
            "delay_score": get_application_delay_score(app=app),
            "privacy_score": get_application_privacy_score(app=app),
        }
        apps_metadata.append(app_attrs)

    # Gathering the application with the highest delay and privacy score to be provisioned
    min_and_max = find_minimum_and_maximum(metadata=apps_metadata)
    apps_metadata = sorted(
        apps_metadata,
        key=lambda app: (
                get_norm(metadata=app, attr_name="delay_score", min=min_and_max["minimum"], max=min_and_max["maximum"])
                + get_norm(metadata=app, attr_name="privacy_score", min=min_and_max["minimum"],
                           max=min_and_max["maximum"])
        ),
        reverse=True,
    )

    # Iterating over the sorted list of applications to provision their services
    for app_metadata in apps_metadata:
        app = app_metadata["object"]
        user = app.users[0]

        # Iterating over the list of services that compose the application
        for service in app.services:

            #print(service, "being provisioned:", service.being_provisioned)

            if service.being_provisioned:
                service.drop = True

            # if not ser.being_provisioned: #If service needs to be migrated
            if not service.drop:

                # Gathering the list of edge servers candidates for hosting the service
                edge_servers = get_host_candidates(user=user, service=service)

                # Finding the minimum and maximum values for the edge server attributes
                min_and_max = find_minimum_and_maximum(metadata=edge_servers)

                # Sorting edge server host candidates based on the number of SLA violations they
                # would cause to the application and their power consumption and delay costs
                edge_servers = sorted(
                    edge_servers,
                    key=lambda s: (
                        s["sla_violations"],
                        get_norm(metadata=s, attr_name="affected_services_cost", min=min_and_max["minimum"],
                                 max=min_and_max["maximum"])
                        + get_norm(metadata=s, attr_name="power_consumption", min=min_and_max["minimum"],
                                   max=min_and_max["maximum"])
                        + get_norm(metadata=s, attr_name="delay_cost", min=min_and_max["minimum"],
                                   max=min_and_max["maximum"]),
                    ),
                )

                for edge_server_metadata in edge_servers:
                    edge_server = edge_server_metadata["object"]
                    # Check if the edge server has resources to host the service
                    if edge_server.has_capacity_to_host(service=service):
                        # We just need to migrate the service if it's not already in the least occupied edge server
                        if service.server == None:

                            # print(f"Migrating {service} From {service.server} to {edge_server}")
                            #print(f"Placement: {service} From {service.server} to {edge_server}")
                            service.provision(target_server=edge_server)
                            service.allocated_in_server = edge_server.id
                            print("APP: " + str(service.application))
                            # After start migrating the service we can move on to the next service
                            break
                        #else:
                        #    print(f"Placement is done: {service} is at {service.server}")

            # # Greedily iterating over the list of edge servers to find a host for the service
            # for edge_server_metadata in edge_servers:
            #     print(edge_server_metadata)
            #     edge_server = edge_server_metadata["object"]

            #     # Provisioning the service on the best edge server found it it has enough resources
            #     if edge_server.has_capacity_to_host(service):
            #         print(f"Migrating {service} From {service.server} to {edge_server}")
            #         service.provision(target_server=edge_server)
            #         break

        # Setting the application as provisioned once all of its services have been provisioned
        # if all([service.server != None for service in app.services]):
        #     app.provisioned = True
        # else:
        #     #print(f"{app} could not be provisioned.")
        #     raise Exception(f"{app} could not be provisioned.")

    # show_metrics()
    # print(f"[STEP {parameters['current_step']}]")


def stopping_criterion_services(model: object):
    # Defining a variable that will help us to count the number of services successfully provisioned within the infrastructure
    provisioned_services = 0

    # Iterating over the list of services to count the number of services provisioned within the infrastructure
    for service in Service.all():

        # Initially, services are not hosted by any server (i.e., their "server" attribute is None).
        # Once that value changes, we know that it has been successfully provisioned inside an edge server.
        if service.server != None:
            provisioned_services += 1

    # As EdgeSimPy will halt the simulation whenever this function returns True, its output will be a boolean expression
    # that checks if the number of provisioned services equals to the number of services spawned in our simulation
    stop = False
    if (provisioned_services == Service.count()) | (model.schedule.steps == 60):
        stop = True
    return stop


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