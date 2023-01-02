import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
import json
import datetime as dt
import requests
from google.cloud import storage

def download_public_file(bucket_name, source_blob_name, destination_file_name):
    """Downloads a public blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client.create_anonymous_client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded public blob {} from bucket {} to {}.".format(
            source_blob_name, bucket.name, destination_file_name
        )
    )

st.title("DC Inbox Dashboard")
st.subheader("Official e-newsletters from every member of Congress. In one place. In real time.")
st.caption("Note due to the large amount of data (160K plus e-newsletters) this dashboard takes about 15 mintues to intialize. After the source file is cached, reloading is much faster.")
url="https://www.dcinbox.com/api/csv.php"

#assert len(data.data) > 0
@st.experimental_memo
def get_data():
    # loading the temp.zip and creating a zip object
    #with ZipFile("dcinbox_export.zip", 'r') as zObject:
     #   zObject.extractall()
    file = download_public_file("dcinbox","dc_inbox2.gz", "dc_inbox2.gz")
    df = pd.read_csv('dc_inbox2.gz', engine= 'c', parse_dates=['Date of Birth'])
   
    df['Unix Timestamp'] = df['Unix Timestamp'].apply(lambda x: int(x) /1000)
    df['Date'] = pd.to_datetime(df['Unix Timestamp'],unit='s', origin='unix')
    df = df.drop(['Unix Timestamp'], axis=1)
    df['Full Text'] = df['Subject'] + ' ' +  df['Body']
    df['Full Name'] = df['First Name'] + ' ' + df['Last Name'] + ' (' + df['BioGuide ID'] + ')'
   
    return df
df = get_data()
search = st.text_input(label= 'Search', placeholder = 'e.g. Healthcare')

### sidebar
with st.sidebar:
    party = st.multiselect('Party',list(df.Party.unique()), default = ['Republican','Democrat'])
    chamber = st.multiselect('Chamber', list(df.Chamber.unique()), default = ['House','Senate'])
    gender = st.multiselect('Gender', list(df.Gender.unique()), default = ['M','F'])
    state = st.multiselect('State', list(df.State.unique()))
    district = st.number_input('District', 0, 100)
    start_date = st.date_input('Start Date', value= dt.datetime(2010,1,1))
    end_date = st.date_input('End Date')
  
    name = st.multiselect('Name', list(df['Full Name'].unique()))

filtered_df = df[(df['Party'].isin(party)) & (df['Chamber'].isin(chamber)) & (df.Gender.isin(gender)) & (df['Full Text'].str.contains(search, case = False))]

#chart_df = filtered_df.groupby(pd.Grouper(key = 'Date', freq='W')).agg({'ID':pd.Series.nunique}).reset_index()
chart_df = filtered_df.groupby(pd.Grouper(key = 'Date', freq='M')).agg({'HateSpeechWordCount':pd.Series.sum}).reset_index()

st.subheader("Chart of Divisive Word Counts in Congressional Emails")
chart = alt.Chart(chart_df).mark_line().encode(
x='Date',
y= alt.Y('HateSpeechWordCount', title = "Count of Divisive Words Used"))
st.altair_chart(chart, use_container_width=True)
st.dataframe(filtered_df)
##footer
st.write("Data Sources: [DC Inbox By Professor Lindsey Cormack](https://www.dcinbox.com/)")
st.text('By Sam Kobrin')



