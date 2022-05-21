import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import tweepy as tw
from transformers import pipeline
import tensorflow as tf

import plotly.express as px
#from calendar import month_name
import altair as alt

#from MultiApp import MultiApp
#import Homepage_streamlit_App
#import Sales_Dashboard_Analysis_2021
#import Twitter_Sentiment_Analysis_Brand
#import Contact_Form_Streamlit

#PAGES = {
#    "Home": "C:\\Users\\Christian\\Homepage_streamlit_App.py",
#    "SalesDash": "C:\\Users\\Christian\\Sales_Dashboard_Analysis_2021.py",
#    "Proc-App": "C:\\Users\\Christian\\Twitter_Sentiment_Analysis_Brand.py",
#    "Contact Form": "C:\\Users\\Christian\\Contact_Form_Streamlit.py"
#}

#def app():
#    st.title("SalesDash & Proc-App")

st.set_page_config()

# Horizontal menu (icon)
selected = option_menu(
    menu_title= "Main Menu",
    options= ["Home", "SalesDash", "Proc-App", "Contact"],
    icons=["house", "Graph Stats Square", "Layout Dashboard 1", "contact"],
    menu_icon="cast",
    default_index=0,
    orientation= "horizontal",
)

#page = PAGES[selected]
#page.app()

if selected == "Home":
    image = Image.open("sky is the limit.png")

    st.image(image, caption='Surpassing the Boundaries')

    st.subheader("SalesDash helps to explore Boldal Sales Data for Analysis")
    uploaded_file = st.file_uploader('Upload your file here')

#    st.title(f"You have selected {selected}")

if selected == "SalesDash":
#    st.set_page_config(
    page_title="Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
#)

# ---- READ CSV ----
    @st.cache(allow_output_mutation=True)
    def get_data_from_excel():
        df = pd.read_excel("C:\\Users\\Christian\\Sales Report 2021 - final.xlsx")
        df["hour"] = pd.to_datetime((df["Time"]).astype(str)).dt.hour
        return df

    df = get_data_from_excel()

# ---- SIDEBAR ----
    st.sidebar.header("Please Filter Here")
    year_selected = st.sidebar.radio("Select a Year",pd.unique(df["Year"]))

#date_selection = st.sidebar.multiselect('Select a Month',pd.unique(df['Month']))


    product = st.sidebar.selectbox(
        "Select the Product Category",pd.unique(df["ItemGroup"])
)

    type_of_data = st.sidebar.multiselect("Select the Customer Type", pd.unique(df['CATEGORY1']))

    state = st.sidebar.multiselect(
        "Select the State",pd.unique(df["STATE"])
)


    city = st.sidebar.selectbox(
        "Select the City",pd.unique(df["City"])
)

# Link filters to data
    df = df.query(
        "Year == @year_selected & ItemGroup == @product & CATEGORY1 == @type_of_data & STATE == @state & City == @city"
)

# ---- MAINPAGE ----
    st.markdown('''
# :bar_chart: Real-Time Sales Dashboard
''')


 # KPIs
    total_qty = int(df["TotalQtySold"].sum())
    total_gross_sales = round(((df["GrossSales$"]/1000000).sum()),2)
    total_discount = round(((((df["DiscountOfGoodsSold$"]+df['DiscountOfFreeSoldGoods$'])/1000000).sum())),2)
    total_cost = round(((df["TotalSalesCost$"]/1000000).sum()),2)
    gp_perc = round(((df["GROSSROFIT$"].sum())/(df["InvoicedSales$"].sum()))*100,1)

    first_column, second_column, third_column, fourth_column, fifth_column = st.columns(5)
    with first_column:
        st.subheader("Total Quantity Sold")
        st.subheader(f"{total_qty:,}")
    with second_column:
        st.subheader("Total Gross Sales")
        st.subheader(f"US$ {total_gross_sales:,} M")
    with third_column:
        st.subheader("Total Discount")
        st.subheader(f"US$ {total_discount} M")
    with fourth_column:
        st.subheader("Total Cost")
        st.subheader(f"US$ {total_cost} M")
    with fifth_column:
        st.subheader("Gross Profit")
        st.subheader(f"% {gp_perc}")

    st.markdown("""---""")

# Pie Chart For Gross Sales
    pie_sales = px.pie(
        df,
        values="GrossSales$",
        names="Quarter",
        title="<b>Gross Sales by Quarter</b>",
        color="Quarter",
        color_discrete_map={
            'Q1': 'royalblue',
            'Q2': 'darkblue',
            "Q3": "lightblue",
            "Q4": "darkcyan"
    },
        labels={
            "Quarter": "Quarter",
            "GrossSales$": "Gross Sales"
    },
        template="plotly_white")
