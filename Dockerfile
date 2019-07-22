FROM debian:buster-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
COPY requirements.txt entrypoint.sh /code/
RUN apt-get update && apt-get install --no-install-recommends --yes \
	python3-pip python3-setuptools python3-wheel libpython3.7-dev \
	gcc-7 gcc \
	libmariadbclient-dev libmariadb-dev-compat \
	libmariadb3 && \
    pip3 install -r /code/requirements.txt && \
    apt-get purge -y libpython3.7-dev \
	libmariadbclient-dev libmariadb-dev-compat \
	gcc-7 gcc && \
    apt-get autoremove -y && \
    apt-get clean

WORKDIR /code/ScienceCruiseDataManagement
ENTRYPOINT ["/code/entrypoint.sh"]
