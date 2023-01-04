# cosmos-dev

This is an Astro CLI project used to develop Cosmos.

## Getting Started

1. Ensure you have the Astro CLI >= 1.8.0 installed
2. Clone `astronomer/astronomer-cosmos` into the `include/` directory

## Running

Run `astro dev start` to start the project. By default, this runs against the Airflow metadata database. To reset the database, run `astro dev kill` and then `astro dev start`.

## Examples

This repo comes with a few examples located in the `dags/` and `dbt/` directories. These are meant to be used as a reference for how to use the various features of Cosmos.
