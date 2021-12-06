# Copyright 2021, Battelle Energy Alliance, LLC

import os
import logging
import json
import time
import datetime
import environs
from flask import Flask, request, Response, json
import deep_lynx

import utils
from adapter import ml_adapter
from adapter.deep_lynx_query import deep_lynx_query, deep_lynx_init
from adapter.deep_lynx_import import deep_lynx_import


# configure logging. to overwrite the log file for each run, add option: filemode='w'
logging.basicConfig(filename='MLAdapter.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    datefmt='%m/%d/%Y %H:%M:%S')

print('Application started. Logging to file MLAdapter.log')


def create_app():
    """ This file and aplication is the entry point for the `flask run` command """
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
    env.list("ML_ADAPTER_OBJECTS")
    env.path("QUERY_FILE_NAME")
    env.path("IMPORT_FILE_NAME")
    env.int("QUERY_FILE_WAIT_SECONDS")
    env.int("IMPORT_FILE_WAIT_SECONDS")
    env.int("REGISTER_WAIT_SECONDS")
    env.path("ML_ADAPTER_OBJECT_LOCATION")
    split = json.loads(os.getenv("SPLIT"))
    if not isinstance(split, dict):
        error = "must be dict, not {0}".format(type(split))
        raise TypeError(error)


    # Purpose to run flask once (not twice)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Instantiate deep_lynx
        container_id, data_source_id, api_client = deep_lynx_init()

    @app.route('/events', methods=['POST'])
    def events():
        if request.method == 'POST':
            if 'application/json' not in request.content_type:
                return Response('Unsupported Content Type. Please use application/json', status=400)
            data = request.get_json()

            logging.info('Received event with data: ' + json.dumps(data))
            imports_api = deep_lynx.ImportsApi(api_client)
            import_data = imports_api.list_imports_data(container_id, data['import_id'])

            # check for event object type
            try:
                dl_event = import_data['value'][0]['data']

                if 'instruction' in dl_event:
                    if dl_event['instruction'] == 'run':
                        logging.info('New run event')
                        print('New run event')

                        # if event object type with instruction 'run' is found,
                        # grab original data id or import id and query DL for reactor map data
                        event_data = imports_api.list_imports_data(container_id, data['import_id'])

                        if 'value' not in event_data:
                            return Response(response=json.dumps({'received': True}),
                                            status=200,
                                            mimetype='application/json')

                        ml_data = event_data['value'][0]['data']

                        # update event object and return to Deep Lynx
                        dl_event['status'] = 'in progress'
                        dl_event['received'] = True
                        dl_event['modifiedDate'] = datetime.datetime.now().isoformat()
                        dl_event['modifiedUser'] = os.getenv('DATA_SOURCE_NAME')

                        datasource_api = deep_lynx.DataSourcesApi(api_client)
                        datasource_api.create_manual_import(dl_event, container_id, data_source_id)

                        # TODO 1. Compile all events into an array of json objects called dl_event_data
                        # TODO 2. Create function that initiates ML_Adapter objects and save objects for later events to use

                        return Response(response=json.dumps(dl_event), status=200, mimetype='application/json')

            except KeyError:
                # The incoming payload doesn't have what we need, but still return a 200
                return Response(response=json.dumps({'received': True}), status=200, mimetype='application/json')

    # disable running the code twice upon start in development
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        #register_for_event(container_id, api_client)
        print("")

    return app


def register_for_event(container_id: str, api_client: deep_lynx.ApiClient, iterations=30):
    """ Register with Deep Lynx to receive data_ingested events on applicable data sources """
    registered = False

    # List of adapters to receive events from
    data_ingested_adapters = json.loads(os.getenv("DATA_SOURCES"))

    # Register events for listening from other data sources
    while not registered and iterations > 0:
        # Get a list of data sources and validate that no error occurred
        datasource_api = deep_lynx.DataSourcesApi(api_client)
        data_sources = datasource_api.list_data_sources(container_id)
        if data_sources['isError'] == False:
            for data_source in data_sources['value']:
                # If the data source is found, create a registered event
                if data_source['name'] in data_ingested_adapters:
                    data_source_id = data_source['id']
                    container_id = data_source['container_id']

                    events_api = deep_lynx.EventsApi(api_client)
                    events_api.create_registered_event({
                        "app_name":
                        os.getenv('DATA_SOURCE_NAME'),
                        "app_url":
                        "http://" + os.getenv('FLASK_RUN_HOST') + ":" + os.getenv('FLASK_RUN_PORT') + "/events",
                        "container_id":
                        container_id,
                        "data_source_id":
                        data_source_id,
                        "event_type":
                        "data_ingested"
                    })

                    # Verify the event was registered
                    registered_events = events_api.list_registered_events()
                    if registered_events['isError'] == False:
                        registered_events = registered_events['value']
                        if registered_events:
                            for event in registered_events:
                                if event['data_source_id'] == data_source_id and event['container_id'] == container_id:
                                    data_ingested_adapters.remove(data_source['name'])

                    # If all events are registered
                    if len(data_ingested_adapters) == 0:
                        registered = True
                        return registered

        # If the desired data source and container is not found, repeat
        logging.info(
            f'Datasource(s) {", ".join(data_ingested_adapters)} not found. Next event registration attempt in {os.getenv("REGISTER_WAIT_SECONDS")} seconds.'
        )
        time.sleep(float(os.getenv('REGISTER_WAIT_SECONDS')))
        iterations -= 1

    return registered


def queryDeepLynx(api_client: deep_lynx.ApiClient = None, dl_events: list = None):
    """
    Query Deep Lynx for data
    Args
        api_client (ApiClient): deep lynx api client
        dl_event (list): a list of json objects from a deep lynx event
    Return
        True: if query file is found
        False: query file is not found
    """
    done = False
    didSucceed = False
    start = time.time()

    data_query_api = None
    if api_client is not None:
        data_query_api = deep_lynx.DataQueryApi(api_client)

    deep_lynx_query(data_query_api, dl_events)
    path = os.path.join(os.getcwd() + '/' + os.getenv('QUERY_FILE_NAME'))
    while not done:
        # Check if query file exists
        if os.path.exists(path):
            logging.info(f'Found {os.getenv("QUERY_FILE_NAME")}.')
            done = True
            did_succeed = True
            break
        else:
            logging.info(
                f'Fail: {os.getenv("QUERY_FILE_NAME")} not found. Trying again in {os.getenv("QUERY_FILE_WAIT_SECONDS")} seconds'
            )
            end = time.time()
            # Break out of infinite loop
            if end - start > float(os.getenv("QUERY_FILE_WAIT_SECONDS")) * 20:
                logging.info(f'Fail: In the final attempt, {os.getenv("QUERY_FILE_NAME")} was not found.')
                done = True
                break
            # Sleep for wait seconds
            else:
                logging.info(
                    f'Fail: {os.getenv("QUERY_FILE_NAME")} was not found. Trying again in {os.getenv("QUERY_FILE_WAIT_SECONDS")} seconds'
                )
                time.sleep(int(os.getenv("QUERY_FILE_WAIT_SECONDS")))
    if did_succeed:
        return True
    return False


def importToDeepLynx(api_client: deep_lynx.ApiClient = None,
                     container_id: str = '',
                     data_source_id: str = '',
                     event: dict = None):
    """
    Imports the results into Deep Lynx
    Args
        api_client (ApiClient): deep lynx api client
        container_id (str): deep lynx container id
        data_source_id (str): deep lynx data source id
        event (dictionary): a dictionary of the event information
    """
    done = False
    didSucceed = False
    start = time.time()
    path = os.path.join(os.getcwd() + '/' + os.getenv('IMPORT_FILE_NAME'))
    while not done:
        # Check if query file exists
        if os.path.exists(path):
            logging.info(f'Found {os.getenv("IMPORT_FILE_NAME")}.')
            # Import data into Deep Lynx
            data_sources_api = deep_lynx.DataSourcesApi(api_client)
            deep_lynx_import(data_sources_api, api_client, container_id, data_source_id)
            logging.info('Success: Run complete. Output data sent.')

            if event:
                # Send event signaling ML is done
                event['status'] = 'complete'
                event['modifiedDate'] = datetime.datetime.now().isoformat()
                data_sources_api.create_manual_import(event, container_id, data_source_id)
                logging.info('Event sent.')
            done = True
            didSucceed = True
            break
        else:
            logging.info(
                f'Fail: {os.getenv("IMPORT_FILE_NAME")} not found. Trying again in {os.getenv("IMPORT_FILE_WAIT_SECONDS")} seconds'
            )
            end = time.time()
            # Break out of infinite loop
            if end - start > float(os.getenv("IMPORT_FILE_WAIT_SECONDS")) * 20:
                logging.info(f'Fail: In the final attempt, {os.getenv("IMPORT_FILE_NAME")} was not found.')
                done = True
                break
            # Sleep for wait seconds
            else:
                logging.info(
                    f'Fail: {os.getenv("IMPORT_FILE_NAME")} was not found. Trying again in {os.getenv("IMPORT_FILE_WAIT_SECONDS")} seconds'
                )
                time.sleep(int(os.getenv("IMPORT_FILE_WAIT_SECONDS")))
    if didSucceed:
        return True
    return False
