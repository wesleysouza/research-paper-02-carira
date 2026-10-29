import pandas as pd
from edge_sim_py import EdgeServer, Application, Service, User, BaseStation


def get_app_service_ids(app):
    list_services = []
    for ser in app.services:
        list_services.append(ser.id)
    return list_services

"""
Return provisioned services of App
"""
def get_app_provisioned_services(app):
    list_services_provisioned = []
    for service in app.services:
        if service.allocated_in_server != -1:
            list_services_provisioned.append(service)
    return list_services_provisioned


def get_app_users_ids(app):
    list_users = []
    for user in app.users:
        list_users.append(user.id)
    return list_users


def get_edge_server_service_ids(edge_server):
    list_service_ids = []
    for service in edge_server.services:
        list_service_ids.append(service.id)
    return list_service_ids


def get_number_of_providers():
    num_providers = -1
    for edge_server in EdgeServer.all():
        if edge_server.infrastructure_provider > num_providers:
            num_providers = edge_server.infrastructure_provider
    return num_providers


"""
Get Number of Servers where App Deployed
"""
def get_number_of_servers_where_deploy_app(app):
    list_servers = []
    for service in app.services:
        if service.allocated_in_server != -1:
            list_servers.append(service.allocated_in_server)
    return len(list(set(list_servers)))


"""
Get List of Servers where App Deployed
"""
def get_list_of_servers_where_deploy_app(app):
    list_servers = []
    for service in app.services:
        if service.allocated_in_server != -1:
            list_servers.append(service.allocated_in_server)
    return list(set(list_servers))


"""
Get Number of Providers where App Deployed
"""
def get_number_of_providers_where_deploy_app(app):
    list_servers = get_list_of_servers_where_deploy_app(app)
    list_providers = []
    for edge_server in list_servers:
        list_providers.append(EdgeServer.find_by_id(edge_server).infrastructure_provider)
    return len(list(set(list_providers)))


"""
Get Number of Providers where App Deployed

"""
def get_list_of_providers_where_deploy_app(app):
    list_servers = get_list_of_servers_where_deploy_app(app)
    list_providers = []
    for edge_server in list_servers:
        list_providers.append(EdgeServer.find_by_id(edge_server).infrastructure_provider)
    return list(set(list_providers))

"""
Privacy Score
"""
def app_privacy_score(app):
    number_of_servers = get_number_of_servers_where_deploy_app(app)
    number_of_providers = get_number_of_providers_where_deploy_app(app)
    if number_of_servers == 0:
        return -1
    else:
        return (1 / number_of_servers) * (1 / number_of_providers)


"""
Future Privacy Score
"""
def get_future_app_privacy_score(app, id_server):
    number_of_servers = get_number_of_servers_where_deploy_app(app)
    number_of_providers = get_number_of_providers_where_deploy_app(app)
    list_services = get_app_service_ids(app)

    if number_of_servers == 0:
        return 1
    else:
        #Servers
        if id_server in get_list_of_servers_where_deploy_app(app):
            number_of_servers = number_of_servers + 1

        #Provider
        edge_server = EdgeServer.find_by_id(id_server)
        if edge_server != None:
            new_provider = edge_server.infrastructure_provider
            if new_provider in get_list_of_providers_where_deploy_app(app):
                number_of_providers = number_of_providers + 1
        else:
            number_of_providers = number_of_providers + 1 #TESTE

        return (1 / number_of_servers) * (1 / number_of_providers)



"""
Availability Score
"""
def app_availability_score(app):
    number_of_services = len(get_app_provisioned_services(app))
    number_of_servers = len(get_list_of_servers_where_deploy_app(app))
    if number_of_servers == 0:
        return 0
    return number_of_servers / number_of_services


def app_service_drops(app):
    drops = 0
    for service in app.services:
        if service.allocated_in_server == -1:
            drops += 1
    return drops


"""
Future Availability Score
"""
def get_future_app_availability_score(app, id_server):
    number_of_services = len(get_app_provisioned_services(app))
    number_of_servers = len(get_list_of_servers_where_deploy_app(app))
    list_id_servers = get_list_of_servers_where_deploy_app(app)
    if number_of_services == 0:
        return 1
    else:
        if id_server in list_id_servers:
            return number_of_servers / number_of_services
        else:
            return (number_of_servers + 1) / number_of_services


def apps_report(algo_name, scenario, seed_value):
    list_apps = []
    for app in Application.all():
        list_apps.append([app.id, app.provisioned, get_app_users_ids(app), get_app_service_ids(app),
                          get_list_of_servers_where_deploy_app(app),
                          get_list_of_providers_where_deploy_app(app),
                          app_privacy_score(app), app_availability_score(app),
                          get_future_app_privacy_score(app, 50),
                          get_future_app_availability_score(app, 50)])
    report = pd.DataFrame(list_apps, columns=['id', 'provisioned', 'users_ids', 'services_ids', 'ids_servers_where_deploy',
                                     "ids_providers_where_deploy", "app_privacy_score", 'app_availability_score',
                                              'future_privacy_score', 'future_availability_score'])
    report.to_csv(f"reports/{algo_name}_report_apps_{scenario}_{seed_value}.csv", index=False)


def servers_report(algo_name, scenario, seed_value):
    list_servers = []
    for server in EdgeServer.all():
        list_servers.append([server.id, server.cpu, server.memory, server.cpu_demand, server.memory_demand,
                             server.cpu - server.cpu_demand, server.memory - server.memory_demand,
                             server.infrastructure_provider, get_edge_server_service_ids(server)])
    report = pd.DataFrame(list_servers, columns=['id', 'cpu', 'memory', 'cpu_demand', 'memory_demand', 'free_cpu',
                                                 'free_memory', 'provider_ids', 'services_ids'])
    report.to_csv(f"reports/{algo_name}_report_servers_{scenario}_{seed_value}.csv", index=False)


def services_report(algo_name, scenario, seed_value):
    list_services = []
    for service in Service.all():
        list_services.append([service.id, service.cpu_demand, service.memory_demand, service.drop,
                              service.allocated_in_server])
    report = pd.DataFrame(list_services, columns=['id', 'cpu_demand', 'memory_demand', 'drop', 'allocated_in_server'])
    report.to_csv(f"reports/{algo_name}_report_services_{scenario}_{seed_value}.csv", index=False)


def users_report(algo_name, scenario, seed_value):
    user_services = []
    for user in User.all():
        user_services.append([user.id, user.coordinates, user.applications, user.base_station])
    report = pd.DataFrame(user_services, columns=['id', 'coordinates', 'applications', 'base_station'])
    report.to_csv(f"reports/{algo_name}_report_users_{scenario}_{seed_value}.csv", index=False)


def base_station_reports(algo_name, scenario, seed_value):
    base_stations = []
    for base_station in BaseStation.all():
        base_stations.append([base_station.id, base_station.coordinates, base_station.users])
    report = pd.DataFrame(base_stations, columns=['id', 'coordinates', 'base_station'])
    report.to_csv(f"reports/{algo_name}_report_base_stations_{scenario}_{seed_value}.csv", index=False)

def get_all_reports(algo_name, scenario, seed_value):
    #apps_report(algo_name, scenario, seed_value)
    servers_report(algo_name, scenario, seed_value)
    services_report(algo_name, scenario, seed_value)
    #users_report(algo_name, scenario, seed_value)
    #base_station_reports(algo_name, scenario, seed_value)
