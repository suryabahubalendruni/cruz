from flask import Flask, render_template
from bokeh.embed import autoload_server

app = Flask(__name__)
app.secret_key = "BUSH DID 9/11"
app.static_folder = "static"
app.config["DEBUG"] = True


@app.route('/home')
@app.route('/index', alias=True)
@app.route('/', alias=True)
def index():
    return render_template('index.html', title='Homepage')


@app.route('/address_search')
def address_search():
    script = autoload_server(model=None, app_path="/_address_search")
    return render_template('bokeh.html', bokeh_script=script, title="Individual Address Search")



if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)