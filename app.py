import os
import re
from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

import json
from models import db, Admin, Project, Skill, Message, Experience, Service, Profile, Article
from admin import admin_bp

# -------------------------------------------------------------------
# Construction robuste de l'URL de base de données
# On utilise 'or' au lieu du 2ème arg de .get() pour gérer
# les cas où Vercel stocke la variable comme chaîne vide ""
# -------------------------------------------------------------------
_db_uri = os.environ.get("DATABASE_URI") or None
if not _db_uri:
    _db_user     = os.environ.get("DB_USER")     or "postgres"
    _db_password = quote_plus(os.environ.get("DB_PASSWORD") or "")
    _db_host     = os.environ.get("DB_HOST")     or "localhost"
    _db_port     = os.environ.get("DB_PORT")     or "5432"
    _db_name     = os.environ.get("DB_NAME")     or "postgres"
    _db_uri = f"postgresql://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"

app.config['SQLALCHEMY_DATABASE_URI'] = _db_uri
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

TECH_LOGOS = {
    "html": {"label": "HTML5", "short": "HTML", "class": "html"},
    "html5": {"label": "HTML5", "short": "HTML", "class": "html"},
    "css": {"label": "CSS3", "short": "CSS", "class": "css"},
    "css3": {"label": "CSS3", "short": "CSS", "class": "css"},
    "javascript": {"label": "JavaScript", "short": "JS", "class": "js"},
    "js": {"label": "JavaScript", "short": "JS", "class": "js"},
    "react": {"label": "React", "short": "⚛", "class": "react"},
    "react.js": {"label": "React", "short": "⚛", "class": "react"},
    "typescript": {"label": "TypeScript", "short": "TS", "class": "ts"},
    "tailwind": {"label": "Tailwind CSS", "short": "TW", "class": "tailwind"},
    "tailwind css": {"label": "Tailwind CSS", "short": "TW", "class": "tailwind"},
    "flask": {"label": "Flask", "short": "Fl", "class": "flask"},
    "python": {"label": "Python", "short": "Py", "class": "python"},
}


def skill_logo(skill):
    key = skill.name.strip().lower()
    logo = TECH_LOGOS.get(key, {"label": skill.name, "short": skill.name[:2].upper(), "class": "default"})
    return {"name": skill.name, **logo}

@app.context_processor
def utility_processor():
    def image_url(path, default_placeholder="img/placeholder.png"):
        if not path:
            return url_for('static', filename=default_placeholder)
        if path.startswith('http://') or path.startswith('https://'):
            return path
        return url_for('static', filename=path)
    return dict(image_url=image_url)


