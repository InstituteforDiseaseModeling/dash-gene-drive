# Gene_Drive

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# User Installation

```bash
pip install Gene_Drive --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

## Pre-requisites
- Python 3.9 x64


# Development Environment Setup

When setting up your environment for the first time, you can use the following instructions

## Local Setup
1) Clone the business logic/UI repository:
   ```bash
   > git clone https://github.com/InstituteforDiseaseModeling/dash-gene-drive
   ```
2) Clone the data repository:
   Then clone the repo. 
   ```bash
   > git clone https://github.com/InstituteforDiseaseModeling/dash-gene-drive-data
   ```
3) Create a virtualenv. On Windows, please use venv to create the environment
   `python -m venv dash-gene-drive`
   On Unix(Mac/Linux) you can use venv or virtualenv
4) Activate the virtualenv
5) Set environment variables
   `DATA_DIR = path/to/dash-gene-drive-data`
   `ENVIRONMENT = development`
6) If you are on windows, run `pip install py-make --upgrade --force-reinstall`
7) Then run `python ./.dev_scripts/bootstrap.py`. This will install all the tools. 
8) Run the app 
```
python main.py
```

## Development Tips

There is a Makefile file available for most common development tasks. Here is a list of commands
```bash
clean       -   Clean up temproary files
setup-dev   -   Set up packages in dev mode 
```
On Windows, you can use `pymake` instead of `make`

## Container Setup
### using built in development server
```
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up
```

### using gunicorn
```
docker-compose -f docker-compose.staging.yml build
docker-compose -f docker-compose.staging.yml up
```