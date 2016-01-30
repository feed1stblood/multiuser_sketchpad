# coding=utf-8

from flask import Flask, request, render_template, make_response
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
import json
from mafan import tradify, simplify
from uuid import uuid4

app = Flask(__name__)
app.config['SECRET_KEY'] = 'feed'
socketio = SocketIO(app)

all_rooms = set()
users = {}


@app.route("/d")
def entrance():
    # identify user by cookie
    user_id = request.cookies.get("id")
    resp = make_response(render_template("sketchpad.html"))
    if user_id is None or user_id not in users:
        user_id = uuid4().get_hex()
        users[user_id] = {"id": user_id, "allies": user_id[:5]}
        resp.set_cookie('id', user_id)
    return resp


@app.route("/c")
def convert():
    return simplify(request.args.get("word"))


@socketio.on("connect", namespace="/draw")
def on_connect():
    sid = request.cookies.get("id")
    if sid is not None:
        join_room(sid)
        all_rooms.add(sid)
        # send online users list to connected user
        emit("join", [users[u] for u in all_rooms], room=sid)
        # broadcast user connection to all online users
        for u in all_rooms:
            if u == sid:
                continue
            emit("join", [users[sid]], room=u)


@socketio.on("disconnect", namespace="/draw")
def on_disconnect():
    sid = request.cookies.get("id")
    if sid is not None:
        leave_room(sid)
        all_rooms.remove(sid)
        # broadcast user disconnection to all online users
        for u in all_rooms:
            if u == sid:
                continue
            emit("join", [users[sid]], room=u)


@socketio.on("chat", namespace="/draw")
def on_chat_message(message):
    message = json.loads(message)
    sid = request.sid[:5]
    for room in all_rooms:
        emit("chat", {"message": sid + ": " + tradify(message["message"])}, room=room)


@socketio.on("drawing", namespace="/draw")
def on_draw_message(message):
    for room in all_rooms:
        emit("drawing", message, room=room)


@socketio.on("drew", namespace="/draw")
def on_drew_message():
    for room in all_rooms:
        emit("drew", room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6676, debug=True)

