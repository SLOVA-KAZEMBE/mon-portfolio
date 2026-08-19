import json
import os
import pymysql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

from app import app
from models import db, Admin, Project, Skill, Experience, Service, Profile, Article
from app import PROJECTS, SKILLS_TECH, SKILLS_TOOLS, EXPERIENCE, SERVICES, PROFILE, ABOUT

def init_db():
    db_host = os.environ.get("DB_HOST", "localhost")
    db_user = os.environ.get("DB_USER", "root")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "portfolio_db")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")

    connection = pymysql.connect(host=db_host, user=db_user, password=db_password)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    finally:
        connection.close()

    with app.app_context():
        db.drop_all()
        db.create_all()

        if not Admin.query.filter_by(username='slova').first():
            admin = Admin(username='slova', password_hash=generate_password_hash(admin_password))
            db.session.add(admin)

        if Project.query.count() == 0:
            for p in PROJECTS:
                project = Project(
                    title=p['title'],
                    description=p['description'],
                    category=p['category'],
                    tags=",".join(p.get('tags', [])),
                    color=p.get('color', '1'),
                    status='Publié',
                    link=''
                )
                db.session.add(project)

        if Skill.query.filter_by(type='tech').count() == 0:
            for s in SKILLS_TECH:
                skill = Skill(name=s['name'], level=s['level'], type='tech')
                db.session.add(skill)
                
        if Skill.query.filter_by(type='tool').count() == 0:
            for t in SKILLS_TOOLS:
                skill = Skill(name=t, level=0, type='tool')
                db.session.add(skill)

        if Experience.query.count() == 0:
            for e in EXPERIENCE:
                exp = Experience(
                    period=e['period'],
                    role=e['role'],
                    company=e['company'],
                    description=e['description']
                )
                db.session.add(exp)

        if Service.query.count() == 0:
            for s in SERVICES:
                srv = Service(
                    icon=s['icon'],
                    title=s['title'],
                    description=s['description']
                )
                db.session.add(srv)

        if Profile.query.count() == 0:
            prof = Profile(
                name=PROFILE['name'],
                first_name=PROFILE['first_name'],
                role=PROFILE['role'],
                tagline=PROFILE['tagline'],
                location=PROFILE['location'],
                email=PROFILE['email'],
                phone=PROFILE['phone'],
                availability=PROFILE['availability'],
                cv_url=PROFILE['cv_url'],
                hero_photo=PROFILE['hero_photo'],
                about_photo=PROFILE['about_photo'],
                about_paragraphs=json.dumps(ABOUT['paragraphs']),
                github=PROFILE['socials']['github'],
                linkedin=PROFILE['socials']['linkedin'],
                twitter=PROFILE['socials']['twitter'],
                dribbble=PROFILE['socials']['dribbble'],
                stats_years=next((s['value'] for s in PROFILE['stats'] if s['label'] == "Années d'expérience"), "2+"),
                stats_projects=next((s['value'] for s in PROFILE['stats'] if s['label'] == "Projets réalisés"), "20+"),
                stats_clients=next((s['value'] for s in PROFILE['stats'] if s['label'] == "Clients satisfaits"), "15+"),
                stats_passion=next((s['value'] for s in PROFILE['stats'] if s['label'] == "Passionné"), "100%")
            )
            db.session.add(prof)

        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
