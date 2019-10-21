# base image
FROM continuumio/miniconda3:4.6.14
# note: Using the miniconda base because I want to install numpy with some
# optimisation C-libraries such as openblas which conda does for you
# when you install numpy.

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

RUN conda install --yes --freeze-installed -q \
    -c anaconda \
    python==3.7.3 \
    python-blosc \
    cytoolz \
    conda-forge::pip \
    nomkl \
    numpy==1.17.2 \
    tqdm \
    conda-forge::marshmallow==3.2.0 \
    conda-forge::flask==1.1.1 \
    && conda clean -tipsy \
    && find /opt/conda/ -type f,l -name '*.a' -delete \
    && find /opt/conda/ -type f,l -name '*.pyc' -delete \
    && find /opt/conda/ -type f,l -name '*.js.map' -delete \
    && rm -rf /opt/conda/pkgs
    # dask==2.3.0 \
    # && find /opt/conda/lib/python*/site-packages/bokeh/server/static -type f,l -name '*.js' -not -name '*.min.js' -delete \

# Pillow dependencies
# RUN apk --no-cache add python-dev  jpeg-dev \
#                       zlib-dev \
#                       freetype-dev \
#                       lcms2-dev \
#                       openjpeg-dev \
#                       tiff-dev \
#                       tk-dev \
#                       tcl-dev \
#                       harfbuzz-dev \
#                       fribidi-dev

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --quiet --no-cache-dir -r requirements.txt

# add docker-entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
RUN ln -s /usr/src/app/entrypoint.sh /entrypoint.sh

# add app
COPY . /usr/src/app

# install our arc_logging library
WORKDIR /usr/src/app/arc_logging
RUN python setup.py install

# Install our simulation package
WORKDIR /usr/src/app/arc_simulation
RUN python setup.py install

# go back to app source directory
WORKDIR /usr/src/app

# Start the container with entrypoint or comment to use manual below
ENTRYPOINT ["/entrypoint.sh"]
