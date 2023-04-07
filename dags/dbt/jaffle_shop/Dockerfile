FROM python:3.9

RUN pip install dbt-postgres==1.3.1 psycopg2==2.9.3 pytz

ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST=host.docker.internal
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_HOST=${POSTGRES_HOST}

# Copy the DBT profile
RUN mkdir /root/.dbt
COPY profiles.yml /root/.dbt/profiles.yml

# Copy the DBT project-specific files
COPY . .

