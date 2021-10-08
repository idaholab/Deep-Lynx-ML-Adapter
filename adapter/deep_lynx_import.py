import os
import json
from pdb import set_trace
import settings
import pandas as pd
import datetime
import logging
import deep_lynx
import utils


def deep_lynx_import(dl_service: deep_lynx.DeepLynxService, data_file: str):
    """
    Imports data into Deep Lynx
    Args
        dl_service (DeepLynxService): deep lynx service object
        data_file (string): location of file to read
    """
    # Read file
    json_data = read_file(data_file)
    # Generate a dictionary of payloads to import
    payload = generate_payload(json_data)
    # Check if all payloads are valid
    is_valid = validate_payload(dl_service, payload)
    if is_valid:
        # Convert dictionary to list of payloads
        payload_list = list()
        for key in payload.keys():
            payload_list.extend(payload[key])
        # Manually import the data
        info = create_manual_import(dl_service, payload_list)
        if info['isError'] == False:
            logging.info("Successfully imported data to deep lynx")
            print("Successfully imported data to deep lynx")
        else:
            logging.error(info)
            print("Could not import data into Deep Lynx. Check log file for more information")


def create_manual_import(dl_service: deep_lynx.DeepLynxService, payload: list):
    """
    Creates a manual import using the payload to insert into deep lynx
    Args
        dl_service (DeepLynxService): deep lynx service object
        payload (list): a list of payloads to import into deep lynx
    """

    return dl_service.create_manual_import(dl_service.container_id, dl_service.data_source_id, payload)


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


def validate_payload(dl_service: deep_lynx.DeepLynxService, payload: dict):
    """
    Validates the payload before inserting into deep lynx
    
    Args
        dl_service (DeepLynxService): deep lynx service object
        payload (dictionary): a dictionary of payloads to import into deep lynx e.g. {metatype: list(payload)}
    Return
        is_valid (boolean): whether the payload is valid or not
    """
    # Create deep lynx validator object
    dl_validator = deep_lynx.DeepLynxValidator(dl_service)
    is_valid = True
    for metatype, nodes in payload.items():
        for node in nodes:
            # For each node, validate the its properies
            json_error = dl_validator.validate_properties(metatype, node)
            json_error = json.loads(json_error)
            if json_error["isError"]:
                for error in json_error["error"]:
                    logging.error(error)
                    is_valid = False
    return is_valid
