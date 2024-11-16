# S-Sen
This is a simple yet powerful static site generator that is easy to migrate from html.
## Environments
Python 3.11.x/3.12.x (Recommended)
## Get started
### Install
1. Make virtual env: `python3 -m venv env`
2. Activate virtual env: `source env/bin/activate` for linux/macos or `.\env\Scripts\activate` for windows
3. Run `(python3 -m )pip install git+https://github.com/timomono/sgen.git`

### Create project
```shell
(python3 -m )sgen create example_project
```
### Listen
If you're using VSCode, press Cmd/Ctrl + Shift + B, otherwise
```shell
(python3 -m )sgen listen
```
It will be built automatically when the file changes.

### Run development server
```shell
(python3 -m )sgen runserver
```
Please note that it won't work unless you build it.

Now that the developing server’s running, visit `localhost:8282` with your web browser.

You'll see a simple `Hello world!` page. It worked!

### Make checklist app
Let's create a simple checklist app.
#### Create project
Follow the steps above to create an app named "simple_checklist" and build it, and start the server.
#### Write template
Open `simple_checklist/src/(file name)` in your favorite editor and copy and paste the following:

**src/base.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %} | S-Gen Example</title>
    <style>
        body {
            margin: 0;
        }
        .navbar {
            background-color: brown;
            display: flex;
            align-items: center;
        }
        .navbar * {
            color: white;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <h1 style="margin:0;padding: 1rem;">
            {% block heading %}{% endblock %}
        </h1>
        <ul>
            <li>
                <a href="/">Color</a>
                <a href="/animal.html">Animal</a>
            </li>
        </ul>
    </div>
    <div style="padding: 1rem;">
        {% block body %}{% endblock %}
    </div>
</body>
</html>
```

**src/index.html**
```html
{% extends "base.html" %}
{% block title %}Favorite color{% endblock %}
{% block heading %}Color{% endblock %}
{% block body %}
<label for="favorite-color">What color do you like?</label>
<select id="favorite-color">
    {% for color in ["red","green","blue"] %}
    <option value="{{color}}">{{color}}</option>
    {% endfor %}
</select>
{% endblock %}
```
**src/animal.html**
```html
{% extends "base.html" %}
{% block title %}Favorite animal{% endblock %}
{% block heading %}Animal{% endblock %}
{% block body %}
<label for="favorite-color">What animal do you like?</label>
<select id="favorite-color">
    {% for color in ["zebra","lion","cat"] %}
    <option value="{{color}}">{{color}}</option>
    {% endfor %}
</select>
{% endblock %}
```
A dropdown menu will appear.

This is as short as it gets. If we were to write raw HTML, it would be much longer.