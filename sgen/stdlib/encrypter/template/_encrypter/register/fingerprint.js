"use strict";
import { sha256 } from './hash.js';

function trunc(v, n = 48) {
    const s = String(v);
    return s.length > n ? s.slice(0, n) + '…' : s;
}

function row(key, val) {
    const ok = val !== null && val !== undefined && val !== '' && val !== 'N/A' && val !== 'error';
    return { key, val: ok ? val : 'N/A', ok };
}

async function collectNavigator() {
    const nav = navigator;
    return [
        row('userAgent', trunc(nav.userAgent)),
        row('language', nav.language),
        row('languages', (nav.languages || []).join(', ')),
        row('platform', nav.platform),
        row('hardwareConcurrency', nav.hardwareConcurrency),
        row('deviceMemory', nav.deviceMemory != null ? nav.deviceMemory + ' GB' : 'N/A'),
        row('maxTouchPoints', nav.maxTouchPoints),
        row('cookieEnabled', nav.cookieEnabled),
        row('doNotTrack', nav.doNotTrack ?? 'N/A'),
        row('pdfViewer', nav.pdfViewerEnabled != null ? nav.pdfViewerEnabled : 'N/A'),
    ];
}

const isDesktop = () => {
    const ua = navigator.userAgent.toLowerCase();

    return !/mobile|android|iphone|ipad|tablet/.test(ua);
};

async function collectScreen() {
    return [
        row('screen.width', screen.width),
        row('screen.height', screen.height),
        // row('availWidth', screen.availWidth), // it depends on fullscreen/not
        // row('availHeight', screen.availHeight),
        row('colorDepth', screen.colorDepth),
        row('pixelDepth', screen.pixelDepth),
        row('devicePixelRatio', window.devicePixelRatio),
    ];
}

async function collectTimezone() {
    const dtf = Intl.DateTimeFormat().resolvedOptions();
    return [
        row('timeZone', dtf.timeZone),
        row('tzOffset (min)', new Date().getTimezoneOffset()),
        row('locale', dtf.locale),
        row('calendar', dtf.calendar),
        row('numberFormat', new Intl.NumberFormat().format(1234567.89)),
        row('dateOrder', new Intl.DateTimeFormat().format(new Date(2000, 0, 31))),
    ];
}

async function collectCanvas() {
    try {
        const c = document.createElement('canvas');
        c.width = 300; c.height = 60;
        const ctx = c.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('!𝐚Z̴̛̛̛̛͌̈́̽͋̒̍͌̈́͑͋̈́̓̓̓̾͛̐̑͆̑̎̾̈́̈́̈́́̾̾̾̍̈́̎̈́̈́͑̾̎̈́̑̈́͆̈́͆̽̄͛̈́̈́̎͑́̈́̈́̑̍̀̀̀̀̾̄̈́͑̄̈́̽͆̀́̑̍̾̈́́̈́͑̎́́̾̈́̀̄͑́̀̈́̈́͆́̀̈́̀̀̀̈́́̈́́́́̾̎̄̈́̀̈́̀̀̀́̈́̈́̀́́́̈́̀̀̀̀̀̀́̀̀̀̀̀̀̀̀̀̚̕͝͠͝͝͠͠͝͝͠͝͠͠͠͝͠͝͝͠͝͝͝͝͝͠͝͝͝͝͝͝͝𝚌ꜱｔⓛ🄴ne̶e̲□�', 2, 15);
        ctx.fillStyle = 'rgba(102,204,0,0.7)';
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(255,0,255,0.5)';
        ctx.shadowOffsetX = 5;
        ctx.shadowOffsetY = 5;
        ctx.fillText('Canvas test', 4, 35);
        const dataUrl = c.toDataURL();
        const hash = await sha256(dataUrl);
        return [
            row('canvas hash', hash.slice(0, 32)),
            row('dataURL length', dataUrl.length),
        ];
    } catch (e) { return [row('canvas', 'blocked')]; }
}

async function collectWebGL() {
    try {
        const c = document.createElement('canvas');
        const gl = c.getContext('webgl') || c.getContext('experimental-webgl');
        if (!gl) return [row('webgl', 'not supported')];
        const dbg = gl.getExtension('WEBGL_debug_renderer_info');
        const vendor = dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : 'N/A';
        const renderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : 'N/A';
        const exts = gl.getSupportedExtensions() || [];
        return [
            row('vendor', trunc(vendor, 40)),
            row('renderer', trunc(renderer, 40)),
            row('version', trunc(gl.getParameter(gl.VERSION), 40)),
            row('shadingLang', trunc(gl.getParameter(gl.SHADING_LANGUAGE_VERSION), 40)),
            row('extensions', exts.length + ' supported'),
            row('maxTexture', gl.getParameter(gl.MAX_TEXTURE_SIZE)),
        ];
    } catch (e) { return [row('webgl', 'error')]; }
}

