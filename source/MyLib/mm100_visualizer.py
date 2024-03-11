import collections
import shutil
import datetime
import os
import pickle
from math import log10
from pprint import pprint
from typing import List,Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# from MyLib.util import convert_sec,get_lim


def main():
    # ファイルのパス　txtでもncでも可　先頭にrをつける(windows)
    paths=[
        # '/Users/klab_mac1/Library/CloudStorage/GoogleDrive-s208486s@st.go.tuat.ac.jp/共有ドライブ/Klab/個人フォルダ/Emura/共有/mm100/AD025E06.txt',
        # '/Users/klab_mac1/Library/CloudStorage/GoogleDrive-s208486s@st.go.tuat.ac.jp/共有ドライブ/Klab/個人フォルダ/Emura/共有/mm100/AD025C07.txt',
        '/Users/klab_mac1/Library/CloudStorage/GoogleDrive-s208486s@st.go.tuat.ac.jp/共有ドライブ/Klab/個人フォルダ/Emura/共有/mm100/AD041C04.txt',
        # '/Users/klab_mac1/Library/CloudStorage/GoogleDrive-s208486s@st.go.tuat.ac.jp/共有ドライブ/Klab/個人フォルダ/Emura/共有/mm100/AS100T00.txt',
    ]

    # # すべてのファイルを並べる
    # fig=compare_nc(paths,st='wxy')
    fig=compare_nc(paths)

    # xyをプロット
    # fig=compare_nc(paths,st='xy',single_graph=True)

    # # それぞれの区画の開始300秒をプロット
    # for p in paths:
    #     fig=show_each_region(p)

    # # 経過時間とファイルの行数の関係をプロット
    # for p in paths:
    #     fig=show_index()

    # plt.show()
    savefig(fig)

################################################################################

def change_printf(func):
    global print
    print=func
basepath=''
def change_basepath(path):
    global basepath
    basepath=path

def convert_sec(s):
    if s < 60:
        return f'{s:.1f}s'
    elif s < 3600:
        return f'{s//60:.0f}m {s%60:.1f}s'
    else:
        return f'{s//3600:.0f}h {s//60%60:.0f}m {s%60:.1f}s'

def get_lim(s, e, margin=0.05):
    return s-(e-s)*margin, e+(e-s)*margin

class CommandparsedList(list):
    command_list_fl = 'XYZFIJR'
    command_list_in = 'GSMHT'
    command_list = command_list_fl+command_list_in
    command_dict = {f: i for i, f in enumerate(command_list)}

    def __init__(self, arr=None):
        self.reset()
        self.history=collections.deque(maxlen=10)
        super().__init__(arr or [0]*len(self.command_list))

    def reset(self):
        self.updated = [0]*len(self.command_list)

    def get_new(self, letter: str):
        k=self.command_dict[letter]
        return self[k] if self.updated[k] else None
    
    def get(self, letter: str):
        return self[self.command_dict[letter]]

    def set(self, letter: str, value):
        self[self.command_dict[letter]] = value
        self.updated[self.command_dict[letter]] = 1
        return value

    def copy(self):
        ul=CommandparsedList(super().copy())
        # ul.history=self.history
        return ul

    def command_parse(self,s:str):
        os = s
        self.history.append(s)
        i = 0
        c = s[0]
        s = s[1:]
        self.reset()
        while True:
            if i >= len(s):
                if c in self.command_list_fl:
                    self.set(c, float(s[:i]))
                else:
                    self.set(c, int(s[:i]))
                break
            elif ord(s[i]) >= 65:
                if c in self.command_list_fl:
                    self.set(c, float(s[:i]))
                else:
                    self.set(c, int(s[:i]))
                c = s[i]
                s = s[i+1:]
                i = 0
            else:
                i += 1
        return self

    def __repr__(self) -> str:
        l = []
        for i in range(len(self.command_list)):
            if not self.updated[i]:
                continue
            l.append(f'{self.command_list[i]}: {self[i]}')
        return ' '.join(l) if len(l) else super().__repr__()


