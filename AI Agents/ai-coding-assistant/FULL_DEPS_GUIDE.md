# ✅ Full Dependencies Setup - Complete Guide

## 🎯 Purpose

Install full dependencies (transformers + torch) to enable all features and remove the skipped test.

---

## 📦 What Gets Installed

| Package | Size | Purpose |
|---------|------|---------|
| **torch** | ~1.5GB | Neural network backend (CPU version) |
| **transformers** | ~400MB | CodeBERT and transformer models |
| **Total** | ~2GB | Full Phase 9.2/9.3 features |

---

## 🚀 Installation Methods

### Method 1: During Setup (Recommended)

When running `scripts\setup.bat`, you'll be asked:

```
Install full dependencies? (y/n):
```

Answer **`y`** to install everything at once.

### Method 2: After Setup

Run the dedicated script:

```bash
install_full_deps.bat
```

### Method 3: Manual

```bash
# Activate virtual environment first
venv\Scripts\activate.bat

# Install torch (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install transformers
pip install transformers>=4.30.0
```

### Method 4: Requirements File

```bash
pip install -r requirements-full.txt
```

---

## ⏱️ Installation Time

- **Download**: 3-8 minutes (depends on connection)
- **Installation**: 2-5 minutes
- **Total**: **5-10 minutes**

---

## 💾 Disk Space Required

- **torch**: ~2GB
- **transformers**: ~500MB
- **Models** (downloaded on first use): ~500MB
- **Total**: **~3GB**

---

## ✨ What You Get

### Before (Basic Dependencies)
```
Ran 10 tests in 24.009s
OK (skipped=1)
```

**Skipped**: test_similarity (Phase 9.2)

### After (Full Dependencies)
```
Ran 10 tests in 30.000s
OK
```

**No skips!** All tests run.

---

## 🎁 Features Enabled

### Phase 9.2: Code Understanding
- ✅ Full CodeBERT embeddings (no fallback)
- ✅ Code similarity computation
- ✅ Semantic code search with CodeBERT
- ✅ test_similarity test runs

### Phase 9.3: Advanced Reranking
- ✅ Cross-encoder reranking
- ✅ Better search relevance
- ✅ Advanced query understanding

---

## ⚡ Quick Start

```bash
# 1. Run installation
install_full_deps.bat

# 2. Wait 5-10 minutes

# 3. Run tests to verify
python run_all_tests.py

# Expected: 7/7 passed, 0 skipped
```

---

## 🔍 Verification

After installation, verify it worked:

```bash
# Test transformers
python -c "import transformers; print('✓ transformers installed')"

# Test torch
python -c "import torch; print('✓ torch installed')"

# Run Phase 9.2 tests
python tests\test_phase_92.py
```

**Expected output:**
```
Ran 10 tests in 30.000s
OK
```

No "(skipped=1)" message!

---

## 🆘 Troubleshooting

### Issue: Slow download

**Solution**: The packages are large (~2GB). Be patient.

### Issue: Installation fails

**Solution**: 
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try again
install_full_deps.bat
```

### Issue: Out of disk space

**Solution**: You need 3GB+ free space. Clear some space and try again.

### Issue: torch installation fails

**Solution**: 
```bash
# Try installing from PyTorch directly
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## 🤔 Do I Need This?

### ✅ Yes, install if:
- You want 100% test coverage (no skips)
- You want advanced CodeBERT features
- You have good internet (download 2GB)
- You have 3GB+ disk space

### ⏭️ No, skip if:
- You only need Phase 11.1 (works without it)
- You're on limited bandwidth
- You're on limited disk space
- You're okay with 1 skipped test

---

## 📊 Comparison

| Aspect | Basic | Full |
|--------|-------|------|
| **Phase 11.1** | ✅ Works | ✅ Works |
| **Basic RAG** | ✅ Works | ✅ Works |
| **Phase 9.2** | ⚠️ Fallback | ✅ Full |
| **Phase 9.3** | ⚠️ Basic | ✅ Advanced |
| **Tests** | 6/7 + 1 skip | 7/7 no skips |
| **Download** | ~200MB | ~2GB |
| **Disk Space** | ~500MB | ~3GB |
| **Install Time** | 2 min | 10 min |

---

## ✅ Recommendation

**For Phase 11.1**: Full dependencies are **optional but recommended** for complete feature coverage.

**For production use**: Install full dependencies to enable all advanced features.

---

## 📞 Next Steps

After installing full dependencies:

1. ✅ Run all tests: `python run_all_tests.py`
2. ✅ Verify no skips: Should see "OK" not "OK (skipped=1)"
3. ✅ Commit Phase 11.1: `cd commits && commit_phase_11_1.bat`

---

**Status**: Ready to install! Run `install_full_deps.bat` when ready. 🚀
