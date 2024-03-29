FROM jupyter/base-notebook

LABEL maintainer="Andrew Che <andrew@neuraldev.io>"

USER root

RUN apt-get update \
  && apt-get install -yq --no-install-recommends graphviz git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER $NB_USER

RUN conda install --yes --freeze-installed -q \
    -c anaconda \
    python-blosc \
    cytoolz \
    dask==2.3.0 \
    nomkl \
    numpy==1.17.2 \
    pandas==0.25.1 \
    ipywidgets \
    pymongo \
    dask-labextension==1.0.0 \
    python-graphviz \
    plotly::plotly \
    plotly::chart-studio \
    && jupyter labextension install @jupyter-widgets/jupyterlab-manager@1.0.1 dask-labextension@1.0.0 \
    && conda clean -tipsy \
    && jupyter lab clean \
    && jlpm cache clean \
    && npm cache clean --force \
    && find /opt/conda/ -type f,l -name '*.a' -delete \
    && find /opt/conda/ -type f,l -name '*.pyc' -delete \
    && find /opt/conda/ -type f,l -name '*.js.map' -delete \
    && find /opt/conda/lib/python*/site-packages/bokeh/server/static -type f,l -name '*.js' -not -name '*.min.js' -delete \
    && rm -rf /opt/conda/pkgs

USER root

# Create the /opt/app directory, and assert that Jupyter's NB_UID/NB_GID values
# haven't changed.
RUN mkdir /opt/app \
    && if [ "$NB_UID" != "1000" ] || [ "$NB_GID" != "100" ]; then \
        echo "Jupyter's NB_UID/NB_GID changed, need to update the Dockerfile"; \
        exit 1; \
    fi

#COPY ./theme-dark-extension $CONDA_DIR/share/jupyter/lab/themes/\@jupyterlab/theme-dark-extension

# Copy over the example as NB_USER. Unfortuantely we can't use $NB_UID/$NB_GID
# in the `--chown` statement, so we need to hardcode these values.
COPY --chown=1000:100 examples/ /home/$NB_USER/examples
COPY --chown=1000:100 notebooks/ /home/$NB_USER/notebooks

COPY ./notebooks /home/$NB_USER/notebooks
WORKDIR /home/$NB_USER

USER $NB_USER


CMD ["start.sh", "jupyter", "lab"]