class MillPosition(list):
    def app(self, ul: CommandparsedList, length: float):
        self.append([ul.get('X'), ul.get('Y'), ul.get('Z'), length/ul.get('F')*60])
        return self
    def app_safe(self, ul: CommandparsedList, length: float):
        if ul.get('F')==0:
            self.append([ul.get('X'), ul.get('Y'), ul.get('Z'),0])
        else:
            self.app(ul,length)
        return self


class GetIntermidiate:
    def __init__(self, div=8) -> None:
        self.dic = {}
        self.dic1 = {}
        self.div = div

    @staticmethod
    def _f(px, py, x, y, r, div):
        A = np.array([px, py])
        B = np.array([x, y])
        AB = B-A
        N = np.array([-AB[1], AB[0]])
        d = np.linalg.norm(AB)
        C = (A+B)/2+N/np.linalg.norm(N)*(r**2-(d/2)**2)**0.5
        CA = A-C
        nCA = CA/np.linalg.norm(CA)
        t = np.arcsin(d/2/r)
        l = 2*r*t
        n = int(l/r/(1.57/div))+1
        li = []
        for th in np.array(range(1, n+1))/n*t*2:
            s, c = np.sin(th), np.cos(th)
            rot = np.array([[c, -s], [s, c]])
            li.append(rot@nCA-nCA)
        l = np.linalg.norm(li[0])*1.01
        return li, l

    @staticmethod
    def _f1(px, py, x, y, r, div):
        A = np.array([px, py])
        B = np.array([x, y])
        AB = B-A
        N = np.array([-AB[1], AB[0]])
        d = np.linalg.norm(AB)
        C = (A+B)/2-N/np.linalg.norm(N)*(r**2-(d/2)**2)**0.5
        CA = A-C
        nCA = CA/np.linalg.norm(CA)
        t = -np.arcsin(d/2/r)
        l = -2*r*t
        n = int(l/r/(1.57/div))+1
        li = []
        for th in np.array(range(1, n+1))/n*t*2:
            s, c = np.sin(th), np.cos(th)
            rot = np.array([[c, -s], [s, c]])
            li.append(rot@nCA-nCA)
        l = np.linalg.norm(li[0])*1.01
        return li, l

    def f(self, px, py, x, y, r, clockwise, div=8):
        key = (x-px, y-py, r)
        dict = [self.dic, self.dic1][clockwise]
        func = [self._f, self._f1][clockwise]
        if key in dict.keys():
            li, l = dict[key]
        else:
            li, l = func(px, py, x, y, r, div)
            dict[key] = [li, l]
        l = l*r
        ret = []
        for p in li:
            x, y = p*r+[px, py]
            ret.append((x, y, l))
        return ret


class GetIntermidiateNew(GetIntermidiate):
    clockwisedict = {3: 0, 2: 1}

    def f(self, pul: MillPosition, ul: MillPosition, r, div=8):
        px = pul[0]
        py = pul[1]
        x = ul[0]
        y = ul[1]
        i = ul.get('I')
        j = ul.get('J')
        G = ul.get('G')
        clockwise = self.clockwisedict[G]
        key = (i, j, r)
        dict = [self.dic, self.dic1][clockwise]
        func = [self._f, self._f1][clockwise]
        if key in dict.keys():
            li, l = dict[key]
        else:
            li, l = func(px, py, x, y, r, div)
            dict[key] = [li, l]
        l = l*r
        ret = []
        for p in li:
            x, y = p*r+[px, py]
            ret.append((x, y, l))
        return ret


def _skip_to_g45(strlist, inin):
    alllen = len(strlist)
    for n, s in enumerate(strlist[inin:]):
        print(f'{n+1+inin} / {alllen}\r', end='')
        s = s.strip()
        if not s:
            continue
        if s == 'G49':
            break
    print()
    return n+1+inin


