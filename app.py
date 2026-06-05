from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

YDL_OPTS_BASE = {
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['web_creator', 'ios'],
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    },
    'socket_timeout': 30,
}

@app.route('/')
def home():
    return jsonify({"status": "yt-dlp API running"})

@app.route('/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_BASE) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('url') and f.get('ext'):
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext':        f.get('ext'),
                        'quality':    f.get('format_note') or str(f.get('height', '')),
                        'filesize':   f.get('filesize'),
                        'vcodec':     f.get('vcodec'),
                        'acodec':     f.get('acodec'),
                        'url':        f.get('url'),
                    })
            return jsonify({
                "title":     info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration":  info.get('duration'),
                "uploader":  info.get('uploader'),
                "platform":  info.get('extractor_key'),
                "formats":   formats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
