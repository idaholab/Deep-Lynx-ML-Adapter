# Prediction

The purpose of this section is to make a prediction on incoming data using an existing model file.

Use case: if your model takes days to train, you can write the model to a serialized file and store the file in Deep Lynx. Deep Lynx is queried for this saved model file and can be used to make a prediction with new data.

The `ML_Prediction` class performs these tasks:

1. Select independent variables from the testing set
2. Write the test file e.g. test.csv
3. Run the customized prediction Jupyter Notebook

## Get Started
The Jupyter Notebook must have these components:
* Retrieve Data
* Standardize the data
* Make a prediction with the incoming data
* Un-standardize the data
* Generate JSON file of results

A sample Jupyter Notebook is included called `sample_prediction.ipynb`.

### Inputs

* data/test.csv
* model serialization file
* standardization information (optional but may be generated from the `ML_Model` Jupyter Notebook)

### Output

* json file of results
