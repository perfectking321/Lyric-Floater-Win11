# ⚡ Quick Start Guide

Get Lyric Floater running in 5 minutes!

---

## 🚀 Fast Setup (First Time)

### 1. Install Python
```powershell
# Download from python.org (3.8+)
# ✅ Check "Add Python to PATH" during installation
python --version  # Verify: Should show Python 3.8+
```

### 2. Install Dependencies
```powershell
cd Lyric-Floater-Win11
pip install -r requirements_pygame.txt
```

### 3. Get Spotify API Credentials

1. Visit: https://developer.spotify.com/dashboard
2. Login → Create App
3. Copy **Client ID** and **Client Secret**
4. Set Redirect URI: `http://localhost:8888/callback`

### 4. Configure
Open `config.json` and paste your credentials:
```json
{
    "spotify_client_id": "PASTE_YOUR_CLIENT_ID",
    "spotify_client_secret": "PASTE_YOUR_CLIENT_SECRET",
    "spotify_redirect_uri": "http://localhost:8888/callback",
    "genius_access_token": ""
}
```

### 5. Run!
```powershell
python main_pygame.py
```

**First time:** Browser opens → Login to Spotify → Copy URL → Paste in terminal → Done!

---

## 🎵 Daily Use

```powershell
cd Lyric-Floater-Win11
python main_pygame.py
```

1. Open Spotify Desktop
2. Play any song
3. Lyrics appear automatically! 🎉

---

## 🔧 If Something Breaks

### No lyrics showing?
```powershell
# Clear cache
Remove-Item lyrics_cache\* -Force
```

### Authorization error?
```powershell
# Re-authenticate
Remove-Item .spotify_cache\* -Force
python main_pygame.py
```

### Module not found?
```powershell
# Reinstall dependencies
pip install -r requirements_pygame.txt --force-reinstall
```

---

## 📚 Full Documentation

For detailed info, troubleshooting, and customization:
👉 See **README.md**

---

**That's it! Enjoy your synced lyrics! 🎶**
