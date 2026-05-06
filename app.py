#!/usr/bin/env python3
"""
Простое Flask-приложение для демонстрации CI/CD
"""
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def hello():
    student_name = os.environ.get('STUDENT_NAME', 'Student')
    return f"""
    <html>
        <head><title>CI/CD Demo</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1 style="color: #4CAF50;">Hello from Jenkins CI/CD Pipeline!</h1>
            <p><strong>Student:</strong> {student_name}</p>
            <p><strong>Hostname:</strong> {socket.gethostname()}</p>
            <p><strong>Version:</strong> 1.0.1</p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({'status': "healthy", "service": "python-app"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
