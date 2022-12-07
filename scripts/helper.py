import textwrap
import pickle
import datetime
import pandas as pd

def cut_sib(sib,char_per_line = 50):
    if len(sib) > char_per_line:
        sib = '<br>'.join(textwrap.wrap(sib,width=char_per_line))
    return sib


def get_page_line(lb):
    # #facs_13_r2l3
    # 13 r2l3
    assert len(lb.split('_',2)) ==3 
    page, line = lb.split('_',2)[1:3]
    page = int(page)
    return page, line


def pack(object='',file_name='',mode='wb'):
    # mode: wb, rb
    # pack(o,f,'wb') write o to f
    # pack(o,f,'rb') read f to o
    if mode=='wb':
        with open(file_name,mode) as f:
            pickle.dump(object, f)
    if mode=='rb':
        with open(file_name, mode) as f:
            object = pickle.load(f)
            return object

# def get_date_range(t1,t2):
#     # t1 = date_list[0]
#     # t2 = date_list[10]
#     pd.date_range(start=t1,end=t2)
#     return pd.date_range(start=t1,end=t2)

def string_to_date(string):
    # 1778-10-13
    _ = string.split('-')
    assert len(_) == 3, f"{string} is not standard format for datetime.date()"
    try: 
        d = datetime.date(int(_[0]),int(_[1]),int(_[2]))
        return d
    except:
        print(f"{_} ???")
        