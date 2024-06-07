<p align="center">
  <img alt="divelogo" width="350" src="https://docs.chenxueyan.com/images/logo_dark-1a726960.png">
</p>

<p align="center">
  <a href="https://docs.chenxueyan.com/" target="blank">Dive API Docs</a>
</p>

## Dive is a managed data platform to build LLM fintech applications

We believe **open-source** is the best way to solve every growth integrations pain, covering the **long tail of data sources**. 

- Handling authentication for your integrations
- Unified data platform that syncs and indexes data from your or your customers' financial data source
- Handle compliance and security

### Managed data sources

CRM, Documentations, Payment, KYC, Databases

### Demo
<p align="center">
  <img alt="divelogo" width="700" src="https://docs.chenxueyan.com/images/demo.png">
</p>

<p align="center">
  <img alt="divelogo" width="700" src="https://docs.chenxueyan.com/images/playground.png">
</p>

 
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

You can install all the required dependencies by running command

Prod ready:
```
pip install -r requirements.txt
```

If you have issue installing chromadb, try to run below command:
```
export HNSWLIB_NO_NATIVE=1 
```

You can add a **.env** file under "dive" folder with the following content:
```
SECRET_KEY=YOUR Secret Key  
DEBUG=True  
ENVIRONMENT=test 
DOMAIN=http://localhost:8000/  
ALLOWED_HOSTS=.localhost  
CORS_ORIGIN_WHITELIST=http://localhost:3000  
HOME_URL=http://localhost:3000  
```

Then simply apply the migrations:
```
python manage.py migrate
```

You can now run the development server:

```
python manage.py runserver
```
Open http://localhost:8000 and follow web app UI instructions to connect with your data sources.

Once authentication is completed, data with default format will be indexed into vector DB. 

### Dive Cloud

<a href="mailto:sherry@diveapi.co">Sign up for cloud version</a>



## Docs and support
Read how to use Dive API in our <a href="https://docs.chenxueyan.com/" target="blank">documentation</a>

Supported business apps can be found at integrations/config.yaml

<a href="mailto:sherry@chenxueyan.com">Ask questions, request integrations or give feedback</a>

## Contributing
Get started by checking Github issues and creating a Pull Request. An easy way to start contributing is to update an existing connector or create a new connector. You can find the code for existing connectors in the connectors directory. The Dive platform is written in python.

## License

See the <a href="https://github.com/DiveDevHQ/dive/blob/master/LICENSE">LICENSE</a> file for licensing information
