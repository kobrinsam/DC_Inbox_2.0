import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
import requests, zipfile, io
from streamlit_lottie import st_lottie  # pip install streamlit-lottie
import json
import datetime as dt


st.title("DC Inbox Dashboard")
st.subheader("Official e-newsletters from every member of Congress. In one place. In real time.")
st.caption("Note due to the large amount of data (160K plus e-newsletters) this dashboard takes about 15 mintues to intialize. After the source file is cached, reloading is much faster.")
url="https://www.dcinbox.com/api/csv.php"

#takes fifteen minutes to download
url= "https://www.dcinbox.com/api/csv.php"
#sample date for development
sample_url = "https://d9fe47c0-6fe3-4799-8aa2-c0b9fc576746.filesusr.com/ugd/f1b05b_dc819d864b47466293d7ebbd60853c9f.csv?dn=09_2021.csv"

#import data
@st.experimental_memo
def get_data():
    df = pd.read_csv("/Users/samkobrin/Downloads/dc_inbox_test_data.csv", parse_dates=['Date of Birth'], converters={'District': convert}, dtype={'District': "int8"})
    df['Date'] = df['Unix Timestamp'].apply(lambda x: dt.datetime.fromtimestamp(x/1000))
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

chart_df = filtered_df.groupby(pd.Grouper(key = 'Date', freq='W')).agg({'ID':pd.Series.nunique}).reset_index()

st.dataframe(filtered_df)
st.dataframe(chart_df)
st.subheader("Chart")
chart = alt.Chart(chart_df).mark_line().encode(
x='Date',
y= alt.Y('ID', title = "Emails Sent"))

st.altair_chart(chart, use_container_width=True)

##footer
st.write("Data Sources: [DC Inbox By Professor Lindsey Cormack](https://www.dcinbox.com/)")
st.text('By Sam Kobrin')



#strokeDash='Party',
#tooltip=['Commodity', 'Amount', 'SC_Unit_Desc', 'Date']).interactive()
    ###lottefile
    # GitHub: https://github.com/andfanilo/streamlit-lottie
    # Lottie Files: https://lottiefiles.com/

def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)


def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    

#lottie_coding = load_lottiefile("lottiefile.json")  # replace link to local lottie file
lottie_wheat = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_t2xm9bsw.json")
st_lottie(
        lottie_wheat,
        speed=1,
        reverse=False,
        loop=True,
        quality="low", # medium ; high
         # canvas
        height=None,
        width=None,
        key=None,
    )

