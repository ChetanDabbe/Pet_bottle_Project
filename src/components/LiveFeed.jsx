import React, { useRef, useState, useEffect, useCallback } from "react";
import axios from "axios";
import "../styles/livefeed.css";

// CRA-compatible environment variable
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function LiveFeed() {
  const [scanning, setScanning] = useState(false);
  const [videoLink, setVideoLink] = useState("");
  const videoRef = useRef(null);
  const canvasRef = useRef(null); // Needed for drawing frames
  const mediaStream = useRef(null);
  const intervalId = useRef(null);

  const captureFrame = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !scanning) return;

    const context = canvasRef.current.getContext("2d");
    context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);

    canvasRef.current.toBlob(async (blob) => {
      if (!blob) return;

      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");

      try {
        const response = await axios.post(`${BACKEND_URL}/stream`, formData);
        const { processed_image, defects } = response.data;
        console.log("✅ Defects:", defects);
        // Optional: you can display processed_image if needed
      } catch (err) {
        console.error("❌ Stream error:", err);
      }
    }, "image/jpeg");
  }, [scanning]);

  const startStreaming = useCallback(async () => {
    try {
      setVideoLink("");
      mediaStream.current = await navigator.mediaDevices.getUserMedia({ video: true });

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream.current;
      }

      intervalId.current = setInterval(captureFrame, 1000); // 1 frame/sec

      const res = await axios.post(`${BACKEND_URL}/start_recording`);
      console.log("🎥 Recording started:", res.data.message);
    } catch (err) {
      console.error("❌ Camera or backend error:", err);
    }
  }, [captureFrame]);

  const stopStreaming = useCallback(async () => {
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach(track => track.stop());
      mediaStream.current = null;
    }

    if (intervalId.current) {
      clearInterval(intervalId.current);
      intervalId.current = null;
    }

    try {
      const res = await axios.post(`${BACKEND_URL}/stop_recording`);
      console.log("🛑 Recording stopped:", res.data.message);

      if (res.data.video_link) {
        setVideoLink(res.data.video_link);
        window.open(res.data.video_link, "_blank");
      }
    } catch (error) {
      console.error("❌ Error stopping recording:", error);
    }
  }, []);

  useEffect(() => {
    if (scanning) {
      startStreaming();
    } else {
      stopStreaming();
    }

    return () => stopStreaming(); // cleanup on unmount
  }, [scanning, startStreaming, stopStreaming]);

  return (
    <div className="live-feed-container">
      <h4 className="live-feed-title">Live Scanning</h4>

      <div className="live-feed-box">
        {scanning ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="live-feed-media"
              width="640"
              height="480"
            />
            <canvas
              ref={canvasRef}
              width="640"
              height="480"
              style={{ display: "none" }}
            />
          </>
        ) : (
          <div className="live-feed-placeholder">📷 Live feed will appear here</div>
        )}
        <div className="moving-line"></div>
      </div>

      <div className="live-feed-buttons">
        <button
          onClick={() => setScanning(prev => !prev)}
          className="live-feed-btn"
        >
          {scanning ? "Stop Scan" : "Start Scan"}
        </button>

        {videoLink && (
          <a
            href={videoLink}
            target="_blank"
            rel="noreferrer"
            className="video-link"
          >
            🔗 View Recorded Video
          </a>
        )}
      </div>
    </div>
  );
}

export default LiveFeed;
