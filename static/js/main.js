// Простое переключение темы (сохранение в localStorage)
const toggle = document.getElementById('themeToggle');
const root = document.documentElement;

function applyTheme(theme) {
  root.setAttribute('data-theme', theme);
}
// Инициализация
const saved = localStorage.getItem('parsermoex-theme') || 'light';
applyTheme(saved);
if (toggle) toggle.checked = (saved === 'dark');

// Переключатель
if (toggle) {
  toggle.addEventListener('change', () => {
    const next = toggle.checked ? 'dark' : 'light';
    localStorage.setItem('parsermoex-theme', next);
    applyTheme(next);
  });
}