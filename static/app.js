document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.quick-add').forEach((form) => {
    form.addEventListener('submit', () => {
      const button = form.querySelector('button');
      if (button) {
        button.textContent = 'Added ✓';
        setTimeout(() => { button.innerHTML = 'Add to cart <span>+</span>'; }, 1200);
      }
    });
  });
});
