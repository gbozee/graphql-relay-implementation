import os
from flask import Flask
from flask_graphql import GraphQLView
from flask_migrate import Migrate
# from .schema import schema
from .schema import schema
from .models import db

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
database = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(database)
db.init_app(app)
migrate = Migrate(app,db)

app.add_url_rule('/', view_func=GraphQLView.as_view(
    'graphql', schema=schema, graphiql=True))

# Optional, for adding batch query support (used in Apollo-Client)
# app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, batch=True))atch=True))