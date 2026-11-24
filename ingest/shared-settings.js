// Unified System Settings Modal (Spec G Phase 4)
// Shared across Cockpit (:8088), Cutroom (:8000), and Beats Studio (:8001).
// Three sections in order: Keys & Accounts, Music & Stings, Prompts & Motion.
(function () {
  function isCutroomOrigin() {
    return window.location.port === '8000' || window.location.pathname.includes('curator');
  }

  function settingsGetUrl() {
    return isCutroomOrigin() ? '/get-settings' : '/api/settings';
  }

  function settingsPostUrl() {
    return isCutroomOrigin() ? '/save-settings' : '/api/settings';
  }

  function cutroomBaseUrl() {
    return 'http://' + window.location.hostname + ':8000';
  }

  function ensureModalDom() {
    if (document.getElementById('shared-settings-modal')) return;
    const overlay = document.createElement('div');
    overlay.id = 'shared-settings-modal';
    overlay.style.cssText = 'display:none; position:fixed; inset:0; background:rgba(28,25,23,0.5); z-index:3000; align-items:center; justify-content:center; padding:16px;';
    overlay.innerHTML = `
      <div style="background:var(--panel-bg, #ffffff); border:1px solid var(--border-color, #e7e5e4); border-radius:12px; width:min(760px, 95vw); max-height:88vh; display:flex; flex-direction:column; color:var(--text-main, #1c1917); box-shadow:0 20px 45px rgba(0,0,0,0.2); overflow:hidden;">
        <div style="display:flex; justify-content:space-between; align-items:center; padding:14px 18px; border-bottom:1px solid var(--border-color, #e7e5e4); background:var(--panel-bg-darker, #f5f5f4);">
          <strong style="font-size:1rem; font-family:var(--font-mono, monospace);">⚙️ System Settings</strong>
          <button type="button" id="sharedSettingsCloseBtn" style="background:transparent; border:none; color:var(--text-muted, #78716c); font-size:1.15rem; cursor:pointer;">✖</button>
        </div>
        <div style="padding:16px 18px; overflow-y:auto; display:flex; flex-direction:column; gap:18px; flex:1;">
          <!-- Section 1: Keys & Accounts -->
          <section data-settings-section="keys-accounts" style="background:var(--panel-bg-darker, #f5f5f4); border:1px solid var(--border-color, #e7e5e4); border-radius:8px; padding:14px;">
            <h3 style="margin:0 0 10px 0; font-size:0.86rem; text-transform:uppercase; letter-spacing:0.04em;">Keys &amp; Accounts</h3>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:10px; font-size:0.78rem;">
              <label>Gemini API Key<input type="password" id="ss-gemini-key" autocomplete="new-password" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Mosaic API Key<input type="password" id="ss-mosaic-key" autocomplete="new-password" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Mosaic Agent ID<input type="text" id="ss-mosaic-agent" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Motion Graphics Node ID<input type="text" id="ss-mosaic-mogr" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Captions Node ID<input type="text" id="ss-mosaic-captions" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Lightning Tips Address<input type="text" id="ss-lightning" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Spotify Show URL<input type="text" id="ss-spotify" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Apple Podcasts URL<input type="text" id="ss-apple" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>YouTube Music URL<input type="text" id="ss-yt-music" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Fountain.fm URL<input type="text" id="ss-fountain" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
              <label>Default Whisper STT Model
                <select id="ss-whisper-model" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);">
                  <option value="large-v3-turbo">large-v3-turbo (Recommended)</option>
                  <option value="small.en">small.en</option>
                  <option value="small">small</option>
                  <option value="base.en">base.en</option>
                  <option value="base">base</option>
                  <option value="medium.en">medium.en</option>
                </select>
              </label>
              <label>External Text Editor<input type="text" id="ss-external-editor" placeholder="gvim" style="width:100%; box-sizing:border-box; margin-top:4px; padding:6px 8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917);"></label>
            </div>
          </section>

          <!-- Section 2: Music & Stings -->
          <section data-settings-section="music-stings" style="background:var(--panel-bg-darker, #f5f5f4); border:1px solid var(--border-color, #e7e5e4); border-radius:8px; padding:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <h3 style="margin:0; font-size:0.86rem; text-transform:uppercase; letter-spacing:0.04em;">Music &amp; Stings</h3>
              <div>
                <button type="button" id="ss-import-music-btn" style="padding:4px 10px; font-size:0.74rem; border-radius:6px; border:1px solid var(--border-color, #e7e5e4); background:var(--card-bg, #ffffff); color:var(--text-main, #1c1917); cursor:pointer;">🎵 Import New Sting</button>
                <input type="file" id="ss-music-upload" accept=".mp3,.wav,.m4a" style="display:none;">
              </div>
            </div>
            <div id="ss-music-list" style="max-height:140px; overflow-y:auto; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; padding:8px; background:var(--bg-color, #fbf9f5); font-size:0.76rem;">Loading music stings…</div>
          </section>

          <!-- Section 3: Prompts & Motion -->
          <section data-settings-section="prompts-motion" style="background:var(--panel-bg-darker, #f5f5f4); border:1px solid var(--border-color, #e7e5e4); border-radius:8px; padding:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <h3 style="margin:0; font-size:0.86rem; text-transform:uppercase; letter-spacing:0.04em;">Prompts &amp; Motion</h3>
              <button type="button" id="ss-reset-mosaic-prompt-btn" style="padding:4px 10px; font-size:0.74rem; border-radius:6px; border:1px solid var(--border-color, #e7e5e4); background:var(--card-bg, #ffffff); color:var(--text-main, #1c1917); cursor:pointer;">↺ Reset Default Prompt</button>
            </div>
            <label style="display:block; font-size:0.78rem;">Mosaic Motion Design Default Prompt
              <textarea id="ss-mosaic-default-prompt" rows="4" style="width:100%; box-sizing:border-box; margin-top:4px; padding:8px; border:1px solid var(--border-color, #e7e5e4); border-radius:6px; background:var(--bg-color, #fbf9f5); color:var(--text-main, #1c1917); font-family:var(--font-mono, monospace); font-size:0.76rem; resize:vertical;"></textarea>
            </label>
          </section>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 18px; border-top:1px solid var(--border-color, #e7e5e4); background:var(--panel-bg-darker, #f5f5f4);">
          <span id="ss-status" style="font-size:0.76rem; color:var(--text-muted, #78716c);"></span>
          <div style="display:flex; gap:8px;">
            <button type="button" id="sharedSettingsCancelBtn" style="padding:6px 12px; border-radius:6px; border:1px solid var(--border-color, #e7e5e4); background:var(--card-bg, #ffffff); color:var(--text-main, #1c1917); cursor:pointer; font-size:0.78rem;">Cancel</button>
            <button type="button" id="sharedSettingsSaveBtn" style="padding:6px 14px; border-radius:6px; border:none; background:var(--primary, #d97706); color:#ffffff; cursor:pointer; font-size:0.78rem; font-weight:700;">💾 Save Settings</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('sharedSettingsCloseBtn').onclick = closeSharedSettingsModal;
    document.getElementById('sharedSettingsCancelBtn').onclick = closeSharedSettingsModal;
    document.getElementById('sharedSettingsSaveBtn').onclick = saveSharedSettings;
    document.getElementById('ss-reset-mosaic-prompt-btn').onclick = async function () {
      try {
        const url = isCutroomOrigin() ? '/get-settings' : (cutroomBaseUrl() + '/get-settings');
        const r = await fetch(url);
        if (r.ok) {
          const d = await r.json();
          if (d.factory_mosaic_prompt || d.default_mosaic_prompt) {
            document.getElementById('ss-mosaic-default-prompt').value = d.factory_mosaic_prompt || d.default_mosaic_prompt;
          }
        }
      } catch (_) {}
    };
    document.getElementById('ss-import-music-btn').onclick = function () {
      document.getElementById('ss-music-upload').click();
    };
    document.getElementById('ss-music-upload').onchange = async function (ev) {
      const file = ev.target.files && ev.target.files[0];
      if (!file) return;
      const base = isCutroomOrigin() ? '' : cutroomBaseUrl();
      try {
        const buf = await file.arrayBuffer();
        await fetch(base + '/upload-music?filename=' + encodeURIComponent(file.name), {
          method: 'POST',
          headers: { 'Content-Type': 'application/octet-stream' },
          body: buf
        });
        await loadSharedMusicList();
      } catch (e) {
        document.getElementById('ss-status').textContent = 'Music import failed: ' + e.message;
      } finally {
        ev.target.value = '';
      }
    };
  }

  async function loadSharedMusicList() {
    const el = document.getElementById('ss-music-list');
    if (!el) return;
    const base = isCutroomOrigin() ? '' : cutroomBaseUrl();
    try {
      const res = await fetch(base + '/list-music');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const files = await res.json();
      if (!Array.isArray(files) || files.length === 0) {
        el.textContent = 'No music stings found.';
        return;
      }
      el.innerHTML = files.map(f => `<div style="padding:3px 4px; border-bottom:1px solid var(--border-color, #e7e5e4);">🎵 ${String(f).replace(/</g, '&lt;')}</div>`).join('');
    } catch (_) {
      el.textContent = 'Music library available when Cutroom (:8000) is running.';
    }
  }

  async function openSharedSettingsModal() {
    ensureModalDom();
    document.getElementById('ss-status').textContent = '';
    try {
      const res = await fetch(settingsGetUrl());
      const s = res.ok ? await res.json() : {};
      document.getElementById('ss-gemini-key').value = s.gemini_api_key || '';
      document.getElementById('ss-mosaic-key').value = s.mosaic_api_key || '';
      document.getElementById('ss-mosaic-agent').value = s.mosaic_agent_id || '';
      document.getElementById('ss-mosaic-mogr').value = s.mosaic_mogr_node_id || '';
      document.getElementById('ss-mosaic-captions').value = s.mosaic_captions_node_id || '';
      document.getElementById('ss-lightning').value = s.lightning_address || '';
      document.getElementById('ss-spotify').value = s.spotify_url || '';
      document.getElementById('ss-apple').value = s.apple_podcasts_url || '';
      document.getElementById('ss-yt-music').value = s.youtube_music_url || '';
      document.getElementById('ss-fountain').value = s.fountain_url || '';
      document.getElementById('ss-whisper-model').value = s.whisper_model || 'large-v3-turbo';
      document.getElementById('ss-external-editor').value = s.external_editor || 'gvim';
      document.getElementById('ss-mosaic-default-prompt').value = s.mosaic_default_prompt || s.default_mosaic_prompt || '';
    } catch (_) {}
    loadSharedMusicList();
    document.getElementById('shared-settings-modal').style.display = 'flex';
  }

  function closeSharedSettingsModal() {
    const el = document.getElementById('shared-settings-modal');
    if (el) el.style.display = 'none';
  }

  async function saveSharedSettings() {
    const payload = {
      gemini_api_key: document.getElementById('ss-gemini-key').value.trim(),
      mosaic_api_key: document.getElementById('ss-mosaic-key').value.trim(),
      mosaic_agent_id: document.getElementById('ss-mosaic-agent').value.trim(),
      mosaic_mogr_node_id: document.getElementById('ss-mosaic-mogr').value.trim(),
      mosaic_captions_node_id: document.getElementById('ss-mosaic-captions').value.trim(),
      lightning_address: document.getElementById('ss-lightning').value.trim(),
      spotify_url: document.getElementById('ss-spotify').value.trim(),
      apple_podcasts_url: document.getElementById('ss-apple').value.trim(),
      youtube_music_url: document.getElementById('ss-yt-music').value.trim(),
      fountain_url: document.getElementById('ss-fountain').value.trim(),
      whisper_model: document.getElementById('ss-whisper-model').value || 'large-v3-turbo',
      whisper_word_timestamps: true,
      external_editor: document.getElementById('ss-external-editor').value.trim() || 'gvim',
      mosaic_default_prompt: document.getElementById('ss-mosaic-default-prompt').value
    };
    try {
      const res = await fetch(settingsPostUrl(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data && data.success) {
        try {
          localStorage.setItem('ddma-gemini-api-key', payload.gemini_api_key);
          localStorage.setItem('ddma-mosaic-api-key', payload.mosaic_api_key);
          localStorage.setItem('ddma-mosaic-agent-id', payload.mosaic_agent_id);
          localStorage.setItem('ddma-mosaic-mogr-node-id', payload.mosaic_mogr_node_id);
          localStorage.setItem('ddma-mosaic-captions-node-id', payload.mosaic_captions_node_id);
          localStorage.setItem('ddma-mosaic-default-prompt', payload.mosaic_default_prompt);
        } catch (_) {}
        closeSharedSettingsModal();
        if (typeof showToast === 'function') showToast('System settings saved');
      } else {
        document.getElementById('ss-status').textContent = 'Save failed.';
      }
    } catch (e) {
      document.getElementById('ss-status').textContent = 'Save error: ' + e.message;
    }
  }

  window.openSharedSettingsModal = openSharedSettingsModal;
  window.closeSharedSettingsModal = closeSharedSettingsModal;
  window.saveSharedSettings = saveSharedSettings;
})();
