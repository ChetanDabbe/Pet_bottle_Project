import cv2
import base64
import numpy as np
import time
import tempfile
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from detect import process_image

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
CORS(app, supports_credentials=True)

video_writer = None
is_recording = False
temp_video_path = None
has_uploaded = False

# Google Drive Folder ID
FOLDER_ID = "1gCUc24lLZvV2YllYPlzxXJ9dY6dO24si"  # Replace with your actual folder ID

# ✅ Decode credentials from base64 env var
def get_credentials_from_env():
    encoded_credentials = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    if not encoded_credentials:
        raise ValueError("Missing GOOGLE_CREDENTIALS_BASE64 environment variable")

    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_info = json.loads(decoded_credentials)

    return service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

# ✅ Upload to Google Drive
def upload_to_drive(file_path):
    print(f"[DRIVE] Uploading to Google Drive: {file_path}")
    credentials = get_credentials_from_env()
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype="video/avi")
    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    file_id = uploaded_file.get("id")
    service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()

    drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    print(f"[DRIVE] ✅ Uploaded: {drive_url}")
    return drive_url

# ✅ Stream image frames and record if enabled
@app.route('/stream', methods=['POST'])
def stream():
    global video_writer, is_recording

    try:
        data = request.json
        image_data = data['image'].split(",")[1]
        image_bytes = base64.b64decode(image_data)

        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("Decoded frame is None")

        processed_image_base64, defects = process_image(frame)

        if is_recording and video_writer:
            video_writer.write(frame)

        return jsonify({"processed_image": processed_image_base64, "defects": defects})

    except Exception as e:
        print("[ERROR] /stream:", e)
        return jsonify({"error": str(e)}), 500

# ✅ Start Recording
@app.route('/start_recording', methods=['POST'])
def start_recording():
    global video_writer, is_recording, temp_video_path, has_uploaded

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
    temp_video_path = temp_file.name
    temp_file.close()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 10  # Adjust this to match the frontend's sending frame rate
    resolution = (640, 480)

    video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, resolution)

    if not video_writer.isOpened():
        return jsonify({"error": "Video writer failed to open"}), 500

    is_recording = True
    has_uploaded = False
    print(f"[RECORDING] Started: {temp_video_path}")
    return jsonify({"message": "Recording started"})

# ✅ Stop Recording and Upload
@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global video_writer, is_recording, temp_video_path, has_uploaded

    if not is_recording or has_uploaded:
        return jsonify({"message": "Recording already stopped or uploaded"}), 400

    is_recording = False

    if video_writer:
        video_writer.release()
        video_writer = None

    try:
        has_uploaded = True
        drive_link = upload_to_drive(temp_video_path)
        os.remove(temp_video_path)
        return jsonify({"message": "Recording stopped", "video_link": drive_link})
    except Exception as e:
        print("[ERROR] Drive upload:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "✅ Flask backend running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render provides the PORT env variable
    app.run(host='0.0.0.0', port=port)
