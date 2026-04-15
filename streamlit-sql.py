# DSC 333
# Streamlit application that interfaces with cardb database
# running locally in MySQL

import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def connect_to_db():
    # SQL_PASS must be defined in .env.
    pw = os.environ.get('SQL_PASS')

    # Connect to DB
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password=pw,
      database="cardb"
    )

    # Return database connection and cursor object for executing queries
    return mydb, mydb.cursor()

def close_connection(db, cursor):
    cursor.close()
    db.close()


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


def exec_query(retail_range, min_mpg, car_type, cursor):
    # SQL query is broken down into multiple f strings for readibility.
    # f strings are concatenated automatically because of parenthesization.
    min_p, max_p = retail_range
    query = (f"SELECT Name, `Retail Price`, `Highway Miles Per Gallon`, Type"
             f" FROM cars WHERE `Retail Price` BETWEEN {min_p} AND {max_p}"
             f" AND `Highway Miles Per Gallon` > {min_mpg}"
             f" AND Type = '{car_type}';")
    print(query)
    # Execute the SQL query
    cursor.execute(query)

    # Put results in a DataFrame
    columns = [desc[0] for desc in cursor.description]
    results_df = pd.DataFrame(cursor.fetchall(), columns = columns)
    return results_df

def main():
    st.title('Car database')
    st.subheader('MySQL-based implementation')
    db, cursor = connect_to_db()
    retail_range, min_mpg, car_type = get_user_selections()
    results = exec_query(retail_range, min_mpg, car_type, cursor)
    st.markdown('---')
    st.subheader('Matches')
    st.dataframe(results, width = 900, height = 300)
    close_connection(db, cursor)

if __name__ == '__main__':
    main()
