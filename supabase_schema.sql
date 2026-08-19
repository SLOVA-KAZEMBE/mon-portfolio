-- Création des tables pour Supabase (PostgreSQL)

CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS project (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    tags VARCHAR(255),
    color VARCHAR(10),
    image VARCHAR(255),
    link VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Publié',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    subject VARCHAR(200),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS experience (
    id SERIAL PRIMARY KEY,
    period VARCHAR(50) NOT NULL,
    role VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service (
    id SERIAL PRIMARY KEY,
    icon VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS article (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Publié',
    image VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profile (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    first_name VARCHAR(50),
    role VARCHAR(100),
    tagline TEXT,
    location VARCHAR(100),
    email VARCHAR(120),
    phone VARCHAR(50),
    availability VARCHAR(100),
    cv_url VARCHAR(255),
    hero_photo VARCHAR(255),
    about_photo VARCHAR(255),
    about_paragraphs TEXT,
    github VARCHAR(255),
    linkedin VARCHAR(255),
    twitter VARCHAR(255),
    dribbble VARCHAR(255),
    stats_years VARCHAR(20),
    stats_projects VARCHAR(20),
    stats_clients VARCHAR(20),
    stats_passion VARCHAR(20)
);

-- Insertion de l'utilisateur admin
INSERT INTO admin (username, password_hash) 
VALUES ('slova', 'scrypt:32768:8:1$e4UAGxYTFMkDlPiM$56d6bea14f490e9cb4e0e039ac3b8b9a7773577d443db1cf3398e698c302cd2c62973adac9fbf9111161c256e91f62c9600cfac06f217726dcc22ab222d9524e')
ON CONFLICT (username) DO NOTHING;
