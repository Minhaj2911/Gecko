# Team Gecko Small Group project

## Team members
The members of the team are:
- Yasmin Alzaid
- Samuel Chilakamari
- Joori Almusaed
- Mohammed Rahman
- Gunel Farajli

## Project structure
The project is called `task_manager`.  It currently consists of a single app `tasks`.

## Deployed version of the application
The deployed version of the application can be found at [*http://chilaks371.pythonanywhere.com/*](*http://chilaks371.pythonanywhere.com/*).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

Used ChatGPT to generate background picture, and Icon pictures
