// // import React, { useRef, useState, useEffect, useCallback } from "react";
// // import axios from "axios";
// // import "../styles/livefeed.css";

// // function LiveFeed() {
// //   const [scanning, setScanning] = useState(false);
// //   const [videoLink, setVideoLink] = useState("");
// //   const videoRef = useRef(null);
// //   const mediaStream = useRef(null);
// //   const intervalId = useRef(null);

// //   const captureFrame = useCallback(async () => {
// //     if (!videoRef.current) return;

// //     const canvas = document.createElement("canvas");
// //     canvas.width = videoRef.current.videoWidth || 640;
// //     canvas.height = videoRef.current.videoHeight || 480;
// //     const ctx = canvas.getContext("2d");
// //     ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

// //     const imageData = canvas.toDataURL("image/jpeg");

// //     try {
// //       const res = await axios.post(
// //         `${process.env.REACT_APP_BACKEND_URL}/stream`,
// //         { image: imageData }
// //       );
// //       console.log("📸 Frame sent | Defects:", res.data.defects);
// //     } catch (error) {
// //       console.error("❌ Error streaming frame:", error);
// //     }
// //   }, []);

// //   const startStreaming = useCallback(async () => {
// //     try {
// //       setVideoLink("");
// //       mediaStream.current = await navigator.mediaDevices.getUserMedia({ video: true });

// //       if (videoRef.current) {
// //         videoRef.current.srcObject = mediaStream.current;
// //       }

// //       intervalId.current = setInterval(captureFrame, 1000); // 1 second frame interval

// //       const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/start_recording`);
// //       console.log("🎥 Recording started:", res.data.message);
// //     } catch (err) {
// //       console.error("❌ Camera or backend error:", err);
// //     }
// //   }, [captureFrame]);

// //   const stopStreaming = useCallback(async () => {
// //     if (mediaStream.current) {
// //       mediaStream.current.getTracks().forEach(track => track.stop());
// //       mediaStream.current = null;
// //     }

// //     if (intervalId.current) {
// //       clearInterval(intervalId.current);
// //       intervalId.current = null;
// //     }

// //     try {
// //       const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/stop_recording`);
// //       console.log("🛑 Recording stopped:", res.data.message);
// //       if (res.data.video_link) {
// //         setVideoLink(res.data.video_link);
// //         console.log("📁 Video saved to Drive:", res.data.video_link);
// //       }
// //     } catch (error) {
// //       console.error("❌ Error stopping recording:", error);
// //     }
// //   }, []);

// //   useEffect(() => {
// //     if (scanning) {
// //       startStreaming();
// //     } else {
// //       stopStreaming();
// //     }
// //     return () => stopStreaming(); // cleanup on unmount
// //   }, [scanning, startStreaming, stopStreaming]);

// //   return (
// //     <div className="live-feed-container">
// //       <h4 className="live-feed-title">Live Scanning</h4>

// //       <div className="live-feed-box">
// //         {scanning ? (
// //           <video ref={videoRef} autoPlay playsInline muted className="live-feed-media" />
// //         ) : (
// //           <div className="live-feed-placeholder">📷 Live feed will appear here</div>
// //         )}
// //         <div className="moving-line"></div>
// //       </div>

// //       <div className="live-feed-buttons">
// //         <button onClick={() => setScanning(prev => !prev)} className="live-feed-btn">
// //           {scanning ? "Stop Scan" : "Start Scan"}
// //         </button>

// //         {videoLink && (
// //           <a href={videoLink} target="_blank" rel="noreferrer" className="video-link">
// //             🔗 View Recorded Video
// //           </a>
// //         )}
// //       </div>
// //     </div>
// //   );
// // }

// // export default LiveFeed;
// import React, { useRef, useState, useEffect, useCallback } from "react";
// import axios from "axios";
// import "../styles/livefeed.css";

// function LiveFeed() {
//   const [scanning, setScanning] = useState(false);
//   const [videoLink, setVideoLink] = useState("");
//   const videoRef = useRef(null);
//   const mediaStream = useRef(null);
//   const intervalId = useRef(null);

//   const captureFrame = useCallback(async () => {
//     if (!videoRef.current) return;

//     const canvas = document.createElement("canvas");
//     canvas.width = videoRef.current.videoWidth || 640;
//     canvas.height = videoRef.current.videoHeight || 480;
//     const ctx = canvas.getContext("2d");
//     ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

//     const imageData = canvas.toDataURL("image/jpeg");

