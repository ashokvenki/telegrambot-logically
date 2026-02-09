import json
import os
import boto3
import uuid
import requests
import re
import logging
import traceback
from datetime import datetime

# ---------------- LOGGING ----------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(level, request_id=None, user_id=None, command=None, outcome=None, error=None):
    log_entry = {
        "level": level,
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "user_id": user_id,
        "command": command,
        "outcome": outcome,
        "error": error
    }

    # CloudWatch IMPORTANT: must be JSON text
    message = json.dumps(log_entry)

    if level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)

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

    send_message(chat_id, f"First subtract {b} from both sides. What do you get? 😊")

def continue_guided(chat_id):
    session = GUIDED_SESSIONS.get(chat_id)
    if not session:
        return False

    if session["step"] == 1:
        session["step"] = 2
        send_message(chat_id, f"Now divide both sides by {session['a']}. What is x?")
        return True

    if session["step"] == 2:
        x_val = (session["c"] - session["b"]) / session["a"]
        send_message(chat_id, f"Great job 🎉 x = {x_val}")
        GUIDED_SESSIONS.pop(chat_id)
        return True

    return False

# ---------------- COMMAND HANDLER ----------------
def handle_command(text, chat_id, user_id, first_name):
    cmd = normalize(text)

    if cmd == "crash":
        raise Exception("Intentional test error for CloudWatch alarm")

    if continue_guided(chat_id):
        return

    if cmd in ["hello", "hi", "hey"]:
        send_message(chat_id, f"Hey {first_name}! 😊 How can I help today?")
        return

    if cmd == "help":
        send_message(chat_id,
            "Here’s what I can help you with 😊\n"
            "• save <note>\n"
            "• list\n"
            "• ask questions\n"
            "• Solve math: solve 12 + 8\n"
            "• Upload files/photos\n"
            "• type crash to test monitoring 😄"
        )
        return

    if cmd.startswith("solve "):
        result = solve_basic_math(cmd.replace("solve ", "", 1))
        if result:
            send_message(chat_id, result)
            return

    percent_result = solve_percentage(cmd)
    if percent_result:
        send_message(chat_id, percent_result)
        return

    if cmd.startswith("help me solve"):
        equation = cmd.replace("help me solve", "").strip()
        start_guided_equation(chat_id, equation)
        return

    if cmd.startswith("save "):
        note = cmd.replace("save ", "", 1)
        table.put_item(Item={
            "user_id": str(user_id),
            "note_id": str(uuid.uuid4()),
            "note": note,
            "created_at": datetime.utcnow().isoformat()
        })
        send_message(chat_id, "Saved! 📝")
        return

    if cmd == "list":
        resp = table.scan()
        notes = [i["note"] for i in resp.get("Items", []) if i["user_id"] == str(user_id)]
        if not notes:
            send_message(chat_id, "No notes yet.")
        else:
            send_message(chat_id, "\n".join(f"• {n}" for n in notes))
        return

    for key, answer in KNOWLEDGE.items():
        if key in cmd:
            send_message(chat_id, answer)
            return

    send_message(chat_id, "I didn't understand that. Type help 😊")

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
    send_message(chat_id, "File saved 😊")

# ---------------- LAMBDA ENTRY ----------------
def lambda_handler(event, context):

    try:
        body = json.loads(event.get("body", "{}"))

        if "message" not in body:
            return {"statusCode": 200, "body": "no message"}

        message = body["message"]
        chat_id = message["chat"]["id"]

        user = message.get("from", {})
        user_id = user.get("id", "unknown")
        first_name = user.get("first_name", "there")

        text = message.get("text", "").lower().strip()
        request_id = context.aws_request_id

        handle_command(text, chat_id, user_id, first_name)

        log_event("INFO", request_id, user_id, text, "success")

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        print(traceback.format_exc())
        log_event("ERROR", context.aws_request_id, user_id if 'user_id' in locals() else "unknown",
                  text if 'text' in locals() else "unknown", "failure", str(e))
        return {"statusCode": 200, "body": "error handled"}