def see_definition(strlist: List[str], b: MillPosition, ul: CommandparsedList, inin:int):
    tmwidth = shutil.get_terminal_size().columns
    alllen = len(strlist)
    for n, s in enumerate(strlist[inin:]):
        ps = f'{n+1+inin} / {alllen}'
        print(ps+' '*10+'\r', end='')
        s = s.strip()
        pul = ul.copy()
        ul.command_parse(s)

        if ul.get_new('M')==8:# 切削に入る
            l = (
                (ul[0]-pul[0])**2 +
                (ul[1]-pul[1])**2 +
                (ul[2]-pul[2])**2
            )**0.5
            b.app_safe(ul, l)
            ul.set('G',1)
            ps=f'Mill:{ul.get("T")}, Speed:{ul.get("S")}'
            b[0][len(b)-2]=ps
            print('\n'+ps)
            print('definition ends with "M08"')
            return n+1+inin, b, ul
        elif ul.get_new('M')==30:# ファイルの終わり
            ps=f'File end'
            b[0][len(b)-2]=ps
            print('\ndefinition ends with "M30"')
            return -1, b, ul
        # elif ul.get_new('M') in [3,6]:# 見たいだけ
        #     print(s+' '*10)


def _trace1(strlist: List[str], b: MillPosition, ul: CommandparsedList, inin:int, calcinter: bool):
    tmwidth = shutil.get_terminal_size().columns
    cinter = GetIntermidiateNew() if calcinter else None
    alllen = len(strlist)
    for n, s in enumerate(strlist[inin:]):
        ps = f'{n+1+inin} / {alllen}'
        print(ps+' '*10+'\r', end='')
        s = s.strip()
        pul = ul.copy()
        ul.command_parse(s)

        if ul.get_new('M')==8:
            print('\nsection ends with "M08"\n')
            return n+inin, b, ul
        elif ul.get('G') == 0 or n==0:
            l = (
                (ul[0]-pul[0])**2 +
                (ul[1]-pul[1])**2 +
                (ul[2]-pul[2])**2
            )**0.5
            b.app_safe(ul, l)
        elif ul.get('G') == 1:
            if sum(ul.updated[:3]) == 1:
                i = ul.updated.index(1)
                l = abs(ul[i]-pul[i])
            else:
                # print(f'- G01 but multi axis: {n+1+inin}: ({ul})')
                l = (
                    (ul[0]-pul[0])**2 +
                    (ul[1]-pul[1])**2 +
                    (ul[2]-pul[2])**2
                )**0.5
            b.app(ul, l)
        elif ul.get('G') in [2, 3]:
            i = ul.get('I')
            j = ul.get('J')
            r = (i*i+j*j)**0.5
            if cinter is not None:
                li = cinter.f(pul, ul, r)
                for lx, ly, ll in li:
                    b.append([lx, ly, ul[2], ll/ul[3]*60])
            else:
                l = (
                    (ul[0]-pul[0])**2 +
                    (ul[1]-pul[1])**2 +
                    (ul[2]-pul[2])**2
                )**0.5
                l = 2*r*np.arcsin(l/2/r)
                b.app(ul, l)
        elif ul.get_new('G')==49:
            print('\nsection ends with "G49"\n')
            return n+1+inin, b, ul
        else:
            print(f'- {n+1+inin}: ({ul})')
            # print(f'{n+1+inin}: {6+2*int(log10(alllen))}C ({ul})')
            if strlist[n+1+inin][0] == '%':
                print('\nfile ends with "%"\n')
                return n+1+inin, b, ul


