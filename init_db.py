import json
import os

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

from app import app
from models import db, Admin, Project, Skill, Experience, Service, Profile, Article


DEFAULT_PROFILE = {
    "name": "Slova Kazembe",
    "first_name": "Slova",
    "role": "Développeur Web Front-end",
    "tagline": "Je crée des expériences web modernes, rapides et agréables à utiliser.",
    "location": "Lubumbashi, RDC",
    "email": "slovakazembe@gmail.com",
    "phone": "",
    "availability": "Disponible pour freelance",
    "cv_url": "https://canva.link/bx6gt0pguhhzg7v",
    "hero_photo": "img/hero-photo.jpg",
    "about_photo": "img/about-photo.jpg",
    "socials": {"github": "#", "linkedin": "#", "twitter": "#", "dribbble": "#"},
    "stats": {"years": "2+", "projects": "10+", "clients": "5+", "passion": "100%"},
}

DEFAULT_ABOUT = [
    "Développeur web passionné, spécialisé dans la création d'interfaces modernes et accessibles.",
    "En formation Bac 3 Informatique à Lubumbashi, je combine apprentissage académique, pratique freelance et sens du détail.",
]

DEFAULT_PROJECTS = [
    {
        "title": "Portfolio personnel",
        "description": "Une vitrine personnelle administrable avec projets, compétences, services et contact.",
        "category": "Web App",
        "tags": "Flask, HTML, CSS, JavaScript",
        "color": "1",
        "status": "Publié",
    },
    {
        "title": "Landing page moderne",
        "description": "Page de présentation responsive pour promouvoir un service ou une offre.",
        "category": "Landing Page",
        "tags": "UI/UX, Responsive, CSS",
        "color": "2",
        "status": "Publié",
    },
]

DEFAULT_TECH_SKILLS = [("HTML", 90), ("CSS", 85), ("JavaScript", 80), ("React", 70), ("Flask", 65)]
DEFAULT_TOOLS = ["Git", "VS Code", "Figma", "Supabase", "Vercel"]

DEFAULT_SERVICES = [
    ("layout", "Intégration web", "Création de pages modernes, propres et responsives."),
    ("code", "Développement front-end", "Interfaces interactives avec une attention forte portée à l'expérience utilisateur."),
    ("smartphone", "Responsive design", "Adaptation mobile, tablette et desktop pour une navigation fluide."),
]

DEFAULT_EXPERIENCES = [
    {
        "period": "2024 - Présent",
        "role": "Développeur web freelance",
        "company": "Indépendant",
        "description": "Conception de sites vitrines, portfolios et interfaces web pour des clients locaux.",
    }
]

DEFAULT_ARTICLES = [
    {
        "title": "Pourquoi un portfolio doit être vivant",
        "category": "Blog",
        "content": "Un bon portfolio ne montre pas seulement des projets. Il raconte une progression, une manière de penser et une capacité à résoudre des problèmes concrets.",
        "status": "Publié",
    }
]


def init_db():
    admin_username = os.environ.get("ADMIN_USERNAME", "slova")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    reset_db = os.environ.get("RESET_DB", "").lower() in {"1", "true", "yes"}

    if not admin_password:
        raise RuntimeError("Définissez ADMIN_PASSWORD dans .env avant d'initialiser la base.")

    with app.app_context():
        if reset_db:
            db.drop_all()
        db.create_all()

        if not Admin.query.filter_by(username=admin_username).first():
            db.session.add(Admin(username=admin_username, password_hash=generate_password_hash(admin_password)))

        if Profile.query.count() == 0:
            db.session.add(Profile(
                name=DEFAULT_PROFILE["name"],
                first_name=DEFAULT_PROFILE["first_name"],
                role=DEFAULT_PROFILE["role"],
                tagline=DEFAULT_PROFILE["tagline"],
                location=DEFAULT_PROFILE["location"],
                email=DEFAULT_PROFILE["email"],
                phone=DEFAULT_PROFILE["phone"],
                availability=DEFAULT_PROFILE["availability"],
                cv_url=DEFAULT_PROFILE["cv_url"],
                hero_photo=DEFAULT_PROFILE["hero_photo"],
                about_photo=DEFAULT_PROFILE["about_photo"],
                about_paragraphs=json.dumps(DEFAULT_ABOUT),
                github=DEFAULT_PROFILE["socials"]["github"],
                linkedin=DEFAULT_PROFILE["socials"]["linkedin"],
                twitter=DEFAULT_PROFILE["socials"]["twitter"],
                dribbble=DEFAULT_PROFILE["socials"]["dribbble"],
                stats_years=DEFAULT_PROFILE["stats"]["years"],
                stats_projects=DEFAULT_PROFILE["stats"]["projects"],
                stats_clients=DEFAULT_PROFILE["stats"]["clients"],
                stats_passion=DEFAULT_PROFILE["stats"]["passion"],
            ))

        if Project.query.count() == 0:
            for item in DEFAULT_PROJECTS:
                db.session.add(Project(**item))

        if Skill.query.filter_by(type="tech").count() == 0:
            for name, level in DEFAULT_TECH_SKILLS:
                db.session.add(Skill(name=name, level=level, type="tech"))

        if Skill.query.filter_by(type="tool").count() == 0:
            for name in DEFAULT_TOOLS:
                db.session.add(Skill(name=name, level=0, type="tool"))

        if Service.query.count() == 0:
            for icon, title, description in DEFAULT_SERVICES:
                db.session.add(Service(icon=icon, title=title, description=description))

        if Experience.query.count() == 0:
            for item in DEFAULT_EXPERIENCES:
                db.session.add(Experience(**item))

        if Article.query.count() == 0:
            for item in DEFAULT_ARTICLES:
                db.session.add(Article(**item))

        db.session.commit()
        print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
