import xloil as xlo
import pandas as pd
from xloil.pandas import PDFrame
import numpy as np
from itertools import groupby
from operator import itemgetter
from num2words import num2words
import portion as por

import xloil.matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


from datetime import datetime

#UTILITY FUNCTIONS
#F1 : Digits to letters
@xlo.func
def chiffre_en_lettre(chiffre : float,langu ='fr') -> str:
    return num2words(chiffre,lang=langu)

#F2 : Correct date conversion from excel
def serialDateToDatetime(DateCol):
    epoch = pd.Timestamp('1899-12-30')
    return pd.to_datetime(DateCol, unit='D', origin=epoch)

#F3 : Transform a range to dataframe with given headins and specifiy date column
@xlo.func
def TO_DF_HEADINGS(data, name_of_date_col: str = None) -> xlo.Cache:
    df = pd.DataFrame(data[1:], columns=data[0])
    if name_of_date_col is not None:
        df[name_of_date_col] = serialDateToDatetime(df[name_of_date_col]
                                                    .astype(int))
    return df

# Interval class
class Interv:
    def __init__(self, start, end, serial=0, ol_score=0) -> None:
        self.start = start
        self.end = end
        self.serial = serial
        self.ol_score = ol_score

    def return_as_tuple(self):
        st = self.start, 's', self.serial
        ed = self.end, 'e', self.serial
        return [st, ed]

    def __str__(self) -> str:
        return f'Interval [{self.start},{self.end}], Id={self.serial}, overlap score = {self.ol_score}'

#F4 : find overlaps in different intervals based on a scoring system
@xlo.func
def IntOverlap(int_range) -> PDFrame:
    arr = []
    for row in int_range:
        arr.append(Interv(row[0], row[1]))

    # Joining the end points of all intervals in one list of tuples
    Ls = []
    i = 0
    for ir in arr:
        ir.serial = i
        Ls = Ls + ir.return_as_tuple()
        i += 1
    Ls = sorted(Ls)

    scounter, ecounter = 0, 0
    idx = []
    for itm in Ls:

        # Tracking is it's a start or an end of an interval
        if itm[1] == 's':
            scounter += 1
        else:
            ecounter += 1
        idx += [(itm[2], scounter - ecounter)]

    ol_index = [(x, sum(map(itemgetter(1), y))) for x, y in groupby(sorted(idx), itemgetter(0))]
    todf = []
    for ir in arr:
        ir.ol_score = ol_index[ir.serial][1]
        todf += [(ir.start, ir.end, ir.ol_score)]
    df = pd.DataFrame(todf, columns=['Start', 'End', 'Overlap_Score'])
    df.sort_values(by=['Start'], inplace=True)
    return df

#F5 Sample function with argument help
@xlo.func(args={'arr': 'Array to be squared'},
          name='SQUARE',
          help='Returns the square of an array')
def square(arr):
    return arr * arr

# Divisiblity by 2
@xlo.func(args={'num': 'Number to be tested'},
          name='DIVBY2',
          help='Returns the number')
def divby2(num):
    tst = num
    while tst % 2 == 0 :
        tst = tst // 2
    return tst


#F6 function to merge intervals
# Python program to merge overlapping Intervals in
# O(n Log n) time and O(1) extra space
@xlo.func
def mergeIntervals(arr):
    
    arr = arr.tolist()
	# Sorting based on the increasing order
	# of the start intervals
    arr.sort(key=lambda x: x[0])

	# Stores index of last element
	# in output array (modified arr[])
    index = 0


	# Traverse all input Intervals starting from
	# second interval
    L=[]
    for i in range(1, len(arr)):
        if (arr[index][1] >= arr[i][0]):
            arr[index][1] = max(arr[index][1], arr[i][1])
            L.append(arr[index])
            
        else:
            index = index + 1
            arr[index] = arr[i]
            L.append(arr[index])
    return np.unique(L, axis=0)


#F7 unite intervals
#union of intervals with help from the portion library 
#recursive recUne and a conversion function     
def recUne(arr):
    if len(arr) == 0 :
        return por.empty()
    else :
        intr = por.closed(arr[0][0],arr[0][1])
        
        return intr | recUne(np.delete(arr, 0, 0))
  
  
#F8 difference between intervals 
def recDiff(basearr,arr):

       baseintr = por.closed(basearr[0,0],basearr[0,1]) 
       for item in arr : 
           intr =   por.closed(item[0],item[1])
           baseintr = baseintr - intr
       return baseintr

@xlo.func
def InterUne(intervals):
    return [(x[1],x[2]) for x in por.to_data(recUne(intervals))]
        
@xlo.func
def InterDiff(baseint,intervals):
    return [(x[1],x[2]) for x in por.to_data(recDiff(baseint,intervals))]
        

#F9 function to plot figures 
@xlo.func(macro=True)
def pyTestPlot(x, y):
    fig, ax = plt.subplots()
    fig.set_size_inches(5,3)
    ax.plot(x, y)
    plt.xticks(rotation=20)
    ax.legend(title='Fruit color')
    return fig

#F10 function to plot figures
#with time series
@xlo.func(macro=True)
def pyTestPlot_date(dt: xlo.Array(int), y,hues,baseline):
    x= serialDateToDatetime(dt)
    c = np.random.randint(1, 5, size=100)
    plt.rcParams['figure.dpi'] = 100
    
    fig, ax = plt.subplots()
    fig.set_size_inches(8,5)
    fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=plt.colormaps["plasma"]),
             ax=ax, label="Tonnages")
    
    # Remove splines. Can be done one at a time or can slice with a list.
    ax.spines[['top','right']].set_visible(False)
    
    ax.axhline(baseline, color ='Red',linestyle = 'dashed')
    ax.scatter(x, y, c=hues,cmap = 'plasma')
    
    ax.plot([0.06, 0.82],[1.0, 1.0],transform=fig.transFigure,
            clip_on=False, color='#040273', linewidth=.6)
    ax.add_patch(plt.Rectangle((0.06,1),0.1,-0.02, facecolor='#040273', 
                               transform=fig.transFigure, clip_on=False, linewidth = 0))
    
    # Add in title and subtitle
    ax.text(x=0.06, y=.94, s="Enrobés etalés", transform=fig.transFigure,
            ha='left', fontsize=13, weight='bold', alpha=.8)
    ax.text(x=0.06, y=.905, s="Répartition de la mise en oeuvre par PK", 
            transform=fig.transFigure, ha='left', fontsize=11, alpha=.8)
    
    plt.grid(axis = 'y')
    plt.xticks(rotation=20)
    ax.legend(title='Total enrobés journalier')
    return fig


#F10 function to plot figures
#with time series
@xlo.func(macro=True)
def pyTestPlot_line(x, y):
    
    fig, ax = plt.subplots()
    fig.set_size_inches(8,5)
    middle = np.max(y)/2
    
    
    ax.axhline(middle, color ='Red',linestyle = 'dashed')
    ax.plot(x, y, color='black')
    plt.xticks(rotation=20)
    ax.legend(title='Production cummulée')
    return fig

import sqlite3
import os
#Playing with sqlite3 dbs
@xlo.func
def MATERIEL_MOJA(mtcl):
    
    filename = os.path.abspath(__file__)
    dbdir = filename.rstrip('TestMod.py')
    dbpath = os.path.join(dbdir, "bareme.db")

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("SELECT cat,unite,cout FROM mat WHERE mtcl= ?",(mtcl,))
    ret  = c.fetchall()
    conn.commit()
    conn.close()
    return ret