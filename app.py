import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

import json
from models import db, Admin, Project, Skill, Message, Experience, Service, Profile, Article
from admin import admin_bp

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI", "sqlite:///portfolio.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "error"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

app.register_blueprint(admin_bp)
# Logos technologiques flottants affichés sur la section d'accueil
TECH_BADGES = [
    {"label": "HTML5", "short": "HTML", "color": "#e34f26"},
    {"label": "CSS3", "short": "CSS", "color": "#2965f1"},
    {"label": "JavaScript", "short": "JS", "color": "#f0db4f", "text_dark": True},
    {"label": "React", "short": "⚛", "color": "#0d1117", "border": "#61dafb", "text_color": "#61dafb"},
    {"label": "TypeScript", "short": "TS", "color": "#3178c6"},
    {"label": "Tailwind CSS", "short": "〜", "color": "#0d1117", "border": "#38bdf8", "text_color": "#38bdf8"},
]


@app.context_processor
def inject_globals():
    """Rend le profil disponible dans tous les templates."""
    prof = Profile.query.first()
    if not prof:
        return {}
    
    about_paragraphs = []
    if prof.about_paragraphs:
        try:
            about_paragraphs = json.loads(prof.about_paragraphs)
        except:
            about_paragraphs = prof.about_paragraphs.split('\n\n')

    profile_dict = {
        "name": prof.name,
        "first_name": prof.first_name,
        "role": prof.role,
        "tagline": prof.tagline,
        "location": prof.location,
        "email": prof.email,
        "phone": prof.phone,
        "availability": prof.availability,
        "cv_url": prof.cv_url,
        "hero_photo": prof.hero_photo,
        "about_photo": prof.about_photo,
        "socials": {
            "github": prof.github,
            "linkedin": prof.linkedin,
            "twitter": prof.twitter,
            "dribbble": prof.dribbble,
        },
        "stats": [
            {"icon": "calendar", "value": prof.stats_years, "label": "Années d'expérience"},
            {"icon": "code", "value": prof.stats_projects, "label": "Projets réalisés"},
            {"icon": "users", "value": prof.stats_clients, "label": "Clients satisfaits"},
            {"icon": "heart", "value": prof.stats_passion, "label": "Passionné"},
        ],
    }
    
    about_dict = {
        "paragraphs": about_paragraphs,
        "info": [
            {"label": "Nom", "value": prof.name},
            {"label": "Email", "value": prof.email},
            {"label": "Localisation", "value": prof.location},
            {"label": "Disponibilité", "value": prof.availability},
        ]
    }
    return {"profile": profile_dict, "about": about_dict}


@app.route("/")
def index():
    projects_db = Project.query.order_by(Project.created_at.desc()).all()
    tech_skills_db = Skill.query.filter_by(type='tech').all()
    tools_skills_db = Skill.query.filter_by(type='tool').all()
    services_db = Service.query.order_by(Service.id.asc()).all()
    experience_db = Experience.query.order_by(Experience.id.asc()).all()
    
    categories = ["Tous"]
    for p in projects_db:
        if p.category not in categories:
            categories.append(p.category)

    return render_template(
        "index.html",
        categories=categories,
        projects=projects_db,
        tech_skills=tech_skills_db,
        tools=[t.name for t in tools_skills_db],
        services=services_db,
        experience=experience_db,
        tech_badges=TECH_BADGES,
    )


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Merci de remplir au moins le nom, l'email et le message.", "error")
    else:
        msg = Message(name=name, email=email, subject=subject, content=message)
        db.session.add(msg)
        db.session.commit()
        flash("Votre message a bien été envoyé. Merci ! Je vous répondrai rapidement.", "success")
    return redirect(url_for("index", _anchor="contact"))


if __name__ == "__main__":
    app.run(debug=True)
