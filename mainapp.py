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


nse=Nse()



# Function to display historical delivery date for a stock
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

def high_low_deliv():
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
     
    bhavcopy = bhavcopy.sort_values("DELIV_PER", ascending=True if sort_by=="Lowest" else False)
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

# creating a dict with keys to display and run the selected function of the key
analysis_dict = {"Bhavcopy":bhavcopy_display,"Delivery":stock_delivery_data,"High Low Delivery":high_low_deliv}


# Give radio options to enable a kind of analysis
with st.sidebar:
    selected_analysis = st.radio("Select Analysis",analysis_dict.keys())
    st.write("---")

# Write the Kind of Analysis being done as header
st.header(selected_analysis)

# Call the selected analysis
analysis_dict[selected_analysis]()
        
    
