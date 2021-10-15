# Deep Lynx Machine Learning

The Deep Lynx Machine Learning (ML) Adapter is a generic adapter that programmatically runs the ML as continuous data is received and imports the ML results to [Deep Lynx](https://github.com/idaholab/Deep-Lynx). Then, Jupyter Notebooks can be customized according to the project for building the machine learning models and performing prediction analysis of incoming data using an existing model.

This project is a [Deep Lynx](https://github.com/idaholab/Deep-Lynx) adapter that utilizes the Deep Lynx event system. After this application registers for events, received events will be parsed for data to be used in machine learning processes.

Logs will be written to a logfile, stored in the root directory of the project. The log filename is set in `ml/__init__.py`. 

## Environment Variables

To run this code, first copy the `.env_sample` file and rename it to `.env`. Several parameters must be present:
* DEEP_LYNX_URL: The base URL at which calls to Deep Lynx should be sent
* CONTAINER_NAME: The container name within Deep Lynx
* DATA_SOURCE_NAME: A name for this data source to be registered with Deep Lynx
* DATA_SOURCES: A list of Deep Lynx data source names which listens for events
* REGISTER_WAIT_SECONDS: the number of seconds to wait between attempts to register for events 
* SPLIT: a json of the parameters for each split method. See section below for more details
* ML_ADAPTER_OBJECTS: a json of information for instantiating a `ML_Adapter` object. See section below for more details
* ML_ADAPTER_OBJECT_LOCATION: specifies a file that contains the data for the current (single) `ML_Adapter` object from the `ML_ADAPTER_OBJECTS` environment variable

### SPLIT Environment Variable

The user should choose the parameters for the following split methods: random, hierarchical clustering, kennard stone (R Jupyter Notebook), sequential, none. 

* `random` - splits the dataset into random training and testing sets
    * `test_size`: a decimal percentage of the dataset to include in the test set or the absolute number of test samples
* `hierarchical clustering` - this algorithm build trees in a bottom-up approach, beginning with n singleton clusters (the number of samples in dataset), and then merging the two closest clusters at each stage. This merging is repeated until only one cluster remains.
    * `N`: the number of samples used in the hierarchical clustering algorithm. Do to performance issues, we recommend maximum N of 1000. The algorithm assigns the other samples to an identified cluster, before splitting into training and testing sets
    * `max_clusters`: the maximum number of clusters to create
    * `test_size`: an approximate decimal percentage of the dataset to include in the test set. Absolute number of test samples not supported
* `kennard stone` - the algorithm takes the pair of samples with the largest Eucledian distance of x-vectors (predictors) and then it sequentially selects a sample to maximize the Eucledian distance between x-vectors of already selected samples and the remaining samples. This process is repeated until the required number of samples is achieved.
    * `N`: the number of samples used in the kennard stone algorithm. Do to performance issues, we recommend maximum N of 40,000.
    * `k`: the number of samples to assign to the training set
* `squential` - splits the dataset sequentially into training and testing sets given a test size. The testing set is composed of the last indices of the dataset at the length of a test size.
    * `test_size`: the number of samples in the testing set
        * `N`: the number of samples in the testing set if the rows in the dataset > `N`
        * `percent`: the percentage of samples in the testing set if the rows in the the dataset <= `N`
* `none` - does not split the data into training and testing sets. The entire dataset becomes the training set.

Default Split Method Parameters
```
SPLIT={"random":{"test_size":0.2}, "hierarchical_clustering":{"N":1000,"max_clusters":10,"test_size":0.2}, "kennard_stone":{"N":10000,"k":6000}, "sequential":{"test_size":{"N":600,"percent":0.1}}, "none":null}
```
 
### ML_ADAPTER_OBJECTS Environment Variable

The R package `dotenv` does not support multi-line variables. Therefore each environment variable must be on a single line. Therefore, the `ML_ADAPTER_OBJECTS` variable must be on a single line.  

## Getting Started

<details>
  <summary>Environment Setup for Python</summary>

* Complete the [Poetry installation](https://python-poetry.org/) 
* All following commands are run in the root directory of the project:
    * Run `poetry install` to install the defined dependencies for the project.
    * Run `poetry shell` to spawns a shell.
    * Finally, run the project with the command `flask run`

</details>

<details>
  <summary>Environment Setup for R: using Kennard Stone split method or R Jupyter Notebook</summary>

### Install Poetry with Anaconda Virtual Environment
1. Install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html), allows for Python and R virtual environments
2. Install [Poetry](https://python-poetry.org/), a package manager for dependencies
3. Configure the Poetry's Virtualenv location

```
poetry config settings.virtualenvs.path <CONDA-INSTALL-LOCATION> # e.g. /Users/username/opt/anaconda3
```

4. Create and activate virtual env with conda

```
$ conda create -n <MY-ENV-NAME> r-essentials r-base python=3.8
$ conda activate <MY-ENV-NAME>
(<MY-ENV-NAME>)$
```

5. Go to your project directory and install from your pyproject.toml

```
(<MY-ENV-NAME>)$ poetry install
```
### Install R Kernel
1. Install the R kernel in Jupyter Notebook
* https://richpauloo.github.io/2018-05-16-Installing-the-R-kernel-in-Jupyter-Lab/
* https://developers.refinitiv.com/en/article-catalog/article/setup-jupyter-notebook-r


2. Verify the `ir` kernel was installed

```
jupyter kernelspec list
```

3. Start Jupyter Notebook from the root directory of this project. Go to `New` to verify the R kernel was installed

```
$ conda activate <MY-ENV-NAME>
(<MY-ENV-NAME>)$ jupyter notebook
```
### Install R Packages
1. Open a new terminal and create an R terminal

```
$ conda activate <MY-ENV-NAME>
(<MY-ENV-NAME>)$ R
```  
2. Install the packages below

```
# R terminal
> install.packages('prospectr', dependencies = TRUE)
> install.packages('reticulate', dependencies = TRUE)
> install.packages('dotenv', dependencies = TRUE)
> install.packages('jsonlite', dependencies = TRUE)
```

### Run Project
Finally, run the project with flask

```
(<MY-ENV-NAME>)$ flask run
```

### Environment Variables
The R package `dotenv` does not support multi-line variables. Therefore each environment variable must be on a single line. Therefore, the `ML_ADAPTER_OBJECTS` variable must be on a single line.  


</details>

## Contributing

This project uses [yapf](https://github.com/google/yapf) for formatting. Please install it and apply formatting before submitting changes (e.g. `yapf --in-place --recursive . --style={column_limit:120}`)

### Other Software
Idaho National Laboratory is a cutting edge research facility which is a constantly producing high quality research and software. Feel free to take a look at our other software and scientific offerings at:

[Primary Technology Offerings Page](https://www.inl.gov/inl-initiatives/technology-deployment)

[Supported Open Source Software](https://github.com/idaholab)

[Raw Experiment Open Source Software](https://github.com/IdahoLabResearch)

[Unsupported Open Source Software](https://github.com/IdahoLabCuttingBoard)

### License

Copyright 2021 Battelle Energy Alliance, LLC

Licensed under the LICENSE TYPE (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://opensource.org/licenses/MIT  

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



Licensing
-----
This software is licensed under the terms you may find in the file named "LICENSE" in this directory.


Developers
-----
By contributing to this software project, you are agreeing to the following terms and conditions for your contributions:

You agree your contributions are submitted under the MIT license. You represent you are authorized to make the contributions and grant the license. If your employer has rights to intellectual property that includes your contributions, you represent that you have received permission to make contributions and grant the required license on behalf of that employer.
