// From line 3 to 10, after two seconds, it automatically searches the entry and displays the necessary alert

let timeout = null;

function auto_search() {
	const searchInput = document.getElementById('search').value;
	clearTimeout(timeout)
	timeout = setTimeout(() => {
		document.getElementById('searchForm').submit();
	}, 2500);
}

// From line 15 to 28, the follow button will be activated and you can send a request to the server by clicking on it.

document.getElementById('followButton').addEventListener('click', function() {
	const searchInput = document.getElementById('search').value;
	const form = document.getElementById('searchForm');
	form.action = '/login/account/add_follow';
	document.getElementById('search').value = searchInput;
	form.submit();
});

window.onload = function () {
    const searchInput = '{{ search | safe }}';
    if (searchInput) {
        document.getElementById('search').value = searchInput;
    }
};
