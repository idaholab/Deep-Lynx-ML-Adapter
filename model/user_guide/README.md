# Model

The user will pick the independent and dependent variables for a model in the `Variable Selection` section. Independent and dependent variables are used to instantiate a `ML_Model` object.

The `ML_Model` class performs these tasks:

1. Select independent and dependent variables from the training and testing set
2. Creates .csv files of the predictors/response for the training and testing sets e.g. X_train.csv, X_test.csv, y_train.csv, y_test.csv
3. Run the customized machine learning Jupyter Notebook

Note: For unsupervised learning, an empty list of dependent_variables is provided to instantiate the `ML_Model` object, and y_train.csv and y_test.csv are not created.

## Get Started
The Jupyter Notebook may have these components:
* Retrieve Data
* Standardize the data
* Create model
* Make a prediction
* Un-standardize the data
* Save model to a serialized file
* Generate JSON file of results


A sample Jupyter Notebook is included called `sample_model.ipynb`.

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

Most data scientists standardize their data before splitting the data into X_train, X_test, y_train, and y_test. However, the ML Adapter splits the data in X_train, X_test, y_train, and y_test before standardization occurs. The README provides an example of the standardization method called mean normalization that standardizes the datasets (X_train, X_test, y_train, and y_test) in Python.


### Unstandardize Data

Unstandardization allows users to view the results without normalization in the response/y/label scientific units. The README provides an example of unstandardizing the data via mean normalization.

## Deciding to Save/ Don't Save Model

### Save Model
Reasons to save the model to a serialize file:
* Can be used in the future to make a prediction on incoming data
* The model takes a long time to train
* Continuous incoming data is received which occurs too quickly to retrain a new model each time

The serialized model file will be stored in Deep Lynx.

If the user chooses to save their model(s) for future use, the user will need to make a `Prediction` Jupyter Notebook that uses a existing model to make a prediction on incoming data. See the user guide in the `prediction` section of the ML Adapter for more information.

If the user standardizes their data, this information will need to be used in the `prediction` section. The recommendation is to write this information (mean, standard deviation, etc) to a json file and store the information in Deep Lynx along with the serialized model file.

Use case: If your model takes days to train, you can write the model to a serialized file and store the file in Deep Lynx. Deep Lynx is queried for this saved model file and can be used to make a prediction with new data.

### Don't Save Model
* The model will be out-of-date after receiving a set of new data
* The model can quickly train on new data

If the user does not save their model(s), the user should ignore the `prediction` section of the ML Adapter.

## Access to Environment Variables

An environment variable called `ML_ADAPTER_OBJECTS` should be created in the .env file that provides the details for each machine learning adapter (`ML_Adapter`) object. The `ML_ADAPTER_OBJECT_LOCATION` environment variable specifies a file that contains the data for the current `ML_Adapter` object. Below is an example of how to access the data for the current `ML_Adapter` object in a Python or R Jupyter Notebook.

Python

```Python
with open(os.getenv("ML_ADAPTER_OBJECT_LOCATION"), 'r') as fp:
    data = json.load(fp)
```
R

```r
library(jsonlite)
load_dot_env(file = ".env")
file_path = Sys.getenv("ML_ADAPTER_OBJECT_LOCATION")
data = fromJSON(txt=file_path)
```

For model, this information can be used to

* Write the machine learning results to the `output_file` specified in the `MODEL` dictionary
* Write the model serialization file to the `model_serialization_file` specified in the `MODEL` dictionary
* Write the standardization information to the `standardization_file` specified in the `MODEL` dictionary

Below shows how to use the `data` variable in Python and R.

Python

```Python
# For writing the output file
location = data["MODEL"]["output_file"]
```
R

```r
# For writing the output file
location = data$MODEL$output_file
```
