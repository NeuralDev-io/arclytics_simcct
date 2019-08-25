FROM continuumio/miniconda3:4.6.14

# This is the base image for both a Dask Scheduler and a Dask Worker.
# The scheduler should only contain 1 container.
# It is possible to replicate and scale the Dask Worker to allow better
# distributed processing.
# To scale on build/run: docker-compose up --scale dask-worker=2
# To scale after run: docker-compose scale dask-worker=2

# Reference:
# https://github.com/dask/dask-docker
# https://docs.dask.org/en/latest/setup/docker.html

# note: Ensure you add all required dependencies if the processing from other
# containers rely on packages.
RUN conda install --yes --freeze-installed -q \
    -c anaconda \
    python==3.7.3 \
    python-blosc \
    cytoolz \
    dask==2.3.0 \
    nomkl \
    numpy==1.16.4 \
    pandas==0.25.0 \
    tini==0.18.0 \
    plotly::plotly==4.1.0 \
    plotly::chart-studio==1.0.0 \
    && conda clean -tipsy \
    && find /opt/conda/ -type f,l -name '*.a' -delete \
    && find /opt/conda/ -type f,l -name '*.pyc' -delete \
    && find /opt/conda/ -type f,l -name '*.js.map' -delete \
    && find /opt/conda/lib/python*/site-packages/bokeh/server/static -type f,l -name '*.js' -not -name '*.min.js' -delete \
    && rm -rf /opt/conda/pkgs

#COPY prepare.sh /usr/bin/prepare.sh

RUN mkdir /opt/app

# The prepare.sh script allows you to add additional dependencies
#ENTRYPOINT ["tini", "-g", "--", "/usr/bin/prepare.sh"]
