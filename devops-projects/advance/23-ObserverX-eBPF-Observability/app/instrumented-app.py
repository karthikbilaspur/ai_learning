from opentelemetry import trace
from flask import Flask
app=Flask(__name__)
@app.route('/')
def hi():
    return 'observed'
app.run(host='0.0.0.0',port=8000)
