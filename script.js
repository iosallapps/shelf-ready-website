// Open the FAQ answer a link points at (support.html#restore), so links from the app land on it.
(function () {
    function openFromHash() {
        var id = decodeURIComponent(location.hash.slice(1));
        if (!id) return;
        var target = document.getElementById(id);
        if (target && target.tagName === 'DETAILS') target.open = true;
    }
    openFromHash();
    window.addEventListener('hashchange', openFromHash);
})();
