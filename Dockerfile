FROM ubuntu:latest

RUN apt update
RUN apt -y install g++ gcc curl
RUN apt -y install python python3 python3-pip python3-venv
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
RUN source $HOME/.poetry/env
RUN poetry install