// Reference search: jumps to references like "Ps 23" or "1 John 2 3".
// The books available in this release are generated into bookmap.js
// (var oebBooks, keyed by space-stripped book name); this file only holds
// the traditional abbreviations. Unknown or unbuilt books get a message
// instead of a broken link. No dependencies.
(function () {
    var abbrevs = {
        'Hk':  'Habakkuk',
        'Jn':  'John',
        'Js':  'James',
        'Mt':  'Matthew',
        'Cl':  'Colossians',
        'Jb':  'Job',
        'Jg':  'Judges',
        '1Jn': '1John',
        '2Jn': '2John',
        '3Jn': '3John',
        'Lk':  'Luke',
        '1Tm': '1Timothy',
        '2Tm': '2Timothy',
        'Zp':  'Zephaniah',
        'Er':  'Ezra',
        'Hg':  'Haggai',
        'Jd':  'Jude',
        'Jl':  'Joel',
        'Mk':  'Mark',
        'Pm':  'Philemon',
        'Tt':  'Titus',
        'Dn':  'Daniel',
        'Dt':  'Deuteronomy',
        'Gn':  'Genesis'
    };

    function pad(value) {
        var n = parseInt(value, 10);
        if (isNaN(n) || n < 1) { n = 1; }
        return ('000' + n).slice(-3);
    }

    // "1 John 2 3" -> "1-john.html#002003"; null when no built book matches.
    function lookup(raw) {
        if (typeof oebBooks === 'undefined') { return null; }
        var parts = raw.split(/[\s,:]+/).filter(function (w) { return w !== ''; });
        if (parts.length === 0) { return null; }
        if (/^[1234]$/.test(parts[0]) && parts.length > 1) {
            parts[0] = parts[0] + parts[1];
            parts.splice(1, 1);
        }
        var name = parts[0].toLowerCase();
        var keys = [];
        var key;
        for (key in abbrevs) { keys.push(key); }
        for (key in oebBooks) { keys.push(key); }
        for (var i = 0; i < keys.length; i++) {
            key = keys[i];
            if (key.substring(0, name.length).toLowerCase() === name) {
                var file = oebBooks[abbrevs[key] || key];
                if (file) {
                    return file + '#' + pad(parts[1]) + pad(parts[2]);
                }
            }
        }
        return null;
    }

    document.addEventListener('DOMContentLoaded', function () {
        var form = document.getElementById('navform');
        var input = document.getElementById('txtSearch');
        if (!form || !input) { return; }
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            var target = lookup(input.value);
            if (target) {
                window.location.href = target;
                return;
            }
            var msg = form.querySelector('.jumpmsg');
            if (!msg) {
                msg = document.createElement('small');
                msg.className = 'jumpmsg';
                msg.setAttribute('aria-live', 'polite');
                form.appendChild(msg);
            }
            msg.textContent = 'Book not found in this release';
        });
    });
})();
