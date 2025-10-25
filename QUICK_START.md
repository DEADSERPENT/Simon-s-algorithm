# Simon's Algorithm - Quick Start Guide

## ⚡ Super Fast Setup (30 seconds)

### Windows Users:
```bash
1. Open Command Prompt or PowerShell
2. Navigate to project: cd C:\Users\DEADSERPENT\Music\QISKIT
3. Run setup:          setup.bat
4. Follow prompts and select 'Y' to run test suite
```

### Linux/macOS Users:
```bash
1. Open Terminal
2. Navigate to project: cd /path/to/QISKIT
3. Make executable:    chmod +x setup.sh
4. Run setup:          ./setup.sh
5. Follow prompts and select 'y' to run test suite
```

---

## 📋 What You'll See

After running the setup, you'll see the **comprehensive test suite** with all 6 cases:

```
Case 1: Trivial success (s=0000)        ✅ SUCCESS
Case 2: Ideal success (s=1101)          ✅ SUCCESS
Case 3: Failure (dependency)            ⚠️  RETRY
Case 4: Failure (uninformative y)       ⚠️  RETRY
Case 5: Realistic success (s=1101)      ✅ SUCCESS
Case 6: Hardware failure (noisy)        ⚠️  RETRY
```

---

## 🔄 Running the Program Again

### After initial setup:

**Windows:**
```bash
venv\Scripts\activate
python simon_qiskit.py
deactivate
```

**Linux/macOS:**
```bash
source venv/bin/activate
python simon_qiskit.py
deactivate
```

---

## 📊 For Your Presentation

### Key Points to Highlight:

1. **Quantum Advantage**
   - Classical: O(2^(n/2)) queries
   - Quantum: O(n) queries
   - **Exponential speedup!**

2. **Real-World Behavior**
   - Not all runs succeed (probabilistic)
   - Need linearly independent measurements
   - Hardware noise is a real challenge

3. **Algorithm Foundation**
   - Inspired Shor's factoring algorithm
   - Demonstrates quantum supremacy
   - Uses superposition + interference

---

## 🎯 Test Cases Summary

| Case | Scenario | Demonstrates |
|------|----------|--------------|
| 1 | s=0000 | Handles trivial (one-to-one) function |
| 2 | s=1101 | Perfect quantum measurements |
| 3 | s=1101 | Linear dependency failure |
| 4 | s=1101 | Uninformative measurements |
| 5 | s=1101 | Robustness to redundancy |
| 6 | s=1101 | Hardware noise simulation |

---

## 🛠️ Troubleshooting

**Q: Script says "Python not found"**
- A: Install Python 3.8+ from https://www.python.org/

**Q: PowerShell execution policy error**
- A: Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Q: ModuleNotFoundError**
- A: Make sure you activated venv: `venv\Scripts\activate`

**Q: Permission denied (Linux/macOS)**
- A: Run: `chmod +x setup.sh`

---

## 📚 Full Documentation

See **README.md** for:
- Complete mathematical background
- Detailed algorithm explanation
- Running on IBM Quantum hardware
- Academic references

---

## 🚀 You're Ready!

Your Simon's Algorithm implementation is now ready to demonstrate quantum supremacy in action!

**Happy Quantum Computing! ⚛️**
