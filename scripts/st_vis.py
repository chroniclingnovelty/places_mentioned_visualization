import streamlit as st
from datetime import datetime,date
from helper import *
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
import time


# ../20221122/1791_Purm_Louw_04.xlsx
# ../20221122/1791_Purm_Louw_04.xml
st.session_state.update(st.session_state)

# start_time = time.time()
chronicle_select = st.multiselect(
    'select chronicles: ',
    ['1791_Purm_Louw_04'],
    ['1791_Purm_Louw_04']) # defalut value shown in selecting box
# print(chronicle_select)   # ['1791_Purm_Louw_04']


# read df for plotly
# ../data/test_df.pkl
df = pack(file_name='../data/test_df.pkl',mode='rb')
# la	lo	hover	date_belong location  raw_location


# date range slider 
date_list = []
for i in df['date_belong'].tolist():
    date_list.append(string_to_date(i))# date(*[int(j) for j in i.split('-')]))
df['date_belong'] = date_list
date_list = sorted(date_list)

date_range = st.slider(
    "select date range or point:",
    value=(date_list[0], date_list[-1]))



select_date = []
for i in date_list:
    if (i <= date_range[1]) & (i >= date_range[0]):
        select_date.append(i)



df_select = df.loc[df['date_belong'].isin(select_date)]
d = go.Scattermapbox(lat = df_select['la'],
                        lon = df_select['lo'],
                        mode='markers',
                        marker = dict(size=12), # go.scattermapbox.Marker
                        text = df_select['hover'].tolist(),
                        # name = str(i),
                        hoverinfo='text')

   
Fig = go.Figure(d)
Fig.update_layout(mapbox=dict(style='open-street-map',
                              center=dict(lat=52.3,lon=4.9),
                              zoom=5
                              )
                              )
Fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
Fig.update_layout(legend=dict(y=0.2,x=1))
# Fig.write_html('test.html')
st.plotly_chart(Fig)


if __name__ == "__main__":
    # pass
    # st.write('You selected:', chronicle_select)
    st.write("date range: ", date_range)
    print('*********************************************************')