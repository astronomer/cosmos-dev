FROM quay.io/astronomer/astro-runtime:7.3.0


USER root

# install cosmos locally as an editable package
WORKDIR /usr/local/airflow/include/astronomer-cosmos
RUN pip install -e .

# install python virtualenv to run dbt
WORKDIR /usr/local/airflow
COPY dbt-requirements.txt ./
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir -r dbt-requirements.txt && deactivate


# create a dbt base wrapper around the venv
RUN echo -e '#!/bin/bash' > /usr/bin/dbt && \
    echo -e 'source /usr/local/airflow/dbt_venv/bin/activate && dbt-ol "$@"' >> /usr/bin/dbt

# give everyone access to the executable
RUN chmod -R 777 /usr/bin/dbt

USER astro