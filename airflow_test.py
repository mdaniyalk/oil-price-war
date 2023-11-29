from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

# Define default_args and DAG
default_args = {
    'owner': 'admin',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_dag',
    default_args=default_args,
    description='My example DAG',
    schedule_interval=timedelta(days=1),  # Set the schedule interval for your DAG
)

# Define tasks
start_task = DummyOperator(task_id='start', dag=dag)

def my_python_function(**kwargs):
    # Your Python function logic goes here
    print("Executing my Python function")

python_task = PythonOperator(
    task_id='python_task',
    python_callable=my_python_function,
    provide_context=True,
    dag=dag,
)

end_task = DummyOperator(task_id='end', dag=dag)

# Define task dependencies
start_task >> python_task >> end_task
