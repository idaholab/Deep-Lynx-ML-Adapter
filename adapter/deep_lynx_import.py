# Copyright 2021, Battelle Energy Alliance, LLC

import os
import json
from pdb import set_trace
import settings
import pandas as pd
import datetime
import logging
import deep_lynx
from deep_lynx.api_client import ApiClient
import utils


def deep_lynx_import(data_sources_api: deep_lynx.DataSourcesApi,
                     api_client: ApiClient,
                     container_id: str,
                     data_source_id: str,
                     data_file: str):
    """
    Imports data into Deep Lynx
    Args
        data_sources_api (deep_lynx.DataSourcesApi): deep lynx data source api
        container_id (str): deep lynx container id
        data_source_id (str): deep lynx data source id
        data_file (string): location of file to read
    """
    # Read file
    json_data = read_file(data_file)
    # Generate a dictionary of payloads to import
    payload = generate_payload(json_data)
    # Check if all payloads are valid
    is_valid = validate_payload(api_client, payload, container_id)
    if is_valid:
        # Convert dictionary to list of payloads
        payload_list = list()
        for key in payload.keys():
            payload_list.extend(payload[key])
        # Manually import the data
        info = create_manual_import(data_sources_api, payload_list, container_id, data_source_id)
        if info['isError'] == False:
            logging.info("Successfully imported data to deep lynx")
            print("Successfully imported data to deep lynx")
        else:
            logging.error(info)
            print("Could not import data into Deep Lynx. Check log file for more information")


def create_manual_import(data_sources_api: deep_lynx.DataSourcesApi = None,
                         payload: list = None,
                         container_id: str = '',
                         data_source_id: str = ''):
    """
    Creates a manual import of the payload to insert into Deep Lynx
    Args
        data_sources_api (deep_lynx.DataSourcesApi): deep lynx data source api
        payload (list): a list of payloads to import into deep lynx
        container_id (str): deep lynx container id
        data_source_id (str): deep lynx data source id
    """
    if data_sources_api and payload:
        return data_sources_api.create_manual_import(body=payload,
                                                     container_id=container_id,
                                                     data_source_id=data_source_id)


def upload_file(data_sources_api: deep_lynx.DataSourcesApi, file_paths: list, container_id: str, data_source_id: str):
    """
    Uploads a file into Deep Lynx   
    Args
        data_sources_api (deep_lynx.DataSourcesApi): deep lynx data source api
        file_paths (list): An array of strings with locations to each file
        to be uploaded.
        container_id (str): deep lynx container id
        data_source_id (str): deep lynx data source id
    """
    file_returns = []
    for file in file_paths:
        file_returns.append(data_sources_api.upload_file(container_id, data_source_id, file))
    return file_returns


def read_file(data_file: str):
    """
    Reads files for import
    
    Args
        data_file (string): the path to a json file
    Return
        json_data (dictionary): a dictionary of the data to import
    """
    utils.validate_extension('.json', data_file)
    utils.validate_paths_exist(data_file)

    with open(data_file, "r") as f:
        json_data = json.load(f)
    return json_data


def generate_payload(json_data: dict):
    """
    Generate a list of payloads to import into deep lynx
    
    Args
        json_data (dictionary): a dictionary of results generated from the Jupyter Notebook
    Return
        payload (dictionary): a dictionary of payloads to import into deep lynx e.g. {metatype: list(payload)}
    """
    payload = dict()
    return payload


def validate_payload(api_client: deep_lynx.ApiClient, payload: dict, container_id: str):
    """
    Validates the payload before inserting into deep lynx
    
    Args
        api_client (deep_lynx.ApiClien): deep lynx api client
        payload (dictionary): a dictionary of payloads to import into deep lynx e.g. {metatype: list(payload)}
        container_id (str): deep lynx container id
    Return
        is_valid (boolean): whether the payload is valid or not
    """
    # Create deep lynx validator object
    metatypes_api = deep_lynx.MetatypesApi(api_client)
    is_valid = True
    for metatype, nodes in payload.items():
        for node in nodes:
            # For each node, validate the its properies
            # assumes the first return is the desired metatype
            metatype_id = metatypes_api.list_metatypes(container_id, name=metatype)[0].id
            json_error = metatypes_api.validate_metatype_properties(container_id, metatype_id, node)
            json_error = json.loads(json_error)
            if json_error["isError"]:
                for error in json_error["error"]:
                    logging.error(error)
                    is_valid = False
    return is_valid
