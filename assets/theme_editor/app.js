// Theme builder mirrors ui.py draw calls on an HTML5 Canvas for live preview

// fallback used when assets/theme.json can't be fetched (e.g. opened via file://)
// keep this in sync with assets/theme.json
const DEFAULT_THEME = {
    name: "default",
    screen: {
        orientation: "portrait",
        preset: "240x320",
        presets: [
            { name: "240x320", w: 240, h: 320 },
            { name: "320x480", w: 320, h: 480 },
            { name: "480x800", w: 480, h: 800 }
        ]
    },
    button: { radius: 0 },
    cover_art: { mode: "fill" },
    visualizer: { n_bars: 24, n_segs: 16 },
    layout: {
        panels: { art: 0.54375, title: 0.06875, seek: 0.075, ctrl: 0.18125 },
        ctrl_buttons: {
            y_off: 0.103448, h: 0.793103,
            prev: { x: 0.016667, w: 0.179167 },
            rev:  { x: 0.2125,   w: 0.179167 },
            play: { x: 0.408333, w: 0.183333 },
            ff:   { x: 0.608333, w: 0.179167 },
            next: { x: 0.804167, w: 0.179167 }
        },
        vol_row: {
            y_off: 0.166667, h: 0.666667,
            shf:       { x: 0.016667, w: 0.15 },
            rpt:       { x: 0.183333, w: 0.15 },
            vol_minus: { x: 0.733333, w: 0.116667 },
            vol_plus:  { x: 0.866667, w: 0.116667 }
        },
        seek_bar: { x: 0.133333, w: 0.733333, y_off: 0.291667, h: 0.416667 },
        vol_bar:  { x: 0.466667, w: 0.25,     y_off: 0.404762, h: 0.190476 }
    },
    palette: {
        BG:         [8,   8,   10],
        ART_BG:     [5,   5,   8],
        PANEL:      [16,  20,  26],
        FG:         [220, 220, 220],
        DIM:        [85,  85,  90],
        ACCENT:     [70,  190, 85],
        BTN_FACE:   [34,  44,  56],
        BTN_HI:     [62,  80,  102],
        BTN_SH:     [12,  15,  19],
        BTN_FG:     [200, 210, 222],
        BTN_ACTIVE:    [55,  165, 72],
        BTN_ACT_FG:    [5,   5,   5],
        SEEK_BG:    [20,  32,  20],
        VOL_BG:     [20,  32,  20],
        BORDER:     [30,  42,  30]
    }
};

let theme = structuredClone(DEFAULT_THEME);

// -------------- //
//   DOM refs
// -------------- //
const canvas          = document.getElementById('preview');
const ctx              = canvas.getContext('2d');
const presetSelect      = document.getElementById('presetSelect');
const orientationSelect = document.getElementById('orientationSelect');
const radiusRange       = document.getElementById('radiusRange');
const radiusValue       = document.getElementById('radiusValue');
const paletteGrid        = document.getElementById('paletteGrid');
const loadInput          = document.getElementById('loadInput');
const trackInput         = document.getElementById('trackInput');
const coverArtModeSelect = document.getElementById('coverArtMode');

// -------------- //
//   Track state
// -------------- //
const track = { title: 'Sample Track Title', coverArt: null };

// reads ID3 tags from an audio file and updates track.title / track.coverArt
function loadTrack(file) {
    jsmediatags.read(file, {
        onSuccess: tag => {
            const tags = tag.tags;
            track.title = tags.title || file.name.replace(/\.[^.]+$/, '');

            const pic = tags.picture;
            if (pic) {
                const url = URL.createObjectURL(
                    new Blob([new Uint8Array(pic.data)], { type: pic.format })
                );
                const img = new Image();
                img.onload = () => {
                    if (track.coverArt) URL.revokeObjectURL(track.coverArt._url);
                    img._url = url;
                    track.coverArt = img;
                    updateVizState();
                };
                img.src = url;
            } else {
                track.coverArt = null;
            }
            updateVizState();
        },
        onError: () => {
            track.title = file.name.replace(/\.[^.]+$/, '');
            track.coverArt = null;
            updateVizState();
        }
    });
}

// -------------- //
//   Color helpers
// -------------- //
const rgb = ([r, g, b]) => `rgb(${r},${g},${b})`;

