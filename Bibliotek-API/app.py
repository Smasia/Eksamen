from flask import Flask, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

con = sqlite3.Connection('database.db', check_same_thread=False) # connection
cur = con.cursor() # cursor

@app.route('/', methods = ["GET"])
def index():
  return "Success", 200