# Apache-Kafka-Airflow-Apache-Cassandra-Containerized-By-Docker-Project
Automated, ETL streaming data (real-time) pipeline that has Random Public API Ingestion . Streams it through Apache Kafka, processes it with Apache Spark, and stores it in Apache Cassandra — all orchestrated by Apache Airflow and containerized with Docker.

# Real-Time Data Engineering Pipeline
A fully automated, end-to-end streaming data pipeline that ingests random user data from a public API, streams it through Apache Kafka, processes it with Apache Spark, and stores it in Apache Cassandra — all orchestrated by Apache Airflow and containerized with Docker.

# Architecture
randomuser.me API
        ↓
  Apache Airflow          ← Orchestrates & schedules the pipeline (@daily)
        ↓
  Kafka Producer          ← Streams formatted user data to topic: 'users_created'
        ↓
  Apache Kafka            ← Message broker (managed via Zookeeper)
        ↓
  Apache Spark            ← Consumes Kafka stream, applies schema & transformations
        ↓
  Apache Cassandra        ← Stores final structured user records

# Tech Stack
ToolPurposePythonCore scripting languageApache AirflowPipeline orchestration & schedulingApache KafkaReal-time message streamingApache ZookeeperKafka cluster coordinationApache SparkStream processing & transformationApache CassandraNoSQL distributed data storageDocker & Docker ComposeContainerized infrastructurePostgreSQLAirflow metadata backend

# Project Structure
DE_Streaming_Project/
├── DAG/
│   ├── Stream-Kafka.py       # Airflow DAG — fetches, formats & streams data to Kafka
│   └── Spark_Stream.py       # Spark job — consumes Kafka & writes to Cassandra
├── docker-compose.yml        # Spins up all infrastructure services
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md

# Getting Started
Prerequisites
Make sure you have the following installed:

# Docker Desktop
Python 3.11 (3.14 is NOT supported by PySpark)
PyCharm or any Python IDE

1. Clone the Repository
bashgit clone https://github.com/your-username/DE_Streaming_Project.git
cd DE_Streaming_Project
2. Install Python Dependencies
bashpip install -r requirements.txt
3. Start All Services with Docker
bashdocker-compose up -d
This spins up: Zookeeper, Kafka Broker, Schema Registry, Kafka Control Center, Airflow (webserver + scheduler), PostgreSQL, Spark (master + worker), and Cassandra.
Allow ~60 seconds for all containers to become healthy.
4. Verify Services Are Running
bashdocker ps
ServiceURLAirflow UIhttp://localhost:8080Kafka Control Centerhttp://localhost:9021Spark Master UIhttp://localhost:9090Cassandralocalhost:9042

# Airflow default credentials: username: admin / password: admin

5. Trigger the Pipeline

Open the Airflow UI at http://localhost:8080
Find the user_automation DAG
Toggle it On and click Trigger DAG

6. Run the Spark Consumer
In a separate terminal, submit the Spark streaming job:
bashdocker exec -it <spark-master-container-id> spark-submit \
  --packages com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1 \
  /path/to/Spark_Stream.py
7. Verify Data in Cassandra
bashdocker exec -it cassandra cqlsh

# Inside cqlsh:
USE spark_streams;
SELECT * FROM created_users LIMIT 10;

#How It Works

Airflow triggers the stream_data_api task on a daily schedule
get_data() calls the Random User API and retrieves a user record
format_data() flattens the nested JSON into a clean dictionary
A Kafka Producer streams the formatted record to the users_created topic
Spark Structured Streaming continuously reads from the Kafka topic
Spark applies a defined schema and writes each record to Cassandra
Data is stored in the spark_streams.created_users table


# Requirements
kafka-python
requests
cassandra-driver
pyspark
apache-airflow

# Common Issues
ProblemFixPySpark import errorMake sure you're using Python 3.11, not 3.13+Kafka connection refusedWait for broker container to be fully healthy (docker ps)Airflow DAG not showingCheck that ./DAG volume is correctly mounted in docker-composeCassandra timeoutAllow extra startup time (~60–90s) before running Spark job

# Future Improvements

Add data quality checks with Great Expectations
Introduce dbt for transformation layer
Deploy to cloud (AWS MSK + EMR + Keyspaces)
Add monitoring with Grafana + Prometheus
Stream multiple API endpoints concurrently


# License
This project is open source and available under the MIT License.

# Acknowledgements

Random User Generator API
Confluent Kafka Docker Images
Bitnami Spark Images