// converts [R,G,B] array to '#rrggbb' for use in color input values
function rgbToHex([r, g, b]) {
    return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
}

// converts '#rrggbb' back to [R,G,B] when a color picker fires
function hexToRgb(hex) {
    const n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

// -------------- //
//   Layout
// -------------- //

// screen dims, swapping w/h for landscape since presets are stored portrait-first
function getDims() {
    const p = theme.screen.presets.find(p => p.name === theme.screen.preset);
    return theme.screen.orientation === 'landscape'
        ? { w: p.h, h: p.w }
        : { w: p.w, h: p.h };
}

// resolves every fraction in theme.layout into absolute pixel rects for the current screen size
function computeLayout(W, H) {
    const L = theme.layout;
    const order = ['art', 'title', 'seek', 'ctrl', 'vol'];
    const panel = {};
    let y = 0;
    order.forEach((name, i) => {
        // last panel absorbs rounding error so panels always tile exactly to H
        const h = i === order.length - 1 ? H - y : Math.round(L.panels[name] * H);
        panel[name] = { y, h };
        y += h;
    });

    const rect = (frac, baseY, baseH) => ({
        x: Math.round(frac.x * W),
        w: Math.round(frac.w * W),
        y: baseY,
        h: baseH
    });

    const cb = L.ctrl_buttons;
    const cbY = panel.ctrl.y + Math.round(cb.y_off * panel.ctrl.h);
    const cbH = Math.round(cb.h * panel.ctrl.h);
    const ctrlBtns = {};
    for (const name of ['prev', 'rev', 'play', 'ff', 'next']) {
        ctrlBtns[name] = rect(cb[name], cbY, cbH);
    }

    const vr = L.vol_row;
    const vrY = panel.vol.y + Math.round(vr.y_off * panel.vol.h);
    const vrH = Math.round(vr.h * panel.vol.h);
    const volBtns = {};
    for (const name of ['shf', 'rpt', 'vol_minus', 'vol_plus']) {
        volBtns[name] = rect(vr[name], vrY, vrH);
    }

    const sb = L.seek_bar;
    const seekBar = rect(sb, panel.seek.y + Math.round(sb.y_off * panel.seek.h), Math.round(sb.h * panel.seek.h));

    const vb = L.vol_bar;
    const volBar = rect(vb, panel.vol.y + Math.round(vb.y_off * panel.vol.h), Math.round(vb.h * panel.vol.h));

    return { panel, ctrlBtns, volBtns, seekBar, volBar };
}

// -------------- //
//   Visualizer
// -------------- //
let waveT     = 0;
let animFrame = null;

// starts the rAF loop that advances waveT and redraws each frame
function startViz() {
    if (animFrame) return;
    let last = null;
    function step(ts) {
        if (last !== null) waveT += (ts - last) / 1000;
        last = ts;
        drawPreview();
        animFrame = requestAnimationFrame(step);
    }
    animFrame = requestAnimationFrame(step);
}

// cancels the animation loop and resets waveT to zero
function stopViz() {
    if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null; }
    waveT = 0;
}

// mirrors ui.py's try_draw_visualizer() only called when no cover art is loaded
function drawVisualizer(W, panel) {
    const p   = theme.palette;
    const { n_bars, n_segs } = theme.visualizer;
    const artY = panel.art.y, artH = panel.art.h;

    ctx.fillStyle = rgb(p.ART_BG);
    ctx.fillRect(0, artY, W, artH);

    const cell_w = W / n_bars;
    const bar_w  = Math.max(1, Math.floor(cell_w) - 2);
    const cy     = artY + Math.floor(artH / 2);
    const seg_h  = Math.max(1, Math.floor((artH / 2 - 6 - (n_segs - 1)) / n_segs));
    const stride = seg_h + 1;

    for (let i = 0; i < n_bars; i++) {
        const freq  = 1.2 + i * 0.15;
        const phase = i * 0.55;
        const amp   = Math.abs(Math.sin(waveT * freq + phase)) * 0.7 +
                      Math.abs(Math.sin(waveT * freq * 0.6 + phase + 1.3)) * 0.3;
        const filled = Math.max(1, Math.floor(amp * n_segs));
        const bx     = Math.floor(i * cell_w + 1);

        for (let s = 0; s < n_segs; s++) {
            const v   = Math.floor(160 + s / Math.max(1, n_segs - 1) * 95);
            const lit = s < filled;
            ctx.fillStyle = lit ? `rgb(${v},${v},${v})` : 'rgb(12,12,14)';
            ctx.fillRect(bx, cy - (s + 1) * stride, bar_w, seg_h);
            const vd = Math.floor(v / 6);
            ctx.fillStyle = lit ? `rgb(${vd},${vd},${vd})` : 'rgb(4,4,5)';
            ctx.fillRect(bx, cy + s * stride, bar_w, seg_h);
        }
    }
}

