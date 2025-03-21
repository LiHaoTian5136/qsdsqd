from flask import Flask, redirect, request
import requests
import os

app = Flask(__name__)

# Discord OAuth2 credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://your-app.onrender.com/callback"
DISCORD_API_URL = "https://discord.com/api/v10"

@app.route("/")
def index():
    # Redirect users to Discord's OAuth2 authorization page
    return redirect(
        f"{DISCORD_API_URL}/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20email"
    )

@app.route("/callback")
def callback():
    # Handle the callback from Discord
    code = request.args.get("code")
    if not code:
        return "Authorization failed: No code provided."

    # Exchange the code for an access token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify email",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{DISCORD_API_URL}/oauth2/token", data=data, headers=headers)
    if response.status_code != 200:
        return f"Authorization failed: {response.text}"

    # Get the user's email and other details
    access_token = response.json().get("access_token")
    user_response = requests.get(f"{DISCORD_API_URL}/users/@me", headers={"Authorization": f"Bearer {access_token}"})
    if user_response.status_code != 200:
        return f"Failed to fetch user details: {user_response.text}"

    user_data = user_response.json()
    email = user_data.get("email")
    username = user_data.get("username")
    user_id = user_data.get("id")

    # Log the user's email (for demonstration purposes only)
    with open("verified_users.txt", "a") as f:
        f.write(f"{user_id}, {username}, {email}\n")

    return f"Verification successful! Logged email: {email}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
