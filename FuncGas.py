import xloil as xlo
import pandas as pd
import numpy as np
from xloil import StatusBar
import xloil.matplotlib
import matplotlib.pyplot as plt
import sqlite3
import os


filename = os.path.abspath(__file__)
dbdir = filename.rstrip('FuncGas.py')
dbpath = os.path.join(dbdir, "gasoil2124.db")


@xlo.func
def detail_gas(mtcl,flipswitch = 0):

    conn = sqlite3.connect(dbpath)
    predata = pd.read_sql_query("SELECT * from gasdata WHERE Engin= ?",con=conn,params=(mtcl,))
    predata['date']=pd.to_datetime(predata['date'])
    data = predata[predata['cons_per_unit']>1]
    conn.close()
    
    if flipswitch > 0 :
        return predata
    else :
        return data


@xlo.func
def recap_gas(mtcl,flipswitch = 0):
    with StatusBar(1000) as status:
        status.msg('Khdam daba')
        data = detail_gas(mtcl, flipswitch)
        sub_data = data[['QteS','Compteur','cons_per_unit']]
        status.msg('Salina')
        return sub_data.describe(percentiles=[.25, .5, .75])
        


@xlo.func
def moy_gas(mtcl, flipswitch = 0):
    data = detail_gas(mtcl, flipswitch)
    return data['cons_per_unit'].mean()


@xlo.func
def quantile_gas(mtcl,quant, flipswitch = 0):
    data = detail_gas(mtcl, flipswitch)
    return data['cons_per_unit'].quantile(quant)



@xlo.func
def box_gas(mtcl, flipswitch = 0):
    data = detail_gas(mtcl, flipswitch)
    cons = data['cons_per_unit']
    
    fig, ax = plt.subplots(layout="constrained")
    fig.set_size_inches(5,3)
    fig.suptitle(f'Boxplot de {mtcl} ({cons.count()} pts)')
    
    
    ax.set_title(f'Consomation moyenne = {round(cons.mean(),2)}',color='blue', fontsize = 10)
    ax.boxplot(x=cons,sym='k+', vert = False, showmeans = True, labels=[mtcl])
    
    quantiles = np.quantile(cons, np.array([0.00, 0.25, 0.50, 0.75, 1.00]))
    quantiles = np.around(quantiles, decimals=2)
    ax.vlines(quantiles, [0] * quantiles.size, [1] * quantiles.size,
          color='b', ls=':', lw=0.5, zorder=0)
    ax.set_ylim(0.5, 1.5)
    ax.set_xticks(ticks=quantiles,labels = quantiles, rotation=30)
    
    return fig



import seaborn as sns

@xlo.func(macro = True)
def kde_gas(mtcl, flipswitch = 0):
    data = detail_gas(mtcl, flipswitch)
    
    fig = plt.figure(figsize=(5,3), layout='tight')
    fig.suptitle(f'Kdeplot de {mtcl}')
    sns.kdeplot(data = data, x='cons_per_unit' , fill=True)
    return fig

@xlo.func(macro = True)
def tserie_gas(mtcl, flipswitch = 0):
    data = detail_gas(mtcl, flipswitch)
    
    fig = plt.figure(figsize=(10,3), layout='tight')
    fig.suptitle(f'conso time series de {mtcl}')
    sns.lineplot(data = data, x='date' , y='cons_per_unit', c="green")
    return fig

