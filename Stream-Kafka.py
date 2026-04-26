from datetime import datetime
#These are packages from Airflow
from airflow import DAG
#This imports nodes & edges w/ dependencies from Apache Airflow
from airflow.operators.python import PythonOperator


#imports Python Operators called Operands for manipulating data | calculations too
default_args ={
    "owner": "airscholar",
    "start_date": datetime(2026, 4, 26, 9, 19)
}
#default_args = stores default argument values for functions, variables, etc.
def get_data():
    import requests  # get Data from API

    resp = requests.get("https://randomuser.me/api/")  # url from random user generator site
    resp = (resp.json())  # resp = response short-hand
    resp = resp['results'][0]

    return resp #sends values back to called

def format_data(resp):
    location = resp['location']

    data['first_name'] = resp['name']['first']
    data['last_name'] = resp['name']['last']
    data['gender'] = resp['gender']
    data['address'] = (f"{str(location['street']['number'])} {location['street']['name']}, "
                       f"{location['city']}, {location['state']}, {location['country']}")
    data['postcode'] = location['postcode']
    data['email'] = resp['email']
    data['username'] = resp['login']['username']
    data['dob'] = resp['dob']['date']
    data['registered_date'] = resp['registered']['date']
    data['phone'] = resp['phone']
    data['picture'] = resp['picture']['medium']

    return data


def stream_data():
    import json #semi-structured Data
    from kafka import KafkaProducer
    import time

    resp = get_data()
    resp = format_data()
    #print(json.dumps(resp, indent=3)

    producer = KafkaProducer(bootstrap_servers=['localhost:29092'], max_block_ms=5000)
    #Kafka runs on port 9092, 9082
    curr_time = time.time()

    while True:
        if time.time() > curr_time + 60:  # streams for 1 minute
            break
        try:
            resp = get_data()
            resp = format_data(resp)
            producer.send('users_created', json.dumps(resp).encode('utf-8'))
        except Exception as e:
            logging.error(f'Error: {e}')
            continue

with DAG('user_automation',
         default_args=default_args,
         schedule="@daily",
         catchup=False) as dag:
#with DAG (context manager) = object that cleans up after you're done
#schedule = shows Airflow how often to run it | can use cron expressions
#catchup=False -> tells Airflow not to run anything from the past & start new
#dag = alias for reference
#@daily = Airflow task
    task_streaming = PythonOperator(
        task_id = "stream_data_api",
        python_callable=stream_data
    )
