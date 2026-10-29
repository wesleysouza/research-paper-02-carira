import pandas as pd
from edge_sim_py import Application
from matplotlib.style.core import available

from lab_utils import get_info

def get_results2(simulator, algo_name, scenario, seed_value):
    logs_edgeserver = pd.DataFrame(simulator.agent_metrics["EdgeServer"])
    logs_edgeserver['CPU Usage'] = (logs_edgeserver['CPU Demand'] * 100) / logs_edgeserver['CPU']
    logs_edgeserver['RAM Usage'] = (logs_edgeserver['RAM Demand'] * 100) / logs_edgeserver['RAM']
    logs_edgeserver['Servers Usage'] = (logs_edgeserver['CPU Usage'] + logs_edgeserver['RAM Usage']) / 2
    dt_server_results = logs_edgeserver.loc[:, ['Object', 'Power Consumption', 'Servers Usage']].groupby(
        by='Object').mean().reset_index()
    dt_server_results.to_csv(f"results/{algo_name}_server_{scenario}_{seed_value}.csv", index=False)
    # logs_networkflow = pd.DataFrame(simulator.agent_metrics["NetworkFlow"])
    # logs_networkswitch = pd.DataFrame(simulator.agent_metrics["NetworkSwitch"])
    logs_service = pd.DataFrame(simulator.agent_metrics["Service"])
    logs_user = pd.DataFrame(simulator.agent_metrics["User"])
    # summary results
    logs_user['Latency SLA Violations'] = False
    logs_user.loc[logs_user['Delay sla deadlines'] < 0, 'Latency SLA Violations'] = True
    dt_user_violation = logs_user.loc[:, ['Object', 'Latency SLA Violations']].groupby(
        by='Object').sum().reset_index()
    dt_user_delays = logs_user.loc[:, ['Object', 'Delays']].groupby(by='Object').mean().reset_index()
    dt_user_delays['Drop SLA Violations'] = False
    dt_user_delays.loc[dt_user_delays['Delays'].isna(), 'Drop SLA Violations'] = True
    dt_user_results = dt_user_violation.merge(dt_user_delays, how='left', on='Object')
    dt_user_results = dt_user_results.rename(columns={'Delays': 'Average Latency'})
    dt_user_results.to_csv(f"results/{algo_name}_user_{scenario}_{seed_value}.csv", index=False)

    # Custom Metrics
    app_privacy_score = []
    app_availability_score = []
    for app in Application.all():
        app_privacy_score.append([app, get_info.app_privacy_score(app)])
        app_availability_score.append([app, get_info.app_availability_score(app)])
    privacy_results = pd.DataFrame(app_privacy_score, columns=["Object", "Privacy Score"])
    privacy_results.to_csv(f"results/{algo_name}_privacy_{scenario}_{seed_value}.csv", index=False)
    availability_results = pd.DataFrame(app_availability_score, columns=["Object", "Availability Score"])
    availability_results.to_csv(f"results/{algo_name}_availability_{scenario}_{seed_value}.csv", index=False)


def get_results(simulator, algo_name, scenario, seed_value):
    logs_edgeserver = pd.DataFrame(simulator.agent_metrics["EdgeServer"])
    logs_edgeserver['CPU Usage'] = (logs_edgeserver['CPU Demand'] * 100) / logs_edgeserver['CPU']
    logs_edgeserver['RAM Usage'] = (logs_edgeserver['RAM Demand'] * 100) / logs_edgeserver['RAM']
    logs_edgeserver['Servers Usage'] = (logs_edgeserver['CPU Usage'] + logs_edgeserver['RAM Usage']) / 2
    dt_server_results = logs_edgeserver.loc[:, ['Object', 'Power Consumption', 'Servers Usage']].groupby(
        by='Object').mean().reset_index()
    dt_server_results.to_csv(f"results/{algo_name}_server_{scenario}_{seed_value}.csv", index=False)
    # logs_networkflow = pd.DataFrame(simulator.agent_metrics["NetworkFlow"])
    # logs_networkswitch = pd.DataFrame(simulator.agent_metrics["NetworkSwitch"])
    logs_service = pd.DataFrame(simulator.agent_metrics["Service"])
    logs_user = pd.DataFrame(simulator.agent_metrics["User"])
    # summary results
    ## Number of requests
    logs_user['Requests'] = logs_user['Delay sla deadlines'].notna()
    dt_user_requests = logs_user.loc[:, ['Object', 'Requests']].groupby(by='Object').sum().reset_index()
    ## Latency Violations
    logs_user['Latency SLA Violations'] = False
    logs_user.loc[logs_user['Delay sla deadlines'] < 0, 'Latency SLA Violations'] = True
    dt_user_violation = logs_user.loc[:, ['Object', 'Latency SLA Violations']].groupby(by='Object').sum().reset_index()
    ## Avarage Latency
    dt_user_delays = logs_user.loc[:, ['Object', 'Delays']].groupby(by='Object').mean().reset_index()
    ## Drop Violations
    dt_user_delays['Drop SLA Violations'] = False
    dt_user_delays.loc[dt_user_delays['Delays'].isna(), 'Drop SLA Violations'] = True
    ## Merging everything
    dt_user_violation = dt_user_violation.merge(dt_user_requests, how='left', on='Object')
    dt_user_results = dt_user_violation.merge(dt_user_delays, how='left', on='Object')
    dt_user_results = dt_user_results.rename(columns={'Delays': 'Average Latency'})
    dt_user_results.to_csv(f"results/{algo_name}_user_{scenario}_{seed_value}.csv", index=False)

    # Custom Metrics
    app_privacy_score = []
    app_availability_score = []
    app_drops = []
    for app in Application.all():
        app_privacy_score.append([app, get_info.app_privacy_score(app)])
        app_availability_score.append([app, get_info.app_availability_score(app)])
        app_drops.append([app, get_info.app_service_drops(app)])
    privacy_results = pd.DataFrame(app_privacy_score, columns=["Object", "Privacy Score"])
    privacy_results.to_csv(f"results/{algo_name}_privacy_{scenario}_{seed_value}.csv", index=False)
    availability_results = pd.DataFrame(app_availability_score, columns=["Object", "Availability Score"])
    availability_results.to_csv(f"results/{algo_name}_availability_{scenario}_{seed_value}.csv", index=False)
    availability_results = pd.DataFrame(app_drops, columns=["Object", "Drops"])
    availability_results.to_csv(f"results/{algo_name}_drops_{scenario}_{seed_value}.csv", index=False)


