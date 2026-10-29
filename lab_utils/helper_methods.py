import os
import json
import numpy as np
from edge_sim_py import Service
from lab_utils import get_info


def create_default_folders(folder_name):
    os.makedirs(f"{folder_name}", exist_ok=True)


def get_experiment_definitions(scenario_name, abspath):
    f = open(f"{abspath}/experiment_definitions.json")
    data = json.load(f)
    definitions = data[scenario_name]
    f.close()
    return definitions


# Custom collect method to measure users
def user_custom_collect_method(self) -> dict:
    # Python libraries
    import copy
    """Method that collects a set of metrics for the object.

    Returns:
        metrics (dict): Object metrics.
    """
    access_history = {}
    availability_score = 0
    for app in self.applications:
        access_history[str(app.id)] = self.access_patterns[str(app.id)].history
        availability_score = get_info.app_availability_score(app)

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
        "Access History": copy.deepcopy(access_history),
        "Availability Score": copy.deepcopy(availability_score),
    }
    return metrics


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


def change_slas_static(path, mu=1, sigma=1):
    # Opening JSON file
    f = open(path)

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    n = len(data['User'])
    sla_values = [22.5, 22.5, 35, 35, 47.5, 22.5, 22.5, 35, 35, 47.5]
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


def change_slas_random(path, mu, sigma):
    # Opening JSON file
    f = open(path)

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    # sla values from probabilistic distribution
    n = len(data['User'])
    sla_values = [20, 35, 50]

    np.random.shuffle(sla_values)

    # list
    for i in range(len(data['User'])):
        print('>>> user', i, "<<<")
        print('before:', data['User'][i].get('attributes').get('delay_slas'))
        data['User'][i].get('attributes').get('delay_slas').update({str(i + 1): sla_values[0]})
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
    if (provisioned_services == Service.count() + 1 ) | (model.schedule.steps == 10):
        stop = True
    return stop


def stopping_criterion_steps(model: object):
    # As EdgeSimPy will halt the simulation whenever this function returns True,
    # its output will be a boolean expression that checks if the current time step is 'n'
    n = 60
    return model.schedule.steps == n


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


def get_delay(user, edge_server):
    user_switch = user.base_station.network_switch
    topology = user_switch.model.topology
    path = find_shortest_path(origin_network_switch=user_switch, target_network_switch=edge_server.network_switch)
    delay = topology.calculate_path_delay(path=path)
    return delay


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