def load(strlist, calcinter):
    # strlist=open('230214_export/cc.nc').readlines()
    x = y = z = pf = 0
    lens = len(strlist)
    for i, s in enumerate(strlist):
        print(f'{i+1} / {len(strlist)}\r', end='')
        if not s:
            continue
        s = s.strip()
        if 'G00' in s:
            break
        if 'X' in s and 'Y' in s:
            x, y = s.index('X'), s.index('Y')
            x, y = float(s[x+1:y]), float(s[y+1:])
        if 'Z' in s:
            z = s.index('Z')
            z = float(s[z+1:])
        if 'F' in s:
            f = s.index('F')
            pf = float(s[f+1:])

    b = [{}, [x, y, z, 0]]
    b_append = b.append
    cinter = GetIntermidiate() if calcinter else None
    for i, s in enumerate(strlist[i:]):
        print(f'{i+1} / {lens}\r', end='')
        if not s:
            continue
        s = s.strip()
        g = int(s[1:3]) if s[0] == 'G' else None
        x = s.index('X') if 'X' in s else None
        y = s.index('Y') if 'Y' in s else None
        z = s.index('Z') if 'Z' in s else None
        r = s.index('R') if 'R' in s else None
        f = s.index('F') if 'F' in s else None

        if i == 470:
            print()
        if g == 0 and z is not None:
            x, y, pz, _ = b[-1]
            z = float(s[z+1:])
            b_append([x, y, z, abs(pz-z)/pf*60])
            continue
        elif g is None and x is not None and y is not None:
            px, py, z, _ = b[-1]
            x = float(s[x+1:y])
            y = float(s[y+1:])
            l = np.linalg.norm((x-px, y-py, z-pz))
            b_append([x, y, z, l/pf*60])
            continue

        px, py, pz, _ = b[-1]
        if g == 1:
            x = float(s[x+1:y])
            y = float(s[y+1:z])
            z = float(s[z+1:f])
            l = np.linalg.norm((x-px, y-py, z-pz))
            pf = f = float(s[f+1:])  # mm/min
            b_append([x, y, z, l/f*60])
        elif g == 2 or g == 3:
            x = float(s[x+1:y])
            y = float(s[y+1:z])
            z = float(s[z+1:r])
            r = float(s[r+1:f])
            pf = f = float(s[f+1:])  # mm/min

            if cinter is not None:
                li = cinter.f(px, py, x, y, r, [0, 0, 1, 0][g])
                for lx, ly, ll in li:
                    b_append([lx, ly, z, ll/f*60])
            else:
                l = np.linalg.norm((x-px, y-py, z-pz))
                l = 2*r*np.arcsin(l/2/r)
                b_append([x, y, z, l/f*60])

    print()
    return b


def load_atc(strlist: List[str], calcinter: bool):
    ul = CommandparsedList()
    b = MillPosition([{}])
    i = _skip_to_g45(strlist, 0)
    while True:
        i, b, ul = see_definition(strlist, b, ul, i)
        if i==-1:break
        i, b, ul = _trace1(strlist, b, ul, i, calcinter)

    # i, ul = _initial_pos(strlist, ul, i)
    # b.append([ul.get('X'), ul.get('Y'), ul.get('Z'), 0])
    # i, b, ul = _trace(strlist, b, ul, calcinter, i)

    print()
    # pprint(b)
    return b


def desc(path, till=None, calcinter=False, type='new', recalc=False):
    name = basepath+'cache/'+os.path.basename(path)+('.inter' if calcinter else '')+(str(till) if till else '')+'.cache'
    if not recalc and os.path.exists(name):
        print('cache found', name)
        (attrs, data) = pickle.load(open(name, 'rb'))
        _, _, _, w = data
        print(f'range: [0:{len(w)}], length: {convert_sec(w[-1])}')
        return attrs, data
    sl = open(path).readlines()[:till] if till is not None else open(path).readlines()
    print('## '+path+(' (recalc)' if recalc and os.path.exists(name) else ''))
    func = {'old': load, 'new': load_atc}[type]
    data = func(sl, calcinter)
    attrs = data[0]
    (x, y, z, w) = tuple(zip(*data[1:]))
    w = np.cumsum(w)
    data = (x, y, z, w)
    print(f'range: [0:{len(w)}], length: {convert_sec(w[-1])}')
    os.makedirs('cache/', exist_ok=True)
    pickle.dump((attrs, data), open(name, 'wb'))
    print('cache saved')
    return attrs, data


