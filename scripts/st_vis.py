import streamlit as st
from datetime import datetime,date
from helper import *
import pandas as pd
import numpy as np
import plotly,time,glob,textwrap
import plotly.graph_objects as go
import plotly.express as px
from process_chronicles_lTag import *
from helper import *
import pickle

# st.session_state.update(st.session_state)


st.title("Chronicles visualization")

###### set up chronicles and load data
chronicle_list = ['1795_Mege_Loef', '1797_Brst_Mori', '1796_Antw_Aars', '1802_Venl_Post', 
                  '1796_Leeu_Buma', '1793_Bred_Ouko', '1802_Brus_Anon', 
                  '1787_Gent_Anon_01', '1790_Mech_Wijn', '1796_Purm_Louw_04', '1808_Gent_Quic', 
                  '1797_Alkm_Anon', '1796_Purm_Louw_05', '1795_Zalt_Kist', 
                  '1792_Brie_Klui_10', '1792_Brie_Klui_11','1795_Maas_Anon'] # '1795_Maas_Anon'

chronicle_colors = dict(zip(chronicle_list, px.colors.qualitative.Dark24[0:len(chronicle_list)]))

# /app/chronicle_vis_project/
with open("/app/chronicle_vis_project/data/Chronicle-Center.pickle", "rb") as f:
    chronicle_center = pickle.load(f)

with open("/app/chronicle_vis_project/data/ChronicleDict.pickle",'rb') as f:
    o_dict = pickle.load(f)

###### sidebar 
with st.sidebar:
    # show edges
    show_edges = st.checkbox('show edges')
    # multiple select
    chronicle_selects = st.multiselect(
        'select chronicles: ',
        chronicle_list,
        ['1795_Mege_Loef','1797_Brst_Mori','1787_Gent_Anon_01'],
        )
    # chronicle_selects: list
# st.write("Selected options:", selected_options)


Figs = px.scatter_mapbox(lat=[],lon=[])
fig_traces = []
summary_tables = []
map_dfs = []
centers_dict = dict()
for chronicle_select in chronicle_selects:
    #### load xml file and generate locatie_date_dict
    # print(chronicle_select)
    # f = f'../../l_tag_format_chronicles/Kronieken_XML_nieuw/{chronicle_select}.xml'
    # chronicle = ChronicleBucket(xml_path=f)
    # xml = chronicle.meta_xml
    # locatie_date_dict, summary_dict = chronicle.locatie_date_pack(nlines=5)
    summary_dict = o_dict[chronicle_select]['summary']
    locatie_date_dict = o_dict[chronicle_select]['locatie_date']
    print(f"-----{chronicle_select} finished------")

    #### summary table
    # 'all_locatie_count', 'locatie_with_date_count', 'locatie_matched'
    summary_table = pd.DataFrame(columns=['all_locatie_count',
                                        'locatie_with_date_count',
                                        'locatie_matched'])
    summary_table.loc[chronicle_select,'all_locatie_count'] = summary_dict['all_locatie_count']
    summary_table.loc[chronicle_select,'locatie_with_date_count'] = summary_dict['locatie_with_date_count']
    summary_table.loc[chronicle_select,'locatie_matched'] = summary_dict['locatie_matched']
    summary_tables.append(summary_table)
    

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
    map_df['chronicle'] = chronicle_select
    # map_df['chro_color'] = chronicle_colors[chronicle_select]
    map_dfs.append(map_df)
    # print(map_df.head())

    center_place,center_la,center_lo = chronicle_center[chronicle_select]['match_place'], chronicle_center[chronicle_select]['la'], chronicle_center[chronicle_select]['lo']
    centers_dict[chronicle_select] = {'center_place':center_place,'la':center_la,'lo':center_lo}
    # {'match_place':'brustem','la':50.8057, 'lo':5.2219}
    
st.table(pd.concat(summary_tables,axis=0))
map_dfs = pd.concat(map_dfs,axis=0)


# date range slider 
date_list = []
for i in map_dfs['belong_date'].tolist():
    date_list.append(string_to_date(i)) # date(*[int(j) for j in i.split('-')]))
map_dfs['belong_date'] = date_list
date_list = sorted(date_list)

d1,d2 = st.slider(
    "select date range: ",
    date_list[0], date_list[-1],value=(date_list[0],date_list[10]))


print(map_dfs.head())
# if matched location is the same, jitter around the la/lo
map_dfs['la_jitter'] = map_dfs['la'].apply(lambda x: x + np.random.normal(0, 0.05))
map_dfs['lo_jitter'] = map_dfs['lo'].apply(lambda x: x + np.random.normal(0, 0.05))


