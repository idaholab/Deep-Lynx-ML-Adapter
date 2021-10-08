import os
import json
import settings
import pandas as pd
import deep_lynx


def deep_lynx_query(dl_service: deep_lynx.DeepLynxService):
    """
    Queries deep lynx for data and writes the dataset to .csv file
    Args
        dl_service (DeepLynxService): deep lynx service object
    """
    dataset = compile_data(dl_service)
    sample_location = "data/sample.csv"
    write_csv(dataset, sample_location)


def query(dl_service: deep_lynx.DeepLynxService, payload: str):
    """
    Queries Deep Lynx for nodes or edges
    Args
        dl_service (DeepLynxService): deep lynx service object
        payload (string): the graphQL query
    Return 
        data (dictionary): a dictionary of nodes or edges
        
    """
    data = dl_service.query(dl_service.container_id, payload)
    return data


def compile_data(dl_service: deep_lynx.DeepLynxService):
    """
    Complies a dataset from deep lynx queries
    Args
        dl_service (DeepLynxService): deep lynx service object
    Return
        dataset (DataFrame): a pandas DataFrame of the data
    """
    dataset = pd.DataFrame()
    return dataset


def write_csv(dataset: pd.DataFrame, path: str):
    """
    Writes the dataset to .csv file
    Args
        dataset (DataFrame): a pandas DataFrame of the data
        path (string): the file path to write the data to e.g. data/*.csv
    """
    dataset.to_csv(path, index=False)
