# # import cv2
# # import base64
# # import numpy as np
# # import os
# # import time
# # from flask import Flask, request, jsonify
# # from flask_cors import CORS
# # from detect import process_image

# # from google.oauth2 import service_account
# # from googleapiclient.discovery import build
# # from googleapiclient.http import MediaFileUpload

# # app = Flask(__name__)
# # CORS(app, supports_credentials=True)

# # VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'recorded_videos')
# # os.makedirs(VIDEO_DIR, exist_ok=True)

# # video_writer = None
# # is_recording = False
# # output_video_path = None

# # # Google Drive shared folder ID
# # FOLDER_ID = "1gCUc24lLZvV2YllYPlzxXJ9dY6dO24si"

# # def upload_to_drive(file_path):
# #     print(f"[DRIVE] Uploading to Google Drive: {file_path}")
# #     credentials = service_account.Credentials.from_service_account_file(
# #         "credentials.json",
# #         scopes=["https://www.googleapis.com/auth/drive"]
# #     )
# #     service = build("drive", "v3", credentials=credentials)

# #     file_metadata = {
# #         "name": os.path.basename(file_path),
# #         "parents": [FOLDER_ID]
# #     }

# #     media = MediaFileUpload(file_path, mimetype="video/mp4")
# #     uploaded_file = service.files().create(
# #         body=file_metadata, media_body=media, fields="id"
# #     ).execute()

# #     file_id = uploaded_file.get("id")
# #     service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()

# #     drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
# #     print(f"[DRIVE] Uploaded successfully: {drive_url}")
# #     return drive_url

# # @app.route('/stream', methods=['POST'])
# # def stream():
# #     global video_writer, is_recording
# #     try:
# #         data = request.json
# #         image_data = data['image'].split(",")[1]
# #         image_bytes = base64.b64decode(image_data)
# #         nparr = np.frombuffer(image_bytes, np.uint8)
# #         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# #         if frame is None:
# #             raise ValueError("Decoded frame is None.")

# #         processed_image_base64, defects = process_image(frame)

# #         if is_recording and video_writer:
# #             video_writer.write(frame)
# #             print(f"[STREAM] Frame written | Detected: {defects}")
# #         else:
# #             print(f"[STREAM] Frame received (not recorded) | Detected: {defects}")

# #         return jsonify({"processed_image": processed_image_base64, "defects": defects})

# #     except Exception as e:
# #         print(f"[ERROR] Error in /stream: {e}")
# #         return jsonify({"error": str(e)}), 500

# # @app.route('/start_recording', methods=['POST'])
# # def start_recording():
# #     global video_writer, is_recording, output_video_path

# #     timestamp = time.strftime("%Y%m%d-%H%M%S")
# #     output_video_path = os.path.join(VIDEO_DIR, f"output_{timestamp}.mp4")

# #     fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # mp4 codec
# #     video_writer = cv2.VideoWriter(output_video_path, fourcc, 10, (640, 480))

# #     if not video_writer.isOpened():
# #         print("[ERROR] Failed to start video writer")
# #         return jsonify({"error": "Failed to start video recording"}), 500

# #     is_recording = True
# #     print(f"[SCAN] ✅ Recording started: {output_video_path}")
# #     return jsonify({"message": "Recording started"})

# # @app.route('/stop_recording', methods=['POST'])
# # def stop_recording():
# #     global video_writer, is_recording, output_video_path

# #     if video_writer:
# #         video_writer.release()
# #         video_writer = None

# #     is_recording = False
# #     print("[SCAN] ⏹️ Recording stopped")

# #     try:
# #         drive_link = upload_to_drive(output_video_path)
# #         return jsonify({"message": "Recording stopped", "video_link": drive_link})
# #     except Exception as e:
# #         print(f"[ERROR] Drive upload failed: {e}")
# #         return jsonify({"message": "Recording stopped", "error": str(e)}), 500

# # @app.route('/')
# # def home():
# #     return "🎉 Flask backend is running!"

# # if __name__ == '__main__':
# #     port = int(os.environ.get("PORT", 10000))
# #     app.run(debug=True, host='0.0.0.0', port=port)



# import cv2
# import base64
# import numpy as np
# import os
# import time
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from detect import process_image

# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# app = Flask(__name__)
# CORS(app, supports_credentials=True)

# # ✅ Cross-platform video directory
# VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'recorded_videos')
# os.makedirs(VIDEO_DIR, exist_ok=True)

# # ✅ Google Drive shared folder ID
# FOLDER_ID = "1gCUc24lLZvV2YllYPlzxXJ9dY6dO24si"

# video_writer = None
# is_recording = False
# output_video_path = None

# def upload_to_drive(file_path):
#     try:
#         credentials = service_account.Credentials.from_service_account_file(
#             "credentials.json",
#             scopes=["https://www.googleapis.com/auth/drive"]
#         )
#         service = build("drive", "v3", credentials=credentials)

#         file_metadata = {
#             "name": os.path.basename(file_path),
#             "parents": [FOLDER_ID]
#         }

#         media = MediaFileUpload(file_path, mimetype="video/avi")
#         uploaded_file = service.files().create(
#             body=file_metadata, media_body=media, fields="id"
#         ).execute()

#         file_id = uploaded_file.get("id")
#         service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()

#         drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
#         print(f"[DRIVE] ✅ Uploaded successfully: {drive_url}")
#         return drive_url

#     except Exception as e:
#         print(f"[DRIVE] ❌ Upload failed: {e}")
#         raise e

# @app.route('/stream', methods=['POST'])
# def stream():
#     global video_writer, is_recording

#     try:
#         data = request.json
#         image_data = data['image'].split(",")[1]  
#         image_bytes = base64.b64decode(image_data)

#         nparr = np.frombuffer(image_bytes, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if frame is None:
#             raise ValueError("Decoded frame is None. Check base64 encoding.")

#         processed_image_base64, defects = process_image(frame)

#         if is_recording and video_writer is not None:
#             video_writer.write(frame)

#         return jsonify({"processed_image": processed_image_base64, "defects": defects})

#     except Exception as e:
#         print("[STREAM] ❌ Error processing frame:", e)
#         return jsonify({"error": str(e)}), 500

# @app.route('/start_recording', methods=['POST'])
# def start_recording():
#     global video_writer, is_recording, output_video_path

#     timestamp = time.strftime("%Y%m%d-%H%M%S")
#     output_video_path = os.path.join(VIDEO_DIR, f"output_{timestamp}.avi")

#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     video_writer = cv2.VideoWriter(output_video_path, fourcc, 10, (640, 480))

#     if not video_writer.isOpened():
#         return jsonify({"error": "Failed to start video recording"}), 500

#     is_recording = True
#     print(f"[SCAN] ✅ Recording started: {output_video_path}")
#     return jsonify({"message": "Recording started"})

# @app.route('/stop_recording', methods=['POST'])
# def stop_recording():
#     global video_writer, is_recording, output_video_path

#     if video_writer:
#         video_writer.release()
#         video_writer = None

#     is_recording = False
#     print("[SCAN] ⏹️ Recording stopped")

#     try:
#         drive_link = upload_to_drive(output_video_path)
#         return jsonify({
#             "message": "Recording stopped",
#             "video_link": drive_link
#         })
#     except Exception as e:
#         return jsonify({
#             "message": "Recording stopped, but failed to upload",
#             "error": str(e)
#         }), 500

# @app.route('/get_videos', methods=['GET'])
# def get_videos():
#     try:
#         video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".avi")]
#         video_list = [{"filename": f, "url": f"http://localhost:5000/videos/{f}"} for f in video_files]
#         return jsonify({"videos": video_list})
#     except Exception as e:
#         print("Error listing videos:", e)
#         return jsonify({"error": str(e)}), 500

# @app.route('/videos/<filename>', methods=['GET'])
# def get_video(filename):
#     return send_from_directory(VIDEO_DIR, filename)

# @app.route('/')
# def home():
#     return "🎉 Flask backend is running!"

# if __name__ == '__main__':
#     app.run(debug=True)



import cv2
import base64
import numpy as np
import time
import tempfile
import os
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

FOLDER_ID = "1gCUc24lLZvV2YllYPlzxXJ9dY6dO24si"  # Your Drive folder ID

def upload_to_drive(file_path):
    print(f"[DRIVE] Uploading to Google Drive: {file_path}")
    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
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

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global video_writer, is_recording, temp_video_path, has_uploaded

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".avi")
    temp_video_path = temp_file.name
    temp_file.close()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 20  # Adjust to your frontend's frame rate
    resolution = (640, 480)

    video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, resolution)

    if not video_writer.isOpened():
        return jsonify({"error": "Video writer failed to open"}), 500

    is_recording = True
    has_uploaded = False
    print(f"[RECORDING] Started: {temp_video_path}")
    return jsonify({"message": "Recording started"})

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
    app.run(debug=True)