#st.write(pie_sales)

 # Bar Chart for Customer Type
    df_item = df.groupby(['ItemGroup','Month']).sum().reset_index()
    bar_item = px.bar(
        df_item,
        x="Month",
        y="GROSSROFIT$",
        title="<b>Monthly Gross Profit by Product Category</b>",
        color="ItemGroup",
        color_discrete_map={
            'ADVPROM': 'royalblue',
            'CONSUM': 'darkblue',
            "DELIVERY": "lightblue",
            "GOODS": "darkcyan"
        },
        template="plotly_white",
        barmode="group",
        labels={
            "Month": "Month",
            "ItemGroup": "Product Category"
        },
    )
    bar_item.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )

#st.write(bar_item)

# Sales Customer Category
#df_cust = df.groupby(['Payment', 'CATEGORY1','GrossSales$']).sum().reset_index()
#sales_cust = px.bar(
#    df_cust,
#    x="CATEGORY1",
#    y="GrossSales$",
#    title="<b>Sales by Customer Category per Payment Type</b>",
#    color="Payment",
#    color_discrete_map={
#        'Cash': 'royalblue',
#        'Credit card': 'darkblue'
#    },
#    template="plotly_white",
#    barmode="group",
#    facet_col="CATEGORY1",
#    labels={
#        "CATEGORY1": "Customer Category",
#        "GrossSales$": "Gross Sales",
#    },
#)
#sales_cust.update_layout(
#    plot_bgcolor="rgba(0,0,0,0)",
#    xaxis=(dict(showgrid=False)),
#)

#st.write(sales_cust)

    c1, c2 = st.columns(2)
    c1.plotly_chart(pie_sales, use_container_width=True)
    c2.plotly_chart(bar_item, use_container_width=True)

# Gross Profit per state
    df_state = df.groupby(['Payment', 'STATE']).sum().reset_index()
    sales_state = px.bar(
        df_state,
        x="STATE",
        y="GROSSROFIT$",
        title="<b>Gross Profit per State</b>",
        labels={
            "STATE": "State",
            "GROSSROFIT$": "Gross Profit"
    },
        color="Payment",
        color_discrete_map={
            'Cash': 'royalblue',
            'Credit card': 'darkblue'
    },
        barmode="group",
        template="plotly_white",
)
    sales_state.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False)),
)

#st.write(sales_state)

# Line Chart
#df["Total_Discount"] = df["DiscountOfGoodsSold$"] + df["DiscountOfFreeSoldGoods$"]

#df_hour = df.groupby(["Time", "GrossSales$", "Total_Discount"]).sum().reset_index()
#sales_hour = px.line(
#    df_hour,
#    x="Time",
#    y="GrossSales$", "Total_Discount",
#    title="<b>Gross Sales vs. Total Discount per Hour</b>",
#    color="GrossSales$", "Total_Discount",
#    color_discrete_map={
#        'GrossSales$': 'royalblue',
#        'Total_Discount': 'darkblue'
#    },
#    template="plotly_white"
#)
#sales_hour.update_traces(hoverinfo='text+name', mode='lines+markers')
#sales_hour.update_layout(
#    plot_bgcolor="rgba(0,0,0,0)",
#    xaxis=(dict(showgrid=False)),
#    yaxis=(dict(showgrid=False)),
#)

#line_chart = df_hour(columns = ["GrossSales$", "Total_Discount"])
#plot_hour = st.line_chart(df_hour)
#st.write(line_chart)

#c1, c2 = st.columns(2)
#c1.plotly_chart(sales_state, use_container_width=True)
#c2.plotly_chart(plot_hour, use_container_width=True)

#df_sales_cost = df.groupby(['GrossSales$', 'TotalSalesCost$', "Month"]).sum().reset_index()
#chart_data = df_sales_cost("Month", columns["GrossSales$", "TotalSalesCost$"])
#line_sales_cost = st.linechart(df_sales_cost)
#st.write(line_sales_cost)

#df_sales_cost = df.melt('Month', var_name='name', value_name='value')
#st.write(df)

#chart = alt.Chart(df).mark_line().encode(
#  x=alt.X('Duration:N'),
#  y=alt.Y('value:Q'),
#  color=alt.Color("name:N")
#).properties(title="Hello World")
#st.altair_chart(chart, use_container_width=True)

# SALES BY PRODUCT LINE [BAR CHART]
    sales_by_customer_category = (
        df.groupby(by=["CATEGORY1"]).sum()[["GROSSROFIT$"]].sort_values(by="GROSSROFIT$")
)
    fig_col3 = px.bar(
        sales_by_customer_category,
        x="GROSSROFIT$",
        y=sales_by_customer_category.index,
        orientation="h",
        title="<b>Sales by Customer Category</b>",
        color_discrete_sequence=["#4169e1"] * len(sales_by_customer_category),
        template="plotly_white",
)
    fig_col3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
)

