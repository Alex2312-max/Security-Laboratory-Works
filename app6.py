import flask
import requests_oauthlib
import os
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

app = flask.Flask(__name__)


@app.route("/login")
def login():
    simplelogin = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri="http://localhost:5000/callback")
    authorization_url, _ = simplelogin.authorization_url(AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/callback")
def callback():
    simplelogin = requests_oauthlib.OAuth2Session(CLIENT_ID)
    simplelogin.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=flask.request.url)

    user_info = simplelogin.get(USERINFO_URL).json()
    return f"""
	<!DOCTYPE html>
	<html>
	<head>
	<h3>User information: </h3><br>
	</head>

	Name: {user_info["name"]} <br>

	Email: {user_info["email"]} <br>

	Avatar <img src="{user_info.get('avatar_url')}"> <br>

	<form action="http://localhost:5000/">
		<button>Home</button>
	</form>
	</head>
	</html>
	"""


@app.route("/login_twitter")
def login_twitter():
    facebook = requests_oauthlib.OAuth2Session(TW_CLIENT_ID, redirect_uri="http://localhost:5000/tw-callback")
    authorization_url, _ = facebook.authorization_url(TW_AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/tw-callback")
def callback_twitter():
    facebook = requests_oauthlib.OAuth2Session(TW_CLIENT_ID, scope=FB_SCOPE,
                                               redirect_uri='http://localhost:5000/tw-callback')

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)
    facebook.fetch_token(TW_TOKEN_URL, client_secret=TW_CLIENT_SECRET, authorization_response=flask.request.url, )

    # Fetch a protected resource, i.e. user profile, via Graph API
    facebook_user_data = facebook.get("https://graph.twitter.com/me?fields=id,name,email,picture{url}").json()

    print(facebook_user_data)
    email = None

    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")

    return f"""
	<!DOCTYPE html>
	<html>
	<head>
	<h3>User information: </h3><br>
	</head>

	Name: {facebook_user_data["name"]} <br>

	Email: {email} <br>

	Avatar <img src="{picture_url}"> <br>

	<form action="http://localhost:5000/">
		<button>Home</button>
	</form>
	</head>
	</html>
	"""


@app.route("/login_facebook")
def login_facebook():
    facebook = requests_oauthlib.OAuth2Session(FB_CLIENT_ID, redirect_uri="http://localhost:5000/fb-callback")
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/fb-callback")
def callback_facebook():
    facebook = requests_oauthlib.OAuth2Session(FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri='http://localhost:5000/fb-callback')

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)
    facebook.fetch_token(FB_TOKEN_URL, client_secret=FB_CLIENT_SECRET, authorization_response=flask.request.url ,)

    # Fetch a protected resource, i.e. user profile, via Graph API
    facebook_user_data = facebook.get("https://graph.facebook.com/me?fields=id,name,email,picture{url}").json()

    print(facebook_user_data)
    email = None

    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")

    return f"""
	<!DOCTYPE html>
	<html>
	<head>
	<h3>User information: </h3><br>
	</head>

	Name: {facebook_user_data["name"]} <br>

	Email: {email} <br>

	Avatar <img src="{picture_url}"> <br>

	<form action="http://localhost:5000/">
		<button>Home</button>
	</form>
	</head>
	</html>
	"""


@app.route("/")
def index():
    return """
		<!DOCTYPE html>
	<html>
	<head>
	<style>
	.button {
		border: none;
		color: white;
		padding: 15px 32px;
		text-align: center;
		text-decoration: none;
		display: inline-block;
		font-size: 16px;
		margin: 4px 2px;
		cursor: pointer;
	}

	.button1 {background-color: #4CAF50;} /* Green */
	.button2 {background-color: #008CBA;} /* Blue */
	.button3 {background-color: #008CBA;} /* Blue */
	</style>
	</head>
	<body>

	<form action="login">
		<button class="button button1"> SimpleLogin </button>
	</form>

	<form action="login_facebook">
		<button class="button button2"> Facebook </button>
	</form>

	<form action="login_twitter">
		<button class="button button3"> Twitter </button>
	</form>

	</body>
	</html>
	"""


if __name__ == '__main__':
    app.run(debug=True)