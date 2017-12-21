from flask import Flask, render_template, request, redirect, send_from_directory
import requests
import simplejson as json
import pandas as pd
import datetime

app = Flask(__name__)

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
        checklist_decode = [uname.encode("utf-8") for uname in checklist]
        today = datetime.date.today()
        lastmonth = today - datetime.timedelta(days=30)
        today_str = today.strftime('%Y-%m-%d')
        lastmo_str = lastmonth.strftime('%Y-%m-%d')

        '''
        # original extraction using REST URL for full set of stock data
        # however this REST URL does not allow for filtering, and is too large and inefficient for this milestone project's purposes
        # hence the REST URL for individal stock data which allows for filtering is used instead
        stock_json=requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?api_key=iRHkEhN5P7YxWaAy_djY')
<<<<<<< Updated upstream
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
            stock_data = stock_load['dataset']['data']   #list of lists (rows of data)
            col_names = stock_load['dataset']['column_names']    #list of strings
            df = pd.DataFrame(stock_data, columns=col_names)
            checkedcol = df[[col for col in checklist_decode]]


        if request.form.get('Close'):
                symbol=symbol+'C'


        return render_template('graph.html', value=symbol)

# starts the web server, http://localhost:33507 to view
if __name__ == '__main__':
    app.run(port=33507, debug=True)
