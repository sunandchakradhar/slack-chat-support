import flask
from flask import Flask, request, session
from slackclient import SlackClient
import time, string, random
import sys
import logging
# from flask.ext.session import Session
# from flask import Flask, render_template
import json


app = Flask(__name__)
app.secret_key = 'sfjdfglkdfkgdklfgjldfgsdflksdfklsdf'
app.config['SESSION_TYPE'] = 'filesystem'

# sess = Session()

SC_TOKEN = "xoxp-74775930387-74841388162-74946178247-98ae90f6ea"

SC = SlackClient(SC_TOKEN)


class PZException(Exception):
    pass


def success(data=""):
    return flask.jsonify({
        "success": True,
        "data": data
    })


def _error(msg=""):
    return flask.jsonify({
        "success": False,
        "msg": msg
    })


def create_channel(name):
    resp = SC.api_call("channels.create", name=name)

    if resp["ok"] is not True:
        raise PZException("Error creating channel")

    return resp["channel"]


def get_channel_info(channel_id):
    resp = SC.api_call("channels.info", channel=channel_id)

    if resp["ok"] is not True:
        raise PZException(resp["error"])

    return resp["channel"]


def join_channel(name):
    resp = SC.api_call("channels.join", name=name)

    if resp["ok"] is not True:
        raise PZException("Error joining channel")

    return resp["channel"]


def invite_to_channel(channel_id, user_id):
    resp = SC.api_call("channels.invite", channel=channel_id, user=user_id)

    if resp["ok"] is not True:
        raise PZException("Error joining channel")

    return resp["channel"]


def get_users():
    resp = SC.api_call("users.list", presence=1)
    if resp["ok"] is not True:
        raise PZException("Error getting users list")

    return resp["members"]

def get_bot():
    resp = SC.api_call("bots.info")
    if resp["ok"] is not True:
        raise PZException("Error getting users list")

    return resp["bot"]


def get_user_for_support(users):
    # return active user for now. algo will change in future.
    for user in users:
        if "presence" in user:
            # app.logger.warning("%s- %s" %(user["presence"], user["profile"]["first_name"]))
            if user["presence"] == 'active':
                return user
    return False


def post_message(form):
    resp = SC.api_call(
        "chat.postMessage", text=form["msg"], channel=session["channel"]["id"],
        user=session["name"])
    if resp["ok"] is not True:
        raise PZException(resp["error"])

    return resp


def get_messages(last=None):
    args = {}
    if last is not None:
        args["oldest"] = last
    resp = SC.api_call(
        "channels.history", channel=session["channel"]["id"], count=200,
        **args)

    app.logger.debug("response: %s" % resp)
    # return []
    if resp["ok"] is not True:
        raise PZException("getting messages failed!")

    app.logger.debug("response: %s" % resp)

    return resp["messages"]


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def check_session():
    if 'channel' not in session:
        raise PZException("No Valid session re init")
    return True


# def get_chat_session():
#     if "channel" not in session:
#         email =


# uuid.uuid4()


@app.route("/")
def hello():
    #   "Lets Chat!"
    resp = flask.Response("Lets Chat!")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/logout")
def logout():
    if "name" in session:
        session.pop("name")
    if "email" in session:
        session.pop("email")
    if "channel" in session:
        session.pop("channel")
    if "support_user" in session:
        session.pop("support_user")
    return "get lost!"


@app.route("/get-token", methods=['POST'])
def get_token():
    if 'channel' not in session:
        #  if name and email not null create a channel
        if("name" not in request.form) or (request.form["name"].strip() == ""):
            return _error("Invalid name!")

        if ("email" not in request.form) or (request.form["email"].strip() == ""):
            return _error("Invalid email!")

        name = request.form["name"]
        email = request.form["email"]

        users = get_users()
        if len(users) == 0:
            raise PZException("No user online")
        support_user = get_user_for_support(users)
        if support_user is False:
            return _error("Support Inactive")
        channel_name = name + "-" + support_user["profile"]["first_name"] + '-' + random_string()
        # create channel
        channel = create_channel(channel_name)
        join_channel(channel_name)
        invite_to_channel(channel["id"], support_user["id"])

        session["name"] = name
        session["email"] = email
        session["channel"] = channel
        session["support_user"] = support_user
    else:
        channel_id = session["channel"]["id"]
        channel = get_channel_info(channel_id)
        if channel["is_archived"] is True:
            session.clear()
            return _error("Session Expired")

    # bot = get_bot()

    return success({
        # "logged_user_id": bot["id"],
        "name": session["name"],
        "email": session["email"],
        "token": session["channel"]["id"],
        "support_user": session["support_user"]
    })


@app.route("/send", methods=['POST'])
def send_msg():
    check_session()
    if("msg" not in request.form) or (request.form["msg"].strip() == ""):
        return _error("Invalid msg!")

    # form_data = request.form
    # form_data["attachments"] = json.loads(request.form["attachments"])
    msg = post_message(request.form)
    return success(msg)


@app.route("/get-chat", methods=['GET'])
def get_chat():
    check_session()
    last = None
    if("last" in request.args):
        last = request.args['last']

    msgs = get_messages(last)
    return success(msgs)


@app.route("/get-support-users", methods=['GET'])
def get_support_users():
    # check_session()
    users = get_users()
    print users
    if len(users) == 0:
        raise PZException("No user online")

    return success(users)


@app.errorhandler(PZException)
def handle_pz_exception(error):
    app.logger.error(error)
    return _error(str(error))


# @app.errorhandler(Exception)
# def handle_invalid_usage(error):
#     app.logger.error(error)
#     return _error(str(error))


if __name__ == "__main__":
    app.debug = True

    app.logger.setLevel(logging.INFO)

    # sess.init_app(app)

    app.run()
