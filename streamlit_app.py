from supabase import create_client, Client
import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
import json
import datetime as dt
import requests
url = "https://pmmghxxijwmbhfautdiz.supabase.co"
key = st.secrets(['key'])

#sql query
supabase: Client = create_client(url, key)
data = supabase.table("dcinbox3").select("*").execute()

# Get the JSON data from the APIResponse object
json_data = data.json()
data = json.loads(json_data)
data = data['data']
data = pd.DataFrame(data)

st.title("DC Inbox Dashboard")
st.subheader("Official e-newsletters from every member of Congress. In one place. In real time.")
st.caption("Note due to the large amount of data (160K plus e-newsletters) this dashboard takes about 15 mintues to intialize. After the source file is cached, reloading is much faster.")
url="https://www.dcinbox.com/api/csv.php"

#takes fifteen minutes to download
url= "https://www.dcinbox.com/api/csv.php"
#sample date for development

# data on computer "/Users/samkobrin/Downloads/dc_inbox_test_data.csv"
# data in github
#import data
#data from supabase

#assert len(data.data) > 0
@st.experimental_memo
def get_data():

    #df = pd.read_csv('dc_inbox_test_data.csv', parse_dates=['Date of Birth'])
    df = data
    df['Unix Timestamp'] = df['Unix Timestamp'].apply(lambda x: int(x))
    df['Date'] = pd.to_datetime(df['Unix Timestamp'],unit='s', origin='unix')
    df = df.drop(['Unix Timestamp'], axis=1)
    df['Full Text'] = df['Subject'] + ' ' +  df['Body']
    df['Full Name'] = df['First Name'] + ' ' + df['Last Name'] + ' (' + df['BioGuide ID'] + ')'
   
    return df
df = get_data()
st.dataframe(df)
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
chart_df = filtered_df.groupby(pd.Grouper(key = 'Date', freq='H')).agg({'HateSpeechWordCount':pd.Series.sum}).reset_index()
st.dataframe(filtered_df)
st.dataframe(chart_df)
st.subheader("Chart")
chart = alt.Chart(chart_df).mark_line().encode(
x='Date',
y= alt.Y('HateSpeechWordCount', title = "Count of Divisive Words Used"))

st.altair_chart(chart, use_container_width=True)

##footer
st.write("Data Sources: [DC Inbox By Professor Lindsey Cormack](https://www.dcinbox.com/)")
st.text('By Sam Kobrin')



