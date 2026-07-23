// Reference search: jumps to references like "Ps 23" or "1 John 2 3".
// No dependencies. Anchors are bNNN.html#cccvvv; the fixed nav bar offset
// is handled by scroll-padding-top in style.css.
(function () {
    var bookNames = {
        'Hk':           '035',
        'Jn':           '043',
        'Js':           '059',
        'Mt':           '040',
        'Cl':           '051',
        'Jb':           '018',
        'Jg':           '007',
        '1Jn':          '062',
        '2Jn':          '063',
        '3Jn':          '064',
        'Lk':           '042',
        '1Tm':          '054',
        '2Tm':          '055',
        'Zp':           '036',
        'Er':           '015',
        'Hg':           '037',
        'Jd':           '065',
        'Jl':           '029',
        'Mk':           '041',
        'Pm':           '057',
        'Tt':           '056',
        'Dn':           '027',
        'Dt':           '005',
        'Gn':           '001',
    'Genesis':          '001',
    'Exodus':           '002',
    'Leviticus':        '003',
    'Numbers':          '004',
    'Deuteronomy':      '005',
    'Joshua':           '006',
    'Judges':           '007',
    'Ruth':             '008',
    '1Samuel':          '009',
    '2Samuel':          '010',
    '1Kings':           '011',
    '2Kings':           '012',
    '1Chronicles':      '013',
    '2Chronicles':      '014',
    'Ezra':             '015',
    'Nehemiah':         '016',
    'Esther':           '017',
    'Job':              '018',
    'Psalms':           '019',
    'Proverbs':         '020',
    'Ecclesiastes':     '021',
    'Song of Solomon':  '022',
    'Isaiah':           '023',
    'Jeremiah':         '024',
    'Lamentations':     '025',
    'Ezekiel':          '026',
    'Daniel':           '027',
    'Hosea':            '028',
    'Joel':             '029',
    'Amos':             '030',
    'Obadiah':          '031',
    'Jonah':            '032',
    'Micah':            '033',
    'Nahum':            '034',
    'Habakkuk':         '035',
    'Zephaniah':        '036',
    'Haggai':           '037',
    'Zechariah':        '038',
    'Malachi':          '039',
    'Matthew':          '040',
    'Mark':             '041',
    'Luke':             '042',
    'John':             '043',
    'Acts':             '044',
    'Romans':           '045',
    '1Corinthians':     '046',
    '2Corinthians':     '047',
    'Galatians':        '048',
    'Ephesians':        '049',
    'Philippians':      '050',
    'Colossians':       '051',
    '1Thessalonians':   '052',
    '2Thessalonians':   '053',
    '1Timothy':         '054',
    '2Timothy':         '055',
    'Titus':            '056',
    'Philemon':         '057',
    'Hebrews':          '058',
    'James':            '059',
    '1Peter':           '060',
    '2Peter':           '061',
    '1John':            '062',
    '2John':            '063',
    '3John':            '064',
    'Jude':             '065',
    'Revelation':       '066'
    };

    function pad(value) {
        var n = parseInt(value, 10);
        if (isNaN(n) || n < 1) { n = 1; }
        return ('000' + n).slice(-3);
    }

    // "1 John 2 3" -> "b062.html#002003"; null when no book matches.
    function lookup(raw) {
        var parts = raw.split(/[\s,:]+/).filter(function (w) { return w !== ''; });
        if (parts.length === 0) { return null; }
        if (/^[1234]$/.test(parts[0]) && parts.length > 1) {
            parts[0] = parts[0] + parts[1];
            parts.splice(1, 1);
        }
        var name = parts[0].toLowerCase();
        for (var key in bookNames) {
            if (key.substring(0, name.length).toLowerCase() === name) {
                return 'b' + bookNames[key] + '.html#' + pad(parts[1]) + pad(parts[2]);
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
            msg.textContent = 'Book not found';
        });
    });
})();