// start/stop the animation loop based on whether cover art is loaded
function updateVizState() {
    !track.coverArt ? startViz() : stopViz();
    if (track.coverArt) drawPreview();
}

// -------------- //
//   Drawing
// -------------- //
// builds a rounded-rectangle path on ctx without stroking or filling
function pathRoundRect(x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
}

// mirrors ui.py's _bevel(): filled face + a light/dark edge to fake a raised look
function drawBevel(rect, face, hi, sh) {
    const { x, y, w, h } = rect;
    const r = Math.min(theme.button.radius, w / 2, h / 2);
    ctx.fillStyle = rgb(face);
    pathRoundRect(x, y, w, h, r);
    ctx.fill();

    // inset each line by r so edges stop at the arc endpoints, not across the corners
    ctx.strokeStyle = rgb(hi);
    ctx.beginPath();
    ctx.moveTo(x + r,     y);            // top
    ctx.lineTo(x + w - r, y);
    ctx.moveTo(x,         y + r);        // left
    ctx.lineTo(x,         y + h - r);
    ctx.stroke();

    ctx.strokeStyle = rgb(sh);
    ctx.beginPath();
    ctx.moveTo(x + r,     y + h - 1);   // bottom
    ctx.lineTo(x + w - r, y + h - 1);
    ctx.moveTo(x + w - 1, y + r);       // right
    ctx.lineTo(x + w - 1, y + h - r);
    ctx.stroke();
}

// mirrors ui.py's _btn()
function drawButton(rect, label, { pressed = false, active = false } = {}) {
    const p = theme.palette;
    drawBevel(rect,
        active ? p.BTN_ACTIVE : p.BTN_FACE,
        pressed ? p.BTN_SH : p.BTN_HI,
        pressed ? p.BTN_HI : p.BTN_SH);

    ctx.fillStyle = rgb(active ? p.BTN_ACT_FG : p.BTN_FG);
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, rect.x + rect.w / 2, rect.y + rect.h / 2 + (pressed ? 1 : 0));
}

// mirrors ui.py's _bar()
function drawBar(rect, progress, bg) {
    const p = theme.palette;
    ctx.fillStyle = rgb(bg);
    ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
    const fw = Math.round(rect.w * Math.max(0, Math.min(1, progress)));
    if (fw) {
        ctx.fillStyle = rgb(p.ACCENT);
        ctx.fillRect(rect.x, rect.y, fw, rect.h);
    }
    ctx.strokeStyle = rgb(p.BORDER);
    ctx.strokeRect(rect.x + 0.5, rect.y + 0.5, rect.w - 1, rect.h - 1);
}

// renders the full player UI onto the canvas using current theme + track state
function drawPreview() {
    const { w: W, h: H } = getDims();
    const p = theme.palette;
    const { panel, ctrlBtns, volBtns, seekBar, volBar } = computeLayout(W, H);

    ctx.fillStyle = rgb(p.BG);
    ctx.fillRect(0, 0, W, H);

    // art panel real cover art if loaded, otherwise placeholder
    ctx.fillStyle = rgb(p.ART_BG);
    ctx.fillRect(0, panel.art.y, W, panel.art.h);
    if (track.coverArt) {
        const img = track.coverArt;
        const iw = img.naturalWidth, ih = img.naturalHeight;
        const mode = theme.cover_art.mode;
        let dx, dy, dw, dh;

        if (mode === 'stretch') {
            dx = 0; dy = panel.art.y; dw = W; dh = panel.art.h;
        } else if (mode === 'bars') {
            // contain: scale to fit, ART_BG fill handles the bars
            const scale = Math.min(W / iw, panel.art.h / ih);
            dw = iw * scale; dh = ih * scale;
            dx = (W - dw) / 2; dy = panel.art.y + (panel.art.h - dh) / 2;
        } else {
            // fill (default): scale to cover, crop excess
            const scale = Math.max(W / iw, panel.art.h / ih);
            dw = iw * scale; dh = ih * scale;
            dx = -(dw - W) / 2; dy = panel.art.y - (dh - panel.art.h) / 2;
        }

        ctx.save();
        ctx.beginPath();
        ctx.rect(0, panel.art.y, W, panel.art.h);
        ctx.clip();
        ctx.drawImage(img, dx, dy, dw, dh);
        ctx.restore();
    } else {
        drawVisualizer(W, panel);
    }

    // title panel
    ctx.fillStyle = rgb(p.PANEL);
    ctx.fillRect(0, panel.title.y, W, panel.title.h);
    ctx.fillStyle = rgb(p.FG);
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(track.title, 6, panel.title.y + panel.title.h / 2);

    // seek panel
    ctx.fillStyle = rgb(p.PANEL);
    ctx.fillRect(0, panel.seek.y, W, panel.seek.h);
    ctx.fillStyle = rgb(p.DIM);
    ctx.font = '9px monospace';
    ctx.textAlign = 'left';
    ctx.fillText('1:23', 2, panel.seek.y + panel.seek.h / 2);
    ctx.textAlign = 'right';
    ctx.fillText('3:45', W - 2, panel.seek.y + panel.seek.h / 2);
    drawBar(seekBar, 0.35, p.SEEK_BG);

    // control panel
    ctx.fillStyle = rgb(p.PANEL);
    ctx.fillRect(0, panel.ctrl.y, W, panel.ctrl.h);
    drawButton(ctrlBtns.prev, '|<');
    drawButton(ctrlBtns.rev,  '<<');
    drawButton(ctrlBtns.play, '||', { active: true });
    drawButton(ctrlBtns.ff,   '>>');
    drawButton(ctrlBtns.next, '>|');

    // volume row
    ctx.fillStyle = rgb(p.PANEL);
    ctx.fillRect(0, panel.vol.y, W, panel.vol.h);
    drawButton(volBtns.shf, 'SHF', { active: true });
    drawButton(volBtns.rpt, 'RPT');
    ctx.fillStyle = rgb(p.DIM);
    ctx.font = '9px monospace';
    ctx.textAlign = 'left';
    ctx.fillText('VOL', volBtns.rpt.x + volBtns.rpt.w + 8, panel.vol.y + panel.vol.h / 2);
    drawBar(volBar, 0.7, p.VOL_BG);
    drawButton(volBtns.vol_minus, '-');
    drawButton(volBtns.vol_plus,  '+');
}

// -------------- //
//   Layout controls
// -------------- //