async function collectAudio() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 44100 });
        const osc = ctx.createOscillator();
        const analyser = ctx.createAnalyser();
        analyser.smoothingTimeConstant = 0;
        analyser.fftSize = 2048;
        const gain = ctx.createGain();
        gain.gain.value = 0;
        osc.connect(analyser);
        analyser.connect(gain);
        gain.connect(ctx.destination);
        osc.start(0);
        const buf = new Float32Array(analyser.frequencyBinCount);
        for (let i = 0; i < 5; i++) {
            analyser.getFloatFrequencyData(buf);
        }
        const quantized = buf.slice(0, 50).map(v => Math.round(v * 100))
        osc.stop();
        ctx.close();
        const sum = buf.reduce((a, v) => a + Math.abs(v), 0);
        const hash = await sha256(buf.slice(0, 50).join(','));
        return [
            row('sampleRate', ctx.sampleRate),
            row('channelCount', ctx.destination.channelCount),
            row('fftSize', analyser.fftSize),
            row('bufferSum', sum.toFixed(2)),
            row('audio hash', hash.slice(0, 32)),
        ];
    } catch (e) { return [row('audio', 'blocked')]; }
}

async function collectFonts() {
    const test = ['Arial', 'Times New Roman', 'Courier New', 'Georgia', 'Verdana',
        'Helvetica', 'Impact', 'Comic Sans MS', 'Trebuchet MS', 'Tahoma',
        'Palatino', 'Garamond', 'Bookman', 'Arial Black', 'Webdings'];
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = '72px monospace';
    const base = ctx.measureText('mmmmmmmmlli').width;
    const found = test.filter(f => {
        ctx.font = `72px '${f}', monospace`;
        return ctx.measureText('mmmmmmmmlli').width !== base;
    });
    return [
        row('detected', found.join(', ') || 'none'),
        row('count', `${found.length} / ${test.length} detected`),
    ];
}

async function collectMedia() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audio = devices.filter(d => d.kind === 'audioinput').length;
        const video = devices.filter(d => d.kind === 'videoinput').length;
        const out = devices.filter(d => d.kind === 'audiooutput').length;
        return [
            row('audioInputs', audio),
            row('videoInputs', video),
            row('audioOutputs', out),
            row('total devices', devices.length),
        ];
    } catch (e) { return [row('media devices', 'permission denied')]; }
}

async function collectNetwork() {
    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (!conn) return [row('connection API', 'not supported')];
    return [
        row('effectiveType', conn.effectiveType ?? 'N/A'),
        row('downlink (Mbps)', conn.downlink ?? 'N/A'),
        row('rtt (ms)', conn.rtt ?? 'N/A'),
        row('saveData', conn.saveData ?? 'N/A'),
    ];
}

async function collectFeatures() {
    const checks = [
        ['localStorage', () => !!window.localStorage],
        ['sessionStorage', () => !!window.sessionStorage],
        ['IndexedDB', () => !!window.indexedDB],
        ['ServiceWorker', () => 'serviceWorker' in navigator],
        ['WebSockets', () => !!window.WebSocket],
        ['WebAssembly', () => !!window.WebAssembly],
        ['SharedArrayBuffer', () => !!window.SharedArrayBuffer],
        ['Notifications', () => 'Notification' in window],
        ['Geolocation', () => 'geolocation' in navigator],
        ['Bluetooth', () => 'bluetooth' in navigator],
        ['USB', () => 'usb' in navigator],
        ['h264 video', () => document.createElement('video').canPlayType('video/mp4;codecs="avc1"') !== ''],
        ['webm video', () => document.createElement('video').canPlayType('video/webm;codecs="vp8"') !== ''],
        ['ogg audio', () => document.createElement('audio').canPlayType('audio/ogg;codecs="vorbis"') !== ''],
    ];
    return checks.map(([name, fn]) => {
        try { return row(name, fn() ? 'yes' : 'no'); }
        catch (e) { return row(name, 'error'); }
    });
}

async function collectSpeech() {
    try {
        const voices = speechSynthesis.getVoices();
        if (!voices.length) await new Promise(r => { speechSynthesis.onvoiceschanged = r; setTimeout(r, 500); });
        const v = speechSynthesis.getVoices();
        const langs = [...new Set(v.map(x => x.lang))].slice(0, 8).join(', ');
        return [
            row('voice count', v.length),
            row('languages', trunc(langs, 50)),
            row('first voice', trunc(v[0]?.name || 'N/A', 40)),
        ];
    } catch (e) { return [row('speech', 'not supported')]; }
}

export async function getFingerprint() {
    const collectors = [
        ['Navigator', collectNavigator],
        ['Screen', collectScreen],
        ['Timezone & Locale', collectTimezone],
        ['Canvas', collectCanvas],
        ['WebGL', collectWebGL],
        ['Audio', collectAudio],
        ['Fonts', collectFonts],
        ['Media Devices', collectMedia],
        ['Network', collectNetwork],
        ['Features', collectFeatures],
        ['Speech Voices', collectSpeech],
    ];

    const allData = {};

    for (const [name, fn] of collectors) {
        try {
            const rows = await fn();
            allData[name] = rows;
        } catch (e) {
            allData[name] = [{ key: 'error', val: e.message, ok: false }];
        }
    }

    const flatValues = Object.values(allData)
        .flat()
        .filter(r => r.val !== 'N/A' && r.val !== 'blocked' && r.val !== 'not supported' && r.val !== 'error')
        .map(r => `${r.key}:${r.val}`)
        .join('|');

    const hash = await sha256(flatValues);

    return hash;
}

