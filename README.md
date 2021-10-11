# Deep Lynx Machine Learning

The Deep Lynx Machine Learning (ML) Adapter is a generic adapter that programmatically runs the ML as continuous data is received and imports the ML results to [Deep Lynx](https://github.com/idaholab/Deep-Lynx). Then, Jupyter Notebooks can be customized according to the project for building the machine learning models and performing prediction analysis of incoming data using an existing model.

This project is a [Deep Lynx](https://github.com/idaholab/Deep-Lynx) adapter that utilizes the Deep Lynx event system. After this application registers for events, received events will be parsed for data to be used in machine learning processes.

To run this code, first copy the `.env_sample` file and rename it to `.env`. Several parameters must be present:
* DEEP_LYNX_URL: The base URL at which calls to Deep Lynx should be sent
* CONTAINER_NAME: The container name within Deep Lynx
* DATA_SOURCE_NAME: A name for this data source to be registered with Deep Lynx


Logs will be written to a logfile, stored in the root directory of the project. The log filename is set in `ml/__init__.py`.  

## Getting Started
1. Install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html), allows for Python and R virtual environments
2. Install [Poetry](https://python-poetry.org/), a package manager for dependencies
3. Configure the Poetry's Virtualenv location

```
poetry config settings.virtualenvs.path <CONDA-INSTALL-LOCATION> # e.g. /Users/username/opt/anaconda3
```

4. Create and activate virtual env with conda

```
conda create -n <MY-ENV-NAME> r-essentials r-base python=3.8
conda activate <MY-ENV-NAME>
```

5. Go to your project directory and install from your pyproject.toml

```
poetry install
```

6. Install the R kernel in Jupyter Notebook
* https://richpauloo.github.io/2018-05-16-Installing-the-R-kernel-in-Jupyter-Lab/
* https://developers.refinitiv.com/en/article-catalog/article/setup-jupyter-notebook-r


7. Verify the `ir` kernel was installed

```
jupyter kernelspec list
```

8. Start Jupyter Notebook from the root directory of this project. Go to `New` to verify the R kernel was installed

```
conda activate <MY-ENV-NAME>
jupyter notebook
```

6. Create a poetry shell

```
poetry shell
```
7. Finally, run the project with flask

```
flask run
```

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
