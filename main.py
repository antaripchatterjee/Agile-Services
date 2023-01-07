from flask import Flask
from agileservices.ext._flask import register_flask_app

app = Flask(__name__)
register_flask_app(app, 'services')

if __name__ == '__main__':
    app.run(debug=True)