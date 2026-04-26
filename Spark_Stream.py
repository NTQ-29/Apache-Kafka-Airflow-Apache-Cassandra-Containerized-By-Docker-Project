import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)
    print("Keyspace created successfully!")

def create_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS spark_streams.created_users (
            id UUID PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            address TEXT,
            postcode TEXT,
            email TEXT,
            username TEXT,
            dob TEXT,
            registered_date TEXT,
            phone TEXT,
            picture TEXT
        );
    """)
    print("Table created successfully!")

def create_spark_connection():
    try:
        s_conn = (SparkSession.builder
                  .appName('SparkDataStreaming')
                  .config('spark.jars.packages',
                          "com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,"
                          "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1")
                  .config('spark.cassandra.connection.host', 'localhost')
                  .getOrCreate())
        s_conn.sparkContext.setLogLevel("ERROR")
        return s_conn
    except Exception as e:
        logging.error(f"Spark connection error: {e}")
        return None

def connect_to_kafka(spark_conn):
    try:
        df = (spark_conn.readStream
              .format('kafka')
              .option('kafka.bootstrap.servers', 'localhost:9092')
              .option('subscribe', 'users_created')
              .option('startingOffsets', 'earliest')
              .load())
        return df
    except Exception as e:
        logging.warning(f"Kafka connection error: {e}")
        return None

def create_cassandra_connection():
    from cassandra.cluster import Cluster
    try:
        cluster = Cluster(['localhost'])
        return cluster.connect()
    except Exception as e:
        logging.error(f"Cassandra connection error: {e}")
        return None

def create_selection_df(df):
    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("postcode", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("dob", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False),
    ])
    return (df.selectExpr("CAST(value AS STRING)")
              .select(from_json(col('value'), schema).alias('data'))
              .select("data.*"))

if __name__ == "__main__":
    spark_conn = create_spark_connection()

    if spark_conn:
        df = connect_to_kafka(spark_conn)
        selection_df = create_selection_df(df)
        session = create_cassandra_connection()

        if session:
            create_keyspace(session)
            create_table(session)

            stream_query = (selection_df.writeStream
                            .format("org.apache.spark.sql.cassandra")
                            .option('checkpointLocation', '/tmp/checkpoint')
                            .options(table="created_users", keyspace="spark_streams")
                            .start())

            stream_query.awaitTermination()