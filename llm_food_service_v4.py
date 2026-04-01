# llm_food_service_v4.py

import random
import requests
from flask import Flask, request, jsonify, session
from llm_aggregator_v3 import get_user_profile, get_all_user_ids

app = Flask(__name__)
app.secret_key = "67qFfTfOMsNdGe5pDjT6bRa1i0kX/G3mmzJ/Ea0r"

# -------------------------------
# 👤 SESSION USER (DYNAMIC)
# -------------------------------
def get_user():
    if "user_id" not in session:
        user_ids = get_all_user_ids()
        if user_ids:
            session["user_id"] = random.choice(user_ids)
        else:
            session["user_id"] = None
    return session.get("user_id")

# -------------------------------
# 🤖 LLM CALL
# -------------------------------
def call_mistral(prompt):
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        return res.json().get("response", "").strip()
    except Exception as e:
        print("LLM ERROR:", e)
        return None

# -------------------------------
# 🍽️ RECOMMENDATION ENGINE
# -------------------------------
def chat_recommend(message, profile):

    available_food_names = [f["name"] for f in profile["available_food"]]

    prompt = f"""
You are Swipe2Eat AI.

User Name: {profile['name']}
Budget: {profile['budget']}
Spice Level: {profile['spice_level']}
Likes: {profile['likes']}
Dislikes: {profile['dislikes']}

User request: {message}

Available food: {available_food_names}

Recommend ONLY 3 foods within budget and spice level.
Avoid dislikes strictly.
Format: Hi {profile['name']}, Swipe2Eat recommends: <food1>, <food2>, <food3>
Make it interesting, descriptive, and appealing.
"""

    llm_output = call_mistral(prompt)

    # -------------------------------
    # 🔁 FALLBACK MECHANISM
    # -------------------------------
    if not llm_output:
        print("⚠️ Using fallback")

        filtered = [
            f for f in profile["available_food"]
            if f["price"] <= profile["budget"]
            and f["spice_level"] <= profile["spice_level"]
            and f["name"] not in profile["dislikes"]
        ]

        fallback_items = [f["name"] for f in filtered[:3]]

        if not fallback_items:
            fallback_items = ["Veg Noodles", "Fried Rice", "Paneer Butter Masala"]

        return f"Hi {profile['name']}, Swipe2Eat recommends: {', '.join(fallback_items)}"

    return llm_output

# -------------------------------
# 🔁 RESET SESSION
# -------------------------------
@app.route("/reset")
def reset():
    session.clear()
    return "✅ Session cleared! Reload the page to pick a new user."

# -------------------------------
# 🌐 CHAT UI (CHATGPT STYLE)
# -------------------------------
@app.route("/")
def home():
    user_id = get_user()
    if not user_id:
        return "❌ No users found in DB"

    profile = get_user_profile(user_id)
    if not profile:
        return "❌ User not found in DB"

    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    font-family: Arial;
    background: #f5f5f5;
    display: flex;
    justify-content: center;
}}
.chat-container {{
    width: 500px;
    height: 650px;
    background: white;
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 20px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}}
.header {{
    padding: 15px;
    background: #10a37f;
    color: white;
    font-weight: bold;
}}
.chat-box {{
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    display: flex;
    flex-direction: column;
}}
.bubble {{
    padding: 10px 14px;
    border-radius: 12px;
    margin: 5px 0;
    max-width: 75%;
    line-height: 1.4;
}}
.user {{
    background: #dcf8c6;
    align-self: flex-end;
}}
.bot {{
    background: #ececec;
    align-self: flex-start;
}}
.input-box {{
    display: flex;
    border-top: 1px solid #ddd;
}}
input {{
    flex: 1;
    padding: 12px;
    border: none;
    outline: none;
}}
</style>
</head>

<body>
<div class="chat-container">
    <div class="header">
        👋 {profile['name']} | Swipe2Eat AI
    </div>

    <div id="chatBox" class="chat-box"></div>

    <div class="input-box">
        <input id="msg" placeholder="Type your food preference..." />
    </div>
</div>

<script>
const input = document.getElementById("msg");
const chatBox = document.getElementById("chatBox");

input.addEventListener("keypress", function(e) {{
    if (e.key === "Enter") send();
}});

function send() {{
    let text = input.value;
    if (!text.trim()) return;

    add(text, "user");
    input.value = "";

    let typing = add("Swipe2Eat is thinking...", "bot");

    fetch("/chat", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ message: text }})
    }})
    .then(res => res.json())
    .then(data => {{
        typing.remove();
        add(data.reply, "bot");
    }});
}}

function add(text, cls) {{
    let div = document.createElement("div");
    div.className = "bubble " + cls;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}}
</script>
</body>
</html>
"""

# -------------------------------
# 🔌 CHAT API
# -------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_id = get_user()
    if not user_id:
        return jsonify({"reply": "❌ No users found in DB"})

    profile = get_user_profile(user_id)
    if not profile:
        return jsonify({"reply": "❌ User not found in DB"})

    msg = request.json.get("message")
    reply = chat_recommend(msg, profile)

    return jsonify({"reply": reply})

# -------------------------------
# 🏃 RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)