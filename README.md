<p align="center">
  <img alt="divelogo" width="350" src="https://docs.diveapi.co/images/logo_dark-1a726960.png">
</p>

<p align="center">
  <a href="https://docs.diveapi.co/" target="blank">Dive API Docs</a>
</p>

## Dive is a managed data platform to build LLM customer support applications

We believe **open-source** is the best way to solve every growth integrations pain, covering the **long tail of data sources**. 

- Handling authentication for your integrations
- Unified data platform that syncs and indexes data from your or your customers' SaaS applications

### Managed data sources

CRM, Ticketing, Documentations, Databases

## Table of Contents

- [Quick start](#quick-start)
- [Docs and support](#docs-and-support)
- [Contributing](#contributing)

## Quick start

### Requirements

- Python 3.11

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

If you have trouble install chromadb, you might need to run below command
```
export HNSWLIB_NO_NATIVE=1 
```

You can add .env file under "dive" folder with following:

SECRET_KEY=YOUR Secret Key <br/>
DEBUG=True <br/>
ENVIRONMENT=test <br/>
DOMAIN=http://localhost:8000/ <br/>
ALLOWED_HOSTS=.localhost <br/>
CORS_ORIGIN_WHITELIST=http://localhost:3000 <br/>
HOME_URL=http://localhost:3000

Then simply apply the migrations:
```
python manage.py migrate
```

You can now run the development server:

```
python manage.py runserver
```

Then setup frontend, open your terminal and cd into "frontend" folder, run the following command.

```
npm install
npm start
```

You can now open http://localhost:3000 to view the web app, and follow web app UI instructions to connect with your data sources.

Once authentication is completed, data with default format will be indexed into vector DB. 

### Dive Cloud

<a href="mailto:sherry@diveapi.co">Sign up for cloud version</a>



## Docs and support
Read how to use Dive API in our <a href="https://docs.diveapi.co/" target="blank">documentation</a>

Supported business apps can be found at integrations/config.yaml

<a href="mailto:sherry@diveapi.co">Ask questions, request integrations or give feedback</a>

## Contributing
Get started by checking Github issues and creating a Pull Request. An easy way to start contributing is to update an existing connector or create a new connector. You can find the code for existing connectors in the connectors directory. The Dive platform is written in python.

## License

See the <a href="https://github.com/DiveDevHQ/dive/blob/master/LICENSE">LICENSE</a> file for licensing information
