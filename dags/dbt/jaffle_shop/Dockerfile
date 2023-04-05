FROM python:3.9

RUN pip install dbt-postgres==1.3.1 psycopg2==2.9.3 pytz

ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST=host.docker.internal
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_HOST=${POSTGRES_HOST}

# TO REMOVE:
RUN mkdir -p dags/dbt/jaffle_shop
COPY . dags/dbt/jaffle_shop

RUN mkdir /root/.dbt
COPY profiles.yml /root/.dbt/profiles.yml

COPY . .

