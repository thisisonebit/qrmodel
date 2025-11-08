// Client-side search for products. Queries /search?q= and shows clickable results.
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('product_search');
    const results = document.getElementById('search_results');
    const hidden = document.getElementById('product_select');
    const nameInput = document.getElementById('product_name');

    let timeout = null;

    function clearResults() {
        results.innerHTML = '';
    }

    function render(items) {
        clearResults();
        if (!items || items.length === 0) return;
        items.forEach(it => {
            const li = document.createElement('li');
            li.className = 'search-item';
            li.textContent = it.name + (it.short_name ? ` (${it.short_name})` : '');
            li.dataset.key = it.key;
            li.addEventListener('click', () => {
                // Fill hidden select and product_name for form submission
                hidden.value = it.key;
                nameInput.value = it.name;
                clearResults();
                input.value = it.name;
            });
            results.appendChild(li);
        });
    }

    async function doSearch(q) {
        try {
            const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
            if (!res.ok) return;
            const data = await res.json();
            render(data);
        } catch (e) {
            console.error('Search error', e);
        }
    }

    input.addEventListener('input', function (e) {
        const q = e.target.value.trim();
        window.clearTimeout(timeout);
        if (!q) {
            clearResults();
            hidden.value = '';
            return;
        }
        timeout = setTimeout(() => doSearch(q), 250);
    });

    // initial list (empty query returns a short listing)
    doSearch('');
});