#st.write(fig_col3)

    c3, c4 = st.columns(2)
    c3.plotly_chart(sales_state, use_container_width=True)
    c4.plotly_chart(fig_col3, use_container_width=True)


#######################################################
#######################################################
#chart_data = df(["Month"], df[['GrossSales$', "TotalSalesCost$"]])

#a = alt.Chart(df).mark_area(opacity=1).encode(
#    x='Month', y='GrossSales$')

#b = alt.Chart(df).mark_area(opacity=0.6).encode(
#    x='Month', y='TotalSalesCost$')

#c = alt.layer(a, b)

#sales_cost = st.altair_chart(c, use_container_width=True)
#st.write(sales_cost)

# Pie Chart For Product Category
    pie_cost = px.pie(
        df,
        values="TotalSalesCost$",
        names="Quarter",
        title="<b>Cost by Product Category</b>",
        color="Quarter",
        color_discrete_map={
            'Q1': 'royalblue',
            'Q2': 'darkblue',
            "Q3": "lightblue",
            "Q4": "darkcyan"
    },
        labels={
            "Quarter": "Quarter",
            "TotalCostSales$": "Cost"
    },
        template="plotly_white")
#st.write(pie_cost)

# SALES BY SalesRep
    sales_by_salesrep = (
        df.groupby(by=["Salesrep"]).sum()[["GrossSales$"]].sort_values(by="GrossSales$")
)
    fig_col6 = px.bar(
        sales_by_salesrep,
        x="GrossSales$",
        y=sales_by_salesrep.index,
        orientation="h",
        title="<b>Sales by Sales Rep</b>",
        color_discrete_sequence=["#00b6cc"] * len(sales_by_salesrep),
        template="plotly_white",
)
    fig_col6.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
)


    c5, c6 = st.columns(2)
    c5.plotly_chart(pie_cost, use_container_width=True)
    c6.plotly_chart(fig_col6, use_container_width=True)
#    st.title(f"You have selected {selected}")
#if selected == "Brand Procurement App":
#    st.title(f"You have selected {selected}")
#if selected == "Contact":
#    st.title(f"You have selected {selected}")


if selected == "Proc-App":
    # Get authorization to extract tweets
    consumer_key = 'zxQklJv949O0M58c90mH0OdZR'
    consumer_secret = 'eSjGZX7Z6gVrnq7MFXDTz29n73J4C8fgsxLKgZOo7bngUwMs3a'
    access_token = '1157400281094774785-Q41eNXVxH2RIFQwWCAqhXZRK2qmDTp'
    access_token_secret = 'fWhXOYPjZx2p5YqltKjIWCixiZOY36R20uJZGlnWG9lKQ'
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)

# define sentiment analysis using pipeline of hugging face transformers
    classifier = pipeline('sentiment-analysis')
    st.title('Branding Procurement based on Sentiment Analysis of Tweets')
    st.header("Changing the Face of Retail Brand Procurement")
    st.subheader('Advanced approach to help procurement process to get in shape for the future')
    st.markdown('A tool that surpasses the traditional branding procurement, by deriving the latest tweets from Twitter along with its corresponding Sentiment Analysis based on what is included in the below box.')

# Create the app
    def run():
        with st.form(key='Enter name'):
            search_words = st.text_input('Enter the Brand name for which you want to know the tendency')
            number_of_tweets = st.number_input('Enter the number of latest tweets for which you want to know the sentiment (Max 50 tweets)', 0,50,10)
            submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                tweets =tw.Cursor(api.search_tweets,q=search_words,lang="en").items(number_of_tweets)
                tweet_list = [i.text for i in tweets]
                p = [i for i in classifier(tweet_list)]
                q=[p[i]['label'] for i in range(len(p))]
                df = pd.DataFrame(list(zip(tweet_list, q)),columns =['Latest '+str(number_of_tweets)+' Tweets'+' on '+search_words, 'sentiment'])
                st.write(df)

    if __name__=="__main__":
            run()

if selected == "Contact":
    st.header(":mailbox: Get in Touch with Me!")

    contact_form = """
    <form action ="https://formsubmit.co/codingisfun.com.testuser@gmail.com" method ="POST">
    <input type="hidden" name="_captcha" value="false>
    <input type="text" name="text" placeholder="Your name" required>
    <input type="email" name="email" placeholder="Your email" required>
    <textarea name="message" placeholder="Details of your inquiry"></textarea>
    <button type="submit">Send</button>
</form>
"""

    st.markdown(contact_form, unsafe_allow_html=True)

# Use local CSS file
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("Contact_Form_Style.txt")



