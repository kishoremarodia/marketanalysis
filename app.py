# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 22:01:53 2021

@author: kmarodia
"""

import streamlit as st
from pynse import *
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.express as pe
import pandas as pd


nse=Nse()

# Function to display historical delivery data for a stock
def stock_delivery_data():
    with st.sidebar:
        symbol = st.selectbox("Select symbol",nse.symbols[IndexSymbol.All.name])
        from_date = st.date_input("From Date",datetime.date.today()-datetime.timedelta(30))
        to_date = st.date_input("To Date",datetime.date.today()) 
    
    trading_days = nse.get_hist(from_date=from_date,to_date=to_date).index
    trading_days = list(trading_days.map(lambda x:x.date()))
    data = pd.DataFrame()
    
    for date in trading_days:
        try:
            bhav = nse.bhavcopy(date).loc[symbol]
            bhav.set_index("DATE1",inplace=True)
            data = data.append(bhav)
        except Exception as e:
            print(f"error {e} for date {date}")
    
    data = data.astype(float)
    data.index=data.index.map(pd.to_datetime)
    data = data [["OPEN_PRICE","HIGH_PRICE","LOW_PRICE","CLOSE_PRICE","TTL_TRD_QNTY","DELIV_QTY","DELIV_PER"]]
    
    
    data.columns = "open high low close volume deliv_qty deliv_per".split()
    
    # candle stick
    deliv_data = [mpf.make_addplot(data["deliv_per"], panel=2,ylabel="deliv %")]
    fig, ax = mpf.plot(
        data,
        addplot=deliv_data,
        type="candle",
        style="yahoo",
        volume=True,
        returnfig=True,
        title=f'{symbol} Delivery%',
        figratio=(16,7),
        figscale=1.2
        )
    
     
    st.write(fig)
    st.write(data)
                 
# Function to display high low delivery % of stocks in a given index for a given date
def high_low_delivery():
    with st.sidebar:
        req_date = st.date_input("From Date",datetime.date.today())
        sort_by=st.radio("Sort by",["Highest","Lowest"])
        index_name = st.selectbox("Index",[i.name for i in IndexSymbol])
        no_of_stocks = st.number_input("No of stocks",value=10,step=1)
        
    req_date = None if req_date >= datetime.date.today() else req_date
    
    bhavcopy = nse.bhavcopy(req_date)
    
    bhavcopy = bhavcopy.reset_index(level=1) #remove series as multi index and flatten
    
    bhavcopy = bhavcopy[
        [
            "OPEN_PRICE",
            "HIGH_PRICE",
            "LOW_PRICE",
            "CLOSE_PRICE",
            "TTL_TRD_QNTY",
            "DELIV_QTY",
            "DELIV_PER",
        ]
    ]
    
    bhavcopy["DELIV_QTY_IVR"]=0
    #Calculate Delivery IVRs
    for rec in bhavcopy.iterrows():
        try:
            rec_data = nse.get_hist(symbol=rec.index,from_date=to_date - timedelta(365),to_date=to_date)
            deliv_qty_min = rec_data["deliv_qty"].min()
            deliv_qty_max = rec_data["deliv_qty"].max()
            rec["DELIV_QTY_IVR"] =100*(rec_data["deliv_qty"] - deliv_qty_min) / (deliv_qty_max - deliv_qty_min)
        except Exception as e:
            print(f"error {e} ")

        

     
    bhavcopy = bhavcopy.sort_values("DELIV_QTY_IVR", ascending=True if sort_by=="Lowest" else False)
    
      
    
    
    bhavcopy = bhavcopy[bhavcopy.index.isin(nse.symbols[index_name])]
    
    st.write(bhavcopy)
    

# Function to display bhavcopy for selected Date and Segment and also enable download
def bhavcopy_display():
    with st.sidebar:
        st.write('Bhavcopy Inputs')
        req_date = st.date_input('Select date',datetime.date.today())
        segment = st.selectbox('Select Segement',['Cash','FnO'])
        
    req_date = None if req_date >= datetime.date.today() else req_date
    
    if segment == "Cash":
        bhavcopy = nse.bhavcopy(req_date)
    else:
        bhavcopy = nse.bhavcopy_fno(req_date)
    
    st.write(f'{segment} bhavcopy for date {req_date}')
    st.download_button("Download",bhavcopy.to_csv(),file_name=f'{segment}_bhav_{req_date}.csv')
    st.write(bhavcopy)

# Function to display beta for a portfolio of stocks
def portfolio_beta():
    st.write('Portfolio Beta')
    pf_file = st.file_uploader("Upload PF")
    if pf_file is not None:
        pf_df = pd.read_csv(pf_file)
        st.write(pf_df)
        st.write("---")
        req_date = datetime.date.today()
        beta=[]
        
        for rec in pf_df.itertuples():
            rec_data = nse.get_hist(rec[1],from_date=req_date - datetime.timedelta(365),to_date=req_date)
            # Get nifty data from NIFTY BEES, later plan to change it to NIFTY
           
            rec_index_data = nse.get_hist('NIFTY 50',from_date=req_date - datetime.timedelta(365),to_date=req_date)
            # Get % change
            rec_data['pct_change'] = rec_data['close'].pct_change().fillna(0)
            rec_index_data['pct_change'] = rec_index_data['Close'].pct_change().fillna(0)
            #pd.DataFrame(rec_data['pct_change'],rec_index_data['pct_change']).to_clipboard(sep=",")
            
            beta.append(rec_data['pct_change'].cov(rec_index_data['pct_change']) / rec_index_data['pct_change'].var())
        
            
        pf_df['BETA']=pd.Series(data=beta)
        
        ltp=[]
        for rec in pf_df.itertuples():
            hist = nse.get_hist(rec[1],from_date=req_date,to_date=req_date)
            st.write(hist)
            ltp.append(hist['close'])
            
        pf_df['LTP']=pd.Series(data=ltp)
        pf_df['LTP']=pf_df['LTP'].astype(float)
               
        
        st.write(pf_df)
        pf_beta = ( pf_df['BETA'] * pf_df['QTY'] * pf_df['LTP'] ).sum() / ( (pf_df['QTY'] * pf_df['LTP']).sum() )
        st.write("Portfolio Beta")
        st.write(pf_beta)
        
    
    
        
    



# creating a dict with keys to display and run the selected function of the key
analysis_dict = {"Bhavcopy":bhavcopy_display,"Stock Delivery":stock_delivery_data,"High Low Delivery":high_low_delivery,"PF Beta":portfolio_beta}


# Give radio options to enable a kind of analysis
with st.sidebar:
    selected_analysis = st.radio("Select Analysis",analysis_dict.keys())
    st.write("---")

# Write the Kind of Analysis being done as header
st.header(selected_analysis)

# Call the selected analysis and
analysis_dict[selected_analysis]()
        
    
