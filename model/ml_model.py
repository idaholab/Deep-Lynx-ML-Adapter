# Copyright 2021, Battelle Energy Alliance, LLC

import os
import json
import pandas as pd

import utils
import settings


class ML_Model():
    """
    Split into predictors/response for the training and testing datasets that are used by the Jupyter Notebook to create a machine learning model

        1. Select independent and dependent variables from the training and testing set
        2. Creates .csv files of the predictors/response for the training and testing sets e.g. X_train.csv, X_test.csv, y_train.csv, y_test.csv
        3. Run the customized machine learning Jupyter Notebook
    
    Return
        Generates a machine learning serialized model and ML results

    """
    def __init__(self, independent_variables, dependent_variables):
        self.independent_variables = independent_variables
        self.dependent_variables = dependent_variables

        self.create_model()

    def create_model(self):
        """
        Creates a machine learning model and produces ML results
        """
        # Preprocess data
        training_path = os.path.abspath(os.path.join("data", "training_set.csv"))
        utils.validate_extension('.csv', training_path)
        utils.validate_paths_exist(training_path)
        training_set = pd.read_csv(training_path, 'r', delimiter=',')

        testing_path = os.path.abspath(os.path.join("data", "testing_set.csv"))
        utils.validate_extension('.csv', testing_path)
        utils.validate_paths_exist(testing_path)
        testing_set = pd.read_csv(testing_path, 'r', delimiter=',')

        # Determine independent variables dataset (Features, X, Predictors)
        X_train = training_set[self.independent_variables]
        X_test = testing_set[self.independent_variables]

        # Determine dependent variables dataset (Response, y, Label)
        y_train = None
        y_test = None
        # If supervised learning
        if self.dependent_variables:
            y_train = training_set[self.dependent_variables]
            y_test = testing_set[self.dependent_variables]

        # Write X_train, X_test, y_train, y_test to .csv files
        self.create_training_testing_files(X_train, X_test, y_train, y_test)

        # Run the Jupyter Notebook
        with open(os.getenv("ML_ADAPTER_OBJECT_LOCATION"), 'r') as fp:
            data = json.load(fp)
        utils.run_jupyter_notebook(data["MODEL"]["notebook"], data["MODEL"]["kernel"])

    def create_training_testing_files(self, X_train, X_test, y_train, y_test):
        """
        Creates .csv files of the predictors/response for the training and testing sets
        """
        # If supervised learning
        if y_train is not None and y_test is not None:
            paths = ['X_train.csv', 'X_test.csv', 'y_train.csv', 'y_test.csv']
            sets = [X_train, X_test, y_train, y_test]
        # Else unsupervised learning
        else:
            paths = ['X_train.csv', 'X_test.csv']
            sets = [X_train, X_test]

        # Validate extension and path existance before creation
        for path in paths:
            utils.validate_extension('.csv', path)
        dir_path = os.path.abspath('data')
        utils.validate_paths_exist(dir_path)

        # Write files to .csv file
        for i in range(len(paths)):
            file_path = os.path.join(dir_path, paths[i])
            sets[i].to_csv(file_path)


def main():
    """
    Main entry point for script
    """

    independent_variables = []
    dependent_variables = []

    experiment = ML_Model(independent_variables=independent_variables, dependent_variables=dependent_variables)


if __name__ == "__main__":
    main()
