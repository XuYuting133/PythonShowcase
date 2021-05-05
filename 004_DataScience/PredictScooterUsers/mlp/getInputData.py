#-------------------------------------------------------------------------------
# Name:        getInputData.py
# Purpose:     Import input dataset and return a pandas dataframe/Answers to Part 1 of the assessment.
#
# Author:      Xu Yuting
#
# Created:     22/04/2020
# Copyright:   (c) ytxu 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pyodbc
import pandas as pd

def run():
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server=aice.database.windows.net;'
                          'Database=aice;'
                          'UID=aice_candidate;'
                          'PWD=@ic3_a3s0c1at3;')
    sql_query = "\
    select date, hr, weather, temperature, feels_like_temperature, relative_humidity, windspeed, psi, guest_scooter \
    from rental_data \
    where date between '2011-01-01' and '2012-12-31'\
    "

    df = pd.io.sql.read_sql(sql_query,conn)

    return df

