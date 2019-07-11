FROM continuumio/miniconda3:4.6.14

RUN conda install --yes --freeze-installed \
    -c anaconda \
    python==3.7.3 \
    pip \
    nomkl \
    numpy==1.16.4 \
    marshmallow==3.0.0b8 \
    anaconda::redis==5.0.3 \
    conda-forge::flask==1.0.2 \
    conda-forge::socat \
    && conda clean -tipsy \
    && find /opt/conda/ -type f,l -name '*.a' -delete \
    && find /opt/conda/ -type f,l -name '*.pyc' -delete \
    && find /opt/conda/ -type f,l -name '*.js.map' -delete \
    && rm -rf /opt/conda/pkgs

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add docker-entrypoint.sh
COPY ./docker-entrypoint.sh /usr/src/app/docker-entrypoint.sh
RUN chmod +x /usr/src/app/docker-entrypoint.sh
RUN ln -s /usr/src/app/docker-entrypoint.sh /docker-entrypoint.sh

# add app
COPY . /usr/src/app

# which conda --> /opt/conda/bin/conda
# which python --> /opt/conda/bin/python

# Start the container with entrypoint or comment to use manual below
ENTRYPOINT ["/docker-entrypoint.sh"]
