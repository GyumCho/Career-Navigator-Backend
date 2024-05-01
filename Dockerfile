# Author: Rolf van Kleef, Stichting Inter-Actief Personal Computing, Drienerlose Zeilvereniging Euros
# Licensed under LGPL v2

FROM python:3.12 as build

RUN mkdir /project
WORKDIR /project

RUN apt-get update && apt-get -y install gettext                        &&\
    pip3 --no-input install uvicorn[standard] psycopg                           &&\
    find /usr -type d -name __pycache__ -exec rm -r {} +                &&\
    rm -rf /usr/lib/python*/ensurepip                                   &&\
    rm -rf /usr/lib/python*/turtledemo                                  &&\
    rm -rf /usr/lib/python*/idlelib                                     &&\
    rm -f /usr/lib/python*/turtle.py                                    &&\
    rm -f /usr/lib/python*/webbrowser.py                                &&\
    rm -f /usr/lib/python*/doctest.py                                   &&\
    rm -f /usr/lib/python*/pydoc.py                                     &&\
    rm -rf /root/.cache /var/cache

COPY requirements.txt requirements.txt

RUN pip3 --no-input install -r /project/requirements.txt

COPY . /project/

RUN python manage.py compilemessages

VOLUME [ "/project/careernavigator/local.py", "/project/api" ]
EXPOSE 8000
ENTRYPOINT ["/project/entrypoint.sh"]
