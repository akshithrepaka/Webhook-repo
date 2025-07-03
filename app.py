from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(_name_)
CORS(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["webhookDB"]
collection = db["events"]

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Push event
    if "pusher" in data:
        event = {
            "author": data["pusher"]["name"],
            "action": "Push",
            "from_branch": "",
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.utcnow().isoformat()
        }
        collection.insert_one(event)
        return jsonify({"msg": "Push event stored"}), 200

    # Pull Request event
    if "pull_request" in data:
        pr = data["pull_request"]
        action_type = "Pull Request"
        if pr.get("merged"):
            action_type = "Merge"
        event = {
            "author": pr["user"]["login"],
            "action": action_type,
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": datetime.utcnow().isoformat()
        }
        collection.insert_one(event)
        return jsonify({"msg": f"{action_type} event stored"}), 200

    return jsonify({"msg": "Unsupported event"}), 400

@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find({}, {"_id": 0}))
    return jsonify(events)

@app.route("/")
def index():
    return render_template("index.html")

if _name_ == "_main_":
    app.run(debug=True)