def show_attrs(attrs,w,name=''):
    a=[f'{convert_sec(w[k])} : {v}' for k,v in attrs.items()]
    print(f'Attrs : {name}')
    pprint(a)
    print()

def make_ticks(lastw,min=15):
    rmin=int(min*60)
    tile=[f'.{min*i}' for i in range(60//min)]
    tile[0]=''
    xt=np.arange(0,((lastw//rmin)+2)*rmin,rmin)
    tile=np.tile(tile,len(xt)//len(tile)+1)
    return xt,map(lambda x:f'{int(x[0]/3600)}{x[1]}',zip(xt,tile))

###########################################

def compare_nc(paths:str|List[str],st='wz',single_graph=False,recalc=False,millname=None,line_width=3):
    if not isinstance(paths,list):
        paths=[paths]
    h=int(single_graph or len(paths))
    fig, axs = plt.subplots(h, 1, figsize=(14, h*2+1) if 'w' in st else (8,8))
    if not hasattr(axs, "__iter__"):
        axs=[axs]*max(h,len(paths))
    dic={'x':0,'y':1,'z':2,'w':3}
    millname=millname or ['']*4
    ma=0
    for ax,file in zip(axs,paths):
        label = os.path.splitext(os.path.basename(file))[0]
        attrs,xyzw = desc(file,type='new',recalc=recalc, calcinter='w' not in st)
        show_attrs(attrs,xyzw[3],label)
        maxh=3
        if len(st)==2:
            ax.plot(xyzw[dic[st[0]]], xyzw[dic[st[1]]], label=f'{label} {st}')
            maxh=max(xyzw[dic[st[1]]])
        elif len(st)==3:
            ax.plot(xyzw[dic[st[0]]], xyzw[dic[st[1]]], label=f'{label} {st}')
            ax.plot(xyzw[dic[st[0]]], xyzw[dic[st[2]]], label=f'{label} {st}')
            maxh=max(max(xyzw[dic[st[1]]]),max(xyzw[dic[st[2]]]))
        # ax.plot(w, z, label=label)
        ma=max(ma,xyzw[3][-1])
        if 'w' in st:
            for at in attrs:
                ax.scatter(xyzw[3][at],maxh,c='k',marker='x')
                try:
                    add=f' {millname[int(attrs[at][5])-1]}'
                except:
                    add=''
                ax.text(xyzw[3][at],maxh,attrs[at][:6]+add)
    name=label if len(paths)==1 else f"{label}+{len(paths)-1}"
    print('name:',name)
    for ax in axs:
        if not 'w' in st:
            ax.set_aspect('equal')
        else:
            ax.set_xticks(*make_ticks(ma))
            ax.set_xlim(*get_lim(0,ma))
        ax.grid()
        ax.legend()
    fig.tight_layout()
    return fig

def show_each_region(path,initial_region_point:List[int]=None,width=300,recalc=False,millname=None):
    label=os.path.splitext(os.path.basename(path))[0]
    ats,(_,_,z,w) = desc(path,calcinter=False,type='new',recalc=recalc)
    show_attrs(ats,w,label)
    name='region_'+label
    print('name:',name)

    def f(a):
        c=b=10**int(log10(a))
        if a/b>=5:
            c=5*b
        return c
    cp=[0]+([w[v]-w[v]%f(width/5) for v in ats.keys()][:-1] if initial_region_point is None else initial_region_point)
    N=len(cp)
    millname=millname or ['']*4
    la=[label]
    for l in list(ats.values()):
        try:
            add=f' {millname[int(l[5])-1]}'
        except:
            add=''
        la.append(l[:6]+add)
    fig, axs = plt.subplots(N, 1, figsize=(14, max(5,N*1.6)))

    axs[0].set_xticks(*make_ticks(w[-1]))
    for i,(ax,p,l) in enumerate(zip(axs,cp,la)):
        if i==0:
            ax.plot(w, z, label=l)
        else:
            r=get_lim(p,p+width)
            try:
                s=np.argwhere(r[0]<w)[0,0]
            except:
                e=len(w)
            try:
                e=np.argwhere(r[1]<w)[0,0]+1
            except:
                e=len(w)
            ax.plot(w[s:e], z[s:e], label=l)
            ax.set_xlim(*r)
        ax.grid()
        ax.legend()
    fig.tight_layout()
    return fig

def show_xy(paths:List[str],xy='xy'):
    fig, axs = plt.subplots(1, 1,figsize=(8,8))
    dic={'x':0,'y':1,'z':2,'w':3}
    if not 'w' in xy:
        axs.set_aspect('equal')
    for file in paths:
        label=os.path.splitext(os.path.basename(file))[0]
        ats,xyzw = desc(file, calcinter=True,type='new')
        show_attrs(ats,xyzw[3],label)
        axs.plot(xyzw[dic[xy[0]]], xyzw[dic[xy[1]]], label=label)
    name=f'{xy}_'+(label if len(paths)==1 else f"{label}+{len(paths)-1}")
    print('name:',name)
    axs.grid()
    axs.legend()
    fig.tight_layout()
    return fig

def show_index(path:str,region:Tuple[float,float]=None,st='z',recalc=False,calcinter=False,millname=None):
    fig, axs = plt.subplots(3, 1,figsize=(14,8))
    ats,(x, y, z, w) = desc(path,recalc=recalc,calcinter=calcinter)
    x,y,z=np.array(x),np.array(y),np.array(z)
    ind=np.array(range(len(w)))
    k=10/ind.max()
    k=(ind*k).astype(int)/k
    label=os.path.splitext(os.path.basename(path))[0]
    millname=millname or ['']*4
    show_attrs(ats,w,label)
    if region is not None:
        w=np.array(w)
        s=np.argwhere(region[0]<w)[0,0]-1
        e=np.argwhere(region[1]<w)[0,0]+1
        x=x[s:e]
        y=y[s:e]
        z=z[s:e]
        w=w[s:e]
        ind=ind[s:e]
        k=k[s:e]
        axs[2].set_ylim(get_lim(min(ind),max(ind)))
        # axs[0].set_ylim(get_lim(-1.5,-0.5))
    
    for v,arr in zip('xyz',[x,y,z]):
        if not v in st:
            continue
        if region is not None:
            if e-s<1000:
                for i in range(e-s-1):
                    axs[0].plot(w[i:i+2],arr[i:i+2])
            else:
                axs[0].plot(w,arr)
        else:
            axs[0].plot(w,arr,label=label)
        
    sp=(x[1:]-x[:-1])**2+(y[1:]-y[:-1])**2+(z[1:]-z[:-1])**2
    sp=sp**0.5/(w[1:]-w[:-1])*60
    sp=np.array([sp,sp]).T.flatten()
    sw=np.array([w,w]).T.flatten()[1:-1]
    axs[1].plot(sw,sp,label='sp')
    
    axs[2].plot(w,ind,label='index')
    axs[2].plot(w,k,label='step10')
    for ax in axs:
        if region is None:
            # ax.set_xlim(*region)
            ax.set_xticks(*make_ticks(w[-1]))
        ax.grid()
        ax.legend()
    name='index_'+label
    print('name:',name)
    fig.tight_layout()
    return fig

def savefig(fig: Figure, dir='imgs/',format='%y%m%d_%H%M%S.%f.png', dpi=150, tight_layout=True):
    name = datetime.datetime.now().strftime(dir+format)
    if not os.path.exists(os.path.dirname(name)):
        os.makedirs(os.path.dirname(name), exist_ok=True)
    if tight_layout:
        fig.tight_layout()
    fig.savefig(name, dpi=dpi)
    return fig

if __name__ == '__main__':
    main()
