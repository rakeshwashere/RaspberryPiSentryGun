from flask import request, Response, render_template, jsonify, url_for, redirect, g
from .models import User
from index import app, db
from sqlalchemy.exc import IntegrityError
from .utils.auth import generate_token, requires_auth, verify_token
from sentry_service.sentry_service_client import SentryServiceClient
from stream import VideoStreamer
# from shadowservice.sentry_shadow import SentryShadow

# sentry service 
sentry_service_client = SentryServiceClient('WEBSITE')
webcam_streamer = VideoStreamer('localhost', 5555)
sentry_gun_streamer = VideoStreamer('localhost', 5556)

#shadow 
# sentry_shadow = SentryShadow()

def gen():
    while True:
      s = webcam_streamer.stream()
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + s + b'\r\n\r\n')

def gen1():
    while True:
      s = sentry_gun_streamer.stream()
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + s + b'\r\n\r\n')
      

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/webcamera')
def webcamera():
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sentry_gun_camera')
def sentry_gun_camera():
  return Response(gen1(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/sentry/shadow', methods=['POST'])
def set_sentry_shodow():
    incoming = request.get_json()
    sentry_shadow.set_autonomous_mode()

@app.route('/api/sentry', methods=['POST'])
def fire_sentry_gun():
    incoming = request.get_json()
    command = incoming['command']
    
    if command == 'FIRE':
        sentry_service_client.fire()
        print("sentry fired")
    
    elif command == 'PAN_RIGHT':
        angle = incoming.get('angle', 10)
        sentry_service_client.pan_right(angle)
    
    elif command == 'PAN_LEFT':
        angle = incoming.get('angle', 10)
        sentry_service_client.pan_left(angle)
    
    # TODO implement other functions 
    return jsonify(message="fired")


@app.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')


@app.route("/api/user", methods=["GET"])
# @requires_auth
def get_user():
    # print("calling fire")
    # sentry_service_client.fire()
    return jsonify(result=g.current_user)


@app.route("/api/create_user", methods=["POST"])
def create_user():
    incoming = request.get_json()
    user = User(
        email=incoming["email"],
        password=incoming["password"]
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message="User with that email already exists"), 409

    new_user = User.query.filter_by(email=incoming["email"]).first()

    return jsonify(
        id=user.id,
        token=generate_token(new_user)
    )


@app.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = User.get_user_with_email_and_password(
        incoming["email"], incoming["password"])
    if user:
        return jsonify(token=generate_token(user))

    return jsonify(error=True), 403


@app.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        return jsonify(token_is_valid=True)
    else:
        return jsonify(token_is_valid=False), 403
