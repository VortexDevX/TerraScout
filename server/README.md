# 🎮 Minecraft Server

> Local Minecraft server for Terra Scout training.

## 📥 Setup

### Download Server

1. Go to: https://www.minecraft.net/en-us/download/server
2. Download `server.jar` for version 1.21.1
3. Place in this directory

### Or Use PaperMC (Recommended)

1. Go to: https://papermc.io/downloads/paper
2. Download Paper for version 1.21.1
3. Rename to `server.jar`
4. Place in this directory

## 🚀 Start Server

```powershell
./start.ps1
```

## ⚙️ Configuration

Server properties are in `server.properties` (created on first run).

Recommended settings for training:

```properties
online-mode=false
spawn-protection=0
difficulty=normal
gamemode=survival
pvp=false
max-players=1
view-distance=10
enable-command-block=true
```

## 📋 Requirements

- Java 21 or higher
- 2GB+ RAM allocated
