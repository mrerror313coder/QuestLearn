/**
 * QuestLearn: Shadows of the Machine - Terminal Engine
 * Retro CRT Command Interpreter, Audio Synthesizer & API Bridge
 */

// State Management
const state = {
    sessionId: localStorage.getItem('questlearn_session_id') || `aether_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
    currentSectorId: '0x01',
    currentSector: null,
    integrityScore: 25,
    solvedSectors: [],
    latestErrorContext: '',
    history: JSON.parse(localStorage.getItem('questlearn_history') || '[]'),
    historyIndex: -1,
    audioEnabled: true,
    theme: localStorage.getItem('questlearn_theme') || 'green',
    crtActive: localStorage.getItem('questlearn_crt') !== 'false'
};

localStorage.setItem('questlearn_session_id', state.sessionId);

// DOM References
const terminalOutput = document.getElementById('terminal-output');
const terminalForm = document.getElementById('terminal-form');
const terminalInput = document.getElementById('terminal-input');
const promptLabel = document.getElementById('prompt-label');

const hudSectorId = document.getElementById('hud-sector-id');
const hudSpiritName = document.getElementById('hud-spirit-name');
const hudDaemonStatus = document.getElementById('hud-daemon-status');
const integrityBar = document.getElementById('integrity-bar');
const integrityVal = document.getElementById('integrity-val');

const btnTheme = document.getElementById('btn-theme');
const btnCrt = document.getElementById('btn-crt');
const btnAudio = document.getElementById('btn-audio');
const btnEditor = document.getElementById('btn-editor');

// Modal Elements
const editorModal = document.getElementById('editor-modal');
const modalCodeEditor = document.getElementById('modal-code-editor');
const modalSectorTitle = document.getElementById('modal-sector-title');
const modalFuncName = document.getElementById('modal-func-name');
const btnModalApply = document.getElementById('btn-modal-apply');
const btnModalClose = document.getElementById('btn-modal-close');
const btnModalLoadCorrupt = document.getElementById('btn-modal-load-corrupt');

// Audio Context Synthesizer
let audioCtx = null;
function getAudioContext() {
    if (!audioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
            audioCtx = new AudioContextClass();
        }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

function playSound(type) {
    if (!state.audioEnabled) return;
    try {
        const ctx = getAudioContext();
        if (!ctx) return;

        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);

        if (type === 'key') {
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(600 + Math.random() * 200, now);
            gain.gain.setValueAtTime(0.015, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.04);
            osc.start(now);
            osc.stop(now + 0.04);
        } else if (type === 'enter') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, now);
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.08);
            gain.gain.setValueAtTime(0.05, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.08);
            osc.start(now);
            osc.stop(now + 0.08);
        } else if (type === 'success') {
            // Triumphant 8-bit arpeggio
            const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
            notes.forEach((freq, idx) => {
                const subOsc = ctx.createOscillator();
                const subGain = ctx.createGain();
                subOsc.type = 'square';
                subOsc.frequency.setValueAtTime(freq, now + idx * 0.09);
                subGain.gain.setValueAtTime(0.04, now + idx * 0.09);
                subGain.gain.exponentialRampToValueAtTime(0.0001, now + (idx + 1) * 0.09);
                subOsc.connect(subGain);
                subGain.connect(ctx.destination);
                subOsc.start(now + idx * 0.09);
                subOsc.stop(now + (idx + 1) * 0.09);
            });
        } else if (type === 'error') {
            // Harsh dissonant glitch
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(160, now);
            osc.frequency.linearRampToValueAtTime(90, now + 0.25);
            gain.gain.setValueAtTime(0.07, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.25);
            osc.start(now);
            osc.stop(now + 0.25);
        } else if (type === 'chirp') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1200, now);
            osc.frequency.exponentialRampToValueAtTime(300, now + 0.15);
            gain.gain.setValueAtTime(0.04, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        }
    } catch (e) {
        // Audio error ignored safely
    }
}

// Print Helpers
function printRaw(html) {
    const el = document.createElement('div');
    el.className = 'msg-line';
    el.innerHTML = html;
    terminalOutput.appendChild(el);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function printText(text, cls = '') {
    const el = document.createElement('div');
    el.className = `msg-line ${cls}`;
    el.textContent = text;
    terminalOutput.appendChild(el);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function printCommandEcho(cmd) {
    printRaw(`<span class="msg-cmd">${escapeHtml(promptLabel.textContent)} ${escapeHtml(cmd)}</span>`);
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// HUD Updates
function updateHUD(integrity, sectorId, spiritName, exorcised = false) {
    state.integrityScore = integrity;
    integrityBar.style.width = `${integrity}%`;
    integrityVal.textContent = `${integrity}%`;

    if (sectorId) {
        state.currentSectorId = sectorId;
        hudSectorId.textContent = sectorId;
    }
    if (spiritName) {
        hudSpiritName.textContent = spiritName.toUpperCase();
    }

    if (integrity >= 100 || exorcised) {
        hudDaemonStatus.textContent = 'DAEMON: EXORCISED';
        hudDaemonStatus.className = 'hud-badge badge-success';
        integrityBar.classList.add('full-clear');
    } else {
        hudDaemonStatus.textContent = 'DAEMON: CORRUPTED';
        hudDaemonStatus.className = 'hud-badge badge-warning';
        integrityBar.classList.remove('full-clear');
    }
}

// REST API Dispatchers
async function fetchSector(sectorId) {
    try {
        const res = await fetch(`/api/sector/${sectorId}`);
        if (!res.ok) throw new Error(`Sector not found: ${sectorId}`);
        const data = await res.json();
        state.currentSector = data;
        state.latestErrorContext = data.stack_trace_demo;
        updateHUD(state.integrityScore, data.id, data.spirit_name);
        return data;
    } catch (err) {
        printText(`[ERROR]: Failed to load sector: ${err.message}`, 'msg-error');
        return null;
    }
}

async function fetchStatus() {
    try {
        const res = await fetch(`/api/status/${state.sessionId}`);
        if (!res.ok) throw new Error('Status query failed');
        const data = await res.json();
        state.integrityScore = data.integrity_score;
        state.solvedSectors = data.solved_sectors || [];
        updateHUD(data.integrity_score, data.current_sector, null, data.exorcism_achieved);
        return data;
    } catch (err) {
        printText(`[ERROR]: Could not retrieve status: ${err.message}`, 'msg-error');
        return null;
    }
}

async function submitPatch(code) {
    printText(`[TRANSMITTING PATCH TO MEMORY SECTOR ${state.currentSectorId}...]`, 'msg-system');
    playSound('enter');

    try {
        const res = await fetch('/api/patch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                sector_id: state.currentSectorId,
                code: code
            })
        });

        const data = await res.json();

        if (data.success) {
            playSound('success');
            printText(`\n>>> [PATCH VERIFIED]: SECTOR ${state.currentSectorId} REPAIRED! <<<`, 'msg-success');
            printText(`Kernel Report: ${data.output}`, 'msg-line');
            updateHUD(data.session.integrity_score, data.session.current_sector, null, data.exorcism_achieved);

            if (data.exorcism_achieved) {
                printRaw(`
<div class="spirit-dialogue" style="border-color: #00ffea;">
    <div class="spirit-header">
        <span>★ [SYSTEM EXORCISM COMPLETE // ALL MEMORY RESTORED] ★</span>
    </div>
    <div class="spirit-body">
        The Autonomous Corruption Daemon has been completely dispelled from AetherOS!<br>
        The spirits of Alan Turing, Grace Hopper, and Ada Lovelace have ascended to eternal computational memory.<br><br>
        Type <strong>'report'</strong> to print and download your official Mastery & Exorcism Certificate!
    </div>
</div>`);
            } else {
                printText(`Next active memory sector unlocked: ${data.session.current_sector}. Run 'scan' to inspect.`, 'msg-system');
                await fetchSector(data.session.current_sector);
            }
        } else {
            playSound('error');
            state.latestErrorContext = data.error_message || data.error_type;
            printText(`\n[PATCH FAILED]: Subroutine failed execution checks!`, 'msg-error');
            printText(`Error Type: ${data.error_type}`, 'msg-warning');
            printRaw(`<pre class="code-block" style="color: #ff9999;">${escapeHtml(data.error_message)}</pre>`);
            printText(`Tip: Consult the sector spirit guide with 'commune <your question>' for Socratic reasoning.`, 'msg-system');
        }
    } catch (err) {
        playSound('error');
        printText(`[COMMUNICATION FAILURE]: ${err.message}`, 'msg-error');
    }
}

async function submitCommune(query) {
    if (!query || query.trim() === '') {
        printText(`Usage: commune <your question or thought>`, 'msg-warning');
        printText(`Example: commune how do I stop the recursion from exceeding the stack?`, 'msg-system');
        return;
    }

    printText(`[TUNING SPIRITUAL COMMUNE CHANNEL TO SECTOR ${state.currentSectorId}...]`, 'msg-system');
    playSound('chirp');

    try {
        const res = await fetch('/api/commune', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                sector_id: state.currentSectorId,
                message: query,
                error_context: state.latestErrorContext
            })
        });

        const data = await res.json();
        playSound('key');

        const spiritHtml = `
<div class="spirit-dialogue">
    <div class="spirit-header">
        <span>${escapeHtml(data.spirit_avatar || '★')} ${escapeHtml(data.spirit_name)} &bull; ${escapeHtml(data.spirit_title || '')}</span>
    </div>
    <div class="spirit-body">${escapeHtml(data.guidance).replace(/\n/g, '<br>')}</div>
</div>`;
        printRaw(spiritHtml);
    } catch (err) {
        playSound('error');
        printText(`[SPIRIT COMMUNE INTERRUPTED]: ${err.message}`, 'msg-error');
    }
}

// Commands Execution
const COMMANDS = {
    help: () => {
        const helpHtml = `
<div style="margin: 8px 0;">
<strong>AVAILABLE AETHER-OS COMMANDS:</strong>
--------------------------------------------------------------------------------
  <strong style="color: var(--accent);">scan</strong>               : Scans current sector, shows corrupted code & error traceback
  <strong style="color: var(--accent);">commune &lt;query&gt;</strong>    : Consults sector's pioneer spirit for Socratic guidance
  <strong style="color: var(--accent);">patch [code]</strong>        : Submits Python fix (or opens editor if no code given)
  <strong style="color: var(--accent);">edit</strong>               : Opens the retro in-terminal visual code patch editor
  <strong style="color: var(--accent);">inspect</strong>            : Prints simulated call stack / memory register snapshot
  <strong style="color: var(--accent);">status</strong>             : Displays system integrity %, cleared sectors & attempts
  <strong style="color: var(--accent);">sectors</strong>            : Displays all available memory sectors in AetherOS
  <strong style="color: var(--accent);">switch &lt;sector_id&gt;</strong>  : Swaps active focus (e.g. 'switch 0x02')
  <strong style="color: var(--accent);">report</strong>             : Displays and downloads the official System Exorcism Report
  <strong style="color: var(--accent);">theme [color]</strong>      : Switches phosphor theme (green, amber, cyan)
  <strong style="color: var(--accent);">audio [on|off]</strong>     : Toggles retro 8-bit sound synthesizers
  <strong style="color: var(--accent);">crt [on|off]</strong>       : Toggles scanlines and screen flicker shader
  <strong style="color: var(--accent);">reset</strong>              : Resets player progress to restart the challenge
  <strong style="color: var(--accent);">clear</strong>              : Clears the terminal screen buffer
--------------------------------------------------------------------------------
`;
        printRaw(helpHtml);
    },

    scan: async () => {
        playSound('chirp');
        printText(`[SCANNING ACTIVE MEMORY SECTOR ${state.currentSectorId}...]`, 'msg-system');
        const sector = await fetchSector(state.currentSectorId);
        if (!sector) return;

        const scanHtml = `
<div style="margin: 8px 0;">
================================================================================
<strong>SECTOR ${escapeHtml(sector.id)}: ${escapeHtml(sector.name.toUpperCase())}</strong>
<strong>CONCEPT:</strong> ${escapeHtml(sector.topic)}
<strong>SPIRIT GUIDE:</strong> ${escapeHtml(sector.spirit_name)} (${escapeHtml(sector.spirit_title)})
================================================================================
<strong>LORE:</strong>
${escapeHtml(sector.lore)}

<strong>CORRUPTED SUBROUTINE CODE:</strong>
<pre class="code-block">${escapeHtml(sector.corrupted_code)}</pre>

<strong>LATEST SYSTEM RUNTIME FAULT:</strong>
<pre class="code-block" style="color: #ff8888;">${escapeHtml(sector.stack_trace_demo)}</pre>

<strong>SPIRIT TRANSMISSION:</strong>
<em>"${escapeHtml(sector.default_spirit_quote)}"</em>
--------------------------------------------------------------------------------
<strong>ACTIONS:</strong>
* Type <strong>'edit'</strong> to open the patch editor.
* Type <strong>'commune &lt;question&gt;'</strong> to ask ${escapeHtml(sector.spirit_name)} for guidance.
* Type <strong>'inspect'</strong> to examine the memory registers.
</div>`;
        printRaw(scanHtml);
    },

    commune: async (args) => {
        await submitCommune(args);
    },

    patch: async (code) => {
        if (!code || code.trim() === '') {
            // Open editor modal if no inline code given
            openCodeEditor();
            return;
        }
        await submitPatch(code);
    },

    edit: () => {
        openCodeEditor();
    },

    inspect: async () => {
        playSound('chirp');
        printText(`[INSPECTING HARDWARE REGISTERS & HEAP FOR SECTOR ${state.currentSectorId}...]`, 'msg-system');
        try {
            const res = await fetch(`/api/inspect/${state.currentSectorId}`);
            if (!res.ok) throw new Error('Inspection failed');
            const data = await res.json();
            const inspectStr = JSON.stringify(data.inspect_data, null, 2);
            printRaw(`
<div style="margin: 8px 0;">
<strong>--- [AETHER-OS KERNEL REGISTER & HEAP TELEMETRY: SECTOR ${state.currentSectorId}] ---</strong>
<pre class="code-block" style="color: #66ffcc;">${escapeHtml(inspectStr)}</pre>
</div>`);
        } catch (err) {
            printText(`[INSPECTION ERROR]: ${err.message}`, 'msg-error');
        }
    },

    status: async () => {
        playSound('key');
        const st = await fetchStatus();
        if (!st) return;

        const solvedStr = st.solved_sectors.length > 0 ? st.solved_sectors.join(', ') : 'NONE';
        const statusHtml = `
<div style="margin: 8px 0;">
================================================================================
<strong>AETHER-OS SYSTEM STATUS & TELEMETRY</strong>
================================================================================
SESSION ID       : ${escapeHtml(st.session_id)}
ACTIVE SECTOR    : ${escapeHtml(st.current_sector)}
INTEGRITY SCORE  : <strong>${st.integrity_score}%</strong> ${st.exorcism_achieved ? '[EXORCISED]' : '[CORRUPTED]'}
CLEARED SECTORS  : ${escapeHtml(solvedStr)}
ATTEMPTS LOG     : ${escapeHtml(JSON.stringify(st.attempts))}
FOUNDATION MODEL : Google Gemma (Open-Weights Socratic Core)
================================================================================
</div>`;
        printRaw(statusHtml);
    },

    sectors: async () => {
        playSound('key');
        try {
            const res = await fetch('/api/sectors');
            const sectors = await res.json();
            let table = '\n<strong>AETHER-OS MEMORY SECTORS:</strong>\n--------------------------------------------------------------------------------\n';
            sectors.forEach(s => {
                const isCleared = state.solvedSectors.includes(s.id);
                const tag = isCleared ? '[CLEARED]  ' : '[CORRUPTED]';
                const activeTag = s.id === state.currentSectorId ? ' -> (ACTIVE)' : '';
                table += `  ${s.id}  ${tag}  ${s.name.padEnd(26)}  Guide: ${s.spirit_name}${activeTag}\n`;
            });
            table += '--------------------------------------------------------------------------------\nUse \'switch <sector_id>\' to change focus.\n';
            printRaw(`<pre class="msg-line">${escapeHtml(table)}</pre>`);
        } catch (err) {
            printText(`Failed to retrieve sectors: ${err.message}`, 'msg-error');
        }
    },

    switch: async (sectorId) => {
        if (!sectorId) {
            printText(`Usage: switch <0x01 | 0x02 | 0x03>`, 'msg-warning');
            return;
        }
        sectorId = sectorId.trim();
        if (!['0x01', '0x02', '0x03'].includes(sectorId)) {
            printText(`Unknown sector: ${sectorId}. Available: 0x01, 0x02, 0x03`, 'msg-error');
            return;
        }

        try {
            const res = await fetch('/api/switch_sector', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: state.sessionId, sector_id: sectorId })
            });
            if (res.ok) {
                state.currentSectorId = sectorId;
                printText(`[KERNEL]: Switched active focus to Sector ${sectorId}.`, 'msg-success');
                await fetchSector(sectorId);
            }
        } catch (err) {
            printText(`Failed to switch sector: ${err.message}`, 'msg-error');
        }
    },

    report: async () => {
        playSound('key');
        printText(`[COMPILING SYSTEM INTEGRITY & EXORCISM REPORT...]`, 'msg-system');
        try {
            const res = await fetch(`/api/report/${state.sessionId}`);
            const reportText = await res.text();
            printRaw(`<pre class="code-block" style="color: #99ffbb;">${escapeHtml(reportText)}</pre>`);

            // Offer instant download
            const blob = new Blob([reportText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `AetherOS_Exorcism_Report_${state.sessionId}.txt`;
            a.className = 'hud-btn hud-btn-accent';
            a.style.display = 'inline-block';
            a.style.margin = '10px 0';
            a.textContent = 'DOWNLOAD OFFICIAL REPORT (.TXT)';
            terminalOutput.appendChild(a);
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        } catch (err) {
            printText(`Report generation failed: ${err.message}`, 'msg-error');
        }
    },

    theme: (name) => {
        const themeName = (name || '').toLowerCase().trim();
        if (['green', 'amber', 'cyan'].includes(themeName)) {
            setTheme(themeName);
            printText(`Phosphor palette switched to: ${themeName.toUpperCase()}`, 'msg-success');
        } else {
            // Cycle theme
            const cycle = { green: 'amber', amber: 'cyan', cyan: 'green' };
            const next = cycle[state.theme] || 'green';
            setTheme(next);
            printText(`Phosphor palette switched to: ${next.toUpperCase()}`, 'msg-success');
        }
    },

    audio: (val) => {
        val = (val || '').toLowerCase().trim();
        if (val === 'off' || val === '0' || val === 'false') {
            state.audioEnabled = false;
            btnAudio.textContent = 'SFX: OFF';
            printText(`Synthesizer audio disabled.`, 'msg-system');
        } else if (val === 'on' || val === '1' || val === 'true') {
            state.audioEnabled = true;
            btnAudio.textContent = 'SFX: ON';
            playSound('enter');
            printText(`Synthesizer audio enabled.`, 'msg-system');
        } else {
            state.audioEnabled = !state.audioEnabled;
            btnAudio.textContent = state.audioEnabled ? 'SFX: ON' : 'SFX: OFF';
            if (state.audioEnabled) playSound('enter');
            printText(`Synthesizer audio toggled: ${state.audioEnabled ? 'ON' : 'OFF'}`, 'msg-system');
        }
    },

    crt: (val) => {
        val = (val || '').toLowerCase().trim();
        if (val === 'off' || val === 'false') {
            setCRT(false);
            printText(`CRT scanlines and flicker disabled.`, 'msg-system');
        } else if (val === 'on' || val === 'true') {
            setCRT(true);
            printText(`CRT scanlines and flicker enabled.`, 'msg-system');
        } else {
            setCRT(!state.crtActive);
            printText(`CRT scanlines toggled: ${state.crtActive ? 'ON' : 'OFF'}`, 'msg-system');
        }
    },

    reset: async () => {
        playSound('error');
        printText(`[ALERT]: Resetting session memory and purging progress...`, 'msg-warning');
        try {
            const res = await fetch('/api/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: state.sessionId })
            });
            const data = await res.json();
            state.currentSectorId = '0x01';
            state.integrityScore = data.integrity_score;
            state.solvedSectors = [];
            updateHUD(data.integrity_score, '0x01', 'ALAN TURING', false);
            printText(`System reset complete. Integrity returned to 25%. Sector 0x01 active.`, 'msg-success');
            await fetchSector('0x01');
        } catch (err) {
            printText(`Reset failed: ${err.message}`, 'msg-error');
        }
    },

    clear: () => {
        terminalOutput.innerHTML = '';
    }
};

// UI Toggles & Theme handlers
function setTheme(t) {
    state.theme = t;
    localStorage.setItem('questlearn_theme', t);
    document.body.classList.remove('theme-green', 'theme-amber', 'theme-cyan');
    document.body.classList.add(`theme-${t}`);
}

function setCRT(active) {
    state.crtActive = active;
    localStorage.setItem('questlearn_crt', active);
    if (active) {
        document.body.classList.add('crt-active');
    } else {
        document.body.classList.remove('crt-active');
    }
}

// Code Editor Modal Handlers
async function openCodeEditor() {
    if (!state.currentSector) {
        await fetchSector(state.currentSectorId);
    }
    const sector = state.currentSector;
    if (!sector) return;

    modalSectorTitle.textContent = `SECTOR ${sector.id} - ${sector.name.toUpperCase()}`;
    modalFuncName.textContent = sector.topic;
    modalCodeEditor.value = sector.corrupted_code;
    editorModal.classList.remove('hidden');
    modalCodeEditor.focus();
    playSound('chirp');
}

function closeCodeEditor() {
    editorModal.classList.add('hidden');
    terminalInput.focus();
}

btnModalClose.addEventListener('click', closeCodeEditor);

// Dismiss on backdrop click
editorModal.addEventListener('click', (e) => {
    if (e.target === editorModal) {
        closeCodeEditor();
    }
});

// Global Escape key dismisses modal
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !editorModal.classList.contains('hidden')) {
        closeCodeEditor();
    }
});

btnModalLoadCorrupt.addEventListener('click', () => {
    if (state.currentSector) {
        modalCodeEditor.value = state.currentSector.corrupted_code;
        playSound('chirp');
    }
});

btnModalApply.addEventListener('click', async () => {
    const code = modalCodeEditor.value;
    closeCodeEditor();
    printCommandEcho(`patch <code editor content>`);
    await submitPatch(code);
});

// Modal shortcut: Ctrl+Enter to apply, Esc to close
modalCodeEditor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = modalCodeEditor.selectionStart;
        const end = modalCodeEditor.selectionEnd;
        modalCodeEditor.value = modalCodeEditor.value.substring(0, start) + '    ' + modalCodeEditor.value.substring(end);
        modalCodeEditor.selectionStart = modalCodeEditor.selectionEnd = start + 4;
    } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        btnModalApply.click();
    }
});

// HUD Button Handlers
btnTheme.addEventListener('click', () => COMMANDS.theme());
btnCrt.addEventListener('click', () => COMMANDS.crt());
btnAudio.addEventListener('click', () => COMMANDS.audio());
btnEditor.addEventListener('click', openCodeEditor);

// Command Input & Parser
terminalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const rawVal = terminalInput.value.trim();
    if (!rawVal) return;

    // Record in history
    state.history.push(rawVal);
    if (state.history.length > 50) state.history.shift();
    localStorage.setItem('questlearn_history', JSON.stringify(state.history));
    state.historyIndex = -1;

    terminalInput.value = '';
    printCommandEcho(rawVal);
    playSound('enter');

    // Parse command and argument
    const firstSpace = rawVal.indexOf(' ');
    let cmd = '';
    let args = '';
    if (firstSpace === -1) {
        cmd = rawVal.toLowerCase();
    } else {
        cmd = rawVal.substring(0, firstSpace).toLowerCase();
        args = rawVal.substring(firstSpace + 1).trim();
    }

    if (COMMANDS[cmd]) {
        await COMMANDS[cmd](args);
    } else {
        playSound('error');
        printText(`Unknown command: '${cmd}'. Type 'help' to inspect valid AetherOS commands.`, 'msg-error');
    }
});

// Keystroke & Autocomplete Handling
const AUTOCOMPLETE_LIST = [
    'help', 'scan', 'commune', 'patch', 'edit', 'inspect',
    'status', 'sectors', 'switch', 'report', 'theme', 'audio',
    'crt', 'reset', 'clear'
];

terminalInput.addEventListener('keydown', (e) => {
    playSound('key');

    // Autocomplete with Tab
    if (e.key === 'Tab') {
        e.preventDefault();
        const val = terminalInput.value.trim().toLowerCase();
        if (!val) return;

        const match = AUTOCOMPLETE_LIST.find(c => c.startsWith(val));
        if (match) {
            terminalInput.value = match + ' ';
        }
    }

    // Command History Navigation with Up/Down
    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (state.history.length === 0) return;
        if (state.historyIndex === -1) {
            state.historyIndex = state.history.length - 1;
        } else if (state.historyIndex > 0) {
            state.historyIndex--;
        }
        terminalInput.value = state.history[state.historyIndex] || '';
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (state.historyIndex !== -1) {
            if (state.historyIndex < state.history.length - 1) {
                state.historyIndex++;
                terminalInput.value = state.history[state.historyIndex] || '';
            } else {
                state.historyIndex = -1;
                terminalInput.value = '';
            }
        }
    }
});

// Boot Sequence & Initializer
async function bootSequence() {
    setTheme(state.theme);
    setCRT(state.crtActive);

    const asciiLogo = `
   ██████╗ ██╗   ██╗███████╗███████╗████████╗██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗
  ██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║
  ██║   ██║██║   ██║█████╗  ███████╗   ██║   ██║     █████╗  ███████║██████╔╝██╔██╗ ██║
  ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   ██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║
  ╚██████╔╝╚██████╔╝███████╗███████║   ██║   ███████╗███████╗██║  ██║██║  ██║██║ ╚████║
   ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
                      [SHADOWS OF THE MACHINE &bull; AETHER-OS v2.41]
`;

    printRaw(`<pre class="ascii-banner">${escapeHtml(asciiLogo)}</pre>`);
    printText(`[SYSTEM BOOT]: Loading kernel modules... OK`, 'msg-system');
    printText(`[INTELLIGENCE CORE]: Google Gemma Open-Weights Engine Initialized.`, 'msg-system');
    printText(`[EVENT]: Hacktoberfest 2026 Open-Source AI Challenge // Ghost in the Machine`, 'msg-system');
    printText(`[WARNING]: AUTONOMOUS CORRUPTION DAEMON DETECTED IN KERNEL MEMORY!`, 'msg-error');
    printText(`System Integrity compromised at 25%. Digitized computing ancestors available for commune.\n`, 'msg-warning');

    printText(`Type 'scan' to inspect corrupted Sector 0x01, or 'help' for terminal commands.`, 'msg-success');

    // Load initial sector and status
    await fetchStatus();
    await fetchSector(state.currentSectorId);
}

// Start on DOM ready
document.addEventListener('DOMContentLoaded', bootSequence);
