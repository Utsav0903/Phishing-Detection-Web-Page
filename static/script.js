async function checkURL() {
  const url = document.getElementById('url').value.trim();
  const out = document.getElementById('out');
  if (!url) {
    alert('Please enter a URL.');
    return;
  }

  out.innerHTML = `<p style="color:gray;">🔍 Checking the link... please wait.</p>`;

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    const data = await res.json();
    if (!res.ok) {
      out.innerHTML = `<p style="color:red;">❌ ${data.error || 'Server error occurred.'}</p>`;
      return;
    }

    const p = (data.phishing_probability * 100).toFixed(1);
    const isPhishing = data.label === 1;
    const label = isPhishing ? '⚠️ Likely Phishing' : '✅ Likely Safe';
    const cls = isPhishing ? 'danger' : 'safe';
    const barColor = isPhishing ? '#ff4444' : '#00ff80';

    // 🧠 Handle “Why” section (with fallback reasons)
    const reasons = data.explanation && data.explanation.length
      ? data.explanation.map(e => `<li>${getReasonDescription(e)}</li>`).join('')
      : `<li>${isPhishing ? 'Detected suspicious URL structure or risky indicators.' : 'No suspicious indicators found. URL appears safe.'}</li>`;

    out.innerHTML = `
      <div class="result ${cls}">
        <div class="result-title">
          <span>${label}</span>
        </div>
        <div style="color:#bbb;">Probability: <b>${p}%</b></div>

        <div class="progress" style="margin-top:8px;">
          <div id="bar" style="background:${barColor};width:0%;border-radius:8px;transition:width 1.2s ease;"></div>
        </div>

        <div class="why-section">
          <h4 class="why-header" onclick="toggleWhy(this)">
            <span>🔍 Why (click to expand)</span>
            <span class="arrow">▼</span>
          </h4>
          <div class="why-content">
            <ul>${reasons}</ul>
          </div>
        </div>
      </div>
    `;

    // Animate progress bar
    setTimeout(() => {
      const bar = document.getElementById('bar');
      if (bar) bar.style.width = p + '%';
    }, 200);
  } catch (err) {
    out.innerHTML = `<p style="color:red;">🚫 Server error: ${err.message}</p>`;
  }
}

// 🧭 Explanation formatter
function getReasonDescription(raw) {
  const r = raw.toLowerCase();
  if (r.includes('ip')) return "🔢 Uses an IP address instead of a domain (common in phishing).";
  if (r.includes('keyword')) return "⚠️ Contains suspicious words like 'login', 'verify', or 'secure'.";
  if (r.includes('long')) return "🧵 The URL is very long — might be hiding something.";
  if (r.includes('short')) return "🔗 Shortened URL — could be used to mask the destination.";
  if (r.includes('symbol')) return "❌ Contains special characters (like @, -, _) often used in fake URLs.";
  if (r.includes('subdomain')) return "🌐 Too many subdomains — could be imitating a trusted site.";
  if (r.includes('redirect')) return "➡️ Redirect detected — possibly leading to another suspicious site.";
  if (r.includes('https')) return "🔒 Missing or invalid HTTPS certificate.";
  return "⚡ " + raw.charAt(0).toUpperCase() + raw.slice(1);
}

// 🚀 Open URL
function runURL() {
  const url = document.getElementById('url').value.trim();
  if (!url) {
    alert('Please enter a URL before running.');
    return;
  }
  window.open(url, '_blank');
}

// 🔽 Smooth toggle for Why section
function toggleWhy(header) {
  const content = header.nextElementSibling;
  const arrow = header.querySelector('.arrow');

  if (content.style.maxHeight) {
    // collapse
    content.style.maxHeight = null;
    arrow.style.transform = 'rotate(0deg)';
    arrow.style.color = '#999';
  } else {
    // expand
    content.style.maxHeight = content.scrollHeight + "px";
    arrow.style.transform = 'rotate(180deg)';
    arrow.style.color = 'var(--accent)';
  }
}
