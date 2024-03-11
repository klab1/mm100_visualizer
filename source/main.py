import json
import os
import time
import PySimpleGUI as sg
from MyLib.mm100_visualizer import compare_nc, desc, load_atc, savefig,show_each_region,show_index,change_printf,change_basepath
import platform

basepath=''
# basepath=os.path.dirname(__file__)+'/'
# change_basepath(basepath)
sg.theme('Default1')
keys=[
    'inputFilePath',
    'mill_name_1',
    'mill_name_2',
    'mill_name_3',
    'mill_name_4',
    'show_each_region_width',
    'show_index_region',
]
default=[
    '',
    '',
    '',
    '',
    '',
    '300',
    '',
]

def h(values=None,reset=False):
    path=basepath+'cache/param'
    if reset or not os.path.exists(path):
        d={k:de for k,de in zip(keys,default)}
        json.dump(d,open(path,'w',encoding='utf-8'))
    if values is not None:
        d={k:values[k] for k in keys}
        json.dump(d,open(path,'w',encoding='utf-8'))
    else:
        d=json.load(open(path,'r',encoding='utf-8'))
    return d

ini_load_d=h()
# ステップ3. ウィンドウの部品とレイアウト
layout = [
    [
        sg.T('ファイルを選択'), 
        sg.Input(ini_load_d['inputFilePath'], key='inputFilePath',expand_x=True,enable_events=True), 
        sg.FilesBrowse('ブラウズ')
    ],
    [
        sg.Checkbox('recalc',key='recalc', default=False),
        # sg.Checkbox('save',key='save', default=True),
        # sg.Checkbox('show',key='show', default=True),
        sg.Push(),
        sg.T('name Mill4'),
        sg.Input(ini_load_d['mill_name_4'],key='mill_name_4', size=(8, 1),enable_events=True),
    ],
    [
        sg.Checkbox('compare_nc',key='compare_nc', default=True),
        sg.Push(),
        sg.T('Mill3'),
        sg.Input(ini_load_d['mill_name_3'],key='mill_name_3', size=(8, 1),enable_events=True),
    ],
    [
        sg.T('  ',),
        sg.Checkbox('xy', key="compare_nc_xy", default=False),
        sg.Checkbox('wx', key="compare_nc_wx", default=False),
        sg.Checkbox('wy', key="compare_nc_wy", default=False),
        sg.Checkbox('wz', key="compare_nc_wz", default=True),
        sg.Checkbox('wx+wy', key="compare_nc_wxy", default=False),
        sg.T('    ',),
        sg.Checkbox('single_graph',key='compare_nc_single_graph', default=True),
        sg.Push(),
        sg.T('Mill2'),
        sg.Input(ini_load_d['mill_name_2'],key='mill_name_2', size=(8, 1),enable_events=True),
    ],
    [
        sg.Checkbox('show_each_region',key='show_each_region', default=False),
        sg.Push(),
        sg.T('Mill1'),
        sg.Input(ini_load_d['mill_name_1'],key='mill_name_1', size=(8, 1),enable_events=True),
    ],
    [
        sg.T('  ',),
        sg.T('width',),
        sg.Input(ini_load_d['show_each_region_width'],key='show_each_region_width', size=(10, 1),enable_events=True),
    ],
    [sg.Checkbox('show_index',key='show_index', default=False)],
    [
        sg.T('  ',),
        sg.T('region',),
        sg.Input(ini_load_d['show_index_region'],key='show_index_region', size=(20, 1),enable_events=True),
        sg.T('  ',),
        sg.Checkbox('x', key="show_index_region_x", default=False),
        sg.Checkbox('y', key="show_index_region_y", default=False),
        sg.Checkbox('z', key="show_index_region_z", default=True),
    ],
    [
        sg.Button('Confirm', key='confirm'), 
        sg.Push(), 
        sg.Button('Reset', key='reset'), 
        sg.T('ver. 1.3.1')
    ],
    [sg.Output(size=(999,999))]
]

font=('Arial',12) if platform.system()=='Windows' else ('Arial')
window = sg.Window('mm100 visualizer', layout,font=font, resizable=True, size=(700, 360),finalize=True)
window.set_min_size((700,340))

def f(*a,**b):
    # print(*a,**b)
    window.refresh()
    pass
change_printf(f)

def g(event, values):
    if not values['inputFilePath']:
        print('select at least one file')
        return

    paths=values['inputFilePath'].split(';')
    rc=values['recalc']
    millname=[values[f'mill_name_{i+1}'] for i in range(4)]

    if values['compare_nc']:
        print('compare_nc')
        v=[v for v in ['xy','wx','wy','wz','wxy'] if values[f'compare_nc_{v}']]
        for u in v:
            window.refresh()
            savefig(compare_nc(paths,st=u,single_graph=values['compare_nc_single_graph'],recalc=rc,millname=millname),dir=basepath+'imgs/')
        print('saved')

    if values['show_each_region']:
        print('show_each_region')
        for p in paths:
            window.refresh()
            savefig(show_each_region(p,width=int(values['show_each_region_width']),recalc=rc,millname=millname),dir=basepath+'imgs/')
        print('saved')

    if values['show_index']:
        print('show_index')
        for p in paths:
            window.refresh()
            t=tuple(map(float,values['show_index_region'].split('-'))) if values['show_index_region'] else None
            v=''.join([v for v in 'xyz' if values[f'show_index_region_{v}']])
            savefig(show_index(p,region=t,st=v,recalc=rc,calcinter=True,millname=millname),dir=basepath+'imgs/')
        print('saved')

# print('a')
# time.sleep(1)
# window.write_event_value('init',1)
# window.refresh()
# g(*window.read())
# window.refresh()

while True:
    event, values = window.read()
    try:
        if event== sg.WIN_CLOSED: #ウィンドウのXボタンを押したときの処理:
            break
        elif event== 'confirm':
            g(event, values)
            print('done')
        elif event== 'reset':
            d=h(reset=True)
            [window[k](de) for k,de in zip(keys,default)]
            print('saved')
        elif event in keys:
            h(values)
            print('saved')
        else:
            raise ValueError(f'no event defined: {event}')

    except Exception as e:
        print(e)

window.close()
