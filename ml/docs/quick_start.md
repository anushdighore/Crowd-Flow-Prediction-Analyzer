# Quick Start Guide

## 🚀 **Getting Started**

### **Available Models**

- **CSRNet** - Crowd counting via density estimation
- **MCNN** - Multi-column CNN for crowd counting
- **TMTB** (VMamba) - State space model for crowd analysis
- **YOLO** - Object detection for crowd counting

### **Backend API Endpoints**

- `POST /api/v1/csrnet/predict` - CSRNet crowd counting
- `POST /api/v1/tmtb/predict` - TMTB crowd counting

### **Basic Usage**

#### Start Backend Server

```bash
cd backend
python main.py
```

#### Test API Health

```bash
curl http://localhost:8000/api/v1/csrnet/health
```

#### Make Prediction

```bash
curl -X POST http://localhost:8000/api/v1/csrnet/predict \
  -F "file=@your_image.jpg"
```

## 📊 **Performance Benchmarks**

### **Model Performance Comparison**

```
Dataset: ShanghaiTech Part A (Train: 300 images, Test: 182 images)

┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────────┐
│ Model          │ MAE         │ MSE         │ RMSE        │ Training Time   │
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────────┤
│ CSRNet         │             │             │             │                 │
│ CSRNet-Finetuned│             │             │             │                 │
│ VMamba         │             │             │             │                 │
│ VMamba-Finetuned│             │             │             │                 │
│ MCNN           │             │             │             │                 │
│ MCNN-Finetuned │             │             │             │                 │
│ YOLO           │             │             │             │                 │
│ YOLO-Finetuned │             │             │             │                 │
└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────────┘

Dataset: ShanghaiTech Part B (Train: 400 images, Test: 316 images)

┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────────┐
│ Model          │ MAE         │ MSE         │ RMSE        │ Training Time   │
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────────┤
│ CSRNet         │             │             │             │                 │
│ CSRNet-Finetuned│             │             │             │                 │
│ VMamba         │             │             │             │                 │
│ VMamba-Finetuned│             │             │             │                 │
│ MCNN           │             │             │             │                 │
│ MCNN-Finetuned │             │             │             │                 │
│ YOLO           │             │             │             │                 │
│ YOLO-Finetuned │             │             │             │                 │
└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────────┘
```

### **Finetuning Performance Gains**

```
Relative Improvement After Finetuning

┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Model          │ Shanghai A MAE  │ Shanghai B MAE  │ Avg Improvement │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ CSRNet         │                 │                 │                 │
│ VMamba         │                 │                 │                 │
│ MCNN           │                 │                 │                 │
│ YOLO           │                 │                 │                 │
└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```
