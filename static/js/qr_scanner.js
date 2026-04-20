/**
 * PLASU Smart Attendance System — QR Scanner
 * Wraps the camera + jsQR library for student QR scanning.
 * Usage: PLASU.QRScanner.start('video-element-id', callback)
 */
(function (root) {
  'use strict';

  const QRScanner = {
    stream: null,
    animFrame: null,
    active: false,

    /**
     * Start camera and scan for QR codes.
     * @param {string} videoId  — id of <video> element to use
     * @param {Function} onFound — called with decoded URL string
     * @param {Function} onError — called with error message
     */
    start: function (videoId, onFound, onError) {
      const video = document.getElementById(videoId);
      if (!video) { onError && onError('Video element not found'); return; }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        onError && onError('Camera not supported in this browser');
        return;
      }

      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(function (stream) {
          QRScanner.stream = stream;
          QRScanner.active = true;
          video.srcObject = stream;
          video.setAttribute('playsinline', true);
          video.play();
          video.addEventListener('loadedmetadata', function () {
            QRScanner._tick(video, onFound);
          });
        })
        .catch(function (err) {
          onError && onError('Camera access denied: ' + err.message);
        });
    },

    _tick: function (video, onFound) {
      if (!QRScanner.active) return;
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        const canvas = document.createElement('canvas');
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

        // Use jsQR if available
        if (typeof jsQR !== 'undefined') {
          const code = jsQR(imageData.data, imageData.width, imageData.height, {
            inversionAttempts: 'dontInvert',
          });
          if (code && code.data) {
            QRScanner.stop();
            onFound && onFound(code.data);
            return;
          }
        }
      }
      QRScanner.animFrame = requestAnimationFrame(function () {
        QRScanner._tick(video, onFound);
      });
    },

    stop: function () {
      QRScanner.active = false;
      if (QRScanner.animFrame) cancelAnimationFrame(QRScanner.animFrame);
      if (QRScanner.stream) {
        QRScanner.stream.getTracks().forEach(function (t) { t.stop(); });
        QRScanner.stream = null;
      }
    },
  };

  root.PLASU = root.PLASU || {};
  root.PLASU.QRScanner = QRScanner;
})(window);
