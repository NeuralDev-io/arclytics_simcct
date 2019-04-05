# Arclytics SimCCT API

This is the CSIT321 Arclytics SimCCT Django REST back-end API source code repository.

Arclytics SimCCT API (pronounced *ark-lit-icks*) is a project in collaboration with the Australian Nuclear Science and Technology Organisation (ANSTO) to provide a Phase Transformation web application tool. <br><br>
The API provides mathematical algorithms for computing both the Li (98) and Kirkaldo (83) methods for Phase Transformation simulations.<br><br>
[**Play with the tool »**]()  
<br>

[Website](https://uow.neuraldev.io) · [API Documentation](https://bitbucket.org/neuraldev/arclytics_simcct_api/wiki/Home) · [LICENSE](https://bitbucket.org/neuraldev/arclytics_simcct_api/src/master/LICENSE)
<br><br>


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
version `4.6.9`. 

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
```

#### Installing

To install the development environment, the following steps will be required. It is assumed a Linux operating system such as Ubuntu 18.04 will be used for this. Additional installation steps for Windows will be described to be included at a later date. 

```bash
$ conda create -n arclytics_api \ 
	python=3.7.2 \
	conda-forge::django=2.2 \
	conda-forge::djangorestframework=3.9.2 \
	numpy=1.16.2 \
	-c anaconda
$ source activate arclytics_api
```

#### Installing from Environment YAML

You could also install from the provided `environment-dev_unix.yml` (Linux/MacOS) or `environment-dev_win.yml` (Windows) file.

##### Linux/MacOS

```bash
$ conda env create -f environment_unix.yml
```

##### Windows

```bash
> conda env create -f environment_win.yml
```

### Database

To ensure testing, you will need to connect the following database to the Django back-end.

* TBC

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

* Andrew (Dinh) Che \<codeninja55\> (andrew at neuraldev dot io)
* Dinol Shretha \<username\> (email)
* David Matthews \<username\> (email)
* Duong (Dalton) le \<username\> (email)
* Arvy Salazar \<username\> (email)
* Matthew Greentree \<username\> (email)

You can view the awesome contributions each member has made [here](<https://bitbucket.org/neuraldev/arclytics_simcct_api/addon/bitbucket-graphs/graphs-repo-page#!graph=contributors&uuid=edfeb8b1-d219-47a9-a81c-9c3ccced56f8&type=c&group=weeks>).

## Acknowledgements

We thank the following organisations, departments, and individuals for their kind and immense support with this project:

* Australian Nuclear Science and Technology Organisation (ANSTO)
    * Dr. Ondrej Muransky \<omz@ansto.gov.au\>
    * Dr. Philip Bendeich \<pbx@ansto.gov.au\>
    * Dr. Luiz Bortolan \<luizb@ansto.gov.au\>
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