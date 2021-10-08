# ML Adapter
This project is a [Deep Lynx](https://github.com/idaholab/Deep-Lynx) adapter that utilizes the Deep Lynx event system. After this application registers for events, received events will be parsed for data to be used in machine learning processes.

To run this code, first copy the `.env_sample` file and rename it to `.env`. Several parameters must be present:
* DEEP_LYNX_URL: The base URL at which calls to Deep Lynx should be sent
* CONTAINER_NAME: The container name within Deep Lynx
* DATA_SOURCE_NAME: A name for this data source to be registered with Deep Lynx


Logs will be written to a logfile, stored in the root directory of the project. The log filename is set in `ml/__init__.py`.  

## Getting Started
1. Install [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
2. Install [Poetry](https://python-poetry.org/)
3. Configure the Poetry's Virtualenv location
```
poetry config settings.virtualenvs.path <CONDA-INSTALL-LOCATION> # e.g. /Users/username/opt/anaconda3
```
4. Create and activate virtual env with conda:
```
conda create -n <MY-ENV-NAME> r-essentials r-base python=3.8
conda activate <MY-ENV-NAME>
```
5. Go to your project directory and install from your pyproject.toml
```
poetry install
```
6. Create a poetry shell
```
poetry shell
```
7. Finally, run the project with flask 
```
flask run
```