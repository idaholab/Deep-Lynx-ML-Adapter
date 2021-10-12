# Model

The user will pick the independent and dependent variables for a model in the `Variable Selection` section. Independent and dependent variables are used to instantiate a `ML_Model` object.

The `ML_Model` class performs these tasks:

1. Select independent and dependent variables from the training and testing set
2. Creates .csv files of the predictors/response for the training and testing sets e.g. X_train.csv, X_test.csv, y_train.csv, y_test.csv
3. Run the customized machine learning Jupyter Notebook

Note: For unsupervised learning, an empty list of dependent_variables is provided to instantiate the `ML_Model` object, and y_train.csv and y_test.csv are not created.

### Input Files

* data/X_train.csv
* data/X_test.csv
* data/y_train.csv
* data/y_test.csv


### Output Files

* json file of results
* model serialization file (optional)
* standardization information (optional but may be needed for making a `ML_Prediction` using an existing model serialization file)

### Standardize data

Most data scientists standardize their data before splitting the data into X_train, X_test, y_train, and y_test. However, the ML Adapter splits the data in X_train, X_test, y_train, and y_test before standardization occurs. Below is an example of the standardization method called mean normalization that standardizes the datasets (X_train, X_test, y_train, and y_test).

Python

```Python
import pandas as pd

def standardize_mean_normalization(X_train, X_test, y_train, y_test):
    """
    Standardizes the data according to the z-score formula

    z = (x – μ) / σ

    Note: Only the training mean and standard deviation are used for the standardization of the data.
    This ensures that there is no contamination of the test data set.

    Args
        X_train (DataFrame): a subset of the Features, X, Predictors dataset used for training
        X_test (DataFrame): a subset of the Features, X, Predictors dataset used for testing
        y_train (Series): a subset of the Response, y, Label dataset used for training
        y_test (Series): a subset of the Response, y, Label dataset used for testing
    Return
        X_train_standardize (DataFrame): a standardized subset of the Features, X, Predictors dataset used for training
        X_test_standardize (DataFrame): a standardized subset of the Features, X, Predictors dataset used for testing
        y_train_standardize (Series): a standardized subset of the Response, y, Label dataset used for training
        y_test_standardize (Series): a standardized subset of the Response, y, Label dataset used for testing
        standardize (dictionary): a dictionary of the mean and standard deviation for un-standardizing data and standardizing incoming data e.g. {mean: {X_train: "", y_train: ""}, std: {X_train: "", y_train: ""}}
    """
    # Determine the mean and standard deviation
    # If pandas Dataframe
    if isinstance(X_train, pd.DataFrame):
        X_train_mean = list(X_train.mean())
        X_train_std = list(X_train.std())
    # If pandas Series
    else:
        X_train_mean = X_train.mean()
        X_train_std = X_train.std()

    y_train_mean = y_train.mean()
    y_train_std = y_train.std()

    # Standardize data
    X_train_standardize = (X_train - X_train_mean) / X_train_std
    X_test_standardize  = (X_test - X_train_mean) / X_train_std
    y_train_standardize  = (y_train - y_train_mean) / y_train_std
    y_test_standardize  = (y_test - y_train_mean) / y_train_std

    # Create a dictionary of the mean and standard deviation for un-standardizing data and standardizing incoming data
    standardize = dict()
    standardize["mean"] = dict()
    standardize["std"] = dict()
    standardize["mean"]["X_train"] = X_train_mean
    standardize["std"]["X_train"] = X_train_std
    standardize["mean"]["y_train"] = y_train_mean
    standardize["std"]["y_train"] = y_train_std

    return X_train_standardize, X_test_standardize, y_train_standardize, y_test_standardize, standardize
```

### Unstandardize Data

Unstandardization allows users to view the results without normalization in the response/y/label scientific units. Below is an example of unstandardizing the data via mean normalization.

```Python
import pandas as pd

def unstandardize_mean_normalization(y_train, y_test, yhat_train, yhat_test, standardize):
    """
    Unstandardizes the data according to the z-score formula

    z = (x * σ) + μ

    Note: Only the training mean and standard deviation are used for the standardization of the data.
    This ensures that there is no contamination of the test data set.

    Args
        y_train (Series): a standardized subset of the Response, y, Label dataset used for training
        y_test (Series): a standardized subset of the Response, y, Label dataset used for testing
        yhat_train (Series): a standardized estimation of the Response, y, Label for training set
        yhat_test (Series): a standardized estimation of the Response, y, Label for testing set
        standardize (dictionary): a dictionary of the mean and standard deviation for un-standardizing data and standardizing incoming data e.g. {mean: {X_train: "", y_train: ""}, std: {X_train: "", y_train: ""}}
    Return
        y_train (Series): an unstandardized subset of the Response, y, Label dataset used for training
        y_test (Series): an unstandardized subset of the Response, y, Label dataset used for testing
        yhat_train (Series): an unstandardized estimation of the Response, y, Label for training set
        yhat_test (Series): a unstandardized estimation of the Response, y, Label for testing set
        y_train_residuals (Series): the difference between the actual train response and the predicted train response (y_train - yhat_train)
        y_test_residuals (Series): the difference between the actual test response and the predicted test response (y_test - yhat_test)

    """   
    # Unstandardize y and yhat for the training and testing datasets
    y_train_mean = standardize["mean"]["y_train"]
    y_train_std = standardize["std"]["y_train"]

    y_train = (y_train * y_train_std) + y_train_mean
    yhat_train = (yhat_train * y_train_std.values) + y_train_mean.values
    y_test = (y_test * y_train_std ) + y_train_mean
    yhat_test = (yhat_test * y_train_std.values) + y_train_mean.values

    # Reshape if necessary
    y_train = y_train.values.reshape(-1)
    y_test = y_test.values.reshape(-1)

    # Unstandardize residuals for the training and testing datasets
    y_train_residuals = y_train - yhat_train
    y_test_residuals = y_test - yhat_test

    return y_train, y_test, yhat_train, yhat_test, y_train_residuals, y_test_residuals
```
