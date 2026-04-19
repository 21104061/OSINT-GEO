# 🌐 OBSIDIAN OSINT - Geopolitical Intelligence System

**A premium, local-first OSINT intelligence monitoring system with dynamic NLP geocoding and real-time mapping.**

![Status](https://img.shields.io/badge/status-operational-brightgreen)
![Architecture](https://img.shields.io/badge/architecture-local--first-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Overview

OBSIDIAN OSINT is a self-contained geopolitical intelligence gathering and analysis system. The architecture has been completely modernized from its early Colab-based prototypes to a robust, fully local Python application featuring:

- **Premium Glassmorphic Interface**: A sleek "Cybernetic Blue" dark mode UI with interactive controls.
- **True Local Control**: Secure Python Flask backend running locally—no third-party cloud tunnels required.
- **Dynamic NLP Geocoding**: Utilizes `geotext` to actively scan incoming intelligence and `Nominatim` OpenStreetMap API to generate accurate geospatial nodes on the fly.
- **Time & Regional Filtering**: Deep UI integrations allowing users to instantly manipulate timeframes and regional intelligence while adjusting display protocols to their local Time Standard.

---

## ✨ Key Features

### Frontend - The Obsidian Glass Interface
- **🎨 Glassmorphism Aesthetic**: Translucent backgrounds and dynamic electric blue UI elements.
- **⏱️ Timezone Agnostic**: Strict UTC backend cleanly pivots into local, EST, GMT, or JST via front-end selector menus.
- **🗺️ Interactive Situational Map**: High-contrast Leaflet engine with a dedicated *Maximize Map* war-room toggle.
- **⌨️ Omni-Search Command**: Raw command-line data fetching options natively built into the footer (`/fetch`).

### Backend - NLP Engine
- **📰 Free OSINT RSS Aggregation**: Gathers data across public sources (BBC, Reuters, Al Jazeera, CNBC).
- **🧠 Native NLP Processor**: Scans raw news bodies mathematically extracting Cities/Nations across the globe.
- **📍 Smart API Caching**: Local `geocache.json` algorithmic caching prevents rate-limit failures from OpenStreetMap.
- **🔄 Local Storage Strategy**: Secure persistence inside the `./data/` folder block.

---

## � Security

### Security Configuration
This application includes hardened security settings:

**CORS Protection:**
- Restricted to specified origins (default: `localhost:3000`, `localhost:5000`)
- Limited HTTP methods (GET, POST, OPTIONS)
- No wildcard origins or credentials by default
- Updated to Flask-CORS 5.0.0 with security and CORS improvements

**Session Security:**
- HttpOnly cookies prevent JavaScript access
- SameSite protection against CSRF attacks
- Secure cookie transmission (HTTPS in production)
- Session timeout: 1 hour
- Proper `Vary: Cookie` headers for cache control

**Dependency Updates:**
- Flask 3.1.3 - Stable REST API framework
- Flask-CORS 6.0.2 - CORS support with all security patches and regex/case-sensitivity fixes
- Requests 2.33.0 - Secure HTTP client library with .netrc leak and temp file reuse fixes

### Configuration Notes
**⚠️ For Production Deployment:**
1. Update the CORS origins in `backend.py` to your actual frontend URL
2. Set `SESSION_COOKIE_SECURE = True` ensures HTTPS-only transmission
3. Set environment variables or use a `.env` file for sensitive config
4. Use a production-grade WSGI server (Gunicorn, uWSGI) instead of Flask's debug server

---

## �🚀 Quick Start

### Prerequisites
- Modern web browser (Chrome, Firefox, Edge)
- Python 3.9+ 
- Node / Local HTTP Server (optional, for frontend viewing)

### ⚡ Easiest Way - Automated Setup (Recommended for Non-Technical Users)

#### **Windows Users:**
Simply double-click the `setup.bat` file and follow the prompts!

```
setup.bat  ← Double-click this file
```

#### **macOS/Linux Users:**
Open Terminal in the project folder and run:

```bash
chmod +x setup.sh
./setup.sh
```

#### **All Platforms (Alternative):**
Open Terminal/Command Prompt and run:

```bash
python setup.py
```

The setup scripts will automatically:
- ✅ Check Python installation
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Set up data directories
- ✅ Launch the backend server

Then simply open your browser to `http://localhost:8000/index.html`

---

### Manual Setup (5 minutes) - For Advanced Users

#### 1. **Create & Activate Virtual Environment** (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```
*(Dependencies include: feedparser, geopy, geotext, flask, flask-cors, apscheduler, pywebview)*

#### 3. **Launch Intelligence Backend**
Start the background daemon process bridging the REST API to your intelligence gatherer.
```bash
python backend.py
```
*The server will boot locally on `http://127.0.0.1:5000` and immediately trigger an intelligence gathering array.*

#### 4. **Boot Frontend Interface** (In a new terminal)
Launch a quick local server to view the dashboard securely.
```bash
# Windows
python -m http.server 8000

# macOS/Linux
python3 -m http.server 8000
```
Navigate your browser to `http://localhost:8000/index.html`.

**That's it! You're operational.** 🎉

---

## 🛠️ Troubleshooting

### GeoText Import Errors
If you encounter `FileNotFoundError` related to `geotext`, reinstall the package:
```bash
pip install --force-reinstall geotext==0.4.0
```

### Port Already in Use
If port 5000 or 8000 is occupied, specify an alternative:
```bash
# Backend on different port
# Modify backend.py: app.run(port=5001)

# Frontend on different port
python -m http.server 8001
```

### API Connection Issues
Ensure both backend and frontend are running and on the same network. The backend must be accessible at `http://127.0.0.1:5000` from your browser.

---

## 📁 Project Structure

```
.
├── backend.py              # Flask backend & intelligence engine
├── index.html              # Frontend interface (Glassmorphism UI)
├── setup.bat               # Windows automated installer (double-click!)
├── setup.sh                # macOS/Linux automated installer
├── setup.py                # Cross-platform Python installer
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── data/                   # Local persistent storage
    ├── intelligence.json   # Latest intelligence objects
    ├── dedup_cache.json    # Content deduplication filter
    └── geocache.json       # Geocoding coordinate mapping
```

**Setup Files Explained:**
- `setup.bat` - **Windows users: Just double-click this!** Handles everything automatically
- `setup.sh` - **macOS/Linux users: Run `./setup.sh`** Handles everything automatically  
- `setup.py` - Alternative for all platforms, run with `python setup.py`

---

## ⚙️ Configuration & Architecture

### Data Persistence
All operations occur locally in the `./data/` folder, which is tightly ignored by git via `.gitignore` to prevent public leaking of intelligence caches.
- `intelligence.json`: Array hash of the latest intelligence objects.
- `dedup_cache.json`: Content-hashed duplicates filter.
- `geocache.json`: Permanent geocoding tracker resolving NLP entities to OSINT map coordinates.

### Intelligence Categories & Threat Levels
- **Categories**: ATTACKS, CONFLICTS, DIPLOMATIC, ECONOMIC, NAVAL, CYBER.
- **Threat Levels**: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

---

## 🔌 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/intelligence` | Fetch all intelligence records |
| `GET` | `/api/intelligence/<id>` | Get specific intelligence by ID |
| `GET` | `/api/locations` | Fetch mapped geolocation data |
| `POST` | `/api/fetch` | Trigger manual intelligence refresh |
| `GET` | `/api/stats` | Get system statistics |

### WebSocket Events
- Real-time updates stream to connected clients as new intelligence arrives
- Automatic refresh triggered on configurable intervals

---

## 🎓 System Capabilities

### Intelligence Sources
- BBC News RSS
- Reuters RSS
- Al Jazeera RSS
- CNBC RSS
- (Extensible for additional sources)

### NLP Processing
- Automatic location extraction from news articles
- Entity recognition for cities, countries, and regions
- Smart deduplication to filter repetitive reports

### Mapping & Visualization
- Real-time geolocation plotting
- Interactive map interface with zoom/pan controls
- Timezone-aware timestamp display
- Regional filtering capabilities

---

## 💡 Usage Tips

1. **Maximum Map View**: Click the map maximize button in the top-right for a full war-room display
2. **Time Filtering**: Use the timezone selector to view all timestamps in your preferred timezone
3. **Search**: Use the omni-search footer feature with `/fetch` command for manual data retrieval
4. **Export**: Intelligence can be extracted from `./data/intelligence.json` for external analysis

---

## 📊 Performance Notes

- First run processes all available RSS feeds (~30-60 seconds)
- Subsequent runs use deduplication cache for faster processing
- Geocoding is cached to minimize API calls to Nominatim
- Background scheduler runs collection cycles at configurable intervals

---

## 📜 License
MIT License - See LICENSE file for details.

### Attribution
- Google `Inter` and `JetBrains Mono` Typography
- OpenStreetMap and `Nominatim` Map APIs
- Leaflet.js
- BBC, Reuters, and Al Jazeera open-source Public RSS

---

**STATUS**: OPERATIONAL  
**VERSION**: 2.0.0 (Premium Refactor)  

```bash
> SYSTEM INITIALIZED
> AWAITING INSTRUCTIONS...
```
