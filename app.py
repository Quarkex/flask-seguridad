from flask import Flask, render_template, url_for, request, jsonify
from flask_login import LoginManager, current_user
import xmlrpc.client as rpc

# End of imports ###############################################################

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# End of singleton declarations ################################################

class User(object):
    '''
    This provides implementations for the methods that Flask-Login
    expects user objects to have.
    '''

    def get_id(self):
        try:
            return text_type(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __eq__(self, other):
        '''
        Checks the equality of two `User` objects using `get_id`.
        '''
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `User` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

    def __init__(self, id):
        self.id = id
        self.is_active = True
        self.is_authenticated = False
        self.is_anonymous = False

    def get(id):
        for user in users:
            if user.get_id == id:
                return user
        return None

# End of class “User” ##########################################################

#You will need to provide a user_loader callback. This callback is used to
#reload the user object from the user ID stored in the session. It should take
#the unicode ID of a user, and return the corresponding user object. 
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# End of login_manager inner methods ###########################################

info = rpc.ServerProxy('https://demo.odoo.com/start').start()
url, db, username, password = \
            info['host'], info['database'], info['user'], info['password']

users = []

# End of test data #############################################################

common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    parameters = request.get_json(True)
    username = parameters["user"]
    password = parameters["password"]

    uid = common.authenticate(db, username, password, {})

    if uid != False:
        if load_user(uid) != False:
            user = User(uid)
            user.username = username
            user.password = password
            users.append(user)

    response = {
            "uid": uid,
            }

    response["status"] = "success" if (uid != False) else "fail"
    if response["status"] == "success":
        response["uid"] = uid
    return jsonify(response)

@app.route('/api/create', methods=['GET','POST'])
def create():
    return app.send_static_file('dummy/create.json')

@app.route('/api/read', methods=['GET','POST'])
def read():
    return app.send_static_file('dummy/read.json')

@app.route('/api/update', methods=['GET','POST'])
def update():
    return app.send_static_file('dummy/update.json')

@app.route('/api/delete', methods=['GET','POST'])
def delete():
    return app.send_static_file('dummy/delete.json')

@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')

# End of flask route definitions ###############################################

if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')
