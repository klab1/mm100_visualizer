import os
import time
import PySimpleGUI as sg
from MyLib.mm100_visualizer import compare_nc, desc, load_atc, savefig,show_each_region,show_index,change_printf,change_basepath

default_file=''
basepath=''
# basepath=os.path.dirname(__file__)+'/'
# change_basepath(basepath)
sg.theme('Default1')

# ステップ3. ウィンドウの部品とレイアウト
layout = [
    [sg.T('ファイルを選択'), sg.Input(default_file, key='inputFilePath'), sg.FilesBrowse('ブラウズ')],
    [
        sg.Checkbox('recalc',key='recalc', default=False),
        # sg.Checkbox('save',key='save', default=True),
        # sg.Checkbox('show',key='show', default=True),
    ],
    [sg.Checkbox('compare_nc',key='compare_nc', default=True)],
    [
        sg.T('  ',),
        sg.Checkbox('xy', key="compare_nc_xy", default=False),
        sg.Checkbox('wx', key="compare_nc_wx", default=False),
        sg.Checkbox('wy', key="compare_nc_wy", default=False),
        sg.Checkbox('wz', key="compare_nc_wz", default=True),
        sg.T('    ',),
        sg.Checkbox('single_graph',key='compare_nc_single_graph', default=True),
    ],
    [sg.Checkbox('show_each_region',key='show_each_region', default=False)],
    [
        sg.T('  ',),
        sg.T('width',),
        sg.Input('300',key='show_each_region_width', size=(10, 1)),
    ],
    [sg.Checkbox('show_index',key='show_index', default=False)],
    [
        sg.T('  ',),
        sg.T('region',),
        sg.Input('',key='show_index_region', size=(20, 1)),
        sg.T('  ',),
        sg.Checkbox('x', key="show_index_region_x", default=False),
        sg.Checkbox('y', key="show_index_region_y", default=False),
        sg.Checkbox('z', key="show_index_region_z", default=True),
    ],
    [sg.Button('Confirm', key='confirm')],
    [sg.Output(size=(80,2))]
]

window = sg.Window('mm100 visualizer', layout,font=("Arial"))
def f(*a,**b):
    # print(*a,**b)
    window.refresh()
    pass
change_printf(f)
    
def g(event, values):
    paths=values['inputFilePath'].split(';')
    rc=values['recalc']

    if values['compare_nc']:
        print('compare_nc')
        v=[v for v in ['xy','wx','wy','wz'] if values[f'compare_nc_{v}']]
        for u in v:
            window.refresh()
            savefig(compare_nc(paths,st=u,single_graph=values['compare_nc_single_graph'],recalc=rc),dir=basepath+'imgs/')
        print('saved')

    if values['show_each_region']:
        print('show_each_region')
        for p in paths:
            window.refresh()
            savefig(show_each_region(p,width=int(values['show_each_region_width']),recalc=rc),dir=basepath+'imgs/')
        print('saved')

    if values['show_index']:
        print('show_index')
        for p in paths:
            window.refresh()
            t=tuple(map(float,values['show_index_region'].split('-'))) if values['show_index_region'] else None
            v=''.join([v for v in 'xyz' if values[f'show_index_region_{v}']])
            savefig(show_index(p,region=t,st=v,recalc=rc,calcinter=True),dir=basepath+'imgs/')
        print('saved')

while True:
    event, values = window.read()
    try:
        match event:
            case sg.WIN_CLOSED: #ウィンドウのXボタンを押したときの処理:
                break
            case 'confirm':
                if not values['inputFilePath']:
                    print('select at least one file')
                    continue
                g(event, values)
            case _:
                raise ValueError(f'no event defined: {event}')
        print('done')

    except Exception as e:
        print(e)

window.close()