for chronicle_select in chronicle_selects:
    # plotly map
    map_df = map_dfs.loc[map_dfs['chronicle']==chronicle_select,:]
    df_select = map_df.loc[(map_df['belong_date']<=d2)&(map_df['belong_date']>=d1),:]
    df_select['hover'] = ['<br>'.join(textwrap.wrap(t,100)) for t in df_select['hover'].tolist()]
    df_select['size'] = 4
    # st.text(f"{chronicle_select} node counts in the map:{df_select.shape[0]}").style(f'background-color: {chronicle_colors[chronicle_select]};')
    # CSS style color
    t = f"{chronicle_select} node counts in the map:{df_select.shape[0]}"
    select_text = f'<p style="font-family:sans-serif; color:{chronicle_colors[chronicle_select]}; font-size: 20px;">{t}</p>'
    st.markdown(select_text, unsafe_allow_html=True)
    
    # centers_dict[chronicle_select] = {'center_place':center_place,'la':center_la,'lo'
    center_la = centers_dict[chronicle_select]['la']
    center_lo = centers_dict[chronicle_select]['lo']
    Fig = px.scatter_mapbox(df_select,
                            custom_data=['raw_location','matched_location','belong_date','hover'],
                            lat='la_jitter',lon='lo_jitter',
                            size_max=11,
                            size = 'size',
                            color_discrete_sequence=[chronicle_colors[chronicle_select]],
                            center=dict(lat=center_la,lon=center_lo)
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
                                    'name':[centers_dict[chronicle_select]['center_place']]}),
                      lat='la', lon='lo', 
                      color='color',
                      size='size',
                      color_discrete_sequence=[chronicle_colors[chronicle_select]],
                      hover_name="name").data[0]
                  )

    # add edges
    edges = []
    for i in df_select.index.tolist():
        p = df_select.loc[i,'matched_location']
        if p.lower() != center_place:
            edges.append(
                px.line_mapbox(
                    pd.DataFrame({'la':[df_select.loc[i,'la_jitter'],center_la],
                                  'lo':[df_select.loc[i,'lo_jitter'],center_lo],
                                  'chronicles':[i,i]}),
                    lat='la',
                    lon='lo',# line=dict(color='blue',width=5),
                    color_discrete_sequence=[chronicle_colors[chronicle_select]],
                    mapbox_style='open-street-map'
                ).data[0]
            )
        # print(pd.DataFrame({'la':[df_select.loc[i,'la'],center_la],'lo':[df_select.loc[i,'lo'],center_lo]}))
    
    if show_edges:
        fig_traces.extend(edges)
    fig_traces.extend(Fig.data)



Figs = go.Figure(data=fig_traces)
Figs.update_layout(mapbox=dict(style='open-street-map',
                  center=dict(lat=52.3,lon=4.9),
                  zoom=5),
                  margin={"r":0,"t":0,"l":0,"b":0},
                  width=1200,height=800,
                  showlegend=False
                  # legend=dict(y=0.2,x=1)
                   )

st.plotly_chart(Figs, use_container_width=True, height=800,
                ) 





# empty spot reserved
# plot_spot = st.empty()


# plotly map
# df_select = map_df.loc[(map_df['belong_date']<=d2)&(map_df['belong_date']>=d1),:]
# df_select['hover'] = ['<br>'.join(textwrap.wrap(t,100)) for t in df_select['hover'].tolist()]
# df_select.loc[:,'size'] = 6
# st.text(f"node counts in the map:{df_select.shape[0]}")
# Fig = px.scatter_mapbox(df_select,
#                         custom_data=['raw_location','matched_location','belong_date','hover'],
#                         lat='la',lon='lo',
#                         size_max=11,
#                         size='size',
#                         center=dict(lat=center_la,lon=center_lo),
#                         width=1000,height=600)

# Fig.update_traces(hovertemplate = "<br>".join(
#     [
#     "Original location: %{customdata[0]}<br>"
#     "Matched location: %{customdata[1]}",
#     "Date: %{customdata[2]}<br>",
#     "Context:<br> %{customdata[3]}"
#     ]
# ))

# # line_trace = px.line_geo(lat=[51.8,[71,81]],
# #                           lon=[5.3,[11,10]],
# #                           color_discrete_sequence=["blue"]
# #                           )
# # Fig.add_trace(line_trace.data[0])
# for i in df_select.index.tolist():
#     p = df_select.loc[i,'matched_location']
#     if p.lower() != center_place:
#         Fig.add_trace(
#             px.line_mapbox(
#                 pd.DataFrame({'la':[df_select.loc[i,'la'],center_la],'lo':[df_select.loc[i,'lo'],center_lo]}),
#                 lat='la',
#                 lon='lo',# line=dict(color='blue',width=5),
#                 mapbox_style='open-street-map'
#             ).data[0]
#         )




# # fill the spot
# # with plot_spot:




if __name__ == "__main__":
    pass
    # st.write('You selected:', chronicle_select)
    # st.write("date range: ", date_range)
    # print('*********************************************************')