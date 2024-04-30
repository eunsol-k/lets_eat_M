from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_app():
    app = Flask(__name__)

    #routes list
    from routes import routes_list
    routes_list(app)

    @app.route("/")
    def hello_world():
        return "hello world!"
    
    return app

create_app().run()
