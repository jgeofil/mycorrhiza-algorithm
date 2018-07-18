# Set the base image
FROM ubuntu:16.04
# Dockerfile author / maintainer
MAINTAINER Name <email.id@here>

RUN apt-get update
RUN apt-get install -y default-jre python3
RUN apt-get install -y python3-pip python3-tk

RUN pip3 install numpy scikit-learn tqdm pathos scipy matplotlib

COPY / /temp
RUN ls
RUN pip3 install -e temp --force-reinstall
ENV PATH "$PATH:temp/splitstree4"








