/* ============================================================
   BENTELEMOBIL — Homepage Interactions
   ============================================================ */

'use strict';

/* ─── 1. NAV: scroll state + mobile toggle ─── */
(function initNav() {
  const header = document.getElementById('site-header');
  const toggle = document.querySelector('.nav-toggle');
  const links  = document.querySelector('.nav-links');

  // Sticky header class
  const onScroll = () => {
    header.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      links.classList.toggle('open', !expanded);
      document.body.style.overflow = !expanded ? 'hidden' : '';
    });

    // Close on link click
    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        toggle.setAttribute('aria-expanded', 'false');
        links.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // Active nav link on scroll
  const sections = document.querySelectorAll('section[id]');
  const navItems = document.querySelectorAll('.nav-links a[href^="#"]');

  const markActive = () => {
    let current = '';
    sections.forEach(sec => {
      if (window.scrollY >= sec.offsetTop - 120) current = sec.id;
    });
    navItems.forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + current);
    });
  };
  window.addEventListener('scroll', markActive, { passive: true });
})();


/* ─── 2. REVEAL on scroll (IntersectionObserver) ─── */
(function initReveal() {
  const els = document.querySelectorAll('[data-reveal]');
  if (!els.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        // Stagger sibling reveals
        const siblings = Array.from(
          entry.target.parentElement.querySelectorAll('[data-reveal]')
        );
        const delay = siblings.indexOf(entry.target) * 80;
        setTimeout(() => {
          entry.target.classList.add('is-visible');
        }, delay);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  els.forEach(el => io.observe(el));
})();


/* ─── 3. COUNTER ANIMATION (stats bar) ─── */
(function initCounters() {
  const counters = document.querySelectorAll('.stat-number[data-count]');
  if (!counters.length) return;

  const ease = (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;

  const animateCounter = (el) => {
    const target   = parseInt(el.dataset.count, 10);
    const duration = 1800;
    const start    = performance.now();

    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(ease(progress) * target);
      if (progress < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    };
    requestAnimationFrame(tick);
  };

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => io.observe(el));
})();


/* ─── 4. TESTIMONIAL CAROUSEL ─── */
(function initTestimonials() {
  const testimonials = document.querySelectorAll('.testimonial');
  const dots         = document.querySelectorAll('.testimonial-dot');
  if (!testimonials.length || !dots.length) return;

  let current   = 0;
  let autoTimer = null;

  const goTo = (idx) => {
    testimonials[current].classList.remove('active');
    dots[current].classList.remove('active');
    current = (idx + testimonials.length) % testimonials.length;
    testimonials[current].classList.add('active');
    dots[current].classList.add('active');
  };

  const startAuto = () => {
    autoTimer = setInterval(() => goTo(current + 1), 5500);
  };

  const stopAuto = () => clearInterval(autoTimer);

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      stopAuto();
      goTo(parseInt(dot.dataset.index, 10));
      startAuto();
    });
  });

  startAuto();

  // Pause on hover/focus
  const track = document.getElementById('testimonial-track');
  if (track) {
    track.addEventListener('mouseenter', stopAuto);
    track.addEventListener('mouseleave', startAuto);
    track.addEventListener('focusin', stopAuto);
    track.addEventListener('focusout', startAuto);
  }
})();


/* ─── 5. CONTACT FORM (mock submission) ─── */
(function initForm() {
  const form    = document.getElementById('kontakt-form');
  const success = document.getElementById('form-success');
  if (!form || !success) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const btn  = form.querySelector('button[type="submit"]');
    const text = btn.querySelector('.btn-text');

    btn.disabled = true;
    text.textContent = 'Wird gesendet …';

    // Simulate async send
    await new Promise(r => setTimeout(r, 1200));

    form.style.display = 'none';
    success.hidden = false;
    success.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
})();


/* ─── 6. SMOOTH SCROLL polyfill for older Safari ─── */
(function smoothScrollFallback() {
  if ('scrollBehavior' in document.documentElement.style) return;

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const id = anchor.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
})();


/* ─── 7. PARALLAX — hero grid subtle shift ─── */
(function initParallax() {
  const grid = document.querySelector('.hero-grid');
  if (!grid || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    requestAnimationFrame(() => {
      const y = window.scrollY * 0.25;
      grid.style.transform = `translateY(${y}px)`;
      ticking = false;
    });
    ticking = true;
  }, { passive: true });
})();
