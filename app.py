from flask import Flask, request, jsonify
import uuid
import json
import os

app = Flask(__name__)

# তোমার ওয়েবসাইটের মূল লিংক
BASE_URL = "https://curly-bassoon-six.vercel.app/"  # এখানে তোমার ডোমেইন বা Replit লিংক বসাও

# JSON ফাইলের নাম
JSON_FILE = "link.json"

# যদি JSON ফাইল না থাকে, তাহলে একটি খালি ডিকশনারি তৈরি করো
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump({}, f)


# JSON ফাইল থেকে ডাটা পড়ার ফাংশন
def load_data():
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    # যদি ডাটা একটি dictionary না হয়, তাহলে ফাঁকা dictionary ফেরত দাও
    if not isinstance(data, dict):
        return {}

    return data


# JSON ফাইলে ডাটা লেখার ফাংশন
def save_data(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route('/add', methods=['GET'])
def add_video():
    hd_link = request.args.get('hd')
    sd_link = request.args.get('sd')

    if not hd_link or not sd_link:
        return jsonify({"error": "hd এবং sd লিংক প্রয়োজন"}), 400

    # "@"" কে "&" এ পরিবর্তন করো যাতে লিংক সঠিক হয়
    hd_link = hd_link.replace("@", "&")
    sd_link = sd_link.replace("@", "&")

    # ইউনিক আইডি তৈরি
    video_id = str(uuid.uuid4())[:8]

    # JSON ফাইল থেকে পুরানো ডাটা লোড করো
    video_links = load_data()

    # নতুন ভিডিও যোগ করো
    video_links[video_id] = {
        "hd": hd_link,
        "sd": sd_link
    }

    # JSON ফাইলে নতুন ডাটা সংরক্ষণ করো
    save_data(video_links)

    # সম্পূর্ণ লিংক রিটার্ন করো
    full_url = f"{BASE_URL}/video/{video_id}"
    return jsonify({"url": full_url})


@app.route('/video/<video_id>', methods=['GET'])
def get_video(video_id):
    # JSON ফাইল থেকে ডাটা লোড করো
    video_links = load_data()

    # যদি ভিডিও আইডি পাওয়া যায়, তাহলে রিটার্ন করো
    if video_id in video_links:
        return jsonify(video_links[video_id])
    else:
        return jsonify({"error": "ভিডিও পাওয়া যায়নি"}), 404


# ✅✅✅ নতুন `/link` Route ✅✅✅
@app.route('/link', methods=['GET'])
def get_all_links():
    # JSON ফাইল থেকে সব ডাটা লোড করো
    video_links = load_data()

    # যদি কোনো লিংক না থাকে, তাহলে error রিটার্ন করো
    if not video_links:
        return jsonify({"error": "কোনো লিংক পাওয়া যায়নি"}), 404

    # সব লিংকের তালিকা পাঠাও
    return jsonify(video_links)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
