from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "FinalUI.py"

if __name__ == "__main__":
    app.run(debug=True)
