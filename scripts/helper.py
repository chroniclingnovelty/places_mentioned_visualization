import textwrap
import pickle
import datetime,re
import pandas as pd
import plotly.graph_objects as go

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
        

def join_line(line):
    # line: [<datum>1775</datum>, ' tot', <datum> 1788 </datum>, 'enz:;']
    joined = ''
    for i in line:
        try:
            if i.name in ['datum','locatie']:
                joined += f"<b>{i.text.strip(' ')}</b>"
            else:
                joined += f"{i.text.strip(' ')}"
        except:
            joined += f"{i.strip(' ')}"
    return joined

# join_line(d_ab[20]['line'])

def decompose_ab(ab):
    # input: single ab
    # output: 
    ab_dict = {}
    now_ind = None
    now_facs = ''

    for ind,i in enumerate(ab):
        if i.name == 'lb':
            now_ind = ind
            now_facs = i['facs']
            ab_dict[(now_ind,now_facs)] = [] # {'facs':i['facs'],'line':[]}
        else:
            try:
                ab_dict[(now_ind,now_facs)].append(i)  # [now_ind]['line'].append(i)
            except:
                pass
    return ab_dict

# d_ab = decompose_ab(abs[0])



def find_index(d_abs, page, line, region, n):
    # n: how much context do you want, forwards/backwards n lines
    lb_id = f"#facs_{page}_{line}"
    ab_id = f"#facs_{page}_{region}"
    ab_ind = None

    for i in range(len(d_abs)):
        assert len(d_abs[i].keys()) ==1, print(d_abs[i].keys())
        if list(d_abs[i].keys())[0] == ab_id:
            ab_ = d_abs[i]
            ab_ind = i  # assign ab_ind, the position of this ab among all abs in this file

    for ii,i in enumerate(sorted(ab_[ab_id])):
        if i[1] == lb_id:
            r = list(range(ii-(n+1),ii+n+1))
    # print(r,ab_ind)
    return r, ab_ind, ab_id

def generate_output_line(d_abs, r, ab_ind, ab_id):
    # r: a range list, in the middle among them is the text we look for
    # and we are going to find the context of that text (forward X lines, backwards X lines)
    # ab_ind: the position of this ab among all abs in this file
    # in case if we are going to find a previous ab for context
    output_line = []
    for i in r:
        if i < 0:
            try:
                # if ab_ind = 0 , you cannot go backwards in this ab
                # if ab_ind - 1 <=0, then start from 0 # pass
                if ab_ind - 1 <= 0:
                    pass
                else:
                    assert len(d_abs[ab_ind-1].values())==1
                    _ab = list(d_abs[ab_ind-1].keys())[0]
                    lbss = d_abs[ab_ind-1][_ab] # dict
                    lbs = sorted([k for k in lbss.keys()]) # key list
                    output_line += lbss[lbs[i]]
                    # print(list(d_abs[ab_ind-1].values())[0][_k[i]])
            except:
                # print(ab_ind)
                pass


        elif i > len(d_abs[ab_ind][ab_id])-1:
            try:
                assert len(d_abs[ab_ind+1].values())==1
                _k = sorted([k for k in list(d_abs[ab_ind+1].values())[0].keys()])
                output_line += list(d_abs[ab_ind+1].values())[0][_k[i]]
                # print(list(d_abs[ab_ind+1].values())[0][_k[i]])
            except:
                # print(ab_ind)
                pass
        else:
            _k = sorted([k for k in list(d_abs[ab_ind].values())[0].keys()])
            output_line += list(d_abs[ab_ind].values())[0][_k[i]]
            # print(list(d_abs[ab_ind].values())[0][_k[i]])
    return output_line


def find_normed_date(date_page,date_line,date_value,date_excel):
    date_norm = date_excel.query("Page ==@ date_page").query("Line==@ date_line").query("Value==@date_value")
    year = date_norm['year'].values[0]
    month = date_norm['month'].values[0]
    day = date_norm['day'].values[0]
    return f"{year}-{month}-{day}"



###############################
###############################
###############################


# for new format 'l-tag'
def highlight(t):
    h = ''
    for i in t:
        if i.name == 'locatie':
            h += f"<b>{i.text}</b>"
        else:
            h += i.text
    return h

def findNlines(d, n = 3):
    # previous n lines
    # next n lines 
    # d is a l object
    origin = d
    text = []
    for i in range(n):
        try:
            _ = d.findPrevious('l')
            text.append(_)
            d = _
        except:
            pass
    text = text[::-1] + [origin]
    for i in range(n):
        try:
            _ = origin.findNext('l')
            text.append(_)
            origin = _
        except:
            pass
    o = []
    for i in text:
        try:
            o.append(highlight(i))
        except:
            pass
    return '<br>'.join(o)

def generate_timeline(xml_name, xml):
    timeline = []
    for l in xml.find_all('l'):
        try:
            d = l.find(name='datum',datum = re.compile("\d{4}-\d{2}-\w{2}"))
            if d:
                timeline.append(d['datum'])
        except:
            pass

    _ = pd.DataFrame()
    _['d'] = timeline
    _['c'] = [str(i) for i in range(len(timeline))]
    f = go.Scatter(x = [str(i) for i in range(len(timeline))],
                y = timeline,
                mode='markers',
                name = xml_name)

    # fig = go.Figure(data=f)
    # fig.update_layout(
    #     # title="Plot Title",
    #     xaxis_title="chronicle context order (the N th appeared date tag)",
    #     yaxis_title="date")
    return f
