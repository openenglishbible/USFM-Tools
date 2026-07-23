// Cycles the colour theme: auto (follow system) -> light -> dark.
// The stored choice is applied before first paint by an inline script
// in each page's head; this file only drives the toggle button.
(function () {
    function current() {
        var t = null;
        try { t = localStorage.getItem('theme'); } catch (e) {}
        return (t === 'light' || t === 'dark') ? t : 'auto';
    }
    function label(t) {
        if (t === 'light') { return '☀ Light'; }
        if (t === 'dark') { return '☾ Dark'; }
        return '◐ Auto';
    }
    function apply(t) {
        if (t === 'light' || t === 'dark') {
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
            var order = ['auto', 'light', 'dark'];
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
