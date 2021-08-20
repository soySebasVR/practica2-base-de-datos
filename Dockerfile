FROM python:3

RUN apt-get update && apt-get install -y gunicorn
RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "/"]

RUN pipenv install --deploy --system --ignore-pipfile

COPY ["app/", "/src"]
WORKDIR /src/

