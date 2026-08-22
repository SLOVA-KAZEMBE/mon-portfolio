document.addEventListener('DOMContentLoaded', () => {

  /* ---------------- Menu mobile ---------------- */
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  
  if (navToggle && navLinks) {
    const iconMenu = navToggle.querySelector('.icon-menu');
    const iconClose = navToggle.querySelector('.icon-close');

    const setMenuState = (isOpen) => {
      navLinks.classList.toggle('is-open', isOpen);
      document.body.classList.toggle('nav-open', isOpen);
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      navToggle.setAttribute('aria-label', isOpen ? 'Fermer le menu' : 'Ouvrir le menu');
      if (iconMenu && iconClose) {
        iconMenu.style.display = isOpen ? 'none' : 'block';
        iconClose.style.display = isOpen ? 'block' : 'none';
      }
    };

    navToggle.addEventListener('click', () => {
      setMenuState(!navLinks.classList.contains('is-open'));
    });

    // Ferme le menu mobile après un clic sur un lien
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navLinks.classList.contains('is-open')) {
          setMenuState(false);
        }
      });
    });

    document.addEventListener('click', (event) => {
      if (!navLinks.classList.contains('is-open')) return;
      if (navLinks.contains(event.target) || navToggle.contains(event.target)) return;
      setMenuState(false);
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && navLinks.classList.contains('is-open')) {
        setMenuState(false);
      }
    });
  }

  /* ---------------- Thème clair / sombre (icône lune / soleil) ---------------- */
  const themeToggle = document.getElementById('themeToggle');
  const applyTheme = (theme) => {
    document.body.classList.toggle('theme-light', theme === 'light');
  };

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    applyTheme(savedTheme);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    applyTheme('light');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = document.body.classList.toggle('theme-light');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
  }

  /* ---------------- Mise en surbrillance du lien actif au scroll ---------------- */
  const sections = document.querySelectorAll('main section[id]');
  const navItems = document.querySelectorAll('.nav-link');

  if (sections.length && navItems.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navItems.forEach(link => {
            link.classList.toggle('is-active', link.dataset.section === id);
          });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

    sections.forEach(section => observer.observe(section));
  }

  /* ---------------- Filtres de projets ---------------- */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.project-card');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      const filter = btn.dataset.filter;
      cards.forEach(card => {
        const show = filter === 'Tous' || card.dataset.category === filter;
        card.style.display = show ? '' : 'none';
      });
    });
  });
});
