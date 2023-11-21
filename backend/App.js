import React from 'react';

function App() {
  return (
    <div>
      <h1>Camera 1</h1>
      <video width="640" height="480" controls autoPlay>
        <source src="http://localhost:5000/video_feed_cam1" type="multipart/x-mixed-replace; boundary=frame" />
      </video>

      <h1>Camera 2</h1>
      <video width="640" height="480" controls autoPlay>
        <source src="http://localhost:5000/video_feed_cam2" type="multipart/x-mixed-replace; boundary=frame" />
      </video>
    </div>
  );
}

export default App;
