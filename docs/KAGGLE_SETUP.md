# Kaggle API Setup for Dataset Download

Quick guide to setup Kaggle API for downloading ShanghaiTech dataset.

---

## 🎯 Why Kaggle?

**Advantages:**

- ✅ Fast download (good servers)
- ✅ Reliable (won't break like Google Drive links)
- ✅ CLI automation (no manual clicking)
- ✅ Resume support (if download fails)

---

## 📥 Setup Steps

### 1. Install Kaggle CLI

```bash
pip install kaggle
```

**Verify installation:**

```bash
kaggle --version
```

Should output: `Kaggle API 1.x.x`

---

### 2. Get Kaggle API Token

#### Step 2.1: Create Kaggle Account

- Go to: https://www.kaggle.com/
- Click "Register" (if you don't have account)
- Sign up with Google/Email

#### Step 2.2: Generate API Token

1. **Login** to Kaggle
2. Click your **profile picture** (top right)
3. Click **"Settings"**
4. Scroll to **"API"** section
5. Click **"Create New Token"**

This downloads: **`kaggle.json`**

---

### 3. Install API Token

**Where to put `kaggle.json`:**

#### Windows:

```
C:\Users\<YourUsername>\.kaggle\kaggle.json
```

**Steps:**

1. Open File Explorer
2. Go to: `C:\Users\<YourUsername>\`
3. Create folder: `.kaggle` (note the dot)
4. Move `kaggle.json` inside `.kaggle\` folder

**Using Command Prompt:**

```cmd
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\kaggle.json
```

#### Linux/Mac:

```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json  # Set correct permissions
```

---

### 4. Verify Setup

```bash
kaggle datasets list
```

**Expected output:**

```
ref                                  title                          size  lastUpdated
-----------------------------------  ---------------------------  ------  -------------------
crawford/emnist                      EMNIST                        535MB  2019-02-22 20:16:08
...
```

If you see this, ✅ **setup is working!**

---

## 📂 Download ShanghaiTech Dataset

### Method 1: Direct Dataset Download

**Find the dataset:**

```bash
kaggle datasets list -s shanghaitech
```

**Download:**

```bash
kaggle datasets download -d tthien/shanghaitech
```

**Extract:**

```bash
# Windows
tar -xf shanghaitech.zip -C datasets/

# Or using Python
python -m zipfile -e shanghaitech.zip datasets/
```

---

### Method 2: Search and Download

```bash
# Search for ShanghaiTech datasets
kaggle datasets list -s "shanghaitech crowd"

# Pick the best one and download
kaggle datasets download -d <dataset-id>
```

---

## 🔧 Troubleshooting

### Problem 1: "401 Unauthorized"

**Cause:** API token not found or invalid

**Solution:**

1. Delete old token: `del %USERPROFILE%\.kaggle\kaggle.json` (Windows) or `rm ~/.kaggle/kaggle.json` (Linux/Mac)
2. Generate new token from Kaggle website
3. Move to correct location
4. Try again

---

### Problem 2: "kaggle: command not found"

**Cause:** Kaggle CLI not installed or not in PATH

**Solution:**

```bash
# Reinstall
pip install --upgrade kaggle

# Check installation
pip show kaggle

# If still not found, use full path:
python -m kaggle datasets download -d tthien/shanghaitech
```

---

### Problem 3: "Permission denied" (Linux/Mac)

**Cause:** Incorrect file permissions

**Solution:**

```bash
chmod 600 ~/.kaggle/kaggle.json
```

---

### Problem 4: Download very slow

**Cause:** Network issues or server congestion

**Solution:**

1. Try at different time
2. Use alternative download method (Google Drive)
3. Use download manager (see below)

---

## 🚀 Alternative: Manual Download

If Kaggle API doesn't work:

### Option 1: Kaggle Website

1. Go to: https://www.kaggle.com/datasets/tthien/shanghaitech
2. Click **"Download"** button
3. Extract to `datasets/ShanghaiTech/`

### Option 2: Google Drive

1. Go to: https://drive.google.com/drive/folders/1CrdJkgDdwNw4g5D7D-q7wJxJpDlsWfM9
2. Download `ShanghaiTech.zip`
3. Extract to `datasets/ShanghaiTech/`

### Option 3: GitHub Mirror

```bash
git clone https://github.com/desenzhou/ShanghaiTechDataset.git datasets/ShanghaiTech
```

---

## 📊 Expected Download Size

- **ShanghaiTech Part A + Part B**: ~500 MB
- **Download time**: 5-10 minutes (depends on connection)

---

## ✅ Verification

After download and extraction:

```bash
# Check directory structure
dir datasets\ShanghaiTech         # Windows
ls datasets/ShanghaiTech           # Linux/Mac
```

**Expected structure:**

```
datasets/ShanghaiTech/
├── part_A/
│   ├── train_data/
│   │   ├── images/ (300 .jpg files)
│   │   └── ground_truth/ (300 .mat files)
│   └── test_data/
│       ├── images/ (182 .jpg files)
│       └── ground_truth/ (182 .mat files)
└── part_B/
    └── ...
```

**Verify file counts:**

```bash
# Windows (PowerShell)
(Get-ChildItem "datasets\ShanghaiTech\part_A\train_data\images").Count

# Linux/Mac
ls datasets/ShanghaiTech/part_A/train_data/images | wc -l
```

Should output: **300** (for train) and **182** (for test)

---

## 🎯 Next Steps

Once dataset is downloaded:

1. ✅ **Generate density maps**:

   ```bash
   python create_density_maps.py --root datasets/ShanghaiTech --part A
   ```

2. ✅ **Start fine-tuning**:
   ```bash
   python finetune_vmamba.py \
       --checkpoint checkpoints/jhu_5.pth \
       --data-root datasets/ShanghaiTech/part_A
   ```

---

## 💡 Pro Tips

### Tip 1: Download Both Parts

```bash
# Download Part A
kaggle datasets download -d tthien/shanghaitech

# If you want Part B too, it's in the same dataset
# Just extract and use --part B when generating density maps
```

### Tip 2: Use Python for Extraction

```python
import zipfile
import os

zip_path = 'shanghaitech.zip'
extract_to = 'datasets/'

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

print(f"✅ Extracted to: {os.path.abspath(extract_to)}")
```

### Tip 3: Resume Failed Downloads

If download fails midway:

```bash
# Kaggle CLI supports resume
kaggle datasets download -d tthien/shanghaitech --force

# Or use wget with resume support
wget -c <direct-download-url>
```

---

## 📚 Resources

- **Kaggle API Docs**: https://github.com/Kaggle/kaggle-api
- **ShanghaiTech Dataset**: https://www.kaggle.com/datasets/tthien/shanghaitech
- **Alternative Source**: https://drive.google.com/drive/folders/1CrdJkgDdwNw4g5D7D-q7wJxJpDlsWfM9

---

## 🆘 Still Having Issues?

If all methods fail:

1. Check **DATASET_PREPARATION.md** for 3 alternative download methods
2. Ask a friend to download and share via USB/cloud
3. Use a smaller dataset for initial testing (UCF-QNRF, WorldExpo'10)

---

## ✨ Success!

Once you see:

```
datasets/ShanghaiTech/
├── part_A/
│   ├── train_data/images/ (300 images) ✅
│   └── test_data/images/ (182 images) ✅
```

You're ready to proceed! 🎉

**Next:** Run `python create_density_maps.py --root datasets/ShanghaiTech --part A`
