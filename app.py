from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password123",   # change if different
    database="messagesdb"
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content VARCHAR(255)
)
""")
db.commit()

HTML = """
<h2>Simple Flask CI/CD App</h2>
<form method="POST">
  <input name="message" placeholder="Enter message"/>
  <button type="submit">Save</button>
</form>
<ul>
{% for msg in messages %}
<li>{{ msg }}</li>
{% endfor %}
</ul>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        msg = request.form.get("message")
        cursor.execute(
            "INSERT INTO messages (content) VALUES (%s)",
            (msg,)
        )
        db.commit()

    cursor.execute("SELECT content FROM messages")
    messages = [row[0] for row in cursor.fetchall()]
    return render_template_string(HTML, messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
