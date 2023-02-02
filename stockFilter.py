import pandas as pd 
import streamlit as st
import plotly.express as px
import yfinance as yf
from datetime import datetime

#get data from excel file and tidy it up
df = pd.read_excel('Stock Financial Information.xlsx')
df.index = df.iloc[:,0]
df.drop(df.columns[0], axis=1, inplace = True)

#get list of stock names
stocks = df.columns.values.tolist()

#create and display the filters
st.set_page_config(layout = "wide")
st.header("**Stock Filter App**")
st.header("Choose Restrictions")
margins = [0.1,0.2,0.3,0.4,0.5,0.6]
EBITDA = [100,50,25,15,10,5]
profit_margins = [0.05,0.1,0.15,0.2,0.25]
Revenue = [50,25,15,10,5,2]

col1, col2 = st.columns(2)

with col1:
    gross_margin_choice = st.selectbox("Stocks with gross margin greater than",margins)
    Profit_margin_choice = st.selectbox("Stocks with profit margin greater than",profit_margins)
with col2:
    EV_EBITDA_choice = st.selectbox("Stocks with EV / EBITDA less than",EBITDA)
    EV_Revenue_Choice = st.selectbox("Stocks with EV / Revenue less than",Revenue)
    
st.header("Filtered Stocks")

#filter the tavle (transposing it first to make filtering easier)
filtered_df = df.T
filtered_df = filtered_df.loc[filtered_df['grossMargins']>gross_margin_choice]
filtered_df = filtered_df.loc[filtered_df['profitMargins']>Profit_margin_choice]
filtered_df = filtered_df.loc[filtered_df['enterpriseToEbitda']<EV_EBITDA_choice]
filtered_df = filtered_df.loc[filtered_df['enterpriseToRevenue']<EV_Revenue_Choice]
filtered_df = filtered_df.T
st.table(filtered_df)

#display filtered stocks
st.header("Display Stock Data")

#get historical data for the chosen stock
stock = st.selectbox("Filtered Stocks",stocks)
stockInfo = yf.download(stock,"2015-01-01","2023-01-01")
stockInfo["Open"]= stockInfo.index
stockInfo.rename(columns={'Open':'Date','Adj Close':'value'},inplace=True)

#get comps data for the chosen stock
compStocks = []
for newStock in df.columns:
    if df[stock].loc['sector'] == df[newStock].loc['sector']:
        compStocks.append(float(df[newStock].loc['enterpriseToEbitda']))
    
    
#make plots with historical / comps data
fig1 = px.line(stockInfo,x="Date",y="value",title= stock+ ' Stock Price Chart')
fig1['data'][0]['showlegend']=True
fig1['data'][0]['name']='Adj Close'
fig2 = px.box(pd.Series(compStocks)).update_layout(yaxis_title="Comps Set EV / EBITDA", xaxis_title="Comparable Company Analysis")

#display plots
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig1,use_container_width = True)
    
with col4:
    st.plotly_chart(fig2,use_container_width = True)
    
#get data for Recent Analyst Recommendations, and tidy it up
stockInfo2 = yf.Ticker(stock)
df2 = stockInfo2.recommendations
df2 = df2.iloc[::-1]
df2.reset_index(inplace=True)
df2 = df2.drop_duplicates(subset=['Firm'])
df2.reset_index(inplace=True)
df2.drop(columns=['From Grade','Action','index'],inplace=True)
cols = ["Firm","To Grade","Date"]
df2 = df2[cols]
df2.rename(columns={'To Grade':'Grade'},inplace=True)
df2["DateStr"] = ''
for index,row in df2.iterrows():
    time = df2.iloc[index,2]
    dt_obj = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S') 
    df2.at[index,"DateStr"] = dt_obj.strftime('%m/%d/%y')
df2.set_index('Firm',inplace=True)
df2.drop(columns={'Date'},inplace=True)
df2.rename(columns={'DateStr':'Date'},inplace=True)

#display recent analyist recommendations
st.header("Recent Analyst Recommendations")
st.table(df2)
