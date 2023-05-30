<p align="center">
  <img alt="divelogo" src="https://docs.diveapi.co/images/logo_dark-1a726960.png">
</p>

<p align="center">
  <a href="https://docs.diveapi.co/" target="blank">Dive API Docs</a>
</p>

## Dive is an open-source universal API for business integrations

We believe **open-source** is the best way to solve every growth integrations pain, covering the **long tail of data sources**. 

- Handling authentication for your integrations
- Unified one API schema to exchange data with your or your customers' business apps

### Schema docs

[CRM](https://docs.diveapi.co/#crm), Marketing Automation, Accounting, HRIS, Ticketing, Recruiting ATS

## Table of Contents

- [Quick start](#quick-start)
- [Docs and support](#docs-and-support)
- [Contributing](#contributing)

## Quick start

### Requirements

- Python 3.10
- Django 4.2
- Django REST Framework

### Run Dive locally

```
git clone https://github.com/divedevhq/dive.git
cd dive
```
After you cloned the repository, you want to create a virtual environment, by running the command
```
python -m venv venv && source venv/bin/activate
```

You can install all the required dependencies by running
```
pip install -r requirements.txt
```


You can add .env file under dive folder with following:

SECRET_KEY=YOUR Secret Key <br/>
DEBUG=True<br/>
ENVIRONMENT=test<br/>
DOMAIN=http://localhost:8000/<br/>
ALLOWED_HOSTS=.localhost

To connect with other database servers, add DATABASES json to your .env file, for example <br/>
DATABASES= {"default":{"ENGINE": "django.db.backends.postgresql","NAME": "postgres","USER":"postgres", "PASSWORD": "54321","HOST":"localhost","PORT":"5432"}}

Then simply apply the migrations:
```
python manage.py migrate
```

You can now run the development server:

```
python manage.py runserver
```

You can now open http://localhost:8000 to view the web app.
To <a href="https://docs.diveapi.co/#connect-your-instance" target="blank"> connect with your instance</a>, follow web app UI instructions.

To connect with your customer's instances, follow the instructions on web app UI and <a href="https://docs.diveapi.co/#connect-multiple-instances"> API doc</a>.


### Dive Cloud

<a href="mailto:sherry@diveapi.co">Sign up for cloud version</a>



## Docs and support
Read how to use Dive API in our <a href="https://docs.diveapi.co/" target="blank">documentation</a>

Supported business apps can be found at integrations/config.yaml, or open http://localhost:8000/integrations   

<a href="mailto:sherry@diveapi.co">Ask questions, request integrations or give feedback</a>

## Contributing
Get started by checking Github issues and creating a Pull Request. An easy way to start contributing is to update an existing connector or create a new connector. You can find the code for existing connectors in the connectors directory. The Dive platform is written in python.

## License

See the <a href="https://github.com/DiveDevHQ/dive/blob/master/LICENSE">LICENSE</a> file for licensing information
