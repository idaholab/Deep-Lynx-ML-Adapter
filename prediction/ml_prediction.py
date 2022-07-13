# Copyright 2021, Battelle Energy Alliance, LLC

import os
import json
import pandas as pd

import utils
import model
import settings


class ML_Prediction():
    """
    Make a prediction on incoming data using an existing model file

        1. Select independent variables from the testing set
        2. Write the test file 
        3. Run the customized prediction Jupyter Notebook
    """

    def __init__(self, ml_model):
        # Declare variables
        self.ml_model = ml_model

        # Make prediction
        self.make_prediction()

    def make_prediction(self):
        """
        Make a prediction on incoming data using an existing model file
        """
        # Determine test dataset using the independent variables (Features, X, Predictors) from a model
        independent_variables = self.ml_model.independent_variables
        with open(os.getenv("ML_ADAPTER_OBJECT_LOCATION"), 'r') as fp:
            data = json.load(fp)
        dataset = data["DATASET"]
        test_data = pd.read_csv(dataset)
        test_data = test_data[independent_variables]

        # Write test.csv file
        self.create_test_file(test_data)

        # Call Jupyter Notebook
        utils.run_jupyter_notebook(data["PREDICTION"]["notebook"], data["PREDICTION"]["kernel"])

    def create_test_file(self, test_data: pd.DataFrame or pd.Series):
        """
        Creates a test.csv file of the incoming data
        Args
            test_data (DataFrame or Series): a subset of the Features, X, Predictors dataset used for testing
        """
        # Validate extension and path existance before creation
        path = 'test.csv'
        utils.validate_extension('.csv', path)
        dir_path = os.path.abspath('data')
        utils.validate_paths_exist(dir_path)

        key = path.split('.')[0]
        file_path = os.path.join(dir_path, path)
        print(file_path)
        test_data.to_csv(file_path, index=False)


def main():
    """
    Main entry point for script
    """

    independent_variables = []
    dependent_variables = []

    ml_model = model.ML_Model(independent_variables=independent_variables, dependent_variables=dependent_variables)
    ml_prediction = ML_Prediction(ml_model)


if __name__ == "__main__":
    main()
