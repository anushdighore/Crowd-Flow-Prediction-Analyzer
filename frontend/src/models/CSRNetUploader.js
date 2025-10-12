import React, { useState, useRef, useMemo } from "react";

const API_BASE =
  process.env.REACT_APP_API_BASE?.replace(/\/$/, "") ||
  "http://localhost:8000/api/v1";

const normaliseCount = (payload) => {
  if (!payload) return null;
  const candidates = [payload.count, payload.crowd_count, payload.people];
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

function CSRNetUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const displayCount = useMemo(() => normaliseCount(results), [results]);

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        setError("Please select a valid image file");
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB");
        return;
      }

      setSelectedFile(file);
      setError(null);
      setResults(null);

      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  // Handle drag and drop
  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      const fakeEvent = {
        target: { files: [file] },
      };
      handleFileSelect(fakeEvent);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  // Submit image for counting
  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an image first");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      console.log("Sending image to backend:", selectedFile.name);

      const response = await fetch(`${API_BASE}/csrnet/count`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response from backend:", data);
      const normalized = {
        ...data,
        count: normaliseCount(data),
      };
      setResults(normalized);
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Failed to process image: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Clear selection
  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>CSRNet Crowd Counter</h2>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        ref={fileInputRef}
        style={{ display: "none" }}
      />

      <div
        style={{
          border: "2px dashed #ccc",
          borderRadius: "8px",
          padding: "40px",
          textAlign: "center",
          cursor: "pointer",
          marginBottom: "20px",
          backgroundColor: "#f9f9f9",
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current && fileInputRef.current.click()}
      >
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Preview"
            style={{ maxWidth: "100%", maxHeight: "400px" }}
          />
        ) : (
          <p>Click or drag an image here to upload</p>
        )}
      </div>

      <div style={{ marginBottom: "20px" }}>
        <button
          onClick={handleSubmit}
          disabled={!selectedFile || loading}
          style={{
            padding: "10px 20px",
            marginRight: "10px",
            backgroundColor: loading ? "#ccc" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Processing..." : "Count People"}
        </button>

        <button
          onClick={handleClear}
          disabled={loading}
          style={{
            padding: "10px 20px",
            backgroundColor: "#6c757d",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: "10px",
            backgroundColor: "#f8d7da",
            color: "#721c24",
            borderRadius: "4px",
            marginBottom: "20px",
          }}
        >
          {error}
        </div>
      )}

      {results && (
        <div
          style={{
            padding: "20px",
            backgroundColor: "#d4edda",
            border: "2px solid #28a745",
            borderRadius: "8px",
          }}
        >
          <h3 style={{ marginTop: 0, color: "#155724" }}>
            ✅ Crowd Count Results
          </h3>

          <div
            style={{
              fontSize: "48px",
              fontWeight: "bold",
              color: "#155724",
              margin: "20px 0",
            }}
          >
            {displayCount !== null ? displayCount : "—"} People
          </div>

          <div
            style={{ textAlign: "left", fontSize: "14px", color: "#155724" }}
          >
            <p>
              <strong>Image Size:</strong> {results.image_size}
            </p>
            <p>
              <strong>Filename:</strong> {results.filename}
            </p>
            {results.density_map_shape && (
              <p>
                <strong>Density Map Shape:</strong>{" "}
                {results.density_map_shape.join(" x ")}
              </p>
            )}
          </div>

          <details style={{ marginTop: "15px" }}>
            <summary style={{ cursor: "pointer", color: "#155724" }}>
              View Raw JSON Response
            </summary>
            <pre
              style={{
                textAlign: "left",
                fontSize: "12px",
                marginTop: "10px",
                backgroundColor: "#fff",
                padding: "10px",
                borderRadius: "4px",
              }}
            >
              {JSON.stringify(results, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default CSRNetUploader;
