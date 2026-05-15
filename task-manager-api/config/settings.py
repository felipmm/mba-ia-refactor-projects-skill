import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///tasks.db')
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
PORT = int(os.environ.get('PORT', '5000'))
