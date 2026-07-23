// Reader conveniences for book pages: verse permalinks and per-book
// reading-position memory. No dependencies.
(function () {
    var page = location.pathname.split('/').pop();
    var store = 'pos:' + page;

    // Clicking a verse or chapter number puts its fragment in the address
    // bar without scrolling, so the link can be copied and shared. Without
    // JS the plain anchor still works (it just also scrolls).
    document.addEventListener('click', function (event) {
        if (!event.target.closest) { return; }
        var link = event.target.closest('a.verse, a.chapter');
        if (!link) { return; }
        event.preventDefault();
        try { history.replaceState(null, '', link.getAttribute('href')); } catch (e) {}
    });

    // Remember how far down the page the reader was, per book.
    function save() {
        try { localStorage.setItem(store, String(Math.round(window.scrollY))); } catch (e) {}
    }
    var pending = null;
    window.addEventListener('scroll', function () {
        if (pending !== null) { return; }
        pending = window.setTimeout(function () { pending = null; save(); }, 500);
    }, { passive: true });
    window.addEventListener('pagehide', save);

    // Restore on return - but never override an explicit #reference.
    document.addEventListener('DOMContentLoaded', function () {
        if (location.hash) { return; }
        var saved = NaN;
        try { saved = parseInt(localStorage.getItem(store), 10); } catch (e) {}
        if (saved > 200) {
            window.scrollTo(0, saved);
        }
    });
})();
