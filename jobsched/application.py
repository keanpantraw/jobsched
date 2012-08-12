from flask import Flask
from jobsched.rest import bp


app = Flask(__name__)
app.register_blueprint(bp)
