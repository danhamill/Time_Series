# -*- coding: utf-8 -*-
"""
Created on Fri Sep 08 12:46:44 2017

@author: dan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform
import os
from matplotlib import dates

def format_xaxis(fig):
     years = dates.YearLocator(10,month=1,day=1)
     years1=dates.YearLocator(2,month=1,day=1)
     dfmt = dates.DateFormatter('%Y')
     dfmt1 = dates.DateFormatter('%y')
    
     [i.xaxis.set_major_locator(years) for i in fig.axes]
     [i.xaxis.set_minor_locator(years1) for i in fig.axes]
     [i.xaxis.set_major_formatter(dfmt) for i in fig.axes]
     [i.xaxis.set_minor_formatter(dfmt1) for i in fig.axes]
     [i.get_xaxis().set_tick_params(which='major', pad=15) for i in fig.axes]
    
     for t in fig.axes:
         for tick in t.xaxis.get_major_ticks():
             tick.label1.set_horizontalalignment('center')
         for label in t.get_xmajorticklabels() :
             label.set_rotation(0)
             label.set_weight('bold')
         for label in t.xaxis.get_minorticklabels():
             label.set_fontsize('small')
         for label in t.xaxis.get_minorticklabels()[::5]:
             label.set_visible(False)
             
             
def std_err_calc(df,metric):
        mc_std = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc=np.std)
        mc_std = mc_std.rename(columns={metric:'std_dev'})
        mc_count = pd.pivot_table(df, values=[metric], index=['TripDate'], aggfunc='count')
        mc_count = mc_count.rename(columns={metric:'count'})    
        return mc_std.std_dev/np.sqrt(mc_count['count'])
    
def add_vlines(fig):
    hfe_dates = [pd.datetime(1996,4,1),pd.datetime(2004,11,22),pd.datetime(2008,3,8),pd.datetime(2012,11,20),pd.datetime(2013,11,11),pd.datetime(2014,11,11)]
    other_flow = [pd.datetime(1997,11,1),pd.datetime(2000,4,1),pd.datetime(2000,11,1)]
    for i in fig.axes:
        for d in hfe_dates:
            i.axvline(d,color='k',linestyle='-',zorder=1)
        for d in other_flow:
            i.axvline(d,color='k',linestyle='--',zorder=1)
    [i.set_xlim(pd.datetime(1990,01,01), pd.datetime(2018,01,01)) for i in fig.axes]

def excel_group(writer,tmp1,group):
    tmp1.to_excel(writer,sheet_name=group,startcol=0,index=False)
    
def plot_metrics(subset,canyon,r,n,m,m_size,ls,fig,writer):
    subset.loc[:,'Norm_Area']=subset.loc[:,'Area_2D']/subset.loc[:,'Max_Area']
    subset.loc[:,'Norm_Vol'] = subset.loc[:,'Volume']/subset.loc[:,'MaxVol']


    #average normalized metrics for plotting
    tmp1 = pd.pivot_table(subset, index=['TripDate'], values=['Norm_Vol','Norm_Area'],aggfunc=[np.average,len]).reset_index()
    tmp1 = tmp1.ix[:,0:-1]
    tmp1.columns = tmp1.columns.droplevel(0)
    tmp1.columns=['TripDate','Norm_Area','Norm_Vol','N']
    #Volume Plot
    tmp1.plot(x='TripDate',y='Norm_Vol', yerr=std_err_calc(subset,'Norm_Vol'),ax=fig.axes[1],label=r[n]+': ' +canyon,marker=m[n],capsize=2,zorder=10,ms=m_size,c=colors[n],linestyle=ls[n],sharex=fig.axes[1])
    tmp1.plot(x='TripDate',y='Norm_Area', yerr=std_err_calc(subset,'Norm_Area'),marker=m[n],ax=fig.axes[0],label=r[n]+': ' +canyon,capsize=2,zorder=10,ms=m_size,c=colors[n],linestyle=ls[n])
    excel_group(writer,tmp1,canyon)

if __name__ =='__main__':
    
    if platform.system() == 'Darwin':
        sandbar_root = '/Users/danielhamill/git_clones/sandbar_process'
        time_root = '/Users/danielhamill/git_clones/Time_Series'
        out_root = time_root + os.sep + 'Output/Joes_figs'
    elif platform.system() == 'Windows':
        sandbar_root = r'C:\workspace\sandbar_process'
        time_root = r'C:\workspace\Time_Series'
        out_root = time_root + os.sep + r'Output\Joes_figs'

    
    
    #designate groups       
    g_1a = np.array(['145l','022r','213l','084r','030r','081l','137l','119r','122r'])
    g_1b = np.array(['009l','123l','172l','044l','045l','044l','183r','220r','050r','065r','047r'])
    g_1c = np.array(['070r','194l','068r','051l','055r'])

    group1 = np.append(g_1a,g_1b)
    group1 = np.append(group1, g_1c)
    
    
    data_file = sandbar_root + os.sep + 'Merged_Sandbar_data.csv'
    data = pd.read_csv(data_file, sep =',')
    
    data['TripDate'] = pd.to_datetime(data['TripDate'], format='%Y-%m-%d')

    data = data[(data.Time_Series == 'long') & (data.SitePart == 'Eddy')] 
    
    fig , (ax_0,ax_1) = plt.subplots(figsize=(7.5,6),nrows=2,sharex=True)
    r=['Group 1','Group 1','Group 1','Group 1','Group 1','Group 1']
    n=0
    m = ['o','x','d','^','*','s']
    m_size=4
    ls = ['-','--','-.',':','-','--']
    colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c']
    writer = pd.ExcelWriter(out_root + os.sep + "spagetti_plots" + os.sep +'Group1_norm_eddyabv8kdata_mergeMaxArea.xlsx',engine='xlsxwriter')
    
    
    subset = data[data['Site'].isin(group1)]
    #Find Common dates
    subset = subset[subset.Plane_Height != 'eddyminto8k']     
    date_fz = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddy8kto25k') ].SurveyDate.unique()
    date_he = subset[(subset['Volume']>0) & (subset['Plane_Height'] == 'eddyabove25k') ].SurveyDate.unique()
    common_dates = np.intersect1d(date_fz,date_he)
    subset = subset[subset['SurveyDate'].isin(common_dates)]
    
    #calculate above 8k metrics
    subset =  pd.pivot_table(subset,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Area_2D','Area_3D','Volume','Errors','MaxVol'],aggfunc=np.sum).reset_index()
    subset1 = data[data['Site'].isin(group1)]
    
    subset1 = pd.pivot_table(subset1,index=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],values=['Max_Area'],aggfunc=np.average).reset_index()
    subset = subset.merge(subset1, on=['Site','SurveyDate','SitePart','TripDate','SiteRange','Segment','Bar_type','Time_Series','Period'],how='left')
    del subset1
    
    mc_query = 'Segment == ["1_UMC","2_LMC"]'
    gc_query = 'Segment != ["1_UMC","2_LMC"]'
    
    #MC
    mc = subset.query(mc_query)
    gc = subset.query(gc_query)
    
    plot_metrics(mc,"Marble Canyon",r,n,m,m_size,ls,fig,writer)
    plot_metrics(gc,"Grand Canyon",r,n+1,m,m_size,ls,fig,writer)

        
    [i.legend_.remove() for i in fig.axes]
    fig.axes[1].set_xlabel('DATE')
    
    add_vlines(fig)

    fig.legend(handles = ax_1.get_legend_handles_labels()[0], labels=ax_1.get_legend_handles_labels()[1], loc = 'lower center', bbox_to_anchor = (0,0.005,1,1),
            bbox_transform = fig.transFigure,ncol=3)

    
    #Format Axis Options
    format_xaxis(fig)

    fig.axes[0].set_ylabel('NORMALIZED AREA')
    fig.axes[1].set_ylabel('NORMALIZED VOLUME')

    fig.axes[0].set_ylim(0,0.8)
    fig.axes[1].set_ylim(0,0.8)
    [i.tight_layout() for i in [fig]]
    [i.subplots_adjust(bottom=0.18) for i in [fig]] 
    writer.save()
    fig.savefig(out_root + os.sep +'spagetti_plots'+os.sep +'Group1_norm_vol_plot_mergeMaxArea.png')

    