from bs4 import BeautifulSoup
import math,pickle,textwrap,random,os,plotly
import pandas as pd
import re
from datetime import date,datetime
import plotly.graph_objects as go
import plotly.express as px
from pprint import pprint
import numpy as np
from helper import *


class ChronicleBucket:
    # /app/chronicle_vis_project/scripts/
    # ../data/location_mapping.pkl
    with open('/app/chronicle_vis_project/data/location_mapping.pkl', 'rb') as f:
        mapping_location = pickle.load(f)

    def __init__(self,xml_path=None):
        # l-tagged xml have already have normalized date info, 
        # do not need a excel file
        self.summary = None

        self.xml_path = xml_path
        if xml_path:
            with open(self.xml_path,'r') as f:
                file = f.read()
            self.meta_xml = BeautifulSoup(file,'xml')
    
    def l_order(self):
        # return a dictionary:
        # in a context order
        # key          value
        # #facs_3_r1l1 0
        # facs_3_r1l2 1
        # facs_3_r1l3 2
        # facs_3_r1l4 3
        # facs_3_r1l5 4
        d = dict()
        for ind,l in enumerate(self.meta_xml.find_all('l')):
            d[l['facs']] = ind
        return d
    
    def filter_date_range(self,start=1770, end=1815):
        # all_date_tag = []
        all_range_date = []
        xml = self.meta_xml
        for l in xml.find_all('l'):
            for ele in l:
                try:   #### 1770 to 1815
                    if ele.name == 'datum':
                        norm_date = ele['datum']
                        if re.match("\d{4}-\d{2}-\w{2}", norm_date):
                            # all_date_tag.append(norm_date)
                            y,m,d = norm_date.split('-')
                            if start <= int(y) <= end:
                                all_range_date.append(norm_date)
                                ele['in_range'] = 'yes'     # add new attribute           
                except:
                    pass
        return list(set(all_range_date))

    def locatie_date_pack(self, nlines = 5):
        # return locatie_date_dict, summary_dict

        # find locatie's previous date (in a monthly resolution)
        # return a dictionary:
        # #facs_18_r2l7:
        # {{'locatie_origin': 'Nederland',
        #   'locatie_match': {'match_place': 'Nederland',
        #                     'la': 52.2858356,
        #                     'lo': 5.6549386},
        #   'locatie_date_l': '#facs_17_r3l5',
        #   'normal_date': '1786-07-12',
        #   'locatie_date_distance': 62,
        #   'locatie_lines': "Het Waepentuijg ontrukt\nEn ....}}

        # return summary
        # counts and locatie-date distance list

        locate_date_distance = []
        all_locatie_count = 0
        locatie_with_date_count = 0
        locatie_matched = 0

        locatie_date_dict = {}

        xml = self.meta_xml
        # lorder = self.l_order()
        # all_range_date = self.filter_date_range()
        for l in xml.find_all('l'):
            for ele in l:
                if ele.name == 'locatie':
                    all_locatie_count += 1
                    try:
                        locatie_date = ele.findPrevious(name='datum',
                                                        datum=re.compile("^(177\d|178\d|179\d|180\d|181\d)-\d{2}-\w{2}$"))
                                                        # in_range=all_range_date)
                                                        # all_range_date)
                                                        # re.compile("\d{4}-\d{2}-\w{2}"))

                        if locatie_date:
                            normaled_date = locatie_date['datum']
                            locatie_with_date_count += 1
                            locatie_date_l = locatie_date.findPrevious(name='l')['facs']
                            # d = lorder[l['facs']]-lorder[locatie_date_l]
                            ma = self.mapping_location.get(ele.text.strip().lower())
                            if ma:
                                locatie_matched += 1
                            locatie_date_dict[l['facs']] = {"locatie_origin": ele.text.strip(),
                                                            "locatie_match": ma,
                                                            "locatie_date_l": locatie_date_l,
                                                            "normal_date": normaled_date,
                                                            # "locatie_date_distance":d,
                                                            "locatie_lines":findNlines(l,n=nlines)}

                            # print(f"location l: {l['facs']}")
                            # print(f"date l: {locatie_date_l}")
                            # print(f"date: {normaled_date}")
                            # print('_______')
                            # locate_date_distance.append(lorder[l['facs']]-lorder[locatie_date_l])
                    except:
                        pass
        return locatie_date_dict, {# "locatie_date_distance": locate_date_distance, 
                                   "all_locatie_count": all_locatie_count,
                                   "locatie_with_date_count": locatie_with_date_count,
                                   "locatie_matched": locatie_matched}



        
