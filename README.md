# ProofChecker
A web application for verifying mathematical proofs using Truth-Functional Logic (TFL) and First Order Logic (FOL), currently utilized by professors and students in courses at Drexel University.  Developed with the Django (Python) web framework.

This system is live in production and publicly available at https://proof-tool.herokuapp.com/

# Dependencies
These are the dependencies:
- Python 3.8 (https://www.python.org/downloads/)
- pipenv (from the command line, run 'pip install pipenv')

# How to Run
- Clone this git repository, and navigate to the top-level directory
- On the command line, run 'pipenv install' to install project dependencies (e.g. Django)
- On the command line, run 'pipenv shell' to activate the virtual environment
- On the command line, run 'python manage.py makemigrations' to create migration files
- On the command line, run 'python manage.py migrate' to migrate data models to the SQLite database
- On the command line, run 'python manage.py runserver' to initiate the server
- Open an internet browser and navigate to http://127.0.0.1:8000/

# How to Test
- On the command line, run 'python manage.py test' to execute tests
- To run the code coverage tool, on the command line, run 'coverage run manage.py test'
- To view a code coverage report, on the command line, run 'coverage report' (after previous step)
- To view an HTML version of the code coverage report, on the command line, run 'coverage html' and then navigate to the 'htmlcov' directory

# Documentation
The following documentation can be found in the 'docs' folder:
- Requirements Specification and Use Cases
- Architecture and Design Specification
- Test Plan
