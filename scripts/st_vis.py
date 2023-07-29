import streamlit as st
# from streamlit_plotly_events import plotly_events
from datetime import datetime,date
from helper import *
import pandas as pd
import numpy as np
import plotly,time,glob,textwrap
import plotly.graph_objects as go
import plotly.express as px
# from process_chronicles_lTag import *
from helper import *
import pickle
from pathlib import Path

data_dir = Path.cwd().parent
print(data_dir)

st.set_page_config(layout="wide") 
st.title("Horizons of interest: Places mentioned in chronicles 1770-1815")

# /app/chronicle_vis_project/data/corrected_mapping_filter.csv
# maps_df = pd.read_csv("/app/chronicle_vis_project/data/corrected_mapping_filter_rm_chronicle_loc.csv",index_col=0)
maps_df_dir = data_dir / 'corrected_mapping_filter_rm_chronicle_loc.csv'
maps_df = pd.read_csv(maps_df_dir,index_col=0)
maps_df = maps_df.loc[maps_df['address'].notnull(),:]
with open("/app/chronicle_vis_project/data/Chronicle-Center-new.pickle", "rb") as f:
    chronicle_center = pickle.load(f)

# ../data/summary_table.csv
summary_table = pd.read_csv('/app/chronicle_vis_project/data/summary_table_rm_chronicle_loc.csv',index_col=0)


chronicle_list = maps_df['chronicle'].unique()
chronicle_colors = dict(zip(chronicle_list, px.colors.qualitative.Dark24[0:len(chronicle_list)]))


##### sidebar 
with st.sidebar:
    # show edges
    show_edges = st.checkbox('show edges')
    # multiple select
    chronicle_selects = st.multiselect(
        'select chronicles: ',
        chronicle_list,
        ['1795_Mege_Loef','1796_Purm_Louw_04'],
        )
    
st.table(summary_table.loc[chronicle_selects,:])

Figs = px.scatter_mapbox(lat=[],lon=[])
fig_traces = []

maps_df_se = maps_df.loc[maps_df['chronicle'].isin(chronicle_selects),:]



# date range slider 
date_list = []
for i in maps_df_se['belong_date'].tolist():
    date_list.append(string_to_date(i)) # date(*[int(j) for j in i.split('-')]))
maps_df_se['belong_date'] = date_list
date_list = sorted(date_list)

d1,d2 = st.slider(
    "select date range: ",
    date_list[0], date_list[-1],value=(date_list[0],date_list[10]))

maps_df_se = maps_df_se.loc[(maps_df_se['belong_date']<=d2)&(maps_df_se['belong_date']>=d1),:]
maps_df_se = circle_coordinate(maps_df_se,offset_radius=0.01)
print(maps_df_se)

# centers_dict = dict()
for chronicle_select in chronicle_selects:
    # plotly map
    df_select = maps_df_se.loc[maps_df_se['chronicle']==chronicle_select,:]
    # df_select = map_df.loc[(map_df['belong_date']<=d2)&(map_df['belong_date']>=d1),:]
    df_select['hover'] = ['<br>'.join(textwrap.wrap(t,100)) for t in df_select['hover'].tolist()]
    df_select['size'] = 4
    t = f"{chronicle_select} node counts in the map:{df_select.shape[0]}"
    select_text = f'<p style="font-family:sans-serif; color:{chronicle_colors[chronicle_select]}; font-size: 20px;">{t}</p>'
    st.markdown(select_text, unsafe_allow_html=True)
    
    # '1787_Gent_Anon_01': {'match_place': 'Ghent', 'la': 51.05, 'lo': 3.71667},
    center_la = float(chronicle_center[chronicle_select]['la'])
    center_lo = float(chronicle_center[chronicle_select]['lo'])
    center_place = chronicle_center[chronicle_select]['match_place']



    Fig = px.scatter_mapbox(df_select,
                            custom_data=['raw_location','true_place','belong_date','hover'],
                            lat='lat',lon='lng',
                            size_max=11,
                            size = 'size',
                            color_discrete_sequence=[chronicle_colors[chronicle_select]],
                            )


    Fig.update_traces(hovertemplate = "<br>".join(
        [
        "Original location: %{customdata[0]}<br>"
        "Matched location: %{customdata[1]}",
        "Date: %{customdata[2]}<br>",
        "Context:<br> %{customdata[3]}"
        ]
    ))

    # add the center node
    Fig.add_trace(
                   px.scatter_mapbox(
                      pd.DataFrame({'la':[center_la],'lo':[center_lo],
                                    'size':6,'color':'co',
                                    'name':center_place}),# [centers_dict[chronicle_select]['center_place']]}),
                      lat='la', lon='lo', 
                      color='color',
                      size='size',
                      color_discrete_sequence=[chronicle_colors[chronicle_select]],
                      hover_name="name").data[0]
                  )

    # add edges
    edges = []
    for i in df_select.index.tolist():
        p = df_select.loc[i,'true_place']
        if p.lower() != center_place:
            edges.append(
                px.line_mapbox(
                    pd.DataFrame({'la':[df_select.loc[i,'lat'],center_la],
                                  'lo':[df_select.loc[i,'lng'],center_lo],
                                  'chronicles':[i,i]}),
                    lat='la',
                    lon='lo',
                    color_discrete_sequence=[chronicle_colors[chronicle_select]],
                    mapbox_style='open-street-map'
                ).data[0]
            )
        # print(pd.DataFrame({'la':[df_select.loc[i,'la'],center_la],'lo':[df_select.loc[i,'lo'],center_lo]}))
    
    if show_edges:
        fig_traces.extend(edges)
    fig_traces.extend(Fig.data)


# empty spot reserved
plot_spot = st.empty()
Figs = go.Figure(data=fig_traces)
Figs.update_layout(mapbox=dict(style='open-street-map',
                  center=dict(lat=52.3,lon=4.9),
                  zoom=5),
                  margin={"r":0,"t":0,"l":0,"b":0},
                  width=1200,height=800,
                  showlegend=False
                  # legend=dict(y=0.2,x=1)
                   )
with plot_spot:
    st.plotly_chart(Figs, use_container_width=True, height=800,
                    ) 

if __name__ == "__main__":
    pass