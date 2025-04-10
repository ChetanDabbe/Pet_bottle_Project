# import cv2
# import base64
# import numpy as np
# import time
# import tempfile
# import os
# import json
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from detect import process_image  # Make sure this exists

# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# app = Flask(__name__)
# CORS(app)

# # Global state (ensure thread safety if scaling)
# video_writer = None
# is_recording = False
# temp_video_path = None
# has_uploaded = False
# timestamp = None

# FOLDER_ID = "1gCUc24lLZvV2YllYPlzxXJ9dY6dO24si"

# def get_credentials_from_env():
#     encoded_credentials = os.getenv("GOOGLE_CREDENTIALS_BASE64")
#     if not encoded_credentials:
#         raise ValueError("Missing GOOGLE_CREDENTIALS_BASE64 environment variable")
#     decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
#     service_account_info = json.loads(decoded_credentials)
#     return service_account.Credentials.from_service_account_info(
#         service_account_info,
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )

# def upload_to_drive(file_path, timestamp):
#     print(f"[DRIVE] Uploading to Google Drive: {file_path}")
#     credentials = get_credentials_from_env()
#     service = build("drive", "v3", credentials=credentials)

#     file_metadata = {
#         "name": f"PET_Bottle_Scan_{timestamp}.mp4",
#         "parents": [FOLDER_ID]
#     }
#     media = MediaFileUpload(file_path, mimetype="video/mp4")
#     uploaded_file = service.files().create(
#         body=file_metadata, media_body=media, fields="id"
#     ).execute()

#     file_id = uploaded_file.get("id")
#     service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()
#     drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
#     print(f"[DRIVE] ✅ Uploaded: {drive_url}")
#     return drive_url

# @app.route('/stream', methods=['POST'])
# def stream():
#     global video_writer, is_recording
#     try:
#         if 'image' not in request.files:
#             return jsonify({"error": "No image file in request"}), 400

#         file = request.files['image']
#         frame_bytes = file.read()
#         nparr = np.frombuffer(frame_bytes, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if frame is None:
#             return jsonify({"error": "Failed to decode frame"}), 400

#         print(f"[STREAM] Frame received: {frame.shape}")
#         processed_image_base64, defects = process_image(frame)

#         if is_recording and video_writer:
#             video_writer.write(frame)

#         return jsonify({
#             "processed_image": processed_image_base64,
#             "defects": defects
#         })

#     except Exception as e:
#         print("[ERROR] /stream:", e)
#         return jsonify({"error": str(e)}), 500

# @app.route('/start_recording', methods=['POST'])
# def start_recording():
#     global video_writer, is_recording, temp_video_path, has_uploaded, timestamp
#     if is_recording:
#         return jsonify({"message": "Recording already started"}), 400

#     timestamp = time.strftime("%Y%m%d-%H%M%S")
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
#     temp_video_path = temp_file.name
#     temp_file.close()

#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     fps = 10
#     resolution = (640, 480)
#     video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, resolution)

#     if not video_writer.isOpened():
#         return jsonify({"error": "Video writer failed to open"}), 500

#     is_recording = True
#     has_uploaded = False
#     print(f"[RECORDING] Started: {temp_video_path}")
#     return jsonify({"message": "Recording started"})

# @app.route('/stop_recording', methods=['POST'])
# def stop_recording():
#     global video_writer, is_recording, temp_video_path, has_uploaded, timestamp

#     if not is_recording:
#         return jsonify({"message": "Not currently recording"}), 400
#     if has_uploaded:
#         return jsonify({"message": "Already uploaded"}), 400

#     is_recording = False

#     if video_writer:
#         video_writer.release()
#         video_writer = None

#     try:
#         has_uploaded = True
#         drive_link = upload_to_drive(temp_video_path, timestamp)
#         os.remove(temp_video_path)
#         return jsonify({"message": "Recording stopped", "video_link": drive_link})
#     except Exception as e:
#         print("[ERROR] Drive upload:", e)
#         return jsonify({"error": str(e)}), 500

# @app.route('/')
# def home():
#     return "✅ Flask backend is running!"

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host='0.0.0.0', port=port)


import cv2
import base64
import numpy as np
import time
import tempfile
import os
import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from detect import process_image  # your YOLOv8n logic

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
CORS(app)

video_writer = None
is_recording = False
temp_video_path = None
has_uploaded = False
timestamp = None
frame_count = 0

FOLDER_ID = "1gCUc24lLZvV2YllYPlzxXJ9dY6dO24si"  # your Drive folder

def get_credentials_from_env():
    encoded_credentials = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    if not encoded_credentials:
        raise ValueError("Missing GOOGLE_CREDENTIALS_BASE64 env var")
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_info = json.loads(decoded_credentials)
    return service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

def upload_to_drive(file_path, timestamp):
    print(f"[DRIVE] Uploading to Google Drive: {file_path}")
    credentials = get_credentials_from_env()
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": f"PET_Bottle_Scan_{timestamp}.mp4",
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype="video/mp4")
    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    file_id = uploaded_file.get("id")
    service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()
    drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    print(f"[DRIVE] ✅ Uploaded: {drive_url}")
    return drive_url

@app.route('/stream', methods=['POST'])
def stream():
    global video_writer, is_recording, frame_count
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file in request"}), 400

        file = request.files['image']
        frame_bytes = file.read()
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Failed to decode frame"}), 400

        frame = cv2.resize(frame, (416, 416))  # downsized for less RAM
        print(f"[STREAM] Frame received: {frame.shape}")
        processed_image_base64, defects = process_image(frame)

        if is_recording and video_writer:
            frame_count += 1
            if frame_count % 3 == 0:
                video_writer.write(frame)

        return jsonify({
            "processed_image": processed_image_base64,
            "defects": defects
        })

    except Exception as e:
        print("[ERROR] /stream:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global video_writer, is_recording, temp_video_path, has_uploaded, timestamp, frame_count

    if is_recording:
        return jsonify({"message": "Recording already started"}), 400

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_video_path = temp_file.name
    temp_file.close()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 10
    resolution = (416, 416)

    video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, resolution)
    if not video_writer.isOpened():
        return jsonify({"error": "Video writer failed to open"}), 500

    is_recording = True
    has_uploaded = False
    frame_count = 0

    print(f"[RECORDING] Started: {temp_video_path}")
    return jsonify({"message": "Recording started"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global video_writer, is_recording, temp_video_path, has_uploaded, timestamp

    if not is_recording:
        return jsonify({"message": "Not currently recording"}), 400
    if has_uploaded:
        return jsonify({"message": "Already uploaded"}), 400

    is_recording = False
    if video_writer:
        video_writer.release()
        video_writer = None

    def upload_in_background():
        try:
            link = upload_to_drive(temp_video_path, timestamp)
            os.remove(temp_video_path)
            print("[UPLOAD DONE]", link)
        except Exception as e:
            print("[UPLOAD ERROR]", e)

    has_uploaded = True
    threading.Thread(target=upload_in_background).start()

    return jsonify({"message": "Recording stopped. Uploading in background."})

@app.route('/')
def home():
    return "✅ Flask backend is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
