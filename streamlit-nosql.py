# DSC 333
# MongoDB-based implementation of the cars Streamlit application
# Note: Cars collection is created in MongoDB if it doesn't already exist

import pymongo
import os
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import urllib.parse
import streamlit as st

load_dotenv()

MONGO_USER=os.environ.get('MONGO_USER')
MONGO_PASS=os.environ.get('MONGO_PASS')

MONGO_USER = urllib.parse.quote_plus(MONGO_USER)
MONGO_PASS = urllib.parse.quote_plus(MONGO_PASS)

DB_NAME = 'test'

def connect():
    # Replace with your connection string starting with the @
    uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}"+\
        f"YOUR CONNECTION STRING"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    database = client[DB_NAME]

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
    except Exception as e:
        print(e)
    
    return database


def get_collection(db):
    db = connect()

    # Create cars collection from csv file if it doesn't exist
    if 'cars' not in db.list_collection_names():
        df = pd.read_csv('https://raw.githubusercontent.com/iantonios/dsc205/refs/heads/main/cars.csv')
        car_list = df.to_dict(orient='records')
        collection = db['cars']
        result = collection.insert_many(car_list)
    else:
        collection = db['cars']
    return collection
    

def get_user_selections():
    with st.form(key='my_form'):
        retail_range = st.slider('Retail price ($)',
                        0, 100000, (20000, 50000))
        min_mpg = st.slider('Minimum fuel efficiency (highway - mpg)',
                        0, 55, 20)
        car_type = st.radio(
            'Car type',
            ('Sedan', 'Wagon', 'SUV', 'Sports Car')
        )
        submitted = st.form_submit_button(label='Process')

        if submitted:
            return retail_range, min_mpg, car_type
        else:
            return ((20000, 50000), 20, 'Sedan')

def exec_query(collection, retail_range, min_mpg, car_type):
    min_price = int(retail_range[0])
    max_price = int(retail_range[1])

    query = {
        "Type": car_type,
        "Retail Price": {"$gte": min_price, "$lte": max_price},
        "Highway Miles Per Gallon": {"$gte": min_mpg}
    }
    print(query)

    results = collection.find(query)
    return results

# Application Driver
def main():
    st.title('Car database')
    st.subheader('MongoDB-based implementation')
    db = connect()
    collection = get_collection(db)
    retail_range, min_mpg, car_type = get_user_selections()
    results = exec_query(collection, retail_range, min_mpg, car_type)
    st.markdown('---')

    # Convert results (list of tuples) to DataFrame
    results_df = pd.DataFrame(list(results))
    
    if not results_df.empty:
        st.subheader('Matches')
        results_df = results_df.drop(columns=['_id'])
        st.dataframe(results_df, width = 900, height = 300)
    else:
        st.write('No matches -- Try relaxing search criteria.')

if __name__ == '__main__':
    main()
