
from flask import Flask

webapp = Flask(__name__)
webapp.secret_key = 'mpeg8d\xcfZ\xa0p`N\x8e\x05\xaa\xa9zi\xf1Z\xa4\x9a\x7f\xd7'
from app import main, workers, login,autoscaling




