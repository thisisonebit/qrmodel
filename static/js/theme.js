// Simple dark/light theme toggle stored in localStorage
(function () {
    const key = 'qr_theme';
    const html = document.documentElement;
    const btn = document.getElementById('theme_toggle');

    function apply(theme) {
        html.setAttribute('data-theme', theme);
        if (btn) { btn.textContent = theme === 'dark' ? '☀️' : '🌙'; }
        try { localStorage.setItem(key, theme); } catch (e) { }
    }

    const saved = (function () { try { return localStorage.getItem(key); } catch (e) { return null; } })();
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    apply(saved || (prefersDark ? 'dark' : 'light'));

    if (btn) {
        btn.addEventListener('click', function () {
            apply(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
        });
    }
})();