// describes every editable fraction in theme.layout, grouped into accordion sections
const LAYOUT_SECTIONS = [
    {
        id: 'panels', label: 'Panels',
        fields: [
            { path: 'panels.art',   label: 'Art'   },
            { path: 'panels.title', label: 'Title' },
            { path: 'panels.seek',  label: 'Seek'  },
            { path: 'panels.ctrl',  label: 'Ctrl'  },
        ]
    },
    {
        id: 'ctrl_buttons', label: 'Control Buttons',
        fields: [
            { path: 'ctrl_buttons.y_off',   label: 'Y offset' },
            { path: 'ctrl_buttons.h',        label: 'Height'   },
            { path: 'ctrl_buttons.prev.x',   label: 'Prev X'   },
            { path: 'ctrl_buttons.prev.w',   label: 'Prev W'   },
            { path: 'ctrl_buttons.rev.x',    label: 'Rev X'    },
            { path: 'ctrl_buttons.rev.w',    label: 'Rev W'    },
            { path: 'ctrl_buttons.play.x',   label: 'Play X'   },
            { path: 'ctrl_buttons.play.w',   label: 'Play W'   },
            { path: 'ctrl_buttons.ff.x',     label: 'FF X'     },
            { path: 'ctrl_buttons.ff.w',     label: 'FF W'     },
            { path: 'ctrl_buttons.next.x',   label: 'Next X'   },
            { path: 'ctrl_buttons.next.w',   label: 'Next W'   },
        ]
    },
    {
        id: 'vol_row', label: 'Volume Row',
        fields: [
            { path: 'vol_row.y_off',        label: 'Y offset' },
            { path: 'vol_row.h',             label: 'Height'   },
            { path: 'vol_row.shf.x',         label: 'SHF X'    },
            { path: 'vol_row.shf.w',         label: 'SHF W'    },
            { path: 'vol_row.rpt.x',         label: 'RPT X'    },
            { path: 'vol_row.rpt.w',         label: 'RPT W'    },
            { path: 'vol_row.vol_minus.x',   label: 'Vol− X'   },
            { path: 'vol_row.vol_minus.w',   label: 'Vol− W'   },
            { path: 'vol_row.vol_plus.x',    label: 'Vol+ X'   },
            { path: 'vol_row.vol_plus.w',    label: 'Vol+ W'   },
        ]
    },
    {
        id: 'seek_bar', label: 'Seek Bar',
        fields: [
            { path: 'seek_bar.x',     label: 'X'        },
            { path: 'seek_bar.w',     label: 'Width'    },
            { path: 'seek_bar.y_off', label: 'Y offset' },
            { path: 'seek_bar.h',     label: 'Height'   },
        ]
    },
    {
        id: 'vol_bar', label: 'Vol Bar',
        fields: [
            { path: 'vol_bar.x',     label: 'X'        },
            { path: 'vol_bar.w',     label: 'Width'    },
            { path: 'vol_bar.y_off', label: 'Y offset' },
            { path: 'vol_bar.h',     label: 'Height'   },
        ]
    },
];

// reads a dot-path value from theme.layout (e.g. 'ctrl_buttons.prev.x')
const getLayoutVal = path => path.split('.').reduce((o, k) => o[k], theme.layout);

// writes a value into theme.layout via dot-path
function setLayoutVal(path, val) {
    const keys = path.split('.');
    const obj  = keys.slice(0, -1).reduce((o, k) => o[k], theme.layout);
    obj[keys[keys.length - 1]] = val;
}

// builds the accordion DOM structure once at init; call syncLayoutControls() to update values
function buildLayoutControls() {
    const acc = document.getElementById('layoutAccordion');
    acc.innerHTML = '';

    for (const section of LAYOUT_SECTIONS) {
        const rows = section.fields.map(f => `
            <div class="d-flex align-items-center gap-2 mb-1">
                <span class="swatch-label" style="min-width:5rem">${f.label}</span>
                <input type="range" class="form-range layout-ctrl flex-grow-1"
                    min="0" max="1" step="0.001" data-path="${f.path}">
                <span class="swatch-label layout-val" data-path="${f.path}"
                    style="min-width:3.5rem;text-align:right"></span>
            </div>`).join('');

        const item = document.createElement('div');
        item.className = 'accordion-item';
        item.innerHTML = `
            <h2 class="accordion-header">
                <button class="accordion-button collapsed py-2" type="button"
                    data-bs-toggle="collapse" data-bs-target="#acc-${section.id}">
                    ${section.label}
                </button>
            </h2>
            <div id="acc-${section.id}" class="accordion-collapse collapse">
                <div class="accordion-body py-2 px-3">${rows}</div>
            </div>`;
        acc.appendChild(item);
    }

    acc.querySelectorAll('input.layout-ctrl').forEach(input => {
        input.addEventListener('input', () => {
            setLayoutVal(input.dataset.path, Number(input.value));
            document.querySelector(`.layout-val[data-path="${input.dataset.path}"]`)
                .textContent = Number(input.value).toFixed(3);
            drawPreview();
        });
    });
}

// updates slider values from the current theme without rebuilding the DOM
function syncLayoutControls() {
    document.querySelectorAll('input.layout-ctrl').forEach(input => {
        const val = getLayoutVal(input.dataset.path);
        input.value = val;
        document.querySelector(`.layout-val[data-path="${input.dataset.path}"]`)
            .textContent = val.toFixed(3);
    });
}

// -------------- //
//   Controls
// -------------- //
// sets canvas pixel dimensions to the active preset and scales it up via CSS for readability
function resizeCanvas() {
    const { w: W, h: H } = getDims();
    canvas.width = W;
    canvas.height = H;
    // cap upscale so tiny presets don't render as a postage stamp, without blowing up large ones
    const scale = Math.min(380 / W, 520 / H, 3);
    canvas.style.width  = `${W * scale}px`;
    canvas.style.height = `${H * scale}px`;
}

// fills the preset dropdown from theme.screen.presets and selects the active one
function populatePresetSelect() {
    presetSelect.innerHTML = '';
    for (const p of theme.screen.presets) {
        const opt = document.createElement('option');
        opt.value = p.name;
        opt.textContent = `${p.name} (${p.w}×${p.h})`;
        presetSelect.appendChild(opt);
    }
    presetSelect.value = theme.screen.preset;
}

// builds colour picker swatches from theme.palette, wiring each to a live redraw
function populatePalette() {
    paletteGrid.innerHTML = '';
    for (const key of Object.keys(theme.palette)) {
        const col = document.createElement('div');
        col.className = 'col';
        col.innerHTML = `
            <div class="swatch-row">
                <input type="color" data-key="${key}" value="${rgbToHex(theme.palette[key])}">
                <span class="swatch-label">${key}</span>
            </div>`;
        paletteGrid.appendChild(col);
    }
    paletteGrid.querySelectorAll('input[type="color"]').forEach(input => {
        input.addEventListener('input', e => {
            theme.palette[e.target.dataset.key] = hexToRgb(e.target.value);
            drawPreview();
        });
    });
}

// syncs every control on the page to match the current theme object
function populateControls() {
    populatePresetSelect();
    orientationSelect.value        = theme.screen.orientation;
    radiusRange.value              = theme.button.radius;
    radiusValue.textContent        = theme.button.radius;
    coverArtModeSelect.value = theme.cover_art.mode;
    populatePalette();
    syncLayoutControls();
}

// resizes the canvas then redraws; called when preset or orientation changes
function refresh() {
    resizeCanvas();
    drawPreview();
}

presetSelect.addEventListener('change', () => {
    theme.screen.preset = presetSelect.value;
    refresh();
});

orientationSelect.addEventListener('change', () => {
    theme.screen.orientation = orientationSelect.value;
    refresh();
});

coverArtModeSelect.addEventListener('change', () => {
    theme.cover_art.mode = coverArtModeSelect.value;
    drawPreview();
});

radiusRange.addEventListener('input', () => {
    theme.button.radius = Number(radiusRange.value);
    radiusValue.textContent = theme.button.radius;
    drawPreview();
});

document.getElementById('loadBtn').addEventListener('click',  () => loadInput.click());
document.getElementById('trackBtn').addEventListener('click', () => trackInput.click());

trackInput.addEventListener('change', () => {
    const file = trackInput.files[0];
    if (file) loadTrack(file);
    trackInput.value = '';
});

loadInput.addEventListener('change', () => {
    const file = loadInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
        try {
            theme = JSON.parse(reader.result);
            populateControls();
            refresh();
        } catch (err) {
            alert(`Couldn't parse that file as JSON: ${err.message}`);
        }
    };
    reader.readAsText(file);
    loadInput.value = '';
});

document.getElementById('saveBtn').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(theme, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'theme.json';
    a.click();
    URL.revokeObjectURL(a.href);
});

document.getElementById('resetBtn').addEventListener('click', () => {
    theme = structuredClone(DEFAULT_THEME);
    if (track.coverArt) URL.revokeObjectURL(track.coverArt._url);
    track.title = 'Sample Track Title';
    track.coverArt = null;
    populateControls();
    updateVizState();
});

// -------------- //
//   Init
// -------------- //
buildLayoutControls();

// try the real asset first so edits made via the editor start from the repo's actual theme;
// fall back to the embedded default (fetch of a relative file fails under file://)
if (window.location.protocol === 'file:') {
    populateControls();
    resizeCanvas();
    updateVizState();
} else {
    fetch('../theme.json')
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(json => { theme = json; })
        .catch(() => { theme = structuredClone(DEFAULT_THEME); })
        .finally(() => {
            populateControls();
            resizeCanvas();
            updateVizState();
        });
}
