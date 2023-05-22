<p align="center">
  <img alt="divelogo" src="https://docs.diveapi.co/images/logo_dark-d6a70afa.png">
</p>

<p align="center">
  <a href="https://docs.diveapi.co/" target="blank">Dive Api Docs</a>
</p>

## Dive is an open-source universal Api for business integrations

We believe **open-source** is the best way to solve ever growth integrations pain, convering **long tail of data sources**. 

- Handling authentication for your integrated apps
- Normalized one api schema for all your business integrations CRUD needs

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

Then simply apply the migrations:
```
python manage.py migrate
```

You can add .env file under dive folder with following:

SECRET_KEY=YOUR Secret Key <br/>
DEBUG=True<br/>
ENVIRONMENT=test<br/>
DOMAIN=http://localhost:8000/
ALLOWED_HOSTS=.localhost example.com

You can now run the development server:

```
python manage.py runserver
```

To <a href="https://docs.diveapi.co/#connect-your-instance" target="blank"> connect with your instance</a>, follow web app UI http://localhost:8000/ instructions.

To connect with your customer's instances, follow the instructions on web app UI http://localhost:8000/ and <a href="https://docs.diveapi.co/#connect-multiple-instances"> api doc</a>.


### Dive Cloud

<a href="mailto:sherry@diveapi.co">Sign up for cloud version</a>



## Docs and support
Read how to use Dive Api in our <a href="https://docs.diveapi.co/" target="blank">documentation</a>

<a href="mailto:sherry@diveapi.co">Ask questions, request integrations or give feedback</a>

## Contributing
Get started by checking Github issues and creating a Pull Request. An easy way to start contributing is to update an existing connector or create a new connector. You can find the code for existing connectors in the connectors directory. The Dive platform is written in python.

## License

See the <a href="https://github.com/DiveDevHQ/dive/blob/master/LICENSE">LICENSE</a> file for licensing information