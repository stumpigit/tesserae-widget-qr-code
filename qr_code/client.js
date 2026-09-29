const TONES = {
  text: "var(--text-primary)",
  accent_1: "var(--accent-1)",
  accent_2: "var(--accent-2)",
  accent_3: "var(--accent-3)",
  accent_4: "var(--accent-4)",
  accent_5: "var(--accent-5)",
  accent_6: "var(--accent-6)",
};

const KIND_ICONS = {
  text: "ph-text-aa",
  link: "ph-link-simple",
  wifi: "ph-wifi-high",
  vcard: "ph-identification-card",
};

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function kindLabel(kind, t) {
  const labels = {
    text: t("text", "Text"),
    link: t("link", "Link"),
    wifi: t("wifi", "Wi-Fi"),
    vcard: t("vcard", "vCard"),
  };
  return labels[kind] || labels.link;
}

function qrSvg(data) {
  const matrix = Array.isArray(data?.matrix) ? data.matrix : [];
  const size = Number(data?.size) || matrix.length;
  const quiet = Number(data?.quiet) || 4;
  const view = size + quiet * 2;
  const rects = [];

  matrix.forEach((row, y) => {
    let x = 0;
    while (x < row.length) {
      if (row[x] !== "1") {
        x += 1;
        continue;
      }
      const start = x;
      while (x < row.length && row[x] === "1") x += 1;
      rects.push(`<rect class="qr-module" x="${start + quiet}" y="${y + quiet}" width="${x - start}" height="1"/>`);
    }
  });

  return `
    <svg class="qr-svg" viewBox="0 0 ${view} ${view}" role="img" aria-label="QR code" shape-rendering="crispEdges">
      <rect class="qr-bg" x="0" y="0" width="${view}" height="${view}" rx="0"/>
      ${rects.join("")}
    </svg>`;
}

export default function render(shadow, ctx) {
  const opts = ctx?.cell?.options || {};
  const data = ctx?.data || {};
  const t = ctx?.t || ((key, fallback) => fallback ?? key);
  const kind = data.kind || opts.kind || "link";
  const tone = TONES[opts.tone] || TONES.text;
  const title = data.title || kindLabel(kind, t);
  const icon = KIND_ICONS[kind] || KIND_ICONS.link;
  const size = ctx?.cell?.size || "md";
  const showDetails = opts.show_details === true;

  if (data.error || !Array.isArray(data.matrix)) {
    shadow.innerHTML = `
      <link rel="stylesheet" href="/static/style/spectra-widgets.css">
      <div class="w size-${escapeHtml(size)}" data-widget="qr_code" data-kind="${escapeHtml(kind)}">
        <div class="w-title">
          <i class="ph-bold ph-qr-code" style="color:${tone}"></i>
          <h3>${escapeHtml(t("qr_code", "QR Code"))}</h3>
        </div>
        <div class="w-body status-body"><p class="u-muted">${escapeHtml(data.error || t("set_content", "Set QR code content in cell options."))}</p></div>
      </div>`;
    return;
  }

  const summary = data.summary || "";
  const payloadPreview = kind === "wifi" ? summary.replace(" (hidden)", ` - ${t("hidden_network", "Hidden network")}`) : summary;
  const layout = `
    .w[data-widget="qr_code"] .w-body {
      align-items: stretch;
      gap: var(--space-3);
      justify-content: center;
    }
    .qr-wrap {
      align-items: center;
      background: var(--surface-sunken);
      border-radius: var(--radius-2);
      display: flex;
      justify-content: center;
      min-height: 0;
      padding: clamp(var(--space-2), 4cqw, var(--space-5));
    }
    .qr-svg {
      aspect-ratio: 1;
      display: block;
      max-height: 100%;
      max-width: 100%;
      width: min(100%, 62cqh);
    }
    .w[data-widget="qr_code"].is-plain .w-body {
      padding: var(--space-2);
    }
    .w[data-widget="qr_code"].is-plain .qr-wrap {
      flex: 1 1 auto;
      padding: clamp(var(--space-2), 5cqw, var(--space-6));
    }
    .w[data-widget="qr_code"].is-plain .qr-svg {
      width: min(100%, 88cqh);
    }
    .qr-bg { fill: var(--surface); }
    .qr-module { fill: ${tone}; }
    .qr-meta {
      display: grid;
      gap: var(--space-2);
      min-width: 0;
    }
    .qr-kind {
      align-items: center;
      color: var(--text-secondary);
      display: inline-flex;
      font-size: var(--fs-caption);
      font-weight: var(--fw-bold);
      gap: var(--space-2);
      letter-spacing: var(--ls-label);
      text-transform: var(--label-transform, uppercase);
    }
    .qr-kind i { color: ${tone}; font-size: 1.05em; }
    .qr-summary {
      color: var(--text-primary);
      font-size: var(--fs-lead);
      font-weight: var(--fw-bold);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .qr-hint {
      color: var(--text-muted);
      display: flex;
      font-size: var(--fs-caption);
      font-weight: var(--fw-semi);
      justify-content: space-between;
      gap: var(--space-3);
    }
    @container (max-width: 260px) {
      .w[data-widget="qr_code"] .w-title,
      .qr-meta { display: none; }
      .w[data-widget="qr_code"] .w-body { padding: var(--space-2); }
      .qr-wrap { padding: var(--space-2); }
      .qr-svg { width: 100%; }
    }
    @container (min-width: 261px) and (max-width: 420px) {
      .qr-hint { display: none; }
      .qr-summary { font-size: var(--fs-body); }
    }
    @container (min-width: 700px) {
      .w[data-widget="qr_code"]:not(.is-plain) .w-body {
        display: grid;
        grid-template-columns: minmax(0, 0.9fr) minmax(0, 1fr);
        align-items: center;
      }
      .qr-svg { width: min(100%, 58cqw); }
    }
  `;

  const titleEl = showDetails ? `
      <div class="w-title">
        <i class="ph-bold ph-qr-code" style="color:${tone}"></i>
        <h3>${escapeHtml(title)}</h3>
        <span class="w-title-meta">${escapeHtml(kindLabel(kind, t))}</span>
      </div>` : "";
  const detailsEl = showDetails ? `
        <div class="qr-meta">
          <div class="qr-kind"><i class="ph-bold ${escapeHtml(icon)}"></i>${escapeHtml(kindLabel(kind, t))}</div>
          <div class="qr-summary" title="${escapeHtml(payloadPreview)}">${escapeHtml(payloadPreview)}</div>
          <div class="qr-hint">
            <span>${escapeHtml(t("scan_hint", "Scan with your phone"))}</span>
          </div>
        </div>` : "";

  shadow.innerHTML = `
    <link rel="stylesheet" href="/static/style/spectra-widgets.css">
    <style>${layout}</style>
    <div class="w size-${escapeHtml(size)}${showDetails ? "" : " is-plain"}" data-widget="qr_code" data-kind="${escapeHtml(kind)}">
      ${titleEl}
      <div class="w-body stat-body">
        <div class="qr-wrap">${qrSvg(data)}</div>
        ${detailsEl}
      </div>
    </div>`;
}