def get_step_results(simulator, algo_name, scenario, seed_value):
    logs_edgeserver = pd.DataFrame(simulator.agent_metrics["EdgeServer"])
    logs_edgeserver['CPU Usage'] = (logs_edgeserver['CPU Demand'] * 100) / logs_edgeserver['CPU']
    logs_edgeserver['RAM Usage'] = (logs_edgeserver['RAM Demand'] * 100) / logs_edgeserver['RAM']
    logs_edgeserver['Servers Usage'] = (logs_edgeserver['CPU Usage'] + logs_edgeserver['RAM Usage']) / 2
    dt_server_results = logs_edgeserver.loc[:, ['Time Step', 'Power Consumption', 'Servers Usage']].groupby(
        by='Time Step').mean().reset_index()
    dt_server_results.to_csv(f"step_results/{algo_name}_server_{scenario}_{seed_value}.csv", index=False)
    # logs_networkflow = pd.DataFrame(simulator.agent_metrics["NetworkFlow"])
    # logs_networkswitch = pd.DataFrame(simulator.agent_metrics["NetworkSwitch"])
    logs_service = pd.DataFrame(simulator.agent_metrics["Service"])
    logs_user = pd.DataFrame(simulator.agent_metrics["User"])
    # summary results
    ## Number of requests
    logs_user['Requests'] = logs_user['Delay sla deadlines'].notna()
    dt_user_requests = logs_user.loc[:, ['Time Step', 'Requests']].groupby(by='Time Step').sum().reset_index()
    ## Latency Violations
    logs_user['Latency SLA Violations'] = False
    logs_user.loc[logs_user['Delay sla deadlines'] < 0, 'Latency SLA Violations'] = True
    dt_user_violation = logs_user.loc[:, ['Time Step', 'Latency SLA Violations']].groupby(by='Time Step').sum().reset_index()
    ## Avarage Latency
    dt_user_delays = logs_user.loc[:, ['Time Step', 'Delays']].groupby(by='Time Step').mean().reset_index()
    ## Drop Violations
    dt_user_delays['Drop SLA Violations'] = False
    dt_user_delays.loc[dt_user_delays['Delays'].isna(), 'Drop SLA Violations'] = True
    ## Merging everything
    dt_user_violation = dt_user_violation.merge(dt_user_requests, how='left', on='Time Step')
    dt_user_results = dt_user_violation.merge(dt_user_delays, how='left', on='Time Step')
    dt_user_availability = logs_user.loc[:, ['Time Step', 'Availability Score']].groupby(
        by='Time Step').mean().reset_index()
    dt_user_results = dt_user_availability.merge(dt_user_results, how='left', on='Time Step')
    dt_user_results = dt_user_results.rename(columns={'Delays': 'Average Latency'})
    dt_user_results.to_csv(f"step_results/{algo_name}_user_{scenario}_{seed_value}.csv", index=False)


def get_raw_results(simulator, algo_name, scenario, seed_value):
    logs_edgeserver = pd.DataFrame(simulator.agent_metrics["EdgeServer"])
    logs_edgeserver.to_csv(f"raw_results/{algo_name}_server_{scenario}_{seed_value}.csv", index=False)
    logs_user = pd.DataFrame(simulator.agent_metrics["User"])
    logs_user.to_csv(f"raw_results/{algo_name}_user_{scenario}_{seed_value}.csv", index=False)