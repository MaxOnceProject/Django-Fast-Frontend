# https://hub.docker.com/_/python
FROM python:3.10-bullseye

# This is where the project source lives
ARG PROJECT_ROOT=/opt/project
ENV PYTHONPATH=${PROJECT_ROOT}

RUN mkdir -p ${PROJECT_ROOT} \
    && pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org" \
    && pip install -U pip setuptools==67.8.0

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --prefer-binary -r /tmp/requirements.txt

COPY . ${PROJECT_ROOT}
WORKDIR ${PROJECT_ROOT}

RUN pip install -e .

RUN chmod +x manage.py \
#    && python manage.py collectstatic \
    && python manage.py migrate

ENV DJANGO_SETTINGS_MODULE=project.settings
ENV DJANGO_ENVIRONMENT=dev
EXPOSE 8000

