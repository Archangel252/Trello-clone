# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()

cur_board = 0

def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	return session['email'] if 'email' in session else 'Unknown'

def format_email():
    user_decry = getUser()
    if user_decry != 'Unknown':
        user_decry = db.reversibleEncrypt('decrypt',user_decry)
    return user_decry

@app.route('/processlogin', methods=["POST", "GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = form_fields['email']
    password = form_fields['password']
    response = db.authenticate(email,password)
    if response['success']:
        session['email'] = db.reversibleEncrypt('encrypt', form_fields['email'])
        print('successful login')
        return json.dumps({'success': 1})
    else:
        print('failed login')
        return json.dumps({'success': 0})

@app.route('/processsignup', methods=["POST", "GET"])
def processsignup():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = form_fields['email']
    password = form_fields['password']
    response = db.authenticate(email,password)
    if response['success']:
        print('User already exists')
        return json.dumps({'success': 0})
    else:
        db.createUser(email=email ,password=password, role='guest')
        return json.dumps({'success': 1})
        



@app.route('/')
def root():
    return redirect('/login')

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/login')
def login():
    return render_template('login.html', issignup=False)

@app.route('/signup')
def signup():
    return render_template('login.html', issignup=True)

@app.route('/popup')
@login_required
def popup():
    return render_template('popup.html')

@app.route('/create')
@login_required
def create():
    return render_template('create.html')



@app.route('/boards')
@login_required
def boards():
    user_boards = db.getBoards(format_email())
    return render_template('boards.html', boards=user_boards)


@app.route('/home/<int:board_id>')
@login_required
def home(board_id):
    id = board_id
    cur_board = db.get_board(id)
    return render_template('home.html', user = format_email(), board = cur_board, b_id = id)


#######################################################################################
# CHATROOM RELATED
#######################################################################################

@socketio.on('joined', namespace='/cur_board')
def joined(message):
    id = message['board_id']
    room = f'main{id}'
    join_room(room)
    owner = db.isOwner(format_email())
    if owner:
        emit('status', {'msg': format_email() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room=room)
    else:
        emit('status', {'msg': format_email() + ' has entered the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room=room)
    

@socketio.on('left', namespace='/cur_board')
def left(message):
    id = message['board_id']
    room = f'main{id}'
    leave_room(room)
    owner = db.isOwner(format_email())
    if owner:
        emit('status', {'msg': format_email() + ' has left the room.', 'style': 'width: 100%;color:red;text-align: right'}, room=room)
    else:
        emit('status', {'msg': format_email() + ' has left the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room=room)

    
@socketio.on('chat', namespace='/cur_board')
def chat(message):
    id = message['board_id']
    room = f'main{id}'
    owner = db.isOwner(format_email())
    if owner:
        emit('chat', {'msg': message['text'], 'style': 'width: 100%;color:blue;text-align: right'}, room=room)
    else:
        emit('chat', {'msg': message['text'], 'style': 'width: 100%;color:gray;text-align: left'}, room=room) 
# for when a chat comes in

#################################################
# updating board data
#################################################
@socketio.on('addcard', namespace='/cur_board')
def addcard(message):
    id = message['board_id']
    room = f'main{id}'
    card_id = db.AddCard(message['board_id'],message['list_id'])
    emit('createCard',{'id': message['list_id'], 'card_id' : card_id}, room=room, broadcast=True)

@socketio.on('delcard', namespace='/cur_board')
def addcard(message):
    id = message['board_id']
    room = f'main{id}'
    print('calling delete function')
    card_id = message['card_id']
    db.DeleteCard(message['board_id'],card_id)
    print('sending back to delete function')
    emit('delete',{'id': card_id}, room=room, broadcast=True)

@socketio.on('editcard', namespace='/cur_board')
def editcard(message):
    print('recieved edit card')
    id = message['board_id']
    card_id = message['card_id']
    room = f'main{id}'
    edits = message['edits']
    db.EditCard(card_id, edits)
    emit('edit',{'id': id, 'card_id' : card_id, 'edits' : edits}, room=room, broadcast=True)

#####################################
# PASSING BOARD DATA
#####################################
@socketio.on('joined', namespace='/boards')
def joined(message):
    join_room('boards')
    print('joined')

@socketio.on('selectboard', namespace='/boards')
def selectboard(id):
    board_id = id['id']
    redirect_url = url_for('home', board_id=board_id, _external=True)

    # Emit an event with the redirect URL to the client
    emit('redirect', {'url': redirect_url})

####################################################
# CREATING NEW BOARDS
####################################################
@socketio.on('joined', namespace='/create')
def joined(message):
    join_room('newboards')
    print('joined')

@socketio.on('createboard', namespace='/create')
def createboard(name):
    user_id = db.get_user_id(format_email())
    new_board = db.createBoard(user_id,name['name'])
    members = name['members']
    print(members)
    for email in members:
        id = db.get_user_id(email)
        db.addMember(id,new_board['board_id'])
    redirect_url = url_for('home', board_id=new_board['board_id'], _external=True)
    # Emit an event with the redirect URL to the client
    emit('redirect', {'url': redirect_url})

#######################################################################
# EXTRA 
#######################################################################
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
