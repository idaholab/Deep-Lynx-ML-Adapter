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
from adapter.deep_lynx_query import deep_lynx_query
from adapter.deep_lynx_query import deep_lynx_init
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
    utils.validatePathsExist(".env")

    # Check required variables in the .env file, and raise error if not set
    env = environs.Env()
    env.read_env()
    env.url("DEEP_LYNX_URL")
    env.str("CONTAINER_NAME")
    env.str("DATA_SOURCE_NAME")
    env.list("DATA_SOURCES")
    env.path("QUERY_FILE_NAME")
    env.path("IMPORT_FILE_NAME")
    env.int("QUERY_FILE_WAIT_SECONDS")
    env.int("IMPORT_FILE_WAIT_SECONDS")
    env.int("REGISTER_WAIT_SECONDS")


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

            # parse event data and run dt_driver main
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

                        # TODO: ensure incoming objects are of the format {node, parameter, value}

                        # update event object and return to Deep Lynx
                        dl_event['status'] = 'in progress'
                        dl_event['received'] = True
                        dl_event['modifiedDate'] = datetime.datetime.now().isoformat()
                        dl_event['modifiedUser'] = os.getenv('DATA_SOURCE_NAME')

                        datasource_api = deep_lynx.DataSourcesApi(api_client)
                        datasource_api.create_manual_import(dl_event, container_id, data_source_id)

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

def query_deep_lynx(dl_service: deep_lynx.DeepLynxService = None):
    """
    Query Deep Lynx for data
    Args
        dl_service (DeepLynxService): deep lynx service object
    Return
        True: if query file is found
        False: query file is not found
    """
    done = False
    did_succeed = False
    start = time.time()
    deep_lynx_query(dl_service)
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

def import_to_deep_lynx(dl_service: deep_lynx.DeepLynxService = None, event: dict = None):
    """
    Imports the results into Deep Lynx
    Args
        dl_service (DeepLynxService): deep lynx service object
        event (dictionary): a dictionary of the event information
    """
    done = False
    did_succeed = False
    start = time.time()
    path = os.path.join(os.getcwd() + '/' + os.getenv('IMPORT_FILE_NAME'))
    while not done:
        # Check if query file exists
        if os.path.exists(path):
            logging.info(f'Found {os.getenv("IMPORT_FILE_NAME")}.')
            # Import data into Deep Lynx
            deep_lynx_import(dl_service)
            logging.info('Success: Run complete. Output data sent.')

            if event:
                # Send event signaling MOOSE is done
                event['status'] = 'complete'
                event['modifiedDate'] = datetime.datetime.now().isoformat()
                dl_service.create_manual_import(dl_service.container_id, dl_service.data_source_id, event)
                logging.info('Event sent.')
            done = True
            did_succeed = True
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
    if did_succeed:
        return True
    return False