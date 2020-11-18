# Issue Tracker
[![Made with Django](https://img.shields.io/badge/made%20with-Django-orange)](https://pypi.org/project/Django)
[![Build Status](https://travis-ci.com/Floyd-Droid/jf-issue-tracker.svg?branch=master)](https://travis-ci.com/Floyd-Droid/jf-issue-tracker)
![Python](https://img.shields.io/badge/python-3.8-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE.md)

This is a full stack web application made with Django. It allows the user to track and manage issues associated with their projects.

The goal of this project is to develop my personal understanding of web application components, such as CRUD functions, database management, user authentication/permissions, web design, etc.

This app includes the following:

* CRUD functions for data storage and manipulation. Create and modify projects, issues, comments, and user info.
* User, Project, and Issue information is displayed in tables complete with pagination and keyword search capabilities to allow for easy data management. The user can also filter or sort table information.
* User groups can be assigned to users by admins, which determines user permissions.
* Each issue has a comment section where plans can be made by assigned users to resolve the issue.

# Demo

For a demo, visit https://jf-issue-tracker.herokuapp.com

You can log in as a demo user, which allows you to interact with the site as if you have full permissions, but without the ability to make any changes to heroku's postgreSQL database.

You can also create your own account, which will place you in the 'Project Manager' group, allowing you to create and manage your own projects and issues.

# Author

Jourdon Floyd

email: jourdonfloyd@gmail.com

GitHub: https://github.com/Floyd-Droid

# License

This project is licensed under the MIT License - see the LICENSE.md file for details.