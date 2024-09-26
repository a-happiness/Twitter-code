window.onload = function () {
        const searchInput = '{{ search | safe }}';
        if (searchInput) {
            document.getElementById('search').value = searchInput;
        }
    };
