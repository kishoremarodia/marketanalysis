from pynse import *
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.express as pe


nse=Nse()


# Function to display historical delivery date for a stock
def stock_delivery_data_new(symbol,from_date,to_date):
    from_date = to_date -datetime.timedelta(365)
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
    
    deliv_qty_min = data["deliv_qty"].min()
    deliv_qty_max = data["deliv_qty"].max()
    
    from_date = to_date -datetime.timedelta(30)
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
    data["deliv_qty_ivr"] =100*(data["deliv_qty"] - deliv_qty_min) / (deliv_qty_max - deliv_qty_min)
    data.to_clipboard(sep=",")
    
    
    '''
    # candle stick
    deliv_data = [mpf.make_addplot(data["deliv_qty_zscore"], panel=2,ylabel="deliv %")]
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
    '''

def high_low_delivery(from_date,to_date):
    req_date = datetime.date.today() - datetime.timedelta(2)
    index_name = "Nifty50"
    no_of_stocks = 10
        
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
            rec_data = nse.get_hist(symbol='NIFTYBEES',from_date=req_date - datetime.timedelta(365),to_date=req_date)
            rec_data['pct_change'] = rec_data['close'].pct_change().fillna(0)
            DELIV_QTY_MIN = rec_data["DELIV_QTY"].min()
            DELIV_QTY_MAX = rec_data["DELIV_QTY"].max()
            rec["DELIV_QTY_IVR"] =100*(rec_data["dDELIV_QTY"] - DELIV_QTY_MIN) / (deliv_qty_max - DELIV_QTY_MAX)
        except Exception as e:
            print(f"error {e} ")

    bhavcopy = bhavcopy.sort_values("DELIV_QTY_IVR", ascending=False)
    bhavcopy = bhavcopy[bhavcopy.index.isin(nse.symbols[index_name])]
    
    bhavcopy.to_clipboard(sep=",")
    


#stock_delivery_data_new('SBIN',datetime.date(2021,11,3),datetime.date(2021,11,3))
high_low_delivery(datetime.date(2021,11,10),datetime.date(2021,11,10))
