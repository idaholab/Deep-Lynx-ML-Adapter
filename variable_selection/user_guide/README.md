# Variable Selection
The purpose is to generate a `.json` file that contains the relevant information for instantiating numerous machine learning model (`ML_Model`) objects. Samples are provided which include a sample Jupyter Notebook called `sample_variable_selection.ipynb` and a sample output file called `sample.json`.

## JSON File Format
The `.json` file should contain an array of json objects for instantiating machine learning model(`ML_Model`) objects. The next section describes the required format for each json object.

```
[
    {...},
    {...},
    {...}
]
```

## Generate a JSON Object for each Model
Each JSON object of a model requires:
* `independent_variables` - the independent variables (Predictors, X, Features) of a machine learning model
* `dependent_variables` - the dependent variables (Response, y, Label) of a machine learning model

The `independent variables` and `dependent variables` are a list of the column names that will be selected from the dataset. A list of column names for the Response/y/Label was chosen to account for future improvements in the machine learning field which could allow predictions of multiple variables.

Note: For unsupervised learning, an empty list for the dependent_variables should be provided to instantiate the `ML_Model` object.

```JSON
{
    "independent_variables": [
        "Dataset_Column02",
        "Dataset_Column03",
        "Dataset_Column04",
        "Dataset_Column05"
    ],
    "dependent_variables": [
        "Dataset_Column01"
    ]
}
```

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

For variable selection, this information can be used to
* Read the `DATASET` file to obtain the column names
* Write the json information to an `output_file` specified in the `VARIABLE_SELECTION` dictionary

Below shows how to use the `data` variable in Python and R.

Python

```Python
# For reading a dataset
data_file = data["DATASET"]

# For writing the output file
location = data["VARIABLE_SELECTION"]["output_file"]
```
R

```r
# For reading a dataset
data_file = data$DATASET

# For writing the output file
location = data$VARIABLE_SELECTION$output_file
```
