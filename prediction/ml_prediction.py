import os
import json
import pandas as pd

import utils
import model
import settings


class ML_Prediction():
    """
    Make a prediction on incoming data using an existing model file

        1. Select independent and dependent variables from the testing set
        2. Write the test file 
    """
    def __init__(self, ml_model):
        # Declare variables
        self.ml_model = ml_model

        # Make prediction
        self.make_prediction()

    def make_prediction(self):
        """Make a prediction on incoming data using an existing model file"""
        # Determine test dataset using the independent variables (Features, X, Predictors) from a model
        independent_variables = self.ml_model.independent_variables
        with open(os.getenv("ML_ADAPTER_DATA"), 'r') as fp:
            data = json.load(fp)
        dataset = data["DATASET"]
        test_data = pd.read_csv(dataset)
        test_data = test_data[independent_variables]

        # Write test.csv file
        self.create_test_file(test_data)

        # Call Jupyter Notebook
        utils.run_jupyter_notebook(data["PREDICTION"]["notebook"], data["PREDICTION"]["kernel"])

    def create_test_file(self, test_data):
        """Creates a test.csv file of the incoming data """
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
    """Main entry point for script"""
    name = 'Sensor_to_Sensor:Multi Point 3'
    data = {
        'independent_variables': {
            'Sensor': ['Time (s)', 'Multi Point 1', 'Multi Point 2']
        },
        'dependent_variables': {
            'Sensor': ['Multi Point 3']
        }
    }
    datasets = {'Sensor': 'data/incoming_data.csv'}
    split_method = 'random'
    test_size = 0.2
    ml_model = model.ML_Model(name=name, data=data, datasets=datasets, split_method=split_method, test_size=test_size)

    prediction = ML_Prediction(ml_model)


if __name__ == "__main__":
    main()
