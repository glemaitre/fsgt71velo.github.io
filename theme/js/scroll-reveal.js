/**
 * Scroll-triggered reveal animations using IntersectionObserver.
 * Adds .reveal-on-scroll to cards and headings, then .is-visible on scroll.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Respect user preference for reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  // Select elements to animate
  var selectors = [
    '.content > .container .card',
    '.content > .container h2'
  ];

  var elements = document.querySelectorAll(selectors.join(','));

  elements.forEach(function(el) {
    el.classList.add('reveal-on-scroll');
  });

  // Use IntersectionObserver for efficient scroll detection
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  });

  elements.forEach(function(el) {
    observer.observe(el);
  });
});
