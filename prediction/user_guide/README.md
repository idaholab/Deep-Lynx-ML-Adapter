# Prediction

The purpose of this section is to make a prediction on incoming data using an existing model file.

Use case: if your model takes days to train, you can write the model to a serialized file and store the file in Deep Lynx. Deep Lynx is queried for this saved model file and can be used to make a prediction with new data.

The `ML_Prediction` class performs these tasks:

1. Select independent variables from the testing set
2. Write the test file e.g. test.csv
3. Run the customized prediction Jupyter Notebook

## Get Started
The Jupyter Notebook may have these components:
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

For prediction, this information can be used to

* Read the model serialization file from the `model_serialization_file` specified in the `MODEL` dictionary
* Read the standardization information from the `standardization_file` specified in the `MODEL` dictionary
* Write the machine learning results to the `output_file` specified in the `PREDICTION` dictionary

Below shows how to use the `data` variable in Python and R.

Python

```Python
# For writing the output file
location = data["PREDICTION"]["output_file"]
```
R

```r
# For writing the output file
location = data$PREDICTION$output_file
```
