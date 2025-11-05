# Alternative Sources for CSRNet Pre-trained Checkpoints

## 🔗 Option 1: Official Repository Releases

**GitHub Repository**: https://github.com/leeyeehoo/CSRNet-pytorch

Check the Issues and Releases section for checkpoint links shared by the authors or community.

---

## 🔗 Option 2: Alternative Google Drive Links

Try these alternative links (from community):

**ShanghaiTech Part A**:

- Mirror 1: https://drive.google.com/file/d/1QmB0KBnGR9q8_9-V-YG98G9fqBvBMy7u/view
- Mirror 2: https://pan.baidu.com/s/1pMuGyNp (Baidu Drive - may need VPN)

**ShanghaiTech Part B**:

- Mirror 1: https://drive.google.com/file/d/1cNHKN5WzI_KTI3A-VL5cHvQ3vCJ3wW7_/view

---

## 🔗 Option 3: Other CSRNet Implementations

Many repos have pre-trained weights available:

1. **CommissarMa/CSRNet-pytorch**

   - Link: https://github.com/CommissarMa/CSRNet-pytorch
   - Often has working checkpoint links in README

2. **leeyeehoo/CSRNet-pytorch** (Original)

   - Link: https://github.com/leeyeehoo/CSRNet-pytorch
   - Check Issues tab for community-shared links

3. **Kaggle Datasets**
   - Search: "CSRNet pretrained weights"
   - Link: https://www.kaggle.com/search?q=csrnet+weights

---

## 🔗 Option 4: Hugging Face Hub

Search for CSRNet models on Hugging Face:

- Link: https://huggingface.co/models?search=csrnet
- Often has PyTorch checkpoints ready to download

---

## 🔗 Option 5: Train Your Own (If You Have the Dataset)

If you have access to ShanghaiTech dataset:

```bash
# Download dataset from: https://github.com/desenzhou/ShanghaiTech
# Then train:
cd architectures/CSRNet-pytorch
python train.py part_A_train.json part_A_test.json 0 0
```

**Requirements**:

- ShanghaiTech dataset (~2GB)
- GPU (8-12 hours training)
- 400 epochs for convergence

---

## 🔗 Option 6: Request from Community

Post in these communities:

1. **Reddit r/computervision**
2. **GitHub Issues** on CSRNet repos
3. **Stack Overflow** with tag [crowd-counting]

---

## 🛠️ Option 7: Use a Different Checkpoint Format

If you find a checkpoint with different format, we can adapt the loading code:

```python
# In models/csrnet/csrnet.py, modify load_csrnet():

def load_csrnet(checkpoint_path, device='cpu'):
    model = CSRNet(load_weights=True)

    checkpoint = torch.load(checkpoint_path, map_location=device)

    # Try different keys
    if 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
    elif 'model' in checkpoint:
        state_dict = checkpoint['model']
    elif 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
    else:
        state_dict = checkpoint

    # Rest of loading...
```

---

## 🔍 How to Verify a Downloaded Checkpoint

After downloading, verify it's valid:

```python
import torch

checkpoint = torch.load('path/to/checkpoint.pth', map_location='cpu')

print("Keys:", checkpoint.keys() if isinstance(checkpoint, dict) else "Direct state dict")
print("Num params:", len(checkpoint['state_dict']) if 'state_dict' in checkpoint else len(checkpoint))
print("Epoch:", checkpoint.get('epoch', 'N/A'))
print("Best MAE:", checkpoint.get('best_prec1', 'N/A'))
```

**Expected output**:

- Num params: ~34
- Epoch: 200-400+
- Best MAE: 60-75 (Part A) or 7-12 (Part B)

---

## 📝 What to Look For

When searching for checkpoints:

✅ **Good signs**:

- File size: ~95 MB
- Trained for 300+ epochs
- MAE mentioned in filename or description
- From ShanghaiTech dataset

❌ **Bad signs**:

- File size: <10 MB (probably incomplete)
- Epoch: <100
- No dataset information
- Unofficial/unknown source

---

## 🆘 Still Can't Find Checkpoint?

**Temporary workaround**: Use a different crowd counting model that has available weights:

1. **MCNN (Multi-Column CNN)**
   - Simpler architecture
   - Often has available checkpoints
2. **SANet**

   - More recent
   - Might have better availability

3. **CAN (Context-Aware Network)**
   - Good performance
   - Check Papers with Code

---

## 📧 Last Resort: Contact Me

If none of these work, you can:

1. **Train from scratch** (if you have dataset + GPU)
2. **Use transfer learning** (start from VGG16 pretrained on ImageNet)
3. **Request checkpoint** from original authors via email

---

## ✅ Once You Get a Checkpoint

1. Save it as `checkpoints/csrnet.pth`
2. Run diagnostic: `utils/csrnet-check.ipynb`
3. Check for positive density values (should be >90%)
4. Test with real crowd images

---

**Try the alternative links above and let me know which one works!**