@app.context_processor
def inject_globals():
    """Rend le profil disponible dans tous les templates."""
    try:
        prof = Profile.query.first()
    except Exception:
        prof = None

    # --- Profil par défaut si la table est vide ou inaccessible ---
    if not prof:
        default_profile = {
            "name": "Kazembe",
            "first_name": "Slova",
            "role": "Développeur Web Front-end",
            "tagline": "Je crée des expériences web modernes et performantes.",
            "location": "Lubumbashi, RDC",
            "email": "slovakazembe@gmail.com",
            "phone": "",
            "availability": "Disponible pour freelance",
            "cv_url": None,
            "hero_photo": None,
            "about_photo": None,
            "socials": {"github": "#", "linkedin": "#", "twitter": "#", "dribbble": "#"},
            "stats": [
                {"icon": "calendar", "value": "2+", "label": "Années d'expérience"},
                {"icon": "code", "value": "10+", "label": "Projets réalisés"},
                {"icon": "users", "value": "5+", "label": "Clients satisfaits"},
                {"icon": "heart", "value": "100%", "label": "Passionné"},
            ],
        }
        default_about = {
            "paragraphs": [
                "Développeur web passionné, spécialisé dans la création d'interfaces modernes.",
                "En formation Bac 3 Informatique à Lubumbashi, je combine académique et freelance.",
            ],
            "info": [
                {"label": "Nom", "value": "Slova Kazembe"},
                {"label": "Email", "value": "slovakazembe@gmail.com"},
                {"label": "Localisation", "value": "Lubumbashi, RDC"},
                {"label": "Disponibilité", "value": "Disponible pour freelance"},
            ]
        }
        return {"profile": default_profile, "about": default_about}

    # --- Profil depuis la base de données ---
    about_paragraphs = []
    if prof.about_paragraphs:
        try:
            about_paragraphs = json.loads(prof.about_paragraphs)
        except Exception:
            about_paragraphs = prof.about_paragraphs.split('\n\n')

    profile_dict = {
        "name": prof.name or "Kazembe",
        "first_name": prof.first_name or "Slova",
        "role": prof.role or "Développeur Web",
        "tagline": prof.tagline or "",
        "location": prof.location or "Lubumbashi, RDC",
        "email": prof.email or "",
        "phone": prof.phone or "",
        "availability": prof.availability or "Disponible",
        "cv_url": prof.cv_url,
        "hero_photo": prof.hero_photo,
        "about_photo": prof.about_photo,
        "socials": {
            "github": prof.github or "#",
            "linkedin": prof.linkedin or "#",
            "twitter": prof.twitter or "#",
            "dribbble": prof.dribbble or "#",
        },
        "stats": [
            {"icon": "calendar", "value": prof.stats_years or "2+", "label": "Années d'expérience"},
            {"icon": "code", "value": prof.stats_projects or "10+", "label": "Projets réalisés"},
            {"icon": "users", "value": prof.stats_clients or "5+", "label": "Clients satisfaits"},
            {"icon": "heart", "value": prof.stats_passion or "100%", "label": "Passionné"},
        ],
    }

    about_dict = {
        "paragraphs": about_paragraphs,
        "info": [
            {"label": "Nom", "value": prof.name or ""},
            {"label": "Email", "value": prof.email or ""},
            {"label": "Localisation", "value": prof.location or ""},
            {"label": "Disponibilité", "value": prof.availability or ""},
        ]
    }
    return {"profile": profile_dict, "about": about_dict}


@app.route("/")
def index():
    projects_db = Project.query.filter_by(status='Publié').order_by(Project.created_at.desc()).all()
    tech_skills_db = Skill.query.filter_by(type='tech').all()
    tech_skill_cards = [skill_logo(skill) for skill in tech_skills_db]
    tools_skills_db = Skill.query.filter_by(type='tool').all()
    services_db = Service.query.order_by(Service.id.asc()).all()
    experience_db = Experience.query.order_by(Experience.id.asc()).all()
    articles_db = Article.query.filter_by(status='Publié').order_by(Article.created_at.desc()).limit(3).all()
    
    categories = ["Tous"]
    for p in projects_db:
        if p.category not in categories:
            categories.append(p.category)

    return render_template(
        "index.html",
        categories=categories,
        projects=projects_db,
        tech_skills=tech_skill_cards,
        tools=[t.name for t in tools_skills_db],
        services=services_db,
        experience=experience_db,
        tech_badges=TECH_BADGES,
        articles=articles_db,
    )


@app.route("/articles")
def public_articles():
    articles_db = Article.query.filter_by(status='Publié').order_by(Article.created_at.desc()).all()
    return render_template("articles.html", articles=articles_db)


@app.route("/articles/<int:article_id>")
def public_article(article_id):
    article = Article.query.filter_by(id=article_id, status='Publié').first_or_404()
    return render_template("article_detail.html", article=article)


@app.route("/contact", methods=["POST"])
def contact():
    website = request.form.get("website", "").strip()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if website:
        flash("Votre message a bien été envoyé. Merci !", "success")
    elif not name or not email or not message:
        flash("Merci de remplir au moins le nom, l'email et le message.", "error")
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        flash("Merci d'indiquer une adresse email valide.", "error")
    else:
        msg = Message(name=name, email=email, subject=subject, content=message)
        db.session.add(msg)
        db.session.commit()
        flash("Votre message a bien été envoyé. Merci ! Je vous répondrai rapidement.", "success")
    return redirect(url_for("index", _anchor="contact"))


if __name__ == "__main__":
    app.run(debug=True)
