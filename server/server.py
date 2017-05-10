import os, subprocess
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
  return "Execute python module through the uri /<application>"

@app.route("/<application>")
def runApplication(application):
  return subprocess.check_output("python -m" + application, shell=True)

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0')
