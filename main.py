from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

