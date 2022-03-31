# Copyright 2021, Battelle Energy Alliance, LLC

# Python Packages
import os
import json
import pandas as pd
import time

# Repository Modules 
import utils
import model
import settings
api_client = None

import adapter


class ML_Adapter():
    """
    An ML Adapter object instantiates numerous ML_Model objects
        1. Generates training and testing sets
        2. Perform variable selection to determine the independent and dependent variables
        3. Create ML_Model objects with different independent and dependent variables
    """
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.models = list()

        self.write_ml_adapter_object_location_to_file()
        self.generate_training_testing_sets(self.data["SPLIT_METHOD"])
        self.variable_selection()
        self.create_models()

    def write_ml_adapter_object_location_to_file(self):
        """
        Writes the data for the ML_Adapter object to a JSON file

        Note: equivalent to a single JSON object in ML_ADAPTER_OBJECTS environment variable located in the .env file
        """
        self.data["DATASET"] = os.getenv("QUERY_FILE_NAME")
        self.data["MODEL"]["output_file"] = os.getenv("IMPORT_FILE_NAME")
        # Validate path exists
        file_path = os.path.abspath(os.getenv("ML_ADAPTER_OBJECT_LOCATION"))
        utils.validate_extension('.json', file_path)
        path = os.path.split(file_path)
        utils.validate_paths_exist(path[0])

        # Write dictionary to JSON file
        with open(file_path, 'w') as fp:
            json.dump(self.data, fp)

    def generate_training_testing_sets(self, type: str):
        """
        Generates the the training and testing sets from the dataset
        Args
            type (string): the type of split method e.g. none, random, hierarchical_clustering, kennard_stone, sequential
        """
        if type == "none":
            dataset = pd.read_csv(os.getenv("QUERY_FILE_NAME"))
            dataset.to_csv("data/training_set.csv")
        else:
            # Determine name of split file
            file = ".".join([type, "ipynb"])

            # Determine path for .csv file
            file_path = os.path.abspath(os.path.join("split", file))
            utils.validate_paths_exist(file_path)
            utils.validate_extension('.ipynb', file_path)

            # Run Jupyter Notebook
            if type == "random" or type == "hierarchical_clustering" or type == "sequential":
                utils.run_jupyter_notebook(file_path, 'python3')
            elif type == "kennard_stone":
                utils.run_jupyter_notebook(file_path, 'ir')

    def variable_selection(self):
        """
        Creates a json file that specifies the independent and dependent variables for each model
        """
        file_path = os.path.abspath(self.data["VARIABLE_SELECTION"]["notebook"])
        utils.validate_extension('.ipynb', file_path)
        utils.validate_paths_exist(file_path)
        kernel = self.data["VARIABLE_SELECTION"]["kernel"]

        # Run Jupyter Notebook
        utils.run_jupyter_notebook(file_path, kernel)

    def create_models(self):
        """
        Instantiates numerous ML_Model objects specified by the variable selection json file
        """
        # Validate JSON file
        path = self.data["VARIABLE_SELECTION"]["output_file"]
        utils.validate_extension('.json', path)
        utils.validate_paths_exist(path)

        # Read a file containing JSON object
        with open(path) as f:
            models = json.load(f)
            f.close()

        # Create list of models
        for i in range(len(models)):
            self.models.append(
                model.ML_Model(independent_variables=models[i]["independent_variables"],
                               dependent_variables=models[i]["dependent_variables"]))
            print(self.models)

        # Import the results to deep lynx
        print("Begin import to deep lynx")
        did_succeed = adapter.import_to_deep_lynx(self.data["MODEL"]["output_file"])
        print("Deep Lynx Import", did_succeed)

        # File clean up
        if did_succeed and os.path.exists(self.data["MODEL"]["output_file"]):
            os.remove(self.data["MODEL"]["output_file"])
        if did_succeed and os.path.exists(self.data["DATASET"]):
            os.remove(self.data["DATASET"])
        if did_succeed and os.path.exists(os.getenv("ML_ADAPTER_OBJECT_LOCATION")):
            os.remove(os.getenv("ML_ADAPTER_OBJECT_LOCATION"))
        if os.path.exists("data/training_set.csv"):
            os.remove("data/training_set.csv")
        if os.path.exists("data/testing_set.csv"):
            os.remove("data/testing_set.csv")


def main():
    """
    Main entry point for script
    """
    while True:
        if os.path.exists(os.getenv("QUEUE_FILE_NAME")) and adapter.new_data:
            # Apply a lock
            with adapter.lock_:
                adapter.new_data = False
                # Read master queue file
                queue_df = pd.read_csv(os.getenv("QUEUE_FILE_NAME"))
            # Only execute if queue reaches optimal length
            if queue_df.shape[0] == int(os.getenv("QUEUE_LENGTH")):
                # TODO: Change to customized name
                file_name = None
                
                # File paths for local files
                query_file_name = "data/" + file_name
                import_file_name = "data/ML_" + file_name

                #Set environment variables
                os.environ["QUERY_FILE_NAME"] = query_file_name
                os.environ["IMPORT_FILE_NAME"] = import_file_name

                # Write csv
                queue_df.to_csv(query_file_name, index=False)

                # Create ML Adapter objects
                start = time.time()
                ml_adapter_objects = json.loads(os.getenv("ML_ADAPTER_OBJECTS"))
                for ml_adapter in ml_adapter_objects:
                    name = list(ml_adapter.keys())[0]
                    data = ml_adapter[name]
                    ml_adapter = ML_Adapter(name, data)
                end = time.time()
                print(end - start)


if __name__ == "__main__":
    main()
