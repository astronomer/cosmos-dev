FROM quay.io/astronomer/astro-runtime:7.1.0

# install cosmos locally as an editable package
USER root
WORKDIR /usr/local/airflow/include/astronomer-cosmos
RUN pip install -e .[dbt-postgres]
USER astro