# Copyright 2021, Battelle Energy Alliance, LLC

# Python Packages
import os
import logging
import json
import time
import environs
from flask import Flask, request, Response, json
import deep_lynx
import threading

# Repository Modules 
from .deep_lynx_query import query_deep_lynx
from .deep_lynx_import import import_to_deep_lynx
from .ml_adapter import main
import utils

# Global variables
api_client = None
lock_ = threading.Lock()
threads = list()
number_of_events = 1
env = environs.Env()

# configure logging. to overwrite the log file for each run, add option: filemode='w'
logging.basicConfig(filename='MLAdapter.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    datefmt='%m/%d/%Y %H:%M:%S')

print('Application started. Logging to file MLAdapter.log')


def create_app():
    """ This file and aplication is the entry point for the `flask run` command """
    global number_of_events
    global env
    app = Flask(os.getenv('FLASK_APP'), instance_relative_config=True)

    # Validate .env file exists
    utils.validate_paths_exist(".env")

    # Check required variables in the .env file, and raise error if not set
    env = environs.Env()
    env.read_env()
    env.url("DEEP_LYNX_URL")
    env.str("CONTAINER_NAME")
    env.str("DATA_SOURCE_NAME")
    env.list("DATA_SOURCES")
    env.int("IMPORT_FILE_WAIT_SECONDS")
    env.int("REGISTER_WAIT_SECONDS")
    env.path("QUERY_FILE_NAME")
    env.path("IMPORT_FILE_NAME")
    env.path("ML_ADAPTER_OBJECT_LOCATION")
    env.path("METADATA")
    env.path("QUEUE_FILE_NAME")
    env.int("QUEUE_LENGTH")
    env.bool("NEW_DATA")
    env.list("ML_ADAPTER_OBJECTS")

    split = json.loads(os.getenv("SPLIT"))
    if not isinstance(split, dict):
        error = "must be dict, not {0}".format(type(split))
        raise TypeError(error)

    # Purpose to run flask once (not twice)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Instantiate deep_lynx
        container_id, data_source_id, api_client = deep_lynx_init()
        os.environ["CONTAINER_ID"] = container_id
        os.environ["DATA_SOURCE_ID"] = data_source_id

        # Register for events to listen for
        register_for_event(api_client)

        # Create Thread object that runs the machine learning algorithms
        # Thread object: activity that is run in a separate thread of control
        # Daemon: a process that runs in the background. A daemon thread will shut down immediately when the program exits. 
        ml_thread = threading.Thread(target=main, daemon=True, name="ml_thread")
        print("Created ml_thread")
        threads.append(ml_thread)
        # Start the thread’s activity
        ml_thread.start()

        # File clean up
        if os.path.exists(os.getenv("QUEUE_FILE_NAME")):
            os.remove(os.getenv("QUEUE_FILE_NAME"))
        if os.path.exists(os.getenv("ML_ADAPTER_OBJECT_LOCATION")):
            os.remove(os.getenv("ML_ADAPTER_OBJECT_LOCATION"))
        if os.path.exists("data/training_set.csv"):
            os.remove("data/training_set.csv")
        if os.path.exists("data/testing_set.csv"):
            os.remove("data/testing_set.csv")
        ml_adapter_objects = json.loads(os.getenv("ML_ADAPTER_OBJECTS"))
        for ml_adapter in ml_adapter_objects:
            name = list(ml_adapter.keys())[0]
            data = ml_adapter[name]
            if os.path.exists(data["MODEL"]["output_file"]):
                os.remove(data["MODEL"]["output_file"])
            if os.path.exists(data["DATASET"]):
                os.remove(data["DATASET"])
        if os.path.exists("data/X_train.csv"):
            os.remove("data/X_train.csv")
        if os.path.exists("data/X_test.csv"):
            os.remove("data/X_test.csv")
        if os.path.exists("data/y_train.csv"):
            os.remove("data/y_train.csv")
        if os.path.exists("data/y_test.csv"):
            os.remove("data/y_test.csv")


    @app.route('/machinelearning', methods=['POST'])
    def events():
        global number_of_events
        if 'application/json' not in request.content_type:
            logging.warning('Received /events request with unsupported content type')
            return Response('Unsupported Content Type. Please use application/json', status=400)

        # Data from graph has been received
        data = request.get_json()
        print(data)
        file_id = data["query"]["fileID"]
        logging.info('Received event with data: ' + json.dumps(data))

        try:
            # Retrieves file from Deep Lynx
            name = "event_thread_" + str(number_of_events)
            # Thread object: activity that is run in a separate thread of control
            event_thread = threading.Thread(target=query_deep_lynx, args=(file_id, ), name=name)
            print("Created ", name)
            threads.append(event_thread)
            number_of_events += 1
            # Start the thread’s activity
            event_thread.start()
            # Join: Wait until the thread terminates. This blocks the calling thread until the thread whose join() method is called terminates.
            event_thread.join()
            with lock_:
                os.environ["NEW_DATA"] = 'true'
            print(name, " is done")
            
            return Response(response=json.dumps({'received': True}), status=200, mimetype='application/json')

        except KeyError:
            # The incoming payload doesn't have what we need, but still return a 200
            return Response(response=json.dumps({'received': True}), status=200, mimetype='application/json')

    return app


def register_for_event(api_client: deep_lynx.ApiClient, iterations=30):
    """ Register with Deep Lynx to receive data_ingested events on applicable data sources """
    registered = False

    # List of adapters to receive events from
    data_ingested_adapters = json.loads(os.getenv("DATA_SOURCES"))

    # Register events for listening from other data sources
    while registered == False and iterations > 0:
        # Get a list of data sources and validate that no error occurred
        datasource_api = deep_lynx.DataSourcesApi(api_client)
        data_sources = datasource_api.list_data_sources(os.getenv("CONTAINER_ID"))

        if data_sources.is_error == False and len(data_sources.value) > 0:
            #data_sources = data_sources.to_dict()["value"]
            for data_source in data_sources.value:
                # If the data source is found, create a registered event
                if data_source.name in data_ingested_adapters:

                    events_api = deep_lynx.EventsApi(api_client)

                    # verify that this event action does not already exist
                    # by comparing to the established event action we would like to create

                    event_action = deep_lynx.CreateEventActionRequest(
                        data_source.container_id, data_source.id, "file_created", "send_data", None,
                        "http://" + os.getenv('FLASK_RUN_HOST') + ":" + os.getenv('FLASK_RUN_PORT') + "/machinelearning",
                        os.getenv("DATA_SOURCE_ID"), True)

                    actions = events_api.list_event_actions()
                    for action in actions.value:

                        # if destination, event_type, and data_source_id match, we know that this
                        # event action already exists
                        if action.destination == event_action.destination and action.event_type == event_action.event_type \
                            and action.data_source_id == event_action.data_source_id:
                            # this exact event action already exists, remove data source from list
                            logging.info('Event action on ' + data_source.name + ' already exists')
                            data_ingested_adapters.remove(data_source.name)

                    # continue event action creation if the same was not already found
                    if data_source.name in data_ingested_adapters:
                        create_action_result = events_api.create_event_action(event_action)

                        if create_action_result.is_error:
                            logging.warning('Error creating event action: ' + create_action_result.error)
                        else:
                            logging.info('Successful creation of event action on ' + data_source.name + ' datasource')
                            data_ingested_adapters.remove(data_source.name)

                    # If all events are registered
                    if len(data_ingested_adapters) == 0:
                        registered = True
                        logging.info('Successful registration on all adapters')
                        return registered

        # If the desired data source and container is not found, repeat
        logging.info(
            f'Datasource(s) {", ".join(data_ingested_adapters)} not found. Next event registration attempt in {os.getenv("REGISTER_WAIT_SECONDS")} seconds.'
        )
        time.sleep(float(os.getenv('REGISTER_WAIT_SECONDS')))
        iterations -= 1

    return registered

def deep_lynx_init():
    """ 
    Returns the container id, data source id, and api client for use with the DeepLynx SDK.
    Assumes token authentication. 

    Args
        None
    Return
        container_id (str), data_source_id (str), api_client (ApiClient)
    """
    # initialize an ApiClient for use with deep_lynx APIs
    configuration = deep_lynx.configuration.Configuration()
    configuration.host = os.getenv('DEEP_LYNX_URL')
    api_client = deep_lynx.ApiClient(configuration)

    # authenticate via an API key and secret
    """auth_api = deep_lynx.AuthenticationApi(api_client)
    token = auth_api.retrieve_o_auth_token(x_api_key=os.getenv('DEEP_LYNX_API_KEY'),
                                           x_api_secret=os.getenv('DEEP_LYNX_API_SECRET'),
                                           x_api_expiry='12h')"""

    # update header
    #api_client.set_default_header('Authorization', 'Bearer {}'.format(token))

    # get container ID
    container_id = None
    container_api = deep_lynx.ContainersApi(api_client)
    containers = container_api.list_containers()
    for container in containers.value:
        if container.name == os.getenv('CONTAINER_NAME'):
            container_id = container.id
            continue

    if container_id is None:
        print('Container not found')
        return None, None, None

    # get data source ID, create if necessary
    data_source_id = None
    datasources_api = deep_lynx.DataSourcesApi(api_client)

    datasources = datasources_api.list_data_sources(container_id)
    for datasource in datasources.value:
        if datasource.name == os.getenv('DATA_SOURCE_NAME'):
            data_source_id = datasource.id
    if data_source_id is None:
        datasource = datasources_api.create_data_source(
            deep_lynx.CreateDataSourceRequest(os.getenv('DATA_SOURCE_NAME'), 'standard', True), container_id)
        data_source_id = datasource.value.id

    return container_id, data_source_id, api_client