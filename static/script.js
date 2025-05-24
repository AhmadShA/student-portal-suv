// Theme Toggle
document.getElementById('theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    document.cookie = `theme=${theme}; path=/; max-age=${60*60*24*30}`; // Store for 30 days
});

// Apply saved theme
document.addEventListener('DOMContentLoaded', () => {
    const theme = document.cookie.split('; ').find(row => row.startsWith('theme='))?.split('=')[1];
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    }
});