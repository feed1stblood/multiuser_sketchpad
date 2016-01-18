# coding=utf-8

from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'feed'
socketio = SocketIO(app)


all_rooms = []


@app.route("/")
def entrance():
    return render_template("sketchpad.html")


@socketio.on("connect", namespace="/draw")
def on_connect():
    sid = request.sid
    join_room(sid)
    all_rooms.append(sid)
    print sid + "join"


@socketio.on("disconnect", namespace="/draw")
def on_disconnect():
    sid = request.sid
    leave_room(sid)
    all_rooms.remove(sid)
    print sid + "leave"


@socketio.on("chat", namespace="/draw")
def on_chat_message(message):
    message = json.loads(message)
    sid = request.sid[:5]
    for room in all_rooms:
        emit("chat", {"message": sid + ": " + message["message"]}, broadcast=True, room=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=6676, debug=True, logger=True, engineio_logger=True, binary=True)

