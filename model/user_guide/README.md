# Model

### Input Files

The user will pick the independent variables and dependent variables for a model in the Variable Selection section.  

```
data/X_train.csv
data/X_test.csv
data/y_train.csv
data/y_test.csv

# Note: if unsupervised learning, no response/y/labels will be provided
```

### Standardize data
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
