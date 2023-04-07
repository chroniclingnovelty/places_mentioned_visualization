import streamlit as st
from datetime import datetime,date
from helper import *
import pandas as pd
import numpy as np
import plotly,time,glob,textwrap
import plotly.graph_objects as go
import plotly.express as px
from process_chronicles_lTag import *


# ../20221122/1791_Purm_Louw_04.xlsx
# ../20221122/1791_Purm_Louw_04.xml
# st.session_state.update(st.session_state)

# start_time = time.time()
# title
st.title("Chronicles visualization")

chronicle_select = st.selectbox(
    'select one chronicle: ',
    ['1796_Purm_Louw_04', '1795_Mege_Loef','1797_Brst_Mori','1796_Antw_Aars']) # defalut value shown in selecting box
# print(chronicle_select)   # ['1791_Purm_Louw_04']


#### load xml file and generate locatie_date_dict
print(chronicle_select)
f = f'../../l_tag_format_chronicles/Kronieken_XML_nieuw/{chronicle_select}.xml'
chronicle = ChronicleBucket(xml_path=f)
xml = chronicle.meta_xml
locatie_date_dict, summary_dict = chronicle.locatie_date_pack(nlines=5)
# o_dict[chronicle_select] = {"summary":summary_dict,"locatie_date":locatie_date_dict}
print(f"-----{chronicle_select} finished------")

#### summary table
# 'all_locatie_count', 'locatie_with_date_count', 'locatie_matched'
summary_table = pd.DataFrame(columns=['all_locatie_count',
                                      'locatie_with_date_count',
                                      'locatie_matched'])
summary_table.loc[chronicle_select,'all_locatie_count'] = summary_dict['all_locatie_count']
summary_table.loc[chronicle_select,'locatie_with_date_count'] = summary_dict['locatie_with_date_count']
summary_table.loc[chronicle_select,'locatie_matched'] = summary_dict['locatie_matched']

st.table(summary_table)


#### locatie_date_dict-->map
map_df = pd.DataFrame(columns=['la','lo','hover',
                               'matched_location','raw_location',
                               'belong_date'])
for fa,v in locatie_date_dict.items():
    try:
        map_df.loc[fa,'matched_location'] = v['locatie_match']['match_place']
        map_df.loc[fa,'la'] = v['locatie_match']['la']
        map_df.loc[fa,'lo'] = v['locatie_match']['lo']
        map_df.loc[fa,'raw_location'] = v['locatie_origin']
        map_df.loc[fa,'hover'] = v['locatie_lines']
        map_df.loc[fa,'belong_date'] = v['normal_date'].replace('xx','01')

    except:
        pass

map_df = map_df.dropna(axis=0)

# date range slider 
date_list = []
for i in map_df['belong_date'].tolist():
    date_list.append(string_to_date(i)) # date(*[int(j) for j in i.split('-')]))
map_df['belong_date'] = date_list
date_list = sorted(date_list)

d1,d2 = st.slider(
    "select date range: ",
    date_list[0], date_list[-1],value=(date_list[0],date_list[10]))


# empty spot reserved
plot_spot = st.empty()


# plotly map
df_select = map_df.loc[(map_df['belong_date']<=d2)&(map_df['belong_date']>=d1),:]
df_select['hover'] = ['<br>'.join(textwrap.wrap(t,100)) for t in df_select['hover'].tolist()]
df_select.loc[:,'size'] = 6
st.text(f"node counts in the map:{df_select.shape[0]}")
Fig = px.scatter_mapbox(df_select,
                        custom_data=['raw_location','matched_location','belong_date','hover'],
                        lat='la',lon='lo',
                        size_max=11,
                        size='size',
                        width=1000,height=600)
Fig.update_traces(hovertemplate = "<br>".join(
    [
    "Raw location: %{customdata[0]}<br>"
    "Matched location: %{customdata[1]}",
    "Date: %{customdata[2]}<br>",
    "Context:<br> %{customdata[3]}"
    ]
))
# d = go.Scattermapbox(lat = df_select['la'],
#                     lon = df_select['lo'],
#                     mode='markers',
#                     hovertemplate=
#                             'raw location: %{customdata[0]}<br>' + 
#                             'matched location: %{customdata[1]}<br>' + 
#                             'date: %{customdata[2]}<br><br>' +
#                             '%{text}',
#                     marker = dict(size=12), # go.scattermapbox.Marker
#                     text = df_select['hover'].tolist(),
#                     customdata=np.stack((df_select['raw_location'].tolist(),
#                                          df_select['matched_location'].tolist(),
#                                          df_select['belong_date'].tolist()),axis=-1),
#                     # name = str(i),
#                     hoverinfo='text')

# Fig = go.Figure(d)
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