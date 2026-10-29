from edge_sim_py import Application, Service

def get_app_service_ids(app):
    list_services = []
    for ser in app.services:
        list_services.append(ser.id)
    return list_services


def get_app_users_ids(app):
    list_users = []
    for user in app.users:
        list_users.append(user.id)
    return list_users