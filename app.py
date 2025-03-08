from flask import Flask, request, jsonify
import uuid
import json
import os
import requests
import time
import threading

app = Flask(__name__)

BASE_URL = "https://getterlink.onrender.com"
JSON_FILE = "link.json"
UPCOMING_FILE = "upcoming.json"  # আপকামিং UID সংরক্ষণ করার জন্য

# যদি JSON ফাইল না থাকে, তাহলে ফাঁকা ডাটা তৈরি করো
for file in [JSON_FILE, UPCOMING_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f) if file == UPCOMING_FILE else json.dump({}, f)

# JSON ফাইল থেকে ডাটা লোড করার ফাংশন
def load_data(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data if isinstance(data, (dict, list)) else [] if filename == UPCOMING_FILE else {}

# JSON ফাইলে ডাটা সংরক্ষণ করার ফাংশন
def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# ✅✅✅ /up রুট: আপকামিং লিংক যোগ করা ✅✅✅
@app.route('/up', methods=['GET'])
def add_upcoming():
    video_id = request.args.get('')

    if not video_id or len(video_id) < 8:
        return jsonify({"error": "সঠিক ৮ অক্ষরের ইউআইডি প্রদান করুন"}), 400

    upcoming_list = load_data(UPCOMING_FILE)

    if video_id in upcoming_list:
        return jsonify({"message": "এই ইউআইডি ইতিমধ্যেই তালিকায় রয়েছে"}), 400

    upcoming_list.append(video_id)
    save_data(UPCOMING_FILE, upcoming_list)

    return jsonify({"message": "আপকামিং লিংক যোগ করা হয়েছে", "queue_position": len(upcoming_list)})


# ✅✅✅ /add রুট: ভিডিও লিংক যোগ করা ✅✅✅
@app.route('/add', methods=['GET'])
def add_video():
    hd_link = request.args.get('hd')
    sd_link = request.args.get('sd')

    if not hd_link or not sd_link:
        return jsonify({"error": "hd এবং sd লিংক প্রয়োজন"}), 400

    hd_link = hd_link.replace("@", "&")
    sd_link = sd_link.replace("@", "&")

    # ✅ প্রথমে আপকামিং তালিকা চেক করো ✅
    upcoming_list = load_data(UPCOMING_FILE)
    video_id = upcoming_list.pop(0) if upcoming_list else str(uuid.uuid4())[:8]

    # আপডেটেড আপকামিং লিস্ট সংরক্ষণ করো
    save_data(UPCOMING_FILE, upcoming_list)

    video_links = load_data(JSON_FILE)
    video_links[video_id] = {"hd": hd_link, "sd": sd_link}

    save_data(JSON_FILE, video_links)

    full_url = f"{BASE_URL}/video/{video_id}"
    return jsonify({"url": full_url, "video_id": video_id})


# ✅✅✅ /video/<video_id>: নির্দিষ্ট ভিডিও লিংক দেখানো ✅✅✅
@app.route('/video/<video_id>', methods=['GET'])
def get_video(video_id):
    video_links = load_data(JSON_FILE)
    return jsonify(video_links.get(video_id, {"error": "ভিডিও পাওয়া যায়নি"}))


# ✅✅✅ /link: সব ভিডিও লিংক দেখানো ✅✅✅
@app.route('/link', methods=['GET'])
def get_all_links():
    video_links = load_data(JSON_FILE)
    return jsonify(video_links) if video_links else jsonify({"error": "কোনো লিংক পাওয়া যায়নি"}), 404


# ✅✅✅ /ping: সার্ভারের স্ট্যাটাস চেক ✅✅✅
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"})


# ✅✅✅ সার্ভারকে জীবিত রাখার ফাংশন ✅✅✅
def keep_alive():
    url = "https://getterlink.onrender.com"
    while True:
        time.sleep(300)
        try:
            requests.get(url)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, debug=True)
