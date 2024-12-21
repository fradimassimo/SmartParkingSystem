from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello Damiano and Antonio, this is our fucking Smart Parking System!"

if __name__ == "__main__":
    app.run(debug=True)