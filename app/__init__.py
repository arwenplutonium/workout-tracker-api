import os

from flask import Flask
from flask_migrate import Migrate

from .models import db

app = Flask(__name__)
# The engine is built when db.init_app runs, so the test suite overrides this
# through the environment rather than by reassigning the config afterwards.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Ensure routes are registered when importing the app package.
import server  # noqa: F401
