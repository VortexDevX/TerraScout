# 🔧 Troubleshooting Guide

> Solutions to common Terra Scout issues.

---

## 📋 Quick Reference

| Error                 | Quick Fix                | Section                             |
| --------------------- | ------------------------ | ----------------------------------- |
| JAVA_HOME not set     | Set environment variable | [Java Issues](#java-issues)         |
| Visual C++ required   | Install Build Tools      | [Build Issues](#build-issues)       |
| CUDA not available    | Reinstall PyTorch        | [GPU Issues](#gpu-issues)           |
| MineRL import error   | Reinstall MineRL         | [MineRL Issues](#minerl-issues)     |
| Out of memory         | Reduce batch size        | [Memory Issues](#memory-issues)     |
| Training not learning | Check reward/hyperparams | [Training Issues](#training-issues) |

---

## ☕ Java Issues

### Error: JAVA_HOME is not set

**Symptom:**

```
Error: JAVA_HOME is not set and no 'java' command could be found
```

**Solution:**

1. Find Java installation:

```powershell
where java
```

2. Set JAVA_HOME:

```powershell
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\OpenJDK\jdk-1.8.0_472', 'User')
```

3. Restart PowerShell and verify:

```powershell
echo $env:JAVA_HOME
```

---

### Error: Wrong Java Version

**Symptom:**

```
Error: MineRL requires Java 8
```

**Solution:**

1. Check current version:

```powershell
java -version
```

2. If not Java 8, install OpenJDK 8:
   - Download from: https://adoptium.net/temurin/releases/?version=8
   - Install and update JAVA_HOME

3. If multiple Java versions exist:

```powershell
# Point JAVA_HOME specifically to Java 8
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-8.0.XXX-hotspot', 'User')
```

---

### Error: javac not found

**Symptom:**

```
'javac' is not recognized as an internal or external command
```

**Solution:**

You have JRE instead of JDK. Install full JDK:

1. Download JDK 8 (not JRE): https://adoptium.net/temurin/releases/?version=8
2. Ensure you select "JDK" package
3. Update JAVA_HOME to JDK path

---

## 🔨 Build Issues

### Error: Microsoft Visual C++ 14.0 is required

**Symptom:**

```
error: Microsoft Visual C++ 14.0 or greater is required.
```

**Solution:**

1. Download Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Run installer and select:

   ```
   ✅ Desktop development with C++
      ├── ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
      └── ✅ Windows 11 SDK
   ```

3. Install (~5-10 GB)
4. Restart computer
5. Retry pip install

---

### Error: wheel build failed

**Symptom:**

```
Failed building wheel for minerl
```

**Solution:**

1. Ensure Build Tools are installed (see above)

2. Upgrade pip and wheel:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

3. Install with verbose output to see actual error:

```powershell
pip install minerl -v
```

4. If still failing, try:

```powershell
pip install --no-cache-dir minerl
```

---

## 🎮 GPU Issues

### Error: CUDA not available

**Symptom:**

```python
>>> torch.cuda.is_available()
False
```

**Solution:**

1. Check NVIDIA driver:

```powershell
nvidia-smi
```

2. If `nvidia-smi` fails, install/update NVIDIA drivers:
   https://www.nvidia.com/download/index.aspx

3. Reinstall PyTorch with correct CUDA version:

```powershell
# Check CUDA version from nvidia-smi output
# Then install matching PyTorch

# For CUDA 11.8:
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

4. Verify:

```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))  # Should show your GPU
```

---

### Error: CUDA out of memory

**Symptom:**

```
RuntimeError: CUDA out of memory. Tried to allocate X MiB
```

**Solution:**

1. Reduce batch size in config:

```yaml
hyperparameters:
  batch_size: 32 # Reduce from 64
```

2. Reduce n_steps:

```yaml
hyperparameters:
  n_steps: 1024 # Reduce from 2048
```

3. Clear GPU cache before training:

```python
import torch
torch.cuda.empty_cache()
```

4. Close other GPU applications (browsers, games, etc.)

---

## 🎯 MineRL Issues

### Error: No module named 'minerl'

**Symptom:**

```
ModuleNotFoundError: No module named 'minerl'
```

**Solution:**

1. Ensure virtual environment is activated:

```powershell
.\venv\Scripts\Activate.ps1
```

2. Install MineRL:

```powershell
pip install minerl
```

3. If install fails, see [Build Issues](#build-issues)

---

### Error: MineRL environment hangs on reset

**Symptom:**

```python
env.reset()  # Hangs indefinitely
```

**Solution:**

1. First run downloads Minecraft assets (~1GB). Wait patiently.

2. If still hanging after 10+ minutes:

```powershell
# Kill any orphan Java processes
Get-Process java | Stop-Process -Force

# Clear MineRL cache
Remove-Item -Recurse -Force $env:USERPROFILE\.minerl
```

3. Retry

---

### Error: Malmo not found

**Symptom:**

```
FileNotFoundError: Malmo directory not found
```

**Solution:**

1. Reinstall MineRL:

```powershell
pip uninstall minerl
pip install --no-cache-dir minerl
```

2. Check JAVA_HOME is set correctly

3. Ensure Java 8 (not newer)

---

### Error: Port already in use

**Symptom:**

```
Error: Port 9000 already in use
```

**Solution:**

1. Kill existing Minecraft/Java processes:

```powershell
Get-Process -Name java | Stop-Process -Force
Get-Process -Name minecraft | Stop-Process -Force
```

2. Or use different port:

```python
env = gym.make('MineRLNavigateDense-v0', port=9001)
```

---

## 🧠 Training Issues

### Issue: Training reward is flat

**Symptom:**

- Episode reward not increasing
- No learning progress

**Diagnosis:**

```python
# Check if getting any positive rewards
print(f"Mean reward: {np.mean(rewards)}")
print(f"Max reward: {np.max(rewards)}")
print(f"Min reward: {np.min(rewards)}")
```

**Solutions:**

1. **Check reward function:**
   - Is diamond reward being triggered?
   - Are shaping rewards too small?

2. **Increase exploration:**

```yaml
hyperparameters:
  ent_coef: 0.05 # Increase from 0.01
```

3. **Check environment:**

```python
# Verify environment returns expected observations
obs, info = env.reset()
print(f"Observation keys: {obs.keys()}")
```

---

### Issue: Agent keeps dying

**Symptom:**

- Very short episodes
- Low survival rate

**Solutions:**

1. **Increase death penalty:**

```python
DEATH_PENALTY = -500.0  # More severe
```

2. **Add survival rewards:**

```python
# Small reward for staying alive
if not done:
    reward += 0.01
```

3. **Reduce exploration early:**

```yaml
hyperparameters:
  ent_coef: 0.001 # Less random actions
```

---

### Issue: Agent gets stuck

**Symptom:**

- Agent repeats same actions
- Position doesn't change

**Solutions:**

1. **Add stuck penalty:**

```python
if position == last_position:
    stuck_counter += 1
    if stuck_counter > 50:
        reward -= 0.5
```

2. **Add curiosity/exploration bonus:**

```python
if position not in visited_positions:
    reward += 0.1
    visited_positions.add(position)
```

---

### Issue: Catastrophic forgetting

**Symptom:**

- Reward suddenly drops after good progress
- Model "forgets" learned behavior

**Solutions:**

1. **Reduce learning rate:**

```yaml
hyperparameters:
  learning_rate: 0.0001 # From 0.0003
```

2. **Reduce clip range:**

```yaml
hyperparameters:
  clip_range: 0.1 # From 0.2
```

3. **Increase batch size:**

```yaml
hyperparameters:
  batch_size: 128 # From 64
```

---

## 💾 Memory Issues

### Python memory leak

**Symptom:**

- RAM usage grows over time
- Eventually crashes

**Solution:**

1. Ensure environment is closed:

```python
try:
    # Training code
finally:
    env.close()
```

2. Clear Python garbage:

```python
import gc
gc.collect()
```

3. Monitor memory:

```python
import psutil
print(f"RAM: {psutil.Process().memory_info().rss / 1e9:.2f} GB")
```

---

## 🔍 Debugging Commands

### Check Environment

```python
import gymnasium as gym
import minerl

# List available environments
for env_spec in gym.envs.registry.keys():
    if 'MineRL' in env_spec:
        print(env_spec)
```

### Check GPU Memory

```python
import torch

print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Memory allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
print(f"Memory cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
```

### Check System Resources

```powershell
# CPU and RAM
Get-Process python | Select-Object CPU, WorkingSet64

# GPU
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv
```

---

## 🆘 Getting Help

If issues persist:

1. **Check MineRL GitHub Issues:**
   https://github.com/minerllabs/minerl/issues

2. **Check SB3 Documentation:**
   https://stable-baselines3.readthedocs.io/

3. **MineRL Discord:**
   https://discord.gg/minerl

4. **Create detailed issue report:**
   - Python version
   - Error traceback
   - Steps to reproduce
   - System specs

---

## 📎 Related Documents

- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [TRAINING_GUIDE.md](TRAINING_GUIDE.md)
- [../TECH_STACK.md](../TECH_STACK.md)
