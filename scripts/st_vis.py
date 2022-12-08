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
# st.session_state.update(st.session_state)

# start_time = time.time()
chronicle_select = st.multiselect(
    'select chronicles: ',
    ['1791_Purm_Louw_04'],
    ['1791_Purm_Louw_04']) # defalut value shown in selecting box
# print(chronicle_select)   # ['1791_Purm_Louw_04']


# read df for plotly
# ../data/test_df.pkl
df = pack(file_name='data/test_df.pkl',mode='rb')
# la	lo	hover	date_belong location  raw_location

# title
st.title("Plotly map test")

# date range slider 
date_list = []
for i in df['date_belong'].tolist():
    date_list.append(string_to_date(i)) # date(*[int(j) for j in i.split('-')]))
df['date_belong'] = date_list
date_list = sorted(date_list)

d1,d2 = st.slider(
    "select date range or point:",
    date_list[0], date_list[-1],value=(date_list[0],date_list[10]))


# empty spot reserved
plot_spot = st.empty()


# plotly map
df_select = df.loc[(df['date_belong']<=d2)&(df['date_belong']>=d1),:]
df_select.loc[:,'size'] = 6
Fig = px.scatter_mapbox(df_select,
                        lat='la',lon='lo',
                        hover_name='hover',
                        size_max=11,
                        size='size',
                        width=1000,height=600)

Fig.update_layout(mapbox=dict(style='open-street-map',
                  center=dict(lat=52.3,lon=4.9),
                  zoom=5),
                  margin={"r":0,"t":0,"l":0,"b":0},
                      # legend=dict(y=0.2,x=1)
                                )

# fill the spot
with plot_spot:
    st.plotly_chart(Fig)

if __name__ == "__main__":
    pass
    # st.write('You selected:', chronicle_select)
    # st.write("date range: ", date_range)
    # print('*********************************************************')