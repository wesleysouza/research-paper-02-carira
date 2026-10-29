from edge_sim_py import EdgeServer

"""
Get Number of Servers where App Deployed
"""
def get_number_of_servers_where_deploy_app(app):
    list_servers = []
    for service in app.services:
        if service.allocated_in_server != -1:
            list_servers.append(service.allocated_to_the_provider)
    return len(list(set(list_servers)))


"""
Get Number of Providers where App Deployed
"""
def get_number_of_providers_where_deploy_app(app):
    list_servers = get_number_of_servers_where_deploy_app(app)
    list_providers = []
    for edge_server in list_servers:
        list_providers.append(EdgeServer.find_by_id(edge_server).infrastructure_provider)
    return len(list(set(list_servers)))


def app_privacy_score(app):
    number_of_servers = get_number_of_servers_where_deploy_app(app)
    number_of_providers = get_number_of_providers_where_deploy_app(app)
    return (1 / number_of_servers) * (1 / number_of_providers)


def check_if_add_new_provider_violates_privacy(app, new_provider_id):
    list_providers = []
    list_providers.append(new_provider_id)
    for ser in app.services:
        if ser.allocated_to_the_provider != -1:
            list_providers.append(ser.allocated_to_the_provider)
    if len(list(set(list_providers))) == 1:
        return 0
    else:
        return 1