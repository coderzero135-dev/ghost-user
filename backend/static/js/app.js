async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(err || `HTTP ${res.status}`);
    }
    return res.json();
}

function formatDate(iso) {
    return new Date(iso).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function truncate(str, n = 60) {
    return str.length > n ? str.slice(0, n) + '...' : str;
}
