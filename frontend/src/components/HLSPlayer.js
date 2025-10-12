// frontend/src/components/HLSPlayer.js
import React, { useEffect, useRef } from 'react';

const HLSPlayer = ({ streamUrl, autoPlay = true, controls = true, width = "100%", height = "auto" }) => {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);

  useEffect(() => {
    let hls = null;

    const initHLS = async () => {
      try {
        // Dynamic import for HLS.js to avoid issues if not installed
        const Hls = (await import('hls.js')).default;

        if (Hls.isSupported() && videoRef.current) {
          hls = new Hls({
            enableWorker: false,
            lowLatencyMode: true,
            backBufferLength: 90,
          });

          hlsRef.current = hls;

          hls.loadSource(streamUrl);
          hls.attachMedia(videoRef.current);

          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            if (autoPlay) {
              videoRef.current.play().catch(e => {
                console.warn('Auto-play was prevented:', e);
              });
            }
          });

          hls.on(Hls.Events.ERROR, (event, data) => {
            console.error('HLS Error:', data);

            if (data.fatal) {
              switch (data.type) {
                case Hls.ErrorTypes.NETWORK_ERROR:
                  // Try to recover network error
                  console.log('Trying to recover network error...');
                  hls.startLoad();
                  break;
                case Hls.ErrorTypes.MEDIA_ERROR:
                  console.log('Trying to recover media error...');
                  hls.recoverMediaError();
                  break;
                default:
                  // Cannot recover, destroy and recreate
                  console.log('Cannot recover, destroying HLS instance...');
                  destroyHLS();
                  initHLS();
                  break;
              }
            }
          });
        } else if (videoRef.current && videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
          // Native HLS support (Safari)
          videoRef.current.src = streamUrl;
          if (autoPlay) {
            videoRef.current.play().catch(e => {
              console.warn('Auto-play was prevented:', e);
            });
          }
        } else {
          console.error('HLS is not supported in this browser');
        }
      } catch (error) {
        console.error('Failed to load HLS.js:', error);
        // Fallback: try native video element
        if (videoRef.current) {
          videoRef.current.src = streamUrl;
        }
      }
    };

    const destroyHLS = () => {
      if (hls) {
        hls.destroy();
        hlsRef.current = null;
      }
    };

    if (streamUrl) {
      initHLS();
    }

    return () => {
      destroyHLS();
    };
  }, [streamUrl, autoPlay]);

  return (
    <div className="hls-player-container">
      <video
        ref={videoRef}
        controls={controls}
        width={width}
        height={height}
        style={{
          width: width,
          height: height,
          backgroundColor: '#000',
          borderRadius: '8px'
        }}
        playsInline
        muted={autoPlay} // Usually required for auto-play
      />
    </div>
  );
};

export default HLSPlayer;
