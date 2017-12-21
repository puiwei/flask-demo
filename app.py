from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import datetime
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, save, output_file
from bokeh.palettes import Spectral4 as palette
from bokeh.models import SingleIntervalTicker, LinearAxis, DaysTicker
from math import pi

# As all static files get cached, and Bokeh by default outputs a static file, hence bgraph.html is cached
# To work around this, sub-classing the Flask main class to set cache timeout time to 1 sec for bgraph.html so that it would load a new page
class MyFlask(Flask):
    def get_send_file_max_age(self, filename):
        if (filename == "bgraph.html"):
            return 1;
        return Flask.get_send_file_max_age(self, filename)

app = MyFlask(__name__)

# default home page
@app.route('/')
def index():
    return render_template('index.html')

# when /ticker REST URL is evoked, return graph.html with value
@app.route('/ticker', methods=['GET','POST'])
def ticker():
    if request.method == 'POST':
        symbol= request.form['symbol']
        checklist = []
        # get list of checked boxes
        checklist += [check for check in [request.form.get('Close'), request.form.get('Adj_Close'), request.form.get('Open'), request.form.get('Adj_Open')] if check is not None]
        checklist = [uname.encode("utf-8") for uname in checklist]
        today = datetime.date.today()
        lastmonth = today - datetime.timedelta(days=30)
        today_str = today.strftime('%Y-%m-%d')
        lastmo_str = lastmonth.strftime('%Y-%m-%d')

        '''
        # original extraction using REST URL for full set of stock data
        # however this REST URL does not allow for filtering, and is too large and inefficient for this milestone project's purposes
        # hence the REST URL for individal stock data which allows for filtering is used instead
        stock_json=requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?api_key=iRHkEhN5P7YxWaAy_djY')
        stockload = json.loads(stock_json.content)
        stocktable = stockload['datatable']   #dict of data(list of lists) and columns(list of dicts with type and name)
        colname = [col['name'] for col in stocktable['columns']]   #list of column names, with name from each dict in the stocktable columns list
        dframe = pd.DataFrame(stocktable['data'], columns=colname)    #create DataFrame with data(list of rows) and colname(list of column name strings)
        '''

        # get API data using REST URL with user's input stock symbol and date range for past 30 days
        API_data = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/'+symbol+'.json?start_date='+lastmo_str+'&end_date='+today_str+'&api_key=iRHkEhN5P7YxWaAy_djY')
        stock_load = json.loads(API_data.content)
        if stock_load.get('quandl_error'):    # if error arise, likely due to incorrect stock symbol, create an empty DataFrame
            df = pd.DataFrame()
        else:
            stock_data = stock_load['dataset']['data']   # list of lists (rows of data)
            col_names = stock_load['dataset']['column_names']    # list of strings
            df = pd.DataFrame(stock_data, columns=col_names)
            col_list = ['Date'] + checklist    # list of columns to extract
            checkedcol = df[[col for col in col_list]]    # dataframe with only the necessary data



        # Display graph in a static HTML file
        output_file('./static/bgraph.html', title='bokeh plot')

        # Create figure with figure options
        p1 = figure(title = 'Quandl WIKI Stock Prices for '+symbol, x_axis_type='datetime')
        p1.xaxis.axis_label = "Date"
        p1.yaxis.axis_label = "Stock Prices"

        if not df.empty:

            # Convert to Bokeh datetime axis_type to change the display ticks based on scale of the plot
            def convert_date(date):
                return np.array(date, dtype=np.datetime64)

            # Add renderer with visual customizations
            for index, item in enumerate(checklist):
                p1.line(convert_date(df['Date']), df[item], color=palette[index], legend=item)

            # Display x-axis labels at more frequent ticker intervals (every 2 days) than default
            # Orient x-axis labels at a diagonal to prevent overlapping
            p1.xaxis[0].ticker = DaysTicker(days=np.arange(1,31,2))
            p1.xaxis.major_label_orientation = pi/4
            p1.legend.location = 'top_center'

        save(p1)


        return render_template('graph.html')

# starts the web server, http://localhost:33507 to view
if __name__ == '__main__':
    app.run(port=33507, debug=True)
