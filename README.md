# Static Site Gen
## Install
1. Make virtual env: `python -m venv env`
2. Activate virtual env: `source env/bin/activate` for linux/macos or `.\env\Scripts\activate` for windows
3. Run `pip install .`

## Usage
### Create project
```
sgen create example_project
```

### Update listener
```
sgen listen
```
Automatically builds when files change.

### Run development server
```
sgen runserver
```
You can view it at localhost:8282.
Please note that it won't work unless you build it.