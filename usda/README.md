# USDA

Django web app to scrape [USDA-APHIS](https://acissearch.aphis.usda.gov/LPASearch/faces/CustomerSearch.jspx) and serve data in a more powerful user interface and API.

## Installation and Setup

This project is still a work in progress so the README will be updated as it finalizes. In the meantime, you can get a working development environment set up by doing the following.

### App Setup

This is a very basic Django web app. Instructions for local setup are below.

1. Clone the project
2. Create a virtul environment for Python 3.4.x . If you have virtualenv and virtualenvwrapper then `mkvirtualenv openitup_usda -p python3`.
3. Install [PhantomJS](http://phantomjs.org/)
4. Install requirements `pip install -r requirements.txt`. 
5. Configure database settings in `usda/settings.py`. You'll need to create the database if it doesn't exist.
6. Populate database with schema `python manage.py migrate`
7. Populate database with licensee data and start scraping inspection data `python manage.py import_inspections --file data/usda-certificate-status-active-2016-01-05.csv` . This will take a VERY long time to scrape completely.
8. Run development server `python manage.py runserver`. Django defaults to `http://127.0.0.1:8000/`
