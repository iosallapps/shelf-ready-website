// shelfreadyapp.com: three small behaviours, each optional. The page reads fine without them.
(function () {
    'use strict';

    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 1. Support: open the answer a link points at (support.html#restore), so links from the
    //    app land on it.
    function openFromHash() {
        var id = decodeURIComponent(location.hash.slice(1));
        if (!id) return;
        var target = document.getElementById(id);
        if (target && target.tagName === 'DETAILS') target.open = true;
    }
    openFromHash();
    window.addEventListener('hashchange', openFromHash);

    // 2. The before and after. A native range input does the work, so it is keyboard and
    //    screen reader friendly. It takes no pointer events itself: drags anywhere on the
    //    photo move it instead, and touch-action: pan-y keeps vertical scrolling working.
    var compare = document.querySelector('[data-compare]');
    if (compare) {
        var input = compare.querySelector('input[type="range"]');
        var frame = compare.querySelector('.compare-frame');

        var describe = function (value) {
            if (value <= 5) return 'All original photo';
            if (value >= 95) return 'All result';
            if (value > 25 && value < 60) return 'Half and half';
            return value < 50 ? 'Mostly the original photo' : 'Mostly the result';
        };

        var set = function (value) {
            value = Math.max(0, Math.min(100, value));
            compare.style.setProperty('--pos', value + '%');
            input.value = String(Math.round(value));
            input.setAttribute('aria-valuetext', describe(value));
        };

        input.addEventListener('input', function () {
            compare.classList.remove('is-intro');
            set(Number(input.value));
        });

        var dragging = false;
        var fromPointer = function (event) {
            var rect = frame.getBoundingClientRect();
            set(((event.clientX - rect.left) / rect.width) * 100);
        };
        frame.addEventListener('pointerdown', function (event) {
            if (event.pointerType === 'mouse' && event.button !== 0) return;
            dragging = true;
            compare.classList.remove('is-intro');
            // A mouse jumps straight to the click. A finger only moves the line once it moves
            // sideways, so a vertical scroll that starts on the photo leaves it alone.
            if (event.pointerType === 'mouse') fromPointer(event);
        });
        window.addEventListener('pointermove', function (event) { if (dragging) fromPointer(event); });
        window.addEventListener('pointerup', function () { dragging = false; });
        window.addEventListener('pointercancel', function () { dragging = false; });

        // The one moment of motion on the page: the line sweeps from the original photo to the
        // middle, once, so it is clear the photo can be dragged.
        if (!reduceMotion) {
            set(100);
            requestAnimationFrame(function () {
                requestAnimationFrame(function () {
                    compare.classList.add('is-intro');
                    set(31);
                    setTimeout(function () { compare.classList.remove('is-intro'); }, 1300);
                });
            });
        }
    }

    // 3. The swatch book: swap the headphones' background.
    var view = document.querySelector('[data-backdrop-view]');
    if (view) {
        var picture = view.querySelector('picture');
        var name = document.querySelector('[data-backdrop-name]');
        var buttons = document.querySelectorAll('.swatch');
        var widths = [400, 800];

        var srcset = function (id, ext) {
            return widths.map(function (w) { return 'img/swatch-' + id + '-' + w + '.' + ext + ' ' + w + 'w'; }).join(', ');
        };

        Array.prototype.forEach.call(buttons, function (button) {
            button.addEventListener('click', function () {
                var id = button.getAttribute('data-bg');
                var label = button.getAttribute('data-name');
                picture.querySelector('source[type="image/avif"]').srcset = srcset(id, 'avif');
                picture.querySelector('source[type="image/webp"]').srcset = srcset(id, 'webp');
                var img = picture.querySelector('img');
                img.srcset = srcset(id, 'jpg');
                img.src = 'img/swatch-' + id + '-400.jpg';
                img.alt = 'Black over-ear headphones on ' + label + ', with a soft shadow underneath.';
                name.textContent = label;
                Array.prototype.forEach.call(buttons, function (other) {
                    other.setAttribute('aria-pressed', other === button ? 'true' : 'false');
                });
            });
        });
    }
})();
