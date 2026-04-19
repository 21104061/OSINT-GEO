import json
import os
import re
import random
import time
import logging
from datetime import datetime
from collections import defaultdict
import sys
import threading
import webview
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import feedparser
import requests
import hashlib
import email.utils
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from geotext import GeoText
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Secure session configuration (prevents fallback key usage)
app.config['SESSION_COOKIE_SECURE'] = True  # Only send over HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout

# Ensure Vary: Cookie header is sent with session responses
@app.after_request
def add_vary_cookie_header(response):
    """Add Vary: Cookie header to ensure proper caching behavior"""
    if 'Set-Cookie' in response.headers or request.cookies:
        response.vary.add('Cookie')
    return response

# Configure CORS with security restrictions
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000", "http://localhost:5000"],  # Specify allowed origins
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type"],
             "expose_headers": ["Content-Type"],
             "supports_credentials": False,
             "max_age": 3600,
             "send_wildcard": False
         }
     })

# Local data storage
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BASE_DIR

DATA_DIR = os.path.join(APP_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Data will be stored in: {DATA_DIR}")

# Data storage files
INTELLIGENCE_FILE = os.path.join(DATA_DIR, 'intelligence.json')
DEDUP_FILE = os.path.join(DATA_DIR, 'dedup_cache.json')
GEOCACHE_FILE = os.path.join(DATA_DIR, 'geocache.json')

geolocator = Nominatim(user_agent="obsidian_osint_engine_v1")

# Configuration
CONFIG = {
    'max_intelligence': 2000,
    'update_interval': 300,  # 5 minutes
    'cache_ttl': 3600,
    'batch_size': 20,
    'api_timeout': 15,
    'enable_caching': True,
}

# Open source intelligence sources ONLY (RSS feeds with global coverage)
NEWS_SOURCES = {
    'rss_feeds': [
        'http://feeds.bbci.co.uk/news/world/rss.xml',
        'https://feeds.Reuters.com/reuters/worldNews',
        'https://feeds.aljazeera.com/AJEng/NorthAmerica',
        'https://feeds.aljazeera.com/AJEng/MiddleEast',
        'https://feeds.aljazeera.com/AJEng/AsiaPacific',
        'https://www.thehindu.com/news/national/feeder/default.rss',
        'https://indianexpress.com/section/india/feed/',
        'https://feeds.feedburner.com/ndtvnews-top-stories',
        'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
        'https://news.google.com/rss/search?q=India+current+affairs+competitive+exams+when:30d&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=Global+current+affairs+when:30d&hl=en-US&gl=US&ceid=US:en',
    ],
    'gnews_api': 'https://gnews.io/api/v4/search',  # Free gnews API for supplementary lookup
}

# Keywords for threat assessments
THREAT_KEYWORDS = {
    'critical': {
        'keywords': ['supreme court', 'major policy', 'amendment', 'budget', 'prime minister', 'president', 'isro', 'summit', 'brics', 'historic', 'nuclear', 'war'],
        'weight': 4.0
    },
    'high': {
        'keywords': ['parliament', 'election', 'rbi', 'economic', 'international', 'climate', 'defense', 'military', 'threat', 'conflict', 'sanctions'],
        'weight': 2.5
    },
    'medium': {
        'keywords': ['state government', 'scheme', 'court hearing', 'statement', 'visit', 'report', 'index ranking', 'appointment', 'award', 'warning', 'incident', 'diplomatic'],
        'weight': 1.5
    }
}

CATEGORIES = {
    'national': ['india', 'government', 'supreme court', 'parliament', 'lok sabha', 'rajya sabha', 'minister', 'scheme', 'yojana', 'policy'],
    'international': ['summit', 'treaty', 'alliance', 'un', 'united nations', 'g20', 'brics', 'asean', 'diplomacy', 'foreign', 'ambassador'],
    'economy': ['trade', 'tariff', 'commerce', 'export', 'import', 'currency', 'market', 'financial', 'gdp', 'inflation', 'rbi', 'budget', 'finance'],
    'science_tech': ['science', 'space', 'technology', 'isro', 'drdo', 'nasa', 'satellite', 'research', 'innovation', 'ai'],
    'defense': ['military', 'navy', 'army', 'air force', 'missile', 'exercise', 'defense', 'warship', 'security'],
    'environment': ['climate', 'environment', 'pollution', 'warming', 'green', 'sustainable', 'wildlife', 'conservation', 'cop'],
    'sports': ['olympics', 'world cup', 'cricket', 'bcci', 'fifa', 'tournament', 'championship', 'athlete'],
    'current_affairs': ['current affairs', 'general knowledge', 'education', 'exam', 'upsc', 'ssc']
}

ACTORS = {
    'state_us': ['united states', 'usa', 'u.s.', 'washington', 'america', 'american', 'pentagon', 'white house'],
    'state_cn': ['china', 'beijing', 'chinese', 'prc', 'beijing', 'peking'],
    'state_ru': ['russia', 'moscow', 'russian', 'kremlin', 'putin', 'russian federation'],
    'state_ir': ['iran', 'tehran', 'iranian', 'tehran', 'islamic republic'],
    'state_uk': ['united kingdom', 'uk', 'britain', 'england', 'london', 'british'],
    'state_fr': ['france', 'paris', 'french', 'élysée'],
    'state_in': ['india', 'new delhi', 'indian', 'delhi', 'bharat'],
    'state_jp': ['japan', 'tokyo', 'japanese', 'nippon'],
    'state_de': ['germany', 'berlin', 'german', 'bundesrepublik'],
    'nato': ['nato', 'north atlantic', 'nato alliance'],
    'un': ['united nations', 'un', 'u.n.', 'security council'],
    'eu': ['european union', 'eu', 'e.u.', 'brussels'],
}

LOCATION_COORDS = {
    'washington': {'lat': 38.9072, 'lon': -77.0369, 'name': 'Washington DC, USA', 'region': 'North America'},
    'beijing': {'lat': 39.9042, 'lon': 116.4074, 'name': 'Beijing, China', 'region': 'East Asia'},
    'moscow': {'lat': 55.7558, 'lon': 37.6173, 'name': 'Moscow, Russia', 'region': 'Eastern Europe'},
    'london': {'lat': 51.5074, 'lon': -0.1278, 'name': 'London, UK', 'region': 'Western Europe'},
    'paris': {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris, France', 'region': 'Western Europe'},
    'berlin': {'lat': 52.5200, 'lon': 13.4050, 'name': 'Berlin, Germany', 'region': 'Western Europe'},
    'tokyo': {'lat': 35.6762, 'lon': 139.6503, 'name': 'Tokyo, Japan', 'region': 'East Asia'},
    'seoul': {'lat': 37.5665, 'lon': 126.9780, 'name': 'Seoul, South Korea', 'region': 'East Asia'},
    'tehran': {'lat': 35.6892, 'lon': 51.3890, 'name': 'Tehran, Iran', 'region': 'Middle East'},
    'new delhi': {'lat': 28.6139, 'lon': 77.2090, 'name': 'New Delhi, India', 'region': 'South Asia'},
    'brussels': {'lat': 50.8503, 'lon': 4.3517, 'name': 'Brussels, Belgium', 'region': 'Western Europe'},
    'bangkok': {'lat': 13.7563, 'lon': 100.5018, 'name': 'Bangkok, Thailand', 'region': 'Southeast Asia'},
    'dubai': {'lat': 25.2048, 'lon': 55.2708, 'name': 'Dubai, UAE', 'region': 'Middle East'},
    'sydney': {'lat': -33.8688, 'lon': 151.2093, 'name': 'Sydney, Australia', 'region': 'Oceania'},
    'singapore': {'lat': 1.3521, 'lon': 103.8198, 'name': 'Singapore', 'region': 'Southeast Asia'},
    'south china sea': {'lat': 12.0, 'lon': 113.0, 'name': 'South China Sea', 'region': 'Strategic Waterway'},
    'strait of hormuz': {'lat': 26.5667, 'lon': 56.2500, 'name': 'Strait of Hormuz', 'region': 'Strategic Waterway'},
    'persian gulf': {'lat': 26.0, 'lon': 52.0, 'name': 'Persian Gulf', 'region': 'Strategic Waterway'},
    'taiwan strait': {'lat': 24.5, 'lon': 119.5, 'name': 'Taiwan Strait', 'region': 'Strategic Waterway'},
    'red sea': {'lat': 20.0, 'lon': 38.0, 'name': 'Red Sea', 'region': 'Strategic Waterway'},
    'andhra pradesh': {'lat': 15.9129, 'lon': 79.7400, 'name': 'Andhra Pradesh, India', 'region': 'India'},
    'arunachal pradesh': {'lat': 28.2180, 'lon': 94.7278, 'name': 'Arunachal Pradesh, India', 'region': 'India'},
    'assam': {'lat': 26.2006, 'lon': 92.9376, 'name': 'Assam, India', 'region': 'India'},
    'bihar': {'lat': 25.0961, 'lon': 85.3131, 'name': 'Bihar, India', 'region': 'India'},
    'chhattisgarh': {'lat': 21.2787, 'lon': 81.8661, 'name': 'Chhattisgarh, India', 'region': 'India'},
    'goa': {'lat': 15.2993, 'lon': 74.1240, 'name': 'Goa, India', 'region': 'India'},
    'gujarat': {'lat': 22.2587, 'lon': 71.1924, 'name': 'Gujarat, India', 'region': 'India'},
    'haryana': {'lat': 29.0588, 'lon': 76.0856, 'name': 'Haryana, India', 'region': 'India'},
    'himachal pradesh': {'lat': 31.1048, 'lon': 77.1665, 'name': 'Himachal Pradesh, India', 'region': 'India'},
    'jharkhand': {'lat': 23.6102, 'lon': 85.2799, 'name': 'Jharkhand, India', 'region': 'India'},
    'karnataka': {'lat': 15.3173, 'lon': 75.7139, 'name': 'Karnataka, India', 'region': 'India'},
    'kerala': {'lat': 10.8505, 'lon': 76.2711, 'name': 'Kerala, India', 'region': 'India'},
    'madhya pradesh': {'lat': 22.9734, 'lon': 78.6569, 'name': 'Madhya Pradesh, India', 'region': 'India'},
    'maharashtra': {'lat': 19.7515, 'lon': 75.7139, 'name': 'Maharashtra, India', 'region': 'India'},
    'manipur': {'lat': 24.6637, 'lon': 93.9063, 'name': 'Manipur, India', 'region': 'India'},
    'meghalaya': {'lat': 25.4670, 'lon': 91.3662, 'name': 'Meghalaya, India', 'region': 'India'},
    'mizoram': {'lat': 23.1645, 'lon': 92.9376, 'name': 'Mizoram, India', 'region': 'India'},
    'nagaland': {'lat': 26.1584, 'lon': 94.5624, 'name': 'Nagaland, India', 'region': 'India'},
    'odisha': {'lat': 20.9517, 'lon': 85.0985, 'name': 'Odisha, India', 'region': 'India'},
    'punjab': {'lat': 31.1471, 'lon': 75.3412, 'name': 'Punjab, India', 'region': 'India'},
    'rajasthan': {'lat': 27.0238, 'lon': 74.2179, 'name': 'Rajasthan, India', 'region': 'India'},
    'sikkim': {'lat': 27.5330, 'lon': 88.5122, 'name': 'Sikkim, India', 'region': 'India'},
    'tamil nadu': {'lat': 11.1271, 'lon': 78.6569, 'name': 'Tamil Nadu, India', 'region': 'India'},
    'telangana': {'lat': 18.1124, 'lon': 79.0193, 'name': 'Telangana, India', 'region': 'India'},
    'tripura': {'lat': 23.9408, 'lon': 91.9882, 'name': 'Tripura, India', 'region': 'India'},
    'uttar pradesh': {'lat': 26.8467, 'lon': 80.9462, 'name': 'Uttar Pradesh, India', 'region': 'India'},
    'uttarakhand': {'lat': 30.0668, 'lon': 79.0193, 'name': 'Uttarakhand, India', 'region': 'India'},
    'west bengal': {'lat': 22.9868, 'lon': 87.8550, 'name': 'West Bengal, India', 'region': 'India'},
    'delhi': {'lat': 28.7041, 'lon': 77.1025, 'name': 'Delhi, India', 'region': 'India'},
    'jammu and kashmir': {'lat': 33.7782, 'lon': 76.5762, 'name': 'Jammu and Kashmir, India', 'region': 'India'},
    'ladakh': {'lat': 34.1526, 'lon': 77.5771, 'name': 'Ladakh, India', 'region': 'India'}
}

# Global state
intelligence_db = []
dedup_cache = {}
geocache_db = {}
metrics = {'total_fetched': 0, 'duplicates_filtered': 0, 'errors': 0}

def load_cache():
    global dedup_cache, geocache_db
    if os.path.exists(DEDUP_FILE):
        try:
            with open(DEDUP_FILE, 'r') as f:
                dedup_cache = json.load(f)
        except:
            dedup_cache = {}
    if os.path.exists(GEOCACHE_FILE):
        try:
            with open(GEOCACHE_FILE, 'r') as f:
                geocache_db = json.load(f)
        except:
            geocache_db = {}

def save_cache():
    try:
        with open(DEDUP_FILE, 'w') as f:
            json.dump(dedup_cache, f)
        with open(GEOCACHE_FILE, 'w') as f:
            json.dump(geocache_db, f)
    except Exception as e:
        logger.error(f"Save cache error: {e}")

def generate_hash(text):
    return hashlib.md5(text.lower().strip().encode()).hexdigest()

def load_intelligence():
    global intelligence_db
    if os.path.exists(INTELLIGENCE_FILE):
        try:
            with open(INTELLIGENCE_FILE, 'r') as f:
                intelligence_db = json.load(f)
        except:
            intelligence_db = []

def save_intelligence():
    try:
        with open(INTELLIGENCE_FILE, 'w') as f:
            json.dump(intelligence_db, f, indent=2)
    except Exception as e:
        logger.error(f"Save intel error: {e}")

def assess_threat_level(text, title=''):
    combined = f"{title} {text}".lower()
    threat_score = 0
    for level, data in THREAT_KEYWORDS.items():
        for keyword in data['keywords']:
            if keyword.lower() in combined:
                threat_score = max(threat_score, data['weight'])
    if threat_score >= 3.5:
        return 'Critical'
    elif threat_score >= 2.0:
        return 'High'
    elif threat_score >= 1.0:
        return 'Medium'
    return 'Low'

def extract_actors(text):
    actors = []
    text_lower = text.lower()
    for actor_type, aliases in ACTORS.items():
        for alias in aliases:
            if alias.lower() in text_lower:
                actors.append(actor_type.upper())
                break
    if not actors:
        actors = ['UNKNOWN_ACTOR']
    return list(set(actors))

def categorize_intelligence(text):
    text_lower = text.lower()
    matches = {}
    for category, keywords in CATEGORIES.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            matches[category] = count
    if matches:
        return max(matches, key=matches.get)
    return 'intelligence'

def extract_location_coords(text, title=''):
    combined = f"{title}\n{text}"
    # Try hardcoded first to save API
    combined_lower = combined.lower()
    for loc_key, coords in LOCATION_COORDS.items():
        if loc_key in combined_lower:
            return coords
            
    # Fallback to pure geotext NLP
    places = GeoText(combined)
    named_entities = places.cities
    if not named_entities:
        named_entities = places.countries
        
    if named_entities:
        best_entity = named_entities[0]
        if best_entity in geocache_db:
            return geocache_db[best_entity]
            
        # Missing from cache, query geopy
        try:
            location = geolocator.geocode(best_entity, timeout=5)
            time.sleep(1.1) # comply with 1 req/sec limit
            if location:
                result = {'lat': location.latitude, 'lon': location.longitude, 'name': best_entity, 'region': 'Unknown'}
                geocache_db[best_entity] = result
                save_cache()
                return result
        except GeocoderTimedOut:
            pass
        except Exception as e:
            logger.error(f"Geocoding error for {best_entity}: {e}")
            
    return None

def parse_rss_feeds():
    logger.info("Parsing RSS feeds...")
    new_intel = []
    for feed_url in NEWS_SOURCES['rss_feeds']:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.get('title', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                if not title or not summary: continue
                
                content_hash = generate_hash(title + summary)
                if content_hash in dedup_cache:
                    metrics['duplicates_filtered'] += 1
                    continue
                
                full_text = f"{title} {summary}"
                is_relevant = any(kw in full_text.lower() for cats in CATEGORIES.values() for kw in cats)
                if not is_relevant: continue
                
                dedup_cache[content_hash] = datetime.utcnow().isoformat()
                
                category = categorize_intelligence(full_text)
                threat = assess_threat_level(full_text, title)
                actors = extract_actors(full_text)
                location = extract_location_coords(full_text, title)
                pub_date = entry.get('published', datetime.utcnow().isoformat())
                
                intel = {
                    'id': f"RSS_{int(time.time())}_{random.randint(1000, 9999)}",
                    'category': category,
                    'summary': title[:150],
                    'content': summary[:300],
                    'where': location['name'] if location else 'Global',
                    'who': actors,
                    'threatLevel': threat,
                    'timestamp': pub_date,
                    'source': entry.get('link', feed_url),
                    'source_type': 'RSS Feed',
                    'location': location,
                    'confidence': 0.85
                }
                new_intel.append(intel)
                metrics['total_fetched'] += 1
        except Exception as e:
            logger.error(f"Error parsing feed {feed_url}: {e}")
            metrics['errors'] += 1
    save_cache()
    return new_intel

def gather_intelligence():
    global intelligence_db
    logger.info("Gathering Intelligence via Public RSS")
    try:
        new_intel = parse_rss_feeds()
        threat_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        new_intel.sort(key=lambda x: (threat_order.get(x['threatLevel'], 0), x['timestamp']), reverse=True)
        
        intelligence_db = new_intel + intelligence_db
        intelligence_db = intelligence_db[:CONFIG['max_intelligence']]
        
        save_intelligence()
        save_cache()
        return new_intel
    except Exception as e:
        logger.error(f"Critical error in gathering: {e}")
        metrics['errors'] += 1
        return []

@app.route('/api/intelligence', methods=['GET'])
def get_intelligence():
    category = request.args.get('category', 'all')
    limit = int(request.args.get('limit', 50))
    threat = request.args.get('threat', 'all')
    region = request.args.get('region', 'all')
    timeframe = request.args.get('timeframe', 'all')
    
    filtered = intelligence_db
    
    if category != 'all':
        filtered = [i for i in filtered if str(i.get('category', '')).lower() == category.lower()]
    if threat != 'all':
        filtered = [i for i in filtered if str(i.get('threatLevel', '')).lower() == threat.lower()]
    if region != 'all':
        filtered = [i for i in filtered if region.lower() in str(i.get('where', '')).lower() or region.lower() in str(i.get('location', {})).lower()]
        
    if timeframe != 'all':
        try:
            hours = int(timeframe)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            valid_items = []
            for item in filtered:
                ts_str = item.get('timestamp', '')
                try:
                    # Attempt email/GMT format
                    item_dt = email.utils.parsedate_to_datetime(ts_str)
                except:
                    try:
                        # Attempt isoformat fallback
                        item_dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    except:
                        # If parsing fails, exclude it or include it? include it safely
                        valid_items.append(item)
                        continue
                
                # Make sure item_dt is timezone aware
                if item_dt.tzinfo is None:
                    item_dt = item_dt.replace(tzinfo=timezone.utc)
                    
                if item_dt >= cutoff:
                    valid_items.append(item)
            filtered = valid_items
        except ValueError:
            pass
            
    return jsonify(filtered[:limit])

@app.route('/api/gather', methods=['POST'])
def trigger_gather():
    new_intel = gather_intelligence()
    return jsonify({'success': True, 'count': len(new_intel)})

scheduler = BackgroundScheduler()

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

if __name__ == '__main__':
    load_cache()
    load_intelligence()
    if len(intelligence_db) == 0:
        gather_intelligence()
    
    scheduler.add_job(gather_intelligence, 'interval', seconds=CONFIG['update_interval'])
    scheduler.start()
    
    logger.info("Starting local backend server on port 5000")
    
    flask_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    time.sleep(1) # Let flask bind
    
    webview.create_window('OSINT EDUCATIONAL TRACKER', 'http://127.0.0.1:5000/')
    webview.start()
