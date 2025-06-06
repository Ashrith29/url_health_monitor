from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
import requests
from urllib.parse import urlparse, urljoin
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
from werkzeug.security import safe_join

# Custom Jinja2 filter for datetime formatting
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Add the custom filter to Jinja2
app.jinja_env.filters['datetimeformat'] = datetimeformat

# In-memory storage for history and metrics (in production, use a database)
history = []
metrics = defaultdict(lambda: {
    'up_count': 0,
    'total_checks': 0,
    'response_times': deque(maxlen=100),  # Keep last 100 response times
    'last_check': None,
    'downtime_incidents': []
})

def check_url_health(url):
    """Check the health of a single URL"""
    if not url:
        return None
        
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        # Parse the URL to validate it
        parsed_url = urlparse(url)
        if not parsed_url.netloc:  # If no domain is provided
            return {
                'url': url,
                'status': 'INVALID',
                'time': 0,
                'error': 'Invalid URL: No domain provided'
            }
            
        start_time = time.time()
        response = requests.get(
            url,
            timeout=5,  # 5 seconds timeout
            headers={'User-Agent': 'URL Health Monitor'},
            allow_redirects=True,
            verify=True  # Verify SSL certificates
        )
        response_time = round((time.time() - start_time) * 1000, 2)  # Convert to milliseconds
        
        if 200 <= response.status_code < 400:
            status = 'UP'
        else:
            status = f'DOWN ({response.status_code})'
            
        return {
            'url': url,
            'status': status,
            'time': response_time,
            'status_code': response.status_code,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except requests.exceptions.SSLError:
        return {
            'url': url,
            'status': 'DOWN (SSL Error)',
            'time': 0,
            'error': 'SSL certificate verification failed'
        }
    except requests.exceptions.Timeout:
        return {
            'url': url,
            'status': 'DOWN (Timeout)',
            'time': 0,
            'error': 'Request timed out'
        }
    except requests.exceptions.TooManyRedirects:
        return {
            'url': url,
            'status': 'DOWN (Redirect Loop)',
            'time': 0,
            'error': 'Too many redirects'
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status': 'DOWN',
            'time': 0,
            'error': str(e)
        }

@app.route("/", methods=["GET", "POST"])
def index():
    global history  # Declare history as global at the start of the function
    results = []
    
    if request.method == "POST":
        urls_text = request.form.get("urls", "").strip()
        if not urls_text:
            flash('Please enter at least one URL', 'error')
            return redirect(url_for('index'))
            
        urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
        
        if not urls:
            flash('No valid URLs provided', 'error')
            return redirect(url_for('index'))
            
        # Check each URL
        current_check = []
        for url in urls:
            result = check_url_health(url)
            if result:  # Only add if result is not None
                current_check.append(result)
                # Update metrics
                update_metrics(url, 'UP' if result['status'] == 'UP' else 'DOWN', result.get('time', 0))
        
        if current_check:  # Only add to history if we have valid results
            history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': current_check
            })
            
            # Keep only the last 5 checks in history
            history = history[-5:]
            
            results = current_check
    
    # Prepare the history data for JavaScript
    history_data = json.dumps(history[-5:])
    
    return render_template(
        "index.html",
        results=results,
        history=history[-5:],  # Only show last 5 checks in the history panel
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        history_data=history_data
    )

def update_metrics(url, status, response_time):
    """Update metrics for a URL"""
    now = datetime.now()
    metrics[url]['total_checks'] += 1
    metrics[url]['last_check'] = now.isoformat()
    metrics[url]['response_times'].append(response_time)
    
    if status == 'UP':
        metrics[url]['up_count'] += 1
    else:
        # Record downtime incident
        if not metrics[url]['downtime_incidents'] or metrics[url]['downtime_incidents'][-1]['end'] is not None:
            metrics[url]['downtime_incidents'].append({
                'start': now.isoformat(),
                'end': None,
                'duration': None
            })
    
    # Update the most recent downtime incident if it's still ongoing
    for incident in reversed(metrics[url]['downtime_incidents']):
        if incident['end'] is None and status == 'UP':
            incident['end'] = now.isoformat()
            start_time = datetime.fromisoformat(incident['start'])
            incident['duration'] = (now - start_time).total_seconds()

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Clear the history of URL checks"""
    global history
    history = []
    flash('History has been cleared', 'success')
    return redirect(url_for('index'))

@app.route("/metrics")
def show_metrics():
    """Display metrics for all URLs"""
    # Calculate availability percentages
    metrics_with_availability = []
    for url, data in metrics.items():
        if data['total_checks'] > 0:
            availability = (data['up_count'] / data['total_checks']) * 100
            avg_response_time = sum(data['response_times']) / len(data['response_times']) if data['response_times'] else 0
            metrics_with_availability.append({
                'url': url,
                'availability': round(availability, 2),
                'avg_response_time': round(avg_response_time, 2),
                'total_checks': data['total_checks'],
                'last_check': data['last_check'],
                'downtime_incidents': data['downtime_incidents'][-5:]  # Last 5 incidents
            })
    
    return render_template("metrics.html", metrics=sorted(metrics_with_availability, key=lambda x: x['url']))

@app.route("/metrics/<path:url>")
def url_metrics(url):
    """Get metrics for a specific URL"""
    if url not in metrics:
        return jsonify({"error": "URL not found"}), 404
    
    data = metrics[url]
    availability = (data['up_count'] / data['total_checks']) * 100 if data['total_checks'] > 0 else 0
    avg_response_time = sum(data['response_times']) / len(data['response_times']) if data['response_times'] else 0
    
    return jsonify({
        'url': url,
        'availability': round(availability, 2),
        'avg_response_time': round(avg_response_time, 2),
        'total_checks': data['total_checks'],
        'last_check': data['last_check'],
        'response_times': list(data['response_times']),
        'downtime_incidents': data['downtime_incidents']
    })

@app.route("/static/<path:path>")
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
