import json
import os
import boto3
import uuid
import requests
import re
from datetime import datetime

# ---------------- ENV ----------------
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TABLE_NAME = os.environ["DYNAMO_TABLE"]
BUCKET_NAME = os.environ["S3_BUCKET"]

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ---------------- AWS CLIENTS ----------------
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")

# ---------------- KNOWLEDGE BASE ----------------
KNOWLEDGE = {
    "what is cloud computing": "Cloud computing means using computing resources over the internet instead of owning physical servers.",
    "what is aws": "AWS is a cloud platform that provides services like compute, storage, and databases on demand.",
    "what is lambda": "AWS Lambda lets you run code without managing servers. You only pay when your code runs.",
    "what is terraform": "Terraform is a tool that lets you define and manage cloud infrastructure using code.",
    "who made you": "I was built by Ashu as part of a cloud computing project 😊"
}

# ---------------- GUIDED SESSIONS ----------------
GUIDED_SESSIONS = {}

# ---------------- HELPERS ----------------
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=5
    )

def normalize(text):
    return text.lower().strip().lstrip("/")

# ---------------- SOLVERS ----------------
def solve_basic_math(expr):
    try:
        expr = expr.replace("x", "*")
        result = eval(expr, {"__builtins__": {}})
        return f"The answer is {result} 😊"
    except Exception:
        return None

def solve_percentage(text):
    match = re.search(r"(\d+)\s*%\s*of\s*(\d+)", text)
    if not match:
        return None
    percent, value = map(float, match.groups())
    result = (percent / 100) * value
    return f"{percent}% of {value} is {result} 😊"

# ---------------- GUIDED SOLVER ----------------
def start_guided_equation(chat_id, equation):
    match = re.match(r"(\d*)x\s*\+\s*(\d+)\s*=\s*(\d+)", equation)
    if not match:
        send_message(chat_id, "I can help with equations like `2x + 4 = 10` 😊")
        return

    a = int(match.group(1) or 1)
    b = int(match.group(2))
    c = int(match.group(3))

    GUIDED_SESSIONS[chat_id] = {"a": a, "b": b, "c": c, "step": 1}

    send_message(
        chat_id,
        f"Let’s solve this step by step 😊\n\n"
        f"First, subtract {b} from both sides.\nWhat do you get?"
    )

def continue_guided(chat_id):
    session = GUIDED_SESSIONS.get(chat_id)
    if not session:
        return False

    if session["step"] == 1:
        session["step"] = 2
        send_message(chat_id, f"Nice 👍 Now divide both sides by {session['a']}.\nWhat is x?")
        return True

    if session["step"] == 2:
        x_val = (session["c"] - session["b"]) / session["a"]
        send_message(chat_id, f"Great job 🎉\n\nx = {x_val}")
        GUIDED_SESSIONS.pop(chat_id)
        return True

    return False

# ---------------- COMMAND HANDLER ----------------
def handle_command(text, chat_id, user_id, first_name):
    cmd = normalize(text)

    # Continue guided solving
    if continue_guided(chat_id):
        return

    # Greetings
    if cmd in ["hello", "hi", "hey"]:
        send_message(chat_id, f"Hey {first_name}! 😊 How can I help today?")
        return

    # Help
    if cmd == "help":
        send_message(
            chat_id,
            "Here’s what I can help you with 😊\n\n"
            "• Say hello\n"
            "• Save notes: save your note\n"
            "• List notes: list\n"
            "• Upload files or photos\n"
            "• Ask: what is cloud computing\n"
            "• Solve math: solve 12 + 8\n"
            "• Guided math: help me solve 2x + 4 = 10"
        )
        return

    # Math solver
    if cmd.startswith("solve "):
        result = solve_basic_math(cmd.replace("solve ", "", 1))
        if result:
            send_message(chat_id, result)
            return

    # Percentage solver
    percent_result = solve_percentage(cmd)
    if percent_result:
        send_message(chat_id, percent_result)
        return

    # Guided solver
    if cmd.startswith("help me solve"):
        equation = cmd.replace("help me solve", "").strip()
        start_guided_equation(chat_id, equation)
        return

    # Save note
    if cmd.startswith("save "):
        note = cmd.replace("save ", "", 1)
        table.put_item(
            Item={
                "user_id": str(user_id),
                "note_id": str(uuid.uuid4()),
                "note": note,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        send_message(chat_id, "Got it 👍 I’ve saved that for you.")
        return

    # List notes
    if cmd == "list":
        resp = table.scan()
        notes = [i["note"] for i in resp.get("Items", []) if i["user_id"] == str(user_id)]
        if not notes:
            send_message(chat_id, "I don’t remember anything yet.")
        else:
            send_message(chat_id, "Here’s what I remember:\n" + "\n".join(f"• {n}" for n in notes))
        return

    # Knowledge matching (FIXED)
    for key, answer in KNOWLEDGE.items():
        if key in cmd:
            send_message(chat_id, answer)
            return

    # Fallback
    send_message(
        chat_id,
        "Hmm 🤔 I’m not sure about that.\n"
        "You can say `help` to see what I can do."
    )

# ---------------- FILE HANDLER ----------------
def handle_file(message, chat_id, user_id):
    file_info = message.get("document") or message.get("photo", [None])[-1]
    if not file_info:
        return

    file_id = file_info["file_id"]
    file_name = file_info.get("file_name", str(uuid.uuid4()))

    file_path = requests.get(
        f"{TELEGRAM_API_URL}/getFile?file_id={file_id}", timeout=5
    ).json()["result"]["file_path"]

    file_data = requests.get(
        f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=10
    ).content

    s3.put_object(Bucket=BUCKET_NAME, Key=f"{user_id}/{file_name}", Body=file_data)
    send_message(chat_id, "Nice 😊 I’ve saved your file safely.")

# ---------------- LAMBDA ENTRY ----------------
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        message = body.get("message")

        if not message:
            return {"statusCode": 200, "body": "OK"}

        chat_id = message["chat"]["id"]
        user = message["from"]
        user_id = user["id"]
        first_name = user.get("first_name", "there")

        if "text" in message:
            handle_command(message["text"], chat_id, user_id, first_name)
        else:
            handle_file(message, chat_id, user_id)

        return {"statusCode": 200, "body": "OK"}

    except Exception as e:
        print("Error:", e)
        return {"statusCode": 500, "body": "Error"}
