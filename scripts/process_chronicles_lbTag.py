from bs4 import BeautifulSoup
import math,pickle,textwrap,random,os,lxml,plotly
import pandas as pd
from datetime import date,datetime
import plotly.graph_objects as go
import plotly.express as px
from pprint import pprint
import numpy as np
from helper import *


class ChronicleBucket:
    with open('../data/location_mapping.pkl', 'rb') as f:
        mapping_loacation = pickle.load(f)

    def __init__(self,excel_path,xml_path=None):
        # '../data/raw/1791_Purm_Louw_04.xlsx'
        # excel file has datum sheet and Overview sheet
        self.excel_path = excel_path 
        self.meta_datum = pd.read_excel(self.excel_path, sheet_name='datum',engine='openpyxl')
        self.meta_locatie = pd.read_excel(self.excel_path, sheet_name='locatie',engine='openpyxl')
        # self.meta_all = pd.read_excel(self.excel_path, sheet_name='Overview',engine='openpyxl')
        self.summary = None

        self.xml_path = xml_path
        if xml_path:
            with open(self.xml_path,'r') as f:
                file = f.read()
            self.meta_xml = BeautifulSoup(file,'xml')
    
        ## clean date in self.meta_datum
        # in-place change self.meta_datum
        # 1. combine datum and when column
        # 2. extract year, month, day; add to self.meta_datum as column
        # 3. fill xx to 01

        # column datum and when
        for row in self.meta_datum.index.tolist():
            if type(self.meta_datum.loc[row,'datum']) is not str:
                try:
                    self.meta_datum.loc[row,'datum'] = self.meta_datum.loc[row,'when']
                except:
                    pass

        # extract year, month, day for non-null datum value
        _ = self.meta_datum.loc[self.meta_datum['datum'].notnull()]
        for row in _.index.tolist():
            date = self.meta_datum.loc[row,'datum']
            try:
                if (type(date) == str) & (len(date.split('-')) == 3):
                    self.meta_datum.loc[row,'year'],self.meta_datum.loc[row,'month'],self.meta_datum.loc[row,'day'] = date.split('-')
            except:
                print(date)
        
        # Completeness of dates: year, month ,day
        # month_miss = self.meta_datum.loc[self.meta_datum['month']=='xx',:].shape[0]
        # day_miss = self.meta_datum.loc[self.meta_datum['day']=='xx',:].shape[0]
        # print(f"missing month: {month_miss}, missing days: {day_miss}")

        # fill missing to 01
        self.meta_datum['month'] = self.meta_datum['month'].str.replace('xx','01') # .astype('Int64')
        self.meta_datum['day'] = self.meta_datum['day'].str.replace('xx','01') #.astype('Int64')

    def get_all_abs(self):
        abs = self.meta_xml.find_all('ab')
        d_abs = []
        for ab in abs:
            _ = {ab['facs']:decompose_ab(ab)}
            d_abs.append(_)
        return d_abs

    def get_all_lbs_order(self):
        # dict: 
        # #facs_3_r1l1 0
        # #facs_3_r1l2 1
        # #facs_3_r1l3 2
        # #facs_3_r1l4 3
        d_abs = self.get_all_abs()
        ind = 0
        lb_order_l = {}
        for ab in d_abs:
            _ = sorted(list(list(ab.values())[0].keys()))
            _ = [i[1] for i in _]
            for i in _:
                lb_order_l[i] = ind
                ind = ind +1
        return lb_order_l

    def histogram_date(self):
        # histogram: frequency date_time of this chronicle
        df_date_clean = self.meta_datum.loc[self.meta_datum['datum'].str.contains('x')==False,:]
        # print(meta_date.shape, df_date_clean.shape) 
        fig_histo = go.Figure()
        fig_histo.add_trace(go.Histogram(x=df_date_clean['datum'],
                                         xbins = dict(size=2419200000))) # per month
        fig_histo.update_layout(
            title_text=f'date time frequency', # title of plot
            xaxis_title_text='date (each bin is a month)', # xaxis label
            yaxis_title_text='Count')
        return fig_histo
        
    def check_date_order(self):
        # chronicle context order (the N th appeared date tag)
        # to see whether it's continous time date 
        df_date_clean = self.meta_datum.loc[self.meta_datum['datum'].str.contains('x')==False,:]
        d = list([datetime.strptime(i,'%Y-%m-%d') for i in df_date_clean['datum'].tolist()])
        d = [datetime.strftime(i,'%Y-%m-%d') for i in d]
        c = [str(i) for i in range(len(df_date_clean['datum'].tolist()))]
        _ = pd.DataFrame()
        _['d'] = d
        _['c'] = c
        f = px.scatter(_,x=c,y=d)
        f.update_layout(
            # title="Plot Title",
            xaxis_title="chronicle context order (the N th appeared date tag)",
            yaxis_title="date")
        return f

    def get_locatie(self):
        # from chronicle's excel file, get all locatie lb_names, corresponding page, region, lines 
        # return dict()
        # {'#facs_3_r1l5': {'page': 3, 'line': 'r1l5', 'region': 'r1'},...}
        locatie_lb_names = {}
        for i in self.meta_locatie.index:
            page = self.meta_locatie.loc[i,'Page']
            line = self.meta_locatie.loc[i,'Line']
            region = self.meta_locatie.loc[i,'Region']
            _ = f"#facs_{page}_{line}"
            locatie_lb_names[_] = {'page':page,'line':line,'region':region}
        return locatie_lb_names

    def find_locatie_date(self):
        # generate a dictionary 
        # indicate the datum/locatie object's lb_name
        # and the locatie's belonged date

        # output ab_locatie_date_dic is a dict(),
        # the locatie key contains its raw location text, belonged date, the date's raw text and lb_name
        # e.g.
        # key is '#facs_5_r4l4':
        # {'type': 'locatie',
        #  'raw_text': 'Purmerende',
        #  'detail': {'ab_name': '#facs_5_r4'},
        #  'belong_to_date': {'raw_text':raw_text, 
        #                      'date_lb_name':date_lb_name,
        #                      'normed_date':normed_date,
        #                      'date_locatie_d': how many lines between locatie and its belonged date}, ...}

        # and return the number of locatie in this chronicle
        lb_order = self.get_all_lbs_order()
        ab_locatie_date_dic = {}
        locatie_count_ab = 0
        abs = self.meta_xml.find_all('ab')
        for ab in abs:
            for ind,i in enumerate(ab):
                if i.name in ['locatie','datum']:
                    lb_fac = i.findPrevious('lb')['facs'] 
                    # _ind = f"{ind}|{lb_fac}"
                    ab_locatie_date_dic[lb_fac] = {'type':i.name,'raw_text':i.text,
                                                   'detail':{'ab_name':ab['facs']}}
                if i.name == 'locatie':
                    locatie_count_ab += 1
                    # but if try failed, the actual count of locatie with a belonged date would be less than this count here
                    try:
                        raw_text = i.find_previous('datum').text
                        date_lb_name = i.find_previous('datum').findPrevious('lb')['facs']

                        # find normalized date from excel metadata
                        _ = date_lb_name.split('_',2)[1:3]
                        date_page = int(_[0])
                        date_line = _[1]
                        
                        if self.meta_datum.loc[(self.meta_datum['Page']==int(date_page))&(self.meta_datum['Line']==date_line),'datum'].tolist():
                            normed_date = self.meta_datum.loc[(self.meta_datum['Page']==int(date_page))&(self.meta_datum['Line']==date_line),'datum'].tolist()[-1]
                        else:
                            # failed_date_lb.append(v['belong_to_date']['date_lb_name'])
                            # print(f'nodate: {date_lb_name}')
                            date_lb_name = i.find_previous('datum').find_previous('datum').findPrevious('lb')['facs']
                            _ = date_lb_name.split('_',2)[1:3]
                            date_page = int(_[0])
                            date_line = _[1]
                            try:
                                normed_date = self.meta_datum.loc[(self.meta_datum['Page']==int(date_page))&(self.meta_datum['Line']==date_line),'datum'].tolist()[-1]
                            except:
                                normed_date = None

                        ab_locatie_date_dic[lb_fac].update({'belong_to_date':{'raw_text':raw_text, 
                                                                              'date_lb_name':date_lb_name,
                                                                              'normed_date':normed_date,
                                                                              'date_locatie_d':lb_order[lb_fac]-lb_order[date_lb_name]}})
                        
                    except:
                        print(i)
        return ab_locatie_date_dic,locatie_count_ab
    
    def locatie_date_dict(self, n = 3):
        # n: before and after n lines for hover info
        # return a dict():
        # #facs_18_r2l7:
        # {'#facs_3_r1l10': {'type': 'datum',
        #                   'raw_text': ' 1788 ',
        #                   'detail': {'ab_name': '#facs_3_r1'}},
        # '#facs_5_r4l4': {'type': 'locatie',
        #                  'raw_text': 'Purmerende',
        #                  'detail': {'page': '5', 'region': 'r4', 'line': 'r4l4'},
        #                  'belong_to_date': {'text': ' 1788 ', 'date_line': '#facs_3_r1l10'},
        #                  'hover': 'in het ooge Werd gehouden.Voorreeden.\nAan de Waarde,olgwe in d deeze....}}

        locatie_data_dict, _ =  self.find_locatie_date()
        d_abs = self.get_all_abs()
        locaties = [k for k,v in locatie_data_dict.items() if v['type']=='locatie']

        for ab in d_abs:
            for ab_name, lbs in ab.items():
                for lb_name, lb in lbs.items():
                    for i in locaties:
                        if lb_name[1] == i:
                            try:
                                page, line = i.split('_',2)[1:3]
                                page,region = locatie_data_dict[i]['detail']['ab_name'].split('_',2)[1:3]
                                r, ab_ind,ab_id = find_index(d_abs, page, line, region, n)
                                o = generate_output_line(d_abs, r, ab_ind, ab_id)
                                hover_info = join_line(o)
                                locatie_data_dict[i]['detail'] = {'page':page,'region':region,'line':line}
                                locatie_data_dict[i]['hover'] = hover_info
                            except:
                                print(i)
        return locatie_data_dict
    # def df_from_dict()
    # la lo raw_date normalized_date raw_location matched_lacation context(f/b n lines) lb_name chrnicle_name



        
        
