// Fade in main sections
window.addEventListener('DOMContentLoaded', () => {
  const fadeEls = [
    document.querySelector('header'),
    document.querySelector('.hero'),
    document.querySelector('footer')
  ];
  fadeEls.forEach(el => {
    if (el) {
      el.style.opacity = 0;
      el.style.transition = 'opacity 1.2s';
      setTimeout(() => el.style.opacity = 1, 200);
    }
  });
});

// Bounce effect for buttons
function addBounceEffect(btn) {
  btn.addEventListener('mouseenter', () => {
    btn.style.transform = 'scale(1.08)';
    btn.style.transition = 'transform 0.2s';
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.transform = 'scale(1)';
  });
}
document.querySelectorAll('button').forEach(addBounceEffect);

// Smooth scroll for nav links
const navLinks = document.querySelectorAll('nav a[href^="#"]');
navLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    const targetId = this.getAttribute('href').slice(1);
    const target = document.getElementById(targetId);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Scale up product cards on hover (for productos.html)
document.querySelectorAll('.producto-item').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transform = 'scale(1.04)';
    card.style.transition = 'transform 0.2s';
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = 'scale(1)';
  });
});

// Custom cute cursor
const cursorUrl = 'img/strawberry-cursor.png'; // Now using the strawberry image
const style = document.createElement('style');
style.innerHTML = `body { cursor: url('${cursorUrl}') 16 16, auto; }`;
document.head.appendChild(style);


// Compatibilidad Flask / imágenes opcionales
document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn && logoutBtn.dataset.url) {
    logoutBtn.addEventListener('click', () => {
      window.location.href = logoutBtn.dataset.url;
    });
  }
});
