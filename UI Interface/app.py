from flask import Flask, render_template, request, jsonify
import time 

app = Flask(__name__)

# Rotta per la home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/downtown')
def downtown():
    return render_template('downtown.html')

@app.route('/west')
def west():
    return render_template('west.html')

@app.route('/east')
def east():
    return render_template('east.html')

@app.route('/south')
def south():
    return render_template('south.html')

@app.route('/north')
def north():
    return render_template('north.html')


# Rotta che restituisce un dato JSON
@app.route('/data')
def get_data():
    data = {
        'name': 'Flask App',
        'version': '1.0',
        'description': 'Un esempio di applicazione web con Flask'
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
