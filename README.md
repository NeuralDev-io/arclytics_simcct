# Arclytics SimCCT API

This is the CSIT321 Arclytics SimCCT Django REST back-end API source code repository.

Arclytics SimCCT API (pronounced *ark-lit-icks*) is a project in collaboration with the Australian Nuclear Science and Technology Organisation (ANSTO) to provide a Phase Transformation web application tool.

The API provides mathematical algorithms for computing both the Li (98) and Kirkaldo (83) methods for Phase Transformation simulations.


[**Play with the tool »**]()  


[Website](https://uow.neuraldev.io) · [API Documentation](https://bitbucket.org/neuraldev/arclytics_simcct_api/wiki/Home) · [LICENSE](https://bitbucket.org/neuraldev/arclytics_simcct_api/src/master/LICENSE)



## Table of contents

* Getting started
* Prerequisites
* Tests and Examples
* Deployment
* Versioning
* License
* Authors
* Acknowledgements

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Under the hood, Arclytics SimCCT API uses the following dependencies.

### Virtual Environment

To ensure the testing environment works as expected, you will need to have installed [Anaconda](https://www.anaconda.com/)
version `4.6.12`. 



*NOTE: Installation instructions for Anaconda to come*.



To clone the environment, you will need the following packages:

```
name: arclytics_api
channels:
  - anaconda
  - conda-forge
  - nodefaults
dependencies:
  - django=2.2
  - djangorestframework=3.9.2
  - numpy=1.16.2
  - numpy-base=1.16.2
  - pip=19.0.3
  - python=3.7.2
  - setuptools=40.8.0
  - sqlite=3.27.2
  - psycopg2=2.7.6.1
```

#### Installing

To install the development environment, the following steps will be required. It is assumed a Linux operating system such as Ubuntu 18.04 will be used for this. Additional installation steps for Windows will be described to be included at a later date. 

```bash
$ conda create -n arclytics_api \ 
	python=3.7.2 \
	conda-forge::django=2.1.7 \
	conda-forge::djangorestframework=3.9.2 \
	numpy=1.16.2 \
	psycopg2=2.7.6.1 \
	-c anaconda
$ source activate arclytics_api
```

#### Installing from Environment YAML

**IMPORTANT!!!!** DO NOT USER this option for now. 

You could also install from the provided `environment-dev_unix.yml` (Linux/MacOS) or `environment-dev_win.yml` (Windows) file.

##### Linux

```bash
$ conda env create -f environment-dev_unix.yml
```

##### Windows

```bash
> conda env create -f environment-dev_win.yml
```

### Database

You will need the following versions:

```
docker=18.09.2
postgres=10.7
psycopg2=2.7.6.1
```



To get the database running, install docker from [here](https://www.docker.com/get-started). From here, select **Download for Windows** or **Download for Mac**. It will ask you to login or create an account before you can download. Once you have create an account, please select **Get Docker Desktop for Windows (stable)**. During installation, **DO NOT** select the option for Windows containers. 

Optionally, you can download and use the Docker GUI by downloading Kitematic from [here](https://docs.docker.com/toolbox/toolbox_install_windows/) for Windows.

The Docker Postgres documentation can be found [here](https://hub.docker.com/_/postgres). You can download the images from this Docker hub by using the following command in Command Prompt or PowerShell (Windows) or Terminal (macOS and Linux).

**Windows**

```powershell
> docker pull postgres:10.7
```



**1)** Test that you have pulled the correct Docker version and Postgres image:

```powershell
> docker -v 
Docker version 18.09.2, build 6247962

> docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
postgres            10.7                200d7af0a4e1        3 weeks ago         230MB
```



**2)** Create a Postgres Docker container:

```powershell
> docker run -p 5432:5432 --name Arclytics_Sim -e POSTGRES_PASSWORD=ENDGAME -d postgres:10.7
```
Where:

* `-p 5432:5432` connects the exposed Docker port 5432 to your local port 5432
* `--name` is the name of the container you have created.
* `-e POSTGRES_PASSWORD=ENDGAME` sets the environment variable for superuser password for PostgreSQL.
* `-d postgres:10.7`  the Docker image 



To test if the container is running properly:

```powershell
> docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
d021daf7f1af        postgres:10.7       "docker-entrypoint.s…"   16 minutes ago      Up 16 minutes       0.0.0.0:5432->5432/tcp   Arclytics_Sim
```



**3)** Connect to the running container and run some queries using the psql shell:

```bash
> docker exec -it Arclytics_Sim psql -U postgres
```



**4)** Create the Database and User. Additionally grant all the privileges for that database to the user. 

Run all these commands sequentially.

```bash
CREATE USER neuraldev;
ALTER USER neuraldev WITH PASSWORD 'THANOS';
CREATE DATABASE arclytics;
GRANT ALL PRIVILEGES ON DATABASE arclytics TO neuraldev;
```



You could run those steps manually above, or you can be a ninja and do this instead:

Ensure you are in the main `arclytics_sim_api` directory.

```powershell
> docker cp postgres\init-user-db.sql Arclytics_Sim:/docker-entrypoint-initdb.d/init-user-db.sql
> docker exec -u postgres Arclytics_Sim psql postgres postgres -f docker-entrypoint-initdb.d/init-user-db.sql
```

That should create everything for you without you ever having to connect to the psql shell (unless you screw up and have to go in there to delete it ofcourse). 



**5)** If necessary, change the Django settings file to use the running Postgres Docker container instance.

This is what you will see in the default `settings.py`.

```bash
DATABASES = {
	'default': {
    	'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
     }
}	
```

Change `settings.py` as follows:

```bash
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

Some handy docker commands:

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
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                     PORTS               NAMES
2afdef182d29        postgres:10.7       "docker-entrypoint.s…"   12 minutes ago      Exited (0) 4 minutes ago                       Arclytics_Sim
```

**Deleting a container**

```powershell
> docker stop Arclytics_Sim
Arclytics_Sim

> docker container ls -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                     PORTS               NAMES
2afdef182d29        postgres:10.7       "docker-entrypoint.s…"   12 minutes ago      Exited (0) 4 minutes ago                       Arclytics_Sim

> docker container rm Arclytics_Sim
```

*NOTE:* You cannot have two containers of the same name so if you are updating a container, you will need to delete it first before you can create a new one.



P.S. If you want to learn more about Docker click [here](https://docs.docker.com/get-started/).

**IMPORTANT!!!** You must start the Docker container with this command every time you run Django.

`> docker start Arclytics_Sim`



### Running the server

To run the Django server:

```bash
(arclytics_api) $ cd arclytics
(arclytics_api) $ python manage.py runserver 8000
```

*NOTE TO SELF: You must figure out some way to provide instructions on how to create a user to allow access to the web application.*



## Tests and Examples

* TBC

## Deployment

* TBC

### Built with

* TBD

## Versioning

Internally, we use [Semantic Versioning guidelines](https://semver.org/) for our versioning standard. Sometimes we can make a mess of it, but we adhere to those rules whenever possible. 

For the versions available, please see the tags from [release](https://bitbucket.org/neuraldev/arclytics_simcct_api/branches/?branchtype=release) branch directory in this repository. 

## License

To be determined.

You can view the full details of the license at [LICENSE.md](<https://bitbucket.org/neuraldev/arclytics_simcct_api/src/master/README.md>). 

## Authors

* Andrew (Dinh) Che <@codeninja55\> (andrew at neuraldev dot io)
* Dinol Shretha <@dinolsth\> (email)
* David Matthews <username\> (email)
* Duong (Dalton) Le <username\> (email)
* Arvy Salazar <username\> (email)
* Matthew Greentree <username\> (email)

You can view the awesome contributions each member has made [here](<https://bitbucket.org/neuraldev/arclytics_simcct_api/addon/bitbucket-graphs/graphs-repo-page#!graph=contributors&uuid=edfeb8b1-d219-47a9-a81c-9c3ccced56f8&type=c&group=weeks>).

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

We also thank the open source community for making available awesome packages and libraries for our ease of development and deployment. The following are used under the hood of Arclytics SimCCT API:

* [Django](https://www.djangoproject.com/) - a high-level Python Web framework that encourages rapid development and clean, pragmatic design.
* [Django REST Framework](https://www.django-rest-framework.org/) - a powerful and flexible toolkit for building Web APIs. 
* [NumPy](http://www.numpy.org/) - the fundamental package for scientific computing with Python.
* PostgreSQL - \<short sentence description\>