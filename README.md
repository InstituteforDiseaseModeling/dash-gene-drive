# Gene_Drive
Dash Gene Drive Application

#### Install requirements
```
cd Gene_Drive
pip install -r requirements.txt
```
**Note:** `requirements.txt` was created using pip-tools by running `pip-compile` command in the same directory
as `requirements.in`. If you want to add new packages you can update `requirements.in` with the new package's name,
run `pip-compile` then finally run `pip install -r requirements.txt`.

#### Data
Inside the `Gene_Drive` directory we need a `csvs` directory to hold the csvs needed. 

#### Run app.py 
From the Gene_Drive directory  run
```
    python app.py
```
**Note** If you're using Pycharm, and you're running the app in debug mode, you may encounter an error. This is due to the IDE itself. 
Install the latest version of py charm (2021.2.1 RC or latest). 

#### Manually updating licenses file
If you install additional third party packages, the licenses file should reflect the change. From the directory
where `LICENSES.txt` is run `pip-licenses --format=markdown --output-file=LICENSES.txt`


#### Staging
```
pip install gunicorn
cd Gene_Drive
gunicorn app:server -b 0.0.0.0:8050

```