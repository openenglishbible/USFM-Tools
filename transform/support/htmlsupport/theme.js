// Cycles the colour theme: auto (follow system) -> light -> paper -> dark.
// The stored choice is applied before first paint by an inline script
// in each page's head; this file only drives the toggle button.
(function () {
    var THEMES = ['light', 'paper', 'dark'];
    function current() {
        var t = null;
        try { t = localStorage.getItem('theme'); } catch (e) {}
        return THEMES.indexOf(t) >= 0 ? t : 'auto';
    }
    function label(t) {
        if (t === 'light') { return '☀ Light'; }
        if (t === 'paper') { return '❧ Paper'; }
        if (t === 'dark') { return '☾ Dark'; }
        return '◐ Auto';
    }
    function apply(t) {
        if (THEMES.indexOf(t) >= 0) {
            document.documentElement.setAttribute('data-theme', t);
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    }
    document.addEventListener('DOMContentLoaded', function () {
        var button = document.getElementById('themetoggle');
        if (!button) { return; }
        button.textContent = label(current());
        button.addEventListener('click', function () {
            var order = ['auto'].concat(THEMES);
            var next = order[(order.indexOf(current()) + 1) % order.length];
            try {
                if (next === 'auto') {
                    localStorage.removeItem('theme');
                } else {
                    localStorage.setItem('theme', next);
                }
            } catch (e) {}
            apply(next);
            button.textContent = label(next);
        });
    });
})();
