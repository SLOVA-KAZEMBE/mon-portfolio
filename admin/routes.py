import os
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from . import admin_bp
from models import db, Admin, Project, Skill, Message, Experience, Service, Article, Profile
from datetime import datetime
import json
import uuid
from supabase import create_client, Client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(image_file, root_path):
    if not image_file or not allowed_file(image_file.filename):
        return None
    
    filename = secure_filename(image_file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    
    if supabase:
        try:
            # Upload to Supabase Storage bucket named 'portfolio'
            file_bytes = image_file.read()
            supabase.storage.from_('portfolio').upload(unique_filename, file_bytes, {"content-type": image_file.content_type})
            # Get public URL
            public_url = supabase.storage.from_('portfolio').get_public_url(unique_filename)
            return public_url
        except Exception as e:
            print("Erreur upload Supabase:", e)
            return None
    else:
        # Local upload fallback
        upload_folder = os.path.join(root_path, 'static', 'img', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_file.save(os.path.join(upload_folder, unique_filename))
        return f'img/uploads/{unique_filename}'

@admin_bp.context_processor
def inject_admin_globals():
    if current_user.is_authenticated:
        unread = Message.query.filter_by(is_read=False).count()
        return {'unread_messages': unread}
    return {'unread_messages': 0}

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Identifiants invalides.', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    projects_count = Project.query.count()
    skills_count = Skill.query.count()
    new_messages = Message.query.filter_by(is_read=False).count()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(4).all()
    
    return render_template('admin/dashboard.html', 
                           projects_count=projects_count,
                           skills_count=skills_count,
                           new_messages=new_messages,
                           recent_projects=recent_projects,
                           recent_messages=recent_messages)

@admin_bp.route('/projects')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=all_projects)

@admin_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        tags = request.form.get('tags')
        status = request.form.get('status')
        color = request.form.get('color', '1')
        link = request.form.get('link', '')
        
        image_file = request.files.get('image')
        image_path = upload_file(image_file, request.app.root_path)

        project = Project(title=title, category=category, description=description, tags=tags, status=status, color=color, image=image_path, link=link)
        db.session.add(project)
        db.session.commit()
        flash('Projet ajouté avec succès', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', project=None)

@admin_bp.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.category = request.form.get('category')
        project.description = request.form.get('description')
        project.tags = request.form.get('tags')
        project.status = request.form.get('status')
        project.color = request.form.get('color', project.color)
        project.link = request.form.get('link', project.link)
        
        image_file = request.files.get('image')
        new_image_path = upload_file(image_file, request.app.root_path)
        if new_image_path:
            project.image = new_image_path
            
        db.session.commit()
        flash('Projet modifié avec succès', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', project=project)

@admin_bp.route('/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Projet supprimé', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
    if request.method == 'POST':
        name = request.form.get('name')
        level = request.form.get('level')
        type_ = request.form.get('type')
        if name and level:
            skill = Skill(name=name, level=int(level), type=type_)
            db.session.add(skill)
            db.session.commit()
            flash('Compétence ajoutée', 'success')
        return redirect(url_for('admin.skills'))
    
    tech_skills = Skill.query.filter_by(type='tech').all()
    tool_skills = Skill.query.filter_by(type='tool').all()
    return render_template('admin/skills.html', tech_skills=tech_skills, tool_skills=tool_skills)

@admin_bp.route('/skills/delete/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Compétence supprimée', 'success')
    return redirect(url_for('admin.skills'))

@admin_bp.route('/messages')
@login_required
def messages():
    all_messages = Message.query.order_by(Message.created_at.desc()).all()
    for m in all_messages:
        m.is_read = True
    db.session.commit()
    return render_template('admin/messages.html', messages=all_messages)


# --- NOUVELLES ROUTES : EXPERIENCES ---
@admin_bp.route('/experiences', methods=['GET', 'POST'])
@login_required
def experiences():
    if request.method == 'POST':
        period = request.form.get('period')
        role = request.form.get('role')
        company = request.form.get('company')
        description = request.form.get('description')
        if period and role and company:
            exp = Experience(period=period, role=role, company=company, description=description)
            db.session.add(exp)
            db.session.commit()
            flash('Expérience ajoutée', 'success')
        return redirect(url_for('admin.experiences'))
    
    experiences = Experience.query.order_by(Experience.id.desc()).all()
    return render_template('admin/experiences.html', experiences=experiences)

@admin_bp.route('/experiences/delete/<int:id>', methods=['POST'])
@login_required
def delete_experience(id):
    exp = Experience.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    flash('Expérience supprimée', 'success')
    return redirect(url_for('admin.experiences'))


# --- NOUVELLES ROUTES : SERVICES ---
@admin_bp.route('/services', methods=['GET', 'POST'])
@login_required
def services():
    if request.method == 'POST':
        icon = request.form.get('icon')
        title = request.form.get('title')
        description = request.form.get('description')
        if icon and title:
            srv = Service(icon=icon, title=title, description=description)
            db.session.add(srv)
            db.session.commit()
            flash('Service ajouté', 'success')
        return redirect(url_for('admin.services'))
    
    services = Service.query.order_by(Service.id.desc()).all()
    return render_template('admin/services.html', services=services)

@admin_bp.route('/services/delete/<int:id>', methods=['POST'])
@login_required
def delete_service(id):
    srv = Service.query.get_or_404(id)
    db.session.delete(srv)
    db.session.commit()
    flash('Service supprimé', 'success')
    return redirect(url_for('admin.services'))


# --- NOUVELLES ROUTES : ARTICLES / BLOG ---
@admin_bp.route('/articles')
@login_required
def articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=articles)

@admin_bp.route('/articles/add', methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        status = request.form.get('status')
        
        image_file = request.files.get('image')
        image_path = upload_file(image_file, request.app.root_path)

        article = Article(title=title, category=category, content=content, status=status, image=image_path)
        db.session.add(article)
        db.session.commit()
        flash('Article ajouté avec succès', 'success')
        return redirect(url_for('admin.articles'))
    return render_template('admin/article_form.html', article=None)

@admin_bp.route('/articles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.category = request.form.get('category')
        article.content = request.form.get('content')
        article.status = request.form.get('status')
        
        image_file = request.files.get('image')
        new_image_path = upload_file(image_file, request.app.root_path)
        if new_image_path:
            article.image = new_image_path
            
        db.session.commit()
        flash('Article modifié avec succès', 'success')
        return redirect(url_for('admin.articles'))
    return render_template('admin/article_form.html', article=article)

@admin_bp.route('/articles/delete/<int:id>', methods=['POST'])
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('Article supprimé', 'success')
    return redirect(url_for('admin.articles'))


# --- NOUVELLES ROUTES : PROFIL ---
@admin_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    prof = Profile.query.first()
    if not prof:
        prof = Profile(name="Votre Nom")
        db.session.add(prof)
        db.session.commit()

    if request.method == 'POST':
        prof.name = request.form.get('name')
        prof.first_name = request.form.get('first_name')
        prof.role = request.form.get('role')
        prof.tagline = request.form.get('tagline')
        prof.location = request.form.get('location')
        prof.email = request.form.get('email')
        prof.phone = request.form.get('phone')
        prof.availability = request.form.get('availability')
        prof.cv_url = request.form.get('cv_url')
        
        paragraphs = request.form.get('about_paragraphs', '')
        # Simple list parsing if using \n\n as separator
        prof.about_paragraphs = json.dumps([p.strip() for p in paragraphs.split('\n\n') if p.strip()])

        prof.github = request.form.get('github')
        prof.linkedin = request.form.get('linkedin')
        prof.twitter = request.form.get('twitter')
        prof.dribbble = request.form.get('dribbble')

        # Photos
        for field in ['hero_photo', 'about_photo']:
            photo_file = request.files.get(field)
            new_photo_path = upload_file(photo_file, request.app.root_path)
            if new_photo_path:
                setattr(prof, field, new_photo_path)

        db.session.commit()
        flash('Profil mis à jour', 'success')
        return redirect(url_for('admin.profile_settings'))
    
    # Pre-parse paragraphs for form textarea
    about_text = ""
    if prof.about_paragraphs:
        try:
            about_list = json.loads(prof.about_paragraphs)
            about_text = "\n\n".join(about_list)
        except:
            about_text = prof.about_paragraphs

    return render_template('admin/profile.html', profile=prof, about_text=about_text)
