FROM continuumio/miniconda3:4.6.14


LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

RUN conda install --yes --freeze-installed -q \
    -c anaconda \
    python==3.7.3 \
    python-blosc \
    cytoolz \
    pip \
    nomkl \
    dask==2.3.0 \
    numpy==1.16.4 \
    conda-forge::marshmallow==3.0.1 \
    conda-forge::flask==1.0.2 \
    conda-forge::socat \
    && conda clean -tipsy \
    && find /opt/conda/ -type f,l -name '*.a' -delete \
    && find /opt/conda/ -type f,l -name '*.pyc' -delete \
    && find /opt/conda/ -type f,l -name '*.js.map' -delete \
    && find /opt/conda/lib/python*/site-packages/bokeh/server/static -type f,l -name '*.js' -not -name '*.min.js' -delete \
    && rm -rf /opt/conda/pkgs

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --quiet --no-cache-dir -r requirements.txt

# add docker-entrypoint.sh
COPY ./docker-entrypoint.sh /usr/src/app/docker-entrypoint.sh
RUN chmod +x /usr/src/app/docker-entrypoint.sh
RUN ln -s /usr/src/app/docker-entrypoint.sh /docker-entrypoint.sh

# add app
COPY . /usr/src/app

# which conda --> /opt/conda/bin/conda
# which python --> /opt/conda/bin/python

ENTRYPOINT ["/docker-entrypoint.sh"]
