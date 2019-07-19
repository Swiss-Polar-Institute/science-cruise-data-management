FROM debian:stretch-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
COPY requirements.txt entrypoint.sh /code/
RUN apt-get update && apt-get install --no-install-recommends --yes \
	python3-pip python3-setuptools python3-wheel libpython3.5-dev \
	gcc-6 gcc \
	libmariadbclient-dev libmariadbclient18 mysql-common && \
    pip3 install -r /code/requirements.txt && \
    apt-get purge -y libpython3.5-dev libmariadbclient-dev && \
    apt-get autoremove -y && \
    apt-get clean

WORKDIR /code/ScienceCruiseDataManagement
ENTRYPOINT ["/code/entrypoint.sh"]
