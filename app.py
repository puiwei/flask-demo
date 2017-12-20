from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import pandas as pd

app = Flask(__name__)

# default home page
@app.route('/')
def index():
    return render_template('index.html')

# when /static_page_name is evoked, return the page's html
@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s' % page_name)

# when /ticker REST URL is evoked, return graph.html with value
@app.route('/ticker', methods=['GET','POST'])
def ticker():
    if request.method == 'POST':
        value = request.form['symbol']
        checklist = []
        # get list of checked boxes
        checklist += [check for check in [request.form.get('close'), request.form.get('adj_close'), request.form.get('open'), request.form.get('adj_open')] if check is not None]

        stock_json=requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?api_key=iRHkEhN5P7YxWaAy_djY')
        stockload = json.loads(stock_json.content)
        stocktable = stockload['datatable']   #dict of data(list of lists) and columns(list of dicts with type and name)
        colname = [col['name'] for col in stocktable['columns']]   #list of column names, with name from each dict in the stocktable columns list
        df = pd.DataFrame(stocktable['data'], columns=colname)    #create DataFrame with data(list of rows) and colname(list of column name strings)

        if request.form.get('close'):
            value=value+'C'


        return render_template('graph.html', value=value)

# starts the web server, http://localhost:33507 to view
if __name__ == '__main__':
    app.run(port=33507, debug=True)
