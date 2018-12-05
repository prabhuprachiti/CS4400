from flask import Flask
from backend.login import login
from backend.register import register
from backend.search import search
from backend.adddata import add_data
from backend.removedata import remove_data
from backend.logout import logout

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/backend/login', methods=['POST'])
def backend_login():
    return login()


@app.route('/backend/register', methods=['POST'])
def backend_register():
    return register()


@app.route('/backend/logout', methods=['POST'])
def backend_logout():
    return logout()


@app.route('/backend/search', methods=['GET', 'POST'])
def backend_search():
    return search()


@app.route('/backend/add_data', methods=['GET', 'POST'])
def backend_add_data():
    return add_data()


@app.route('/backend/remove_data', methods=['GET', 'POST'])
def backend_remove_data():
    return remove_data()


app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == '__main__':
    app.run()
