from flask import Flask, render_template, request, redirect

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
        value=request.form['symbol']
        if request.form['closing']:
            value=value+'c'
    return render_template('graph.html', value=value)

# starts the web server, http://localhost:33507 to view
if __name__ == '__main__':
    app.run(port=33507, debug=True)
