# Arclytics Sim API

This is the CSIT321 Arclytics Sim Django REST back-end API source code repository.

Arclytics Sim API (pronounced *ark-lit-icks*) is a project in collaboration with the Australian Nuclear Science and Technology Organisation (ANSTO) to provide a Phase Transformation web application tool.

The API provides mathematical algorithms for computing both the Li (98) and Kirkaldo (83) methods for Phase Transformation simulations.


[**Play with the tool »**]()  

[Website](https://uow.neuraldev.io) · [API Documentation](https://bitbucket.org/neuraldev/arclytics_sim_api/wiki/Home) · [LICENSE](https://bitbucket.org/neuraldev/arclytics_sim_api/src/master/LICENSE)



## Table of contents

* [Getting started](#Getting Started)
  * [Prerequisites](#Prerequisites)
  * [Virtual Environment](#Virtual Environment)
  * [Database](#Database)
* [Tests and Examples](#Tests and Examples)
* [Deployment](#Deployment)
* [Versioning](#Versioning)
* [License](#License)
* [Authors](#Authors)
* [Acknowledgements](#Acknowledgements)



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.



### Prerequisites

Under the hood, Arclytics Sim API uses the [Anaconda](https://www.anaconda.com/) virtual environment and [Docker](https://www.docker.com/) container for our [PostgreSQL](https://hub.docker.com/_/postgres) database. 

To ensure this works properly, you will need the following versions as a minimum:

```
conda>=4.6.12
docker>=18.9.5
```



#### Installing Anaconda

For Windows, Linux or macOS, you can download the installer for Anaconda [here](https://www.anaconda.com/distribution/#download-section).

Once installed, if you are using Linux/macOS, open the terminal to create a virtual environment. If you are using Windows, you can open the Anaconda Prompt.

![Windows Anaconda Prompt](./docs/assets/anaconda-prompt-1.png)

To get the database running, install Docker from [here](https://www.docker.com/get-started). From here, select **Download for Windows** or **Download for Mac**. It will ask you to login or create an account before you can download. Once you have create an account, please select **Get Docker Desktop for Windows (stable)**. During installation, **DO NOT** select the option for Windows containers. 

Optionally, you can download and use the Docker GUI by downloading Kitematic from [here](https://docs.docker.com/toolbox/toolbox_install_windows/) for Windows.

![Windows Command Prompt](./docs/assets/cmd-prompt-1.png)



### Virtual Environment

To clone the environment, you will need the following packages:

```
name: arclytics_api
channels:
  - anaconda
  - conda-forge
  - nodefaults
dependencies:
  - django=2.1.7
  - djangorestframework=3.9.2
  - numpy=1.16.2
  - psycopg2=2.7.6.1
  - python=3.7.2
```



#### Creating new Env

To install the development environment, the following steps will be required. 

**Linux/macOS**

```bash
$ conda create --name arclytics_api python=3.7.2 django=2.1.7 conda-forge::djangorestframework=3.9.2 numpy=1.16.2 psycopg2=2.7.6.1 -c anaconda
$ source activate arclytics_api
```

**Windows**

```powershell
> conda create --name arclytics_api python=3.7.2 django=2.1.7 conda-forge::djangorestframework=3.9.2 numpy=1.16.2 psycopg2=2.7.6.1 -c anaconda
> activate arclytics_api
```


#### (Optional) Installing from Environment YAML

You could also install from the provided `environment-dev.yml`.

##### Windows/Linux/macOS

```
$ conda env create -f environment-dev.yml
$ source activate arclytics_api
```


### Database

For this project, we have made our own Docker image for a Postgres container so we can have more control over the initialisation
script used. We can also further extend this image down the track to inlcude testing.

The original Docker Postgres documentation can be found [here](https://hub.docker.com/_/postgres). The Docker repository for the 
image made by <@codeninja55\> can be found [here](https://cloud.docker.com/u/codeninja55/repository/docker/codeninja55/arc-postgres).

You can download the images from this Docker repo by using the following command in Command Prompt or PowerShell (Windows) or Terminal (macOS and Linux). The examples below will be shown in Windows but will be the same for macOS and Linux.

##### Windows

```powershell
> docker pull codeninja55/arc-postgres:latest
```

The `latest` tag will always be maintained for the current version we will be using in development so you can safely use
this tag as it will be maintained internally. 

**1)** Test that you have pulled the correct Docker version and Postgres image:

```powershell
> docker -v 
Docker version 18.09.2, build 6247962

> docker images
REPOSITORY                 TAG                 IMAGE ID            CREATED                  SIZE
codeninja55/arc-postgres   10.7                3ce38d11ff5d        Less than a second ago   230MB
codeninja55/arc-postgres   latest              3ce38d11ff5d        Less than a second ago   230MB
```

**2)** Create a Postgres Docker container:

```powershell
> docker run -p 5432:5432 --name arclytics_db -e POSTGRES_PASSWORD=ENDGAME -d codeninja55/arc-postgres:latest
981cbe28648b4bf08f61b94634bd67e4341ac65cfd4cd6e01ef85874ef301d17
```
Where:

* `-p 5432:5432` connects the exposed Docker port 5432 to your local port 5432
* `--name` is the name of the container you have created.
* `-e POSTGRES_PASSWORD=ENDGAME` sets the environment variable for superuser password for PostgreSQL.
* `-d codeninja55/arc-postgres:latest`  the Docker image 


To test if the container is running properly:

```powershell
> docker ps
CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS              PORTS                    NAMES
981cbe28648b        codeninja55/arc-postgres:latest   "docker-entrypoint.s…"   29 seconds ago      Up 28 seconds       0.0.0.0:5432->5432/tcp   arclytics_db
```

This container has been created with an init script that can be found in `arclytics_sim_api/docker-postgres/init/init-user-db.sh`

```bash
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER neuraldev;
    ALTER USER neuraldev WITH PASSWORD 'THANOS';
    CREATE DATABASE arclytics;
    GRANT ALL PRIVILEGES ON DATABASE arclytics TO neuraldev;
EOSQL
```

It will create the `neuraldev` user that is set as the user in Django settings. 

Optionally, you can connect to the running container and run some queries using the psql shell:

```powershell
> docker exec -it arclytics_db psql -d arclytics -U neuraldev
```
Where:
* Usage: `docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`
* `-i` is the interactive flag to keep the `stdin` open even if not attached.
* `-t` is the flag to allocate a pseudo-TTY
* `psql` will open the psql shell

This will connect to the database `-d arclytics` with the user `-U neuraldev`. Alternatively, you can use the following to connect
to the default `postgres` database with the superuser account `-U postgres`.  

```powershell
> docker exec -it Arclytics_Sim psql -U postgres
```

Some common PostgreSQL commands can be found in [POSTGRES_BASICS.md](./docs/POSTGRES_BASICS.md).


If you ever need to run the init script again, you can do so with the following commands.

Ensure you are in the main `arclytics_sim_api` directory.

```powershell
> docker cp docker-postgres\init-user-db.sql Arclytics_Sim:/docker-entrypoint-initdb.d/init-user-db.sql
> docker exec -u postgres arclytics_db psql postgres postgres -f docker-entrypoint-initdb.d/init-user-db.sql
```
**NOTE:** Using Windows backslashes in this command. 

That should create everything for you without you ever having to connect to the psql shell (unless you screw up and have to go in there to delete it ofcourse). 

**3)** If necessary, change the Django settings file to use the running Postgres Docker container instance.

This is what you will see in the default `settings.py`.

```python
DATABASES = {
	'default': {
    	'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
     }
}	
```

Change `settings.py` as follows:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'arclytics',                      
        'USER': 'neuraldev',
        'PASSWORD': 'THANOS',
        'HOST': 'locahost',
        'PORT': '5432',
    }
}
```

Note: the Docker PSQL runs on port 5432.



#### Docker (Short) Cheatsheet

Some handy Docker commands:

**Starting a container**

```powershell
> docker start <container name>
```
**Stopping a container**

```powershell
> docker stop <container name>
```

**Listing all running containers**

```powershell
> docker ps -a
```

**Listing all containers**

```powershell
> docker container ls -a
CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS                      PORTS               NAMES
981cbe28648b        codeninja55/arc-postgres:latest   "docker-entrypoint.s…"   9 minutes ago       Exited (0) 12 seconds ago                       arclytics_db
```

**Deleting a container**

```powershell
> docker stop arclytics_db
arclytics_db

> docker container ls -a
CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS                      PORTS               NAMES
981cbe28648b        codeninja55/arc-postgres:latest   "docker-entrypoint.s…"   9 minutes ago       Exited (0) 12 seconds ago                       arclytics_db

> docker rm arclytics_db
arclytics_db
```

*NOTE:* You cannot have two containers of the same name so if you are updating a container, you will need to delete it first before you can create a new one.

P.S. If you want to learn more about Docker click [here](https://docs.docker.com/get-started/).



### Running the server

**IMPORTANT!!!** You must start the Docker container with this command every time you run Django.

```bash
$ docker start arclytics_db
```

To run the Django server:

```bash
(arclytics_api) $ cd arclytics
(arclytics_api) $ python manage.py runserver 8000
```

If running the server for the first time, please ensure you migrate the database and create a superuser by doing:
```bash
(arclytics_api) $ cd arclytics
(arclytics_api) $ python manage.py migrate
(arclytics_api) $ python create_superuser.py
(arclytics_api) $ python manage.py runserver 8000
```



## Tests and Examples

* TBC



## Deployment

* TBC



### Built with

* TBD



## Versioning

Internally, we use [Semantic Versioning guidelines](https://semver.org/) for our versioning standard. Sometimes we can make a mess of it, but we adhere to those rules whenever possible. 

For the versions available, please see the tags from [release](https://bitbucket.org/neuraldev/arclytics_sim_api/branches/?branchtype=release) branch directory in this repository. 



## License

To be determined.

You can view the full details of the license at [LICENSE.md](<https://bitbucket.org/neuraldev/arclytics_sim_api/src/master/README.md>). 



## Authors

* Andrew (Dinh) Che <@codeninja55\> (andrew at neuraldev dot io)
* Matthew Greentree <@matthewjgreentree\> (matthew at neuraldev dot io)
* Duong (Dalton) Le <@daltonle_\> (dalton at neuraldev dot io)
* Arvy Salazar <@R-V\> (arvy at neuraldev dot io)
* Dinol Shretha <@dinolsth\> (dinolshrestha at gmail dot com)
* David Matthews <@tree1004\> (davidmatthews1004 at gmail dot com)

You can view the awesome contributions each member has made [here](<https://bitbucket.org/neuraldev/arclytics_sim_api/addon/bitbucket-graphs/graphs-repo-page#!graph=contributors&uuid=edfeb8b1-d219-47a9-a81c-9c3ccced56f8&type=c&group=weeks>).



## Acknowledgements

We thank the following organisations, departments, and individuals for their kind and immense support with this project:

* Australian Nuclear Science and Technology Organisation (ANSTO)
    * Dr. Ondrej Muransky <omz@ansto.gov.au\>
    * Dr. Philip Bendeich <pbx@ansto.gov.au\>
    * Dr. Luiz Bortolan <luizb@ansto.gov.au\>
* University of Wollongong, Faculty of Engineering and Information Sciences, School of Computing and Information Technology
    * Dr. Lei Ye <lei@uow.edu.au\> 
    * Dr. Fenghui Ren <fren@uow.edu.au\>
* University of Wollongong, South Western Sydney campus
    * Dr. Chris Magee
    * Jason Aquilina
    * Student Support Division

We also thank the open source community for making available awesome packages and libraries for our ease of development and deployment. The following are used under the hood of Arclytics Sim API:

* [Django](https://www.djangoproject.com/) - a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
* [Django REST Framework](https://www.django-rest-framework.org/) - a powerful and flexible toolkit for building Web APIs. 
* [NumPy](http://www.numpy.org/) - the fundamental package for scientific computing with Python.
* [PostgreSQL](https://www.postgresql.org/) - a powerful, open-source object-relational database system.