from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

app = Flask(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'flask_app_request_count',
    'Total Request Count',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'flask_app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

DB_CONNECTION_COUNT = Gauge(
    'flask_app_db_connections',
    'Number of active database connections'
)

MESSAGE_COUNT = Gauge(
    'flask_app_total_messages',
    'Total number of messages in database'
)

# Database configuration
db_config = {
    'host': 'mysql',
    'user': 'root',
    'password': 'password',
    'database': 'messagesdb'
}

def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**db_config)
        DB_CONNECTION_COUNT.inc()
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def close_db_connection(conn):
    """Close database connection"""
    if conn:
        conn.close()
        DB_CONNECTION_COUNT.dec()

@app.before_request
def before_request():
    """Record request start time"""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Record metrics after each request"""
    if hasattr(request, 'start_time'):
        request_latency = time.time() - request.start_time
        REQUEST_LATENCY.labels(endpoint=request.endpoint or 'unknown').observe(request_latency)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        http_status=response.status_code
    ).inc()
    
    return response

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.route('/')
def index():
    """Display all messages"""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    messages = cursor.fetchall()
    
    # Update message count metric
    MESSAGE_COUNT.set(len(messages))
    
    cursor.close()
    close_db_connection(conn)
    
    return render_template('index.html', messages=messages)

@app.route('/add', methods=['POST'])
def add_message():
    """Add a new message"""
    message = request.form.get('message')
    if message:
        conn = get_db_connection()
        if not conn:
            return "Database connection failed", 500
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (message) VALUES (%s)", (message,))
        conn.commit()
        cursor.close()
        close_db_connection(conn)
    
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_message(id):
    """Delete a message"""
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    close_db_connection(conn)
    
    return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'flask-app'}, 200

if __name__ == '__main__':
    # Initialize database table
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        close_db_connection(conn)
    
    app.run(host='0.0.0.0', port=5000, debug=True)