# 🚀 Setup Guide

> Complete setup instructions for Terra Scout development environment.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

| Requirement | Version   | Check Command      | Status |
| ----------- | --------- | ------------------ | ------ |
| Windows 11  | -         | `winver`           | ⬜     |
| Python      | 3.10.x    | `python --version` | ⬜     |
| Java JDK    | 8 (1.8.x) | `java -version`    | ⬜     |
| Git         | Any       | `git --version`    | ⬜     |
| Node.js     | 22.x      | `node --version`   | ⬜     |
| NVIDIA GPU  | RTX 2050+ | `nvidia-smi`       | ⬜     |

---

## 📥 Step 1: Clone Repository

```powershell
cd ~\Desktop
git clone https://github.com/VortexDevX/TerraScout.git
cd TerraScout
```

---

## ☕ Step 2: Configure Java Environment

### 2.1 Verify Java 8 Installation

```powershell
java -version
```

Expected output:

```
openjdk version "1.8.0_472"
OpenJDK Runtime Environment (build 1.8.0_472-b01)
OpenJDK 64-Bit Server VM (build 25.472-b01, mixed mode)
```

### 2.2 Verify JDK (not just JRE)

```powershell
javac -version
```

Expected output:

```
javac 1.8.0_472
```

### 2.3 Set JAVA_HOME

Find your Java installation path:

```powershell
where java
```

Set JAVA_HOME (adjust path as needed):

```powershell
# Set for current user (permanent)
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\OpenJDK\jdk-1.8.0_472', 'User')

# Add to PATH
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
[System.Environment]::SetEnvironmentVariable('Path', "$currentPath;%JAVA_HOME%\bin", 'User')
```

### 2.4 Verify JAVA_HOME

**Restart PowerShell**, then:

```powershell
echo $env:JAVA_HOME
```

Should output your Java path.

---

## 🎮 Step 3: Setup Minecraft Server

Terra Scout requires a Minecraft server for the bot to connect to.

### 3.1 Download Server

The `server/` folder is gitignored. Download PaperMC:

```powershell
mkdir server
cd server
# Download PaperMC from https://papermc.io/downloads/paper
# Place paper-1.21.x.jar in server folder
```

### 3.2 Create Start Script

Create `server/start.ps1`:

```powershell
java -Xmx2G -Xms2G -jar paper-1.21.4-118.jar nogui
```

### 3.3 First Run

```powershell
.\start.ps1
```

Accept EULA by editing `eula.txt`: `eula=true`

### 3.4 Configure Server

Edit `server.properties`:

```properties
online-mode=false
spawn-protection=0
difficulty=peaceful
```

---

## 🐍 Step 4: Create Python Virtual Environment

### 4.1 Navigate to Project

```powershell
cd ~\Desktop\TerraScout
```

### 4.2 Create Virtual Environment with Python 3.10

```powershell
py -3.10 -m venv venv
```

### 4.3 Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 4.4 Verify Activation

Your prompt should show `(venv)`:

```
(venv) PS C:\Users\...\TerraScout>
```

### 4.5 Upgrade pip

```powershell
python -m pip install --upgrade pip setuptools wheel
```

---

## 📦 Step 5: Install Dependencies

### 5.1 Install PyTorch (CUDA)

Check your CUDA version:

```powershell
nvidia-smi
```

Install PyTorch with matching CUDA:

```powershell
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 5.2 Verify PyTorch + CUDA

```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```

Expected output:

```
PyTorch: 2.x.x
CUDA available: True
CUDA version: 11.8 (or 12.1)
```

### 5.3 Install Mineflayer Bot

```powershell
cd bot
npm install
cd ..
```

This installs the Node.js bot dependencies:

- `mineflayer` - Minecraft bot framework
- `mineflayer-pathfinder` - Navigation
- `express` - HTTP server for Python bridge

### 5.4 Install Reinforcement Learning Libraries

```powershell
pip install stable-baselines3 gymnasium
```

### 5.5 Install Python Dependencies

```powershell
pip install numpy rich httpx pyyaml tqdm
```

### 5.6 Install Development Libraries (Optional)

```powershell
pip install pytest black isort
```

---

## ✅ Step 6: Verify Installation

### 6.1 Create Verification Script

Create `scripts/verify_installation.py` with content from configuration section below.

### 6.2 Run Verification

```powershell
python scripts/verify_installation.py
```

Expected output:

```
========================================
Terra Scout Installation Verification
========================================

[✓] Python 3.10.x
[✓] JAVA_HOME is set
[✓] Java version 1.8.x
[✓] PyTorch 2.x.x
[✓] CUDA available
[✓] MineRL installed
[✓] Stable-Baselines3 installed
[✓] Gymnasium installed
[✓] All critical packages installed

========================================
Environment Test
========================================

[✓] MineRL environment created successfully
[✓] Environment reset successful
[✓] Environment step successful
[✓] Environment closed

========================================
✅ ALL CHECKS PASSED
Terra Scout is ready for development!
========================================
```

---

## 📁 Step 7: Project Configuration

### 7.1 Create .env File

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your settings.

### 7.2 Install Agent Package (Development Mode)

```powershell
cd agent
pip install -e .
cd ..
```

---

## 🎮 Step 8: First Run Test

### 8.1 Test MineRL Environment

```powershell
python -c "
import gymnasium as gym
import minerl

env = gym.make('MineRLNavigateDense-v0')
obs, info = env.reset()
print(f'Observation keys: {obs.keys()}')
print(f'POV shape: {obs[\"pov\"].shape}')

for i in range(10):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f'Step {i+1}: reward={reward:.4f}')
    if terminated or truncated:
        break

env.close()
print('Test complete!')
"
```

---

## 🔧 Troubleshooting Quick Reference

| Issue                                       | Solution                        |
| ------------------------------------------- | ------------------------------- |
| `JAVA_HOME not set`                         | See Step 2.3                    |
| `error: Microsoft Visual C++ 14.0 required` | See Step 3                      |
| `No module named 'minerl'`                  | `pip install minerl`            |
| `CUDA not available`                        | Reinstall PyTorch with CUDA     |
| `Permission denied`                         | Run PowerShell as Administrator |

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## 📊 Environment Summary

After successful setup:

```
┌─────────────────────────────────────────────────────────────┐
│                 TERRA SCOUT ENVIRONMENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Python:     3.10.x (venv)                                 │
│  Java:       OpenJDK 1.8.0_472                             │
│  PyTorch:    2.x.x (CUDA enabled)                          │
│  MineRL:     1.0.x                                         │
│  SB3:        2.x.x                                         │
│  Gymnasium:  0.29.x                                        │
│                                                             │
│  GPU:        NVIDIA RTX 2050 (CUDA)                        │
│  Training:   Kaggle (T4/P100)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📎 Related Documents

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [TRAINING_GUIDE.md](TRAINING_GUIDE.md)
- [../TECH_STACK.md](../TECH_STACK.md)