//     try {
//       const res = await axios.post(
//         `${process.env.REACT_APP_BACKEND_URL}/stream`,
//         { image: imageData }
//       );
//       console.log("📸 Frame sent | Defects:", res.data.defects);
//     } catch (error) {
//       console.error("❌ Error streaming frame:", error);
//     }
//   }, []);

//   const startStreaming = useCallback(async () => {
//     try {
//       setVideoLink(""); // clear old link
//       mediaStream.current = await navigator.mediaDevices.getUserMedia({ video: true });

//       if (videoRef.current) {
//         videoRef.current.srcObject = mediaStream.current;
//       }

//       intervalId.current = setInterval(captureFrame, 1000); // 1 second interval
//       const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/start_recording`);
//       console.log("🎥 Recording started:", res.data.message);
//     } catch (err) {
//       console.error("❌ Camera or backend error:", err);
//     }
//   }, [captureFrame]);

//   const stopStreaming = useCallback(async () => {
//     if (mediaStream.current) {
//       mediaStream.current.getTracks().forEach(track => track.stop());
//       mediaStream.current = null;
//     }

//     if (intervalId.current) {
//       clearInterval(intervalId.current);
//       intervalId.current = null;
//     }

//     try {
//       const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/stop_recording`);
//       console.log("🛑 Recording stopped:", res.data.message);

//       if (res.data.video_link) {
//         setVideoLink(res.data.video_link);
//         window.open(res.data.video_link, "_blank"); // Auto-open the latest video
//       }
//     } catch (error) {
//       console.error("❌ Error stopping recording:", error);
//     }
//   }, []);

//   useEffect(() => {
//     if (scanning) {
//       startStreaming();
//     } else {
//       stopStreaming();
//     }
//     return () => stopStreaming();
//   }, [scanning, startStreaming, stopStreaming]);

//   return (
//     <div className="live-feed-container">
//       <h4 className="live-feed-title">Live Scanning</h4>

//       <div className="live-feed-box">
//         {scanning ? (
//           <video ref={videoRef} autoPlay playsInline muted className="live-feed-media" />
//         ) : (
//           <div className="live-feed-placeholder">📷 Live feed will appear here</div>
//         )}
//         <div className="moving-line"></div>
//       </div>

//       <div className="live-feed-buttons">
//         <button onClick={() => setScanning(prev => !prev)} className="live-feed-btn">
//           {scanning ? "Stop Scan" : "Start Scan"}
//         </button>

//         {videoLink && (
//           <a
//             href={videoLink}
//             target="_blank"
//             rel="noreferrer"
//             className="video-link"
//           >
//             🔗 View Recorded Video
//           </a>
//         )}
//       </div>
//     </div>
//   );
// }

// export default LiveFeed;


import React, { useRef, useState, useEffect, useCallback } from "react";
import axios from "axios";
import "../styles/livefeed.css";

function LiveFeed() {
  const [scanning, setScanning] = useState(false);
  const [videoLink, setVideoLink] = useState("");
  const videoRef = useRef(null);
  const mediaStream = useRef(null);
  const intervalId = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const captureFrame = useCallback(async () => {
    if (!videoRef.current) return;

    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");

    try {
      const res = await axios.post(`${BACKEND_URL}/stream`, {
        image: imageData,
      });
      console.log("📸 Frame sent | Defects:", res.data.defects);
    } catch (error) {
      console.error("❌ Error streaming frame:", error);
    }
  }, [BACKEND_URL]);

  const startStreaming = useCallback(async () => {
    try {
      setVideoLink(""); // Clear old link
      mediaStream.current = await navigator.mediaDevices.getUserMedia({ video: true });

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream.current;
      }

      intervalId.current = setInterval(captureFrame, 1000); // Send frame every second

      const res = await axios.post(`${BACKEND_URL}/start_recording`);
      console.log("🎥 Recording started:", res.data.message);
    } catch (err) {
      console.error("❌ Camera or backend error:", err);
    }
  }, [captureFrame, BACKEND_URL]);

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
  }, [BACKEND_URL]);

  useEffect(() => {
    if (scanning) {
      startStreaming();
    } else {
      stopStreaming();
    }

    return () => stopStreaming();
  }, [scanning, startStreaming, stopStreaming]);

  return (
    <div className="live-feed-container">
      <h4 className="live-feed-title">Live Scanning</h4>

      <div className="live-feed-box">
        {scanning ? (
          <video ref={videoRef} autoPlay playsInline muted className="live-feed-media" />
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
