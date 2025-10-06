import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const DEFAULT_TMTB_ENDPOINT = "http://localhost:8001/count";

const getEndpoint = () => {
  const raw = process.env.REACT_APP_TMTB_API_URL;
  if (!raw || raw.trim() === "") return DEFAULT_TMTB_ENDPOINT;
  return raw.replace(/\/$/, "");
};

const normaliseCount = (payload) => {
  if (!payload) return null;
  const candidates = [
    payload.crowd_count,
    payload.count,
    payload.predicted_count,
    payload.people,
  ];

  for (const value of candidates) {
    if (typeof value === "number" && Number.isFinite(value)) {
      return Math.round(value);
    }
    if (typeof value === "string") {
      const parsed = Number(value);
      if (!Number.isNaN(parsed)) {
        return Math.round(parsed);
      }
    }
  }

  return null;
};

const formatBytes = (bytes) => {
  if (typeof bytes !== "number" || Number.isNaN(bytes)) return "-";
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
};

function VMambaUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [results, setResults] = useState(null);
  const [heatmapUrl, setHeatmapUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [requestMeta, setRequestMeta] = useState(null);
  const fileInputRef = useRef(null);

  const endpoint = useMemo(() => getEndpoint(), []);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileSelect = useCallback(
    (event) => {
      const file = event.target.files?.[0];
      if (!file) return;

      if (!file.type.startsWith("image/")) {
        setError("Please select a valid image file (JPEG, PNG, BMP, TIFF).");
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }

      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setResults(null);
      setHeatmapUrl(null);
      setRequestMeta(null);
    },
    [previewUrl]
  );

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      if (event.dataTransfer.files?.length) {
        const file = event.dataTransfer.files[0];
        handleFileSelect({ target: { files: [file] } });
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError(null);
    setHeatmapUrl(null);
    setRequestMeta({ startedAt: Date.now(), fileName: selectedFile.name });

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const normalized = {
        ...data,
        crowd_count: normaliseCount(data),
      };
      setResults(normalized);

      if (data.heatmap_overlay) {
        setHeatmapUrl(`data:image/png;base64,${data.heatmap_overlay}`);
      }

      setRequestMeta((prev) =>
        prev
          ? {
              ...prev,
              finishedAt: Date.now(),
            }
          : null
      );
    } catch (err) {
      console.error("VMamba upload failed", err);
      setError(
        err instanceof Error
          ? `Failed to process image: ${err.message}`
          : "Failed to process image."
      );
    } finally {
      setLoading(false);
    }
  }, [endpoint, selectedFile]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setResults(null);
    setHeatmapUrl(null);
    setError(null);
    setRequestMeta(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [previewUrl]);

  const displayCount = normaliseCount(results);
  const timing = results?.timing_breakdown;
  const totalTime = results?.processing_time_ms ?? null;

  const widthFrom = useCallback(
    (value) => {
      if (!totalTime || !value || value <= 0) return "0%";
      return `${Math.min(100, (value / totalTime) * 100).toFixed(1)}%`;
    },
    [totalTime]
  );

  return (
    <section className="upload-section">
      <header style={{ marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>VMamba-TMTB (Best Checkpoint)</h2>
        <p className="upload-subtitle">
          Upload an image and we will run it through the fine-tuned
          <strong> vmamba_shanghai_best.pth</strong> model for ShanghaiTech Part
          A.
        </p>
        <div className="endpoint-hint">
          <span>API endpoint:</span>
          <code>{endpoint}</code>
        </div>
      </header>

      <div
        className={`drop-zone ${previewUrl ? "has-file" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        {previewUrl ? (
          <div className="preview-container">
            <img src={previewUrl} alt="Preview" className="preview-image" />
            <div className="preview-overlay">
              <p>
                <strong>Filename:</strong> {selectedFile?.name}
              </p>
              <p>
                <strong>Size:</strong> {formatBytes(selectedFile?.size)}
              </p>
              <p>
                <strong>Type:</strong> {selectedFile?.type}
              </p>
            </div>
          </div>
        ) : (
          <div className="drop-zone-content">
            <div className="upload-icon">📁</div>
            <p>Drag & drop an image here, or click to browse</p>
            <small>Accepts JPEG, PNG, BMP, TIFF up to 10MB</small>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="file-input"
        onChange={handleFileSelect}
      />

      <div className="action-buttons">
        <button
          className="count-button"
          onClick={handleSubmit}
          disabled={!selectedFile || loading}
        >
          {loading ? "Processing..." : "Count with VMamba"}
        </button>
        <button
          className="reset-button"
          onClick={handleClear}
          disabled={loading}
        >
          Clear
        </button>
      </div>

      {error && (
        <div className="error-section">
          <div className="error-message">❌ {error}</div>
        </div>
      )}

      {results && (
        <article className="results-section">
          <div className="results-header">
            <h2>📊 VMamba-TMTB Inference Results</h2>
          </div>
          <div className="results-grid">
            <div className="result-card main-result">
              <div className="result-value">
                {displayCount !== null ? displayCount : "—"}
              </div>
              <div className="result-label">People Detected</div>
            </div>

            <div className="result-card">
              <div className="result-value">
                {totalTime ? `${totalTime} ms` : "—"}
              </div>
              <div className="result-label">Total Processing Time</div>
            </div>

            <div className="result-card">
              <div className="result-value">
                {results?.image_info?.dimensions || "—"}
              </div>
              <div className="result-label">Image Dimensions</div>
            </div>

            <div className="result-card">
              <div className="result-value">
                {formatBytes(results?.image_info?.size_bytes)}
              </div>
              <div className="result-label">File Size</div>
            </div>
          </div>

          {timing && totalTime && (
            <div className="timing-section">
              <h3>⏱️ Timing Breakdown</h3>
              <div className="timing-bars">
                {timing.preprocess_ms !== undefined && (
                  <div className="timing-item">
                    <span>Preprocess</span>
                    <div className="timing-bar">
                      <div
                        className="timing-fill preprocess"
                        style={{ width: widthFrom(timing.preprocess_ms) }}
                      ></div>
                    </div>
                    <span>{timing.preprocess_ms} ms</span>
                  </div>
                )}
                {timing.inference_ms !== undefined && (
                  <div className="timing-item">
                    <span>Inference</span>
                    <div className="timing-bar">
                      <div
                        className="timing-fill inference"
                        style={{ width: widthFrom(timing.inference_ms) }}
                      ></div>
                    </div>
                    <span>{timing.inference_ms} ms</span>
                  </div>
                )}
                {timing.postprocess_ms !== undefined && (
                  <div className="timing-item">
                    <span>Post-process</span>
                    <div className="timing-bar">
                      <div
                        className="timing-fill postprocess"
                        style={{ width: widthFrom(timing.postprocess_ms) }}
                      ></div>
                    </div>
                    <span>{timing.postprocess_ms} ms</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {heatmapUrl && (
            <div className="results-section" style={{ marginTop: "1.5rem" }}>
              <h3 style={{ marginTop: 0 }}>🔥 Density Heatmap Overlay</h3>
              <img
                src={heatmapUrl}
                alt="Density heatmap overlay"
                style={{ maxWidth: "100%", borderRadius: "8px" }}
              />
            </div>
          )}

          <details style={{ marginTop: "1.5rem" }}>
            <summary style={{ cursor: "pointer" }}>View Raw JSON</summary>
            <pre
              style={{
                background: "#f8f9fa",
                padding: "1rem",
                borderRadius: "8px",
                marginTop: "0.75rem",
                overflowX: "auto",
                fontSize: "0.85rem",
              }}
            >
              {JSON.stringify(results, null, 2)}
            </pre>
          </details>

          {requestMeta && requestMeta.startedAt && requestMeta.finishedAt && (
            <p
              style={{
                marginTop: "1rem",
                fontSize: "0.8rem",
                color: "#6c6d94",
              }}
            >
              Request ID: <strong>{requestMeta.fileName}</strong> · Duration:{" "}
              {requestMeta.finishedAt - requestMeta.startedAt} ms (client)
            </p>
          )}
        </article>
      )}
    </section>
  );
}

export default VMambaUploader;
