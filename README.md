# Issue Tracking System
[![Made with Django](https://img.shields.io/badge/made%20with-Django-orange)](https://pypi.org/project/Django)
[![Build Status](https://travis-ci.com/Floyd-Droid/jf-issue-tracker.svg?branch=master)](https://travis-ci.com/Floyd-Droid/jf-issue-tracker)
![Python](https://img.shields.io/badge/python-3.8-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE.md)

This is a full stack web application made with Django. It is a basic issue tracking system which allows the user to track and manage issues associated with their projects.

The goal of this project is to develop my personal understanding of web application components, such as CRUD functions, relational database management, user authentication/permissions, AJAX, web design, etc.

This app includes the following:

* CRUD functions for data storage and manipulation. Create and modify projects, issues, comments, and user info.
* User, Project, and Issue information is displayed in tables complete with pagination and keyword search capabilities to allow for easy data management. The user can also filter or sort table information.
* Users can be assigned to groups by admins, which determines user permissions.
* Each issue has a comment section where plans can be made by assigned users to resolve the issue. AJAX requests are utilized for faster and more dynamic web pages.

# Demo

For a demo, visit https://jf-issue-tracker.herokuapp.com

You can log in as a demo user, which allows you to interact with the site as if you have full permissions, but without the ability to make any changes to heroku's postgreSQL database.

You can also create your own account, which will place you in the 'Project Manager' group, allowing you to create and manage your own projects and issues. Only you can see the projects, issues, and comments you create, unless you assign another user to your project.

# Used Technologies

* Python 3.8
* HTML5
* CSS3
* JavaScript
* Bootstrap 4
* Django web framework 3.1.1
* PostgreSQL 12.4 (hosted by Heroku)
* AWS S3 API

# Installation

Clone the repo and create a virtual environment within the project directory.
```bash
git clone https://github.com/Floyd-Droid/jf-issue-tracker.git
pip3 -m venv myenv
```

Activate the virtual environment.
```bash
# Linux and OSX
source myenv/bin/activate
# Windows
myenv\scripts\activate.bat
```

Install PostgreSQL, and use pip to install the other requirements.
```bash
pip3 install -r requirements.txt
```

# Deployment

To deploy your web application to Heroku, gather requirements into a text file, and make sure a Procfile is present. Git is required to deploy to Heroku, so commit all necessary project files.

Download the Heroku CLI toolbelt from the website. In the command line, login to your Heroku account with
```bash
heroku login
```
and provide your info. Create a new Heroku app, then push to master.
```bash
heroku create <app_name>
git push heroku master
```

Make migrations to Heroku's PostgreSQL database, and create a superuser for your Heroku app's admin site.
```bash
heroku run python manage.py makemigrations
heroku run python manage.py createsuperuser
```

You will also need to set Heroku's environment variables. For example, set the SECRET_KEY with
```bash
heroku config:set SECRET_KEY=a_key_that_is_secret
```
The same needs to be done for the DATABASE_URL, as well as any necessary AWS S3 or Mailgun variables.

# Author

Jourdon Floyd

email: jourdonfloyd@gmail.com

GitHub: https://github.com/Floyd-Droid

# License

This project is licensed under the MIT License - see the LICENSE.md file for details.