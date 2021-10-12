import os
import json
import pandas as pd

import utils
import model
import settings


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
        # Validate path exists
        file_path = os.path.abspath(os.getenv("ML_ADAPTER_OBJECT_LOCATION"))
        utils.validate_extension('.json', file_path)
        path = os.path.split(file_path)
        utils.validate_paths_exist(path[0])

        # Write dictionary to JSON file
        with open(file_path, 'w') as fp:
            json.dump(self.data, fp)

    def generate_training_testing_sets(self, type):
        """
        Generates the the training and testing sets from the dataset
        """
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


def main(event=None, deep_lynx_service=None):
    """
    Main entry point for script
    """
    ml_adapter_objects = json.loads(os.getenv("ML_ADAPTER_OBJECTS"))
    for ml_adapter in ml_adapter_objects:
        name = list(ml_adapter.keys())[0]
        data = ml_adapter[name]
        ml_adapter = ML_Adapter(name, data)


if __name__ == "__main__":
    main()
