const toggleButton = document.getElementById('theme-toggle');
const body = document.body;

function applyTheme(theme) {
    if (theme === 'dark') {
        body.classList.add('dark-mode');
        toggleButton.textContent = '☀️ Light';
    } else {
        body.classList.remove('dark-mode');
        toggleButton.textContent = '🌙 Dark';
    }
}

const savedTheme = localStorage.getItem('inkverse-theme') || 'light';
applyTheme(savedTheme);

toggleButton.addEventListener('click', function () {
    const isDark = body.classList.contains('dark-mode');
    const newTheme = isDark ? 'light' : 'dark';
    applyTheme(newTheme);
    localStorage.setItem('inkverse-theme', newTheme);
});