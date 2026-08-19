from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(255)) # comma-separated tags
    color = db.Column(db.String(10)) # e.g. "1", "2"
    image = db.Column(db.String(255))
    link = db.Column(db.String(255)) # URL du projet
    status = db.Column(db.String(20), default='Publié') # Publié or Brouillon
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'tech' or 'tool'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Publié')
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    role = db.Column(db.String(100))
    tagline = db.Column(db.Text)
    location = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    availability = db.Column(db.String(100))
    cv_url = db.Column(db.String(255))
    hero_photo = db.Column(db.String(255))
    about_photo = db.Column(db.String(255))
    about_paragraphs = db.Column(db.Text) # Stored as JSON or separated by double newlines
    github = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    dribbble = db.Column(db.String(255))
    # Stats (can be stored as JSON text to keep it simple, or separate columns)
    stats_years = db.Column(db.String(20))
    stats_projects = db.Column(db.String(20))
    stats_clients = db.Column(db.String(20))
    stats_passion = db.Column(db.String(20))
