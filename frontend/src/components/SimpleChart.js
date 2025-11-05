import React, { useRef, useEffect } from 'react';

export default function SimpleChart({ data, title, color = '#4CAF50', yLabel = 'Value' }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !data || data.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Background
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, width, height);

    if (data.length < 2) return;

    // Calculate bounds
    const values = data.map(d => d.count !== undefined ? d.count : d.fps || 0);
    const maxValue = Math.max(...values, 1);
    const minValue = Math.min(...values, 0);
    const range = maxValue - minValue || 1;

    // Padding
    const padding = { top: 30, right: 20, bottom: 30, left: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Draw grid lines
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding.top + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      // Y-axis labels
      const value = maxValue - (range / 5) * i;
      ctx.fillStyle = '#888';
      ctx.font = '10px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(value.toFixed(1), padding.left - 5, y + 3);
    }

    // Draw line
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.forEach((point, index) => {
      const value = point.count !== undefined ? point.count : point.fps || 0;
      const x = padding.left + (chartWidth / (data.length - 1)) * index;
      const y = padding.top + chartHeight - ((value - minValue) / range) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw points
    ctx.fillStyle = color;
    data.forEach((point, index) => {
      const value = point.count !== undefined ? point.count : point.fps || 0;
      const x = padding.left + (chartWidth / (data.length - 1)) * index;
      const y = padding.top + chartHeight - ((value - minValue) / range) * chartHeight;
      
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();
    });

    // Title
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, width / 2, 20);

    // Y-axis label
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.font = '12px Arial';
    ctx.fillStyle = '#888';
    ctx.textAlign = 'center';
    ctx.fillText(yLabel, 0, 0);
    ctx.restore();

  }, [data, title, color, yLabel]);

  return (
    <canvas
      ref={canvasRef}
      width={400}
      height={200}
      style={{ width: '100%', height: 'auto', maxWidth: '400px' }}
    />
  );
}
