FROM continuumio/miniconda3:4.5.12

# Prepare conda
RUN conda update conda -y

# Set up a user different to root which is best practices and needed for mybinder.org.
ARG NB_USER=opensourceeconomics
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# Copy necessary content from the repository.
COPY docs ${HOME}/docs
COPY respy ${HOME}/respy
COPY setup.py ${HOME}
COPY README.rst ${HOME}
COPY environment.yml ${HOME}

# Make everything in the home directory owned by the user.
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}
WORKDIR ${HOME}

# Prepare conda environment.
RUN conda init
RUN conda env create
RUN echo "conda activate respy" >> ~/.bashrc

# Install current version of respy.
RUN conda run --name respy pip install .
