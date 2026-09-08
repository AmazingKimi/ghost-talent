(() => {
  const originalSettingsPanels = window.settingsPanels;
  let connectTimer = null;

  function currentLanguage() {
    return localStorage.getItem('ghostTalentLang') || ((navigator.language || '').toLowerCase().startsWith('zh') ? 'zh' : 'en');
  }

  function currentTheme() {
    return localStorage.getItem('ghostTalentTheme') || 'system';
  }

  window.setGhostTalentLanguage = function setGhostTalentLanguage(value) {
    localStorage.setItem('ghostTalentLang', value);
    location.reload();
  };

  window.setGhostTalentTheme = function setGhostTalentTheme(value) {
    localStorage.setItem('ghostTalentTheme', value);
    location.reload();
  };

  window.disconnectGhostTalentGitHub = async function disconnectGhostTalentGitHub() {
    const response = await fetch('/api/github/connect', { method: 'DELETE' });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      alert(data?.detail?.message || 'Unable to disconnect GitHub.');
      return;
    }
    await window.settingsPanels();
  };

  window.connectGhostTalentGitHub = async function connectGhostTalentGitHub() {
    const lang = currentLanguage();
    const zh = lang === 'zh';
    const response = await fetch('/api/github/connect/start', { method: 'POST' });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const msg = data?.detail?.message || (zh ? '当前版本尚未配置 GitHub OAuth Client ID。' : 'This build has no GitHub OAuth Client ID configured.');
      alert(msg);
      return;
    }

    window.open(data.verification_uri, '_blank', 'noopener,noreferrer');
    const codeBox = document.getElementById('githubDeviceCode');
    const stateBox = document.getElementById('githubConnectState');
    if (codeBox) codeBox.textContent = data.user_code;
    if (stateBox) stateBox.textContent = zh
      ? 'GitHub 已打开。输入上面的验证码并授权，Ghost Talent 会自动完成连接。'
      : 'GitHub opened. Enter the code above and authorize; Ghost Talent will finish connecting automatically.';

    if (connectTimer) clearTimeout(connectTimer);
    const poll = async () => {
      const pollResponse = await fetch(`/api/github/connect/poll?flow_id=${encodeURIComponent(data.flow_id)}`);
      const result = await pollResponse.json().catch(() => ({}));
      if (result.status === 'connected') {
        if (stateBox) stateBox.textContent = zh ? 'GitHub 已连接。' : 'GitHub connected.';
        setTimeout(() => window.settingsPanels(), 500);
        return;
      }
      if (result.status === 'pending') {
        connectTimer = setTimeout(poll, Math.max(5, Number(result.interval || data.interval || 5)) * 1000);
        return;
      }
      if (stateBox) stateBox.textContent = zh ? '授权未完成，请重新连接。' : 'Authorization did not complete. Please try again.';
    };
    connectTimer = setTimeout(poll, Math.max(5, Number(data.interval || 5)) * 1000);
  };

  window.settingsPanels = async function settingsPanelsWithPreferences() {
    if (typeof originalSettingsPanels === 'function') originalSettingsPanels();
    const panels = document.getElementById('panels');
    if (!panels) return;

    const lang = currentLanguage();
    const theme = currentTheme();
    let runtime = null;
    try {
      const response = await fetch('/api/runtime');
      if (response.ok) runtime = await response.json();
    } catch (_) {}

    const zh = lang === 'zh';
    const gh = runtime?.github || {};
    const connected = Boolean(gh.connected);
    const quota = gh.limit ? `${gh.remaining ?? '—'} / ${gh.limit}` : '—';
    const account = gh.login ? `@${gh.login}` : '';
    const modeLabel = gh.mode === 'environment_token'
      ? (zh ? '环境 Token' : 'Environment token')
      : gh.mode === 'github_connected'
        ? (zh ? 'GitHub 已授权' : 'GitHub connected')
        : (zh ? '匿名公共额度' : 'Anonymous public quota');

    panels.insertAdjacentHTML('afterbegin', `
      <div class="settings-preferences">
        <section class="preference-group github-connect-card">
          <h3>${zh ? 'GitHub 连接' : 'GitHub connection'}</h3>
          <p>${connected
            ? (zh ? `已连接 ${account}。当前 REST API 额度：${quota} / 小时额度。` : `Connected ${account}. Current REST API quota: ${quota}.`)
            : (zh ? `当前使用匿名公共额度（通常只有 60 次/小时）。连接自己的 GitHub 后通常可使用 5,000 次/小时的个人认证额度。` : `Currently using anonymous public quota (typically only 60 requests/hour). Connect your GitHub account to use the authenticated personal quota, typically 5,000/hour.`)}</p>
          <div class="preference-actions">
            ${connected
              ? `<button class="active" disabled>${zh ? '✓ 已连接' : '✓ Connected'}</button>${gh.mode !== 'environment_token' ? `<button onclick="disconnectGhostTalentGitHub()">${zh ? '断开连接' : 'Disconnect'}</button>` : ''}`
              : `<button class="active" onclick="connectGhostTalentGitHub()" ${runtime?.github_oauth_client_configured ? '' : 'disabled'}>${zh ? '连接 GitHub' : 'Connect GitHub'}</button>`}
          </div>
          <div class="runtime-note">${modeLabel} · ${zh ? '额度' : 'Quota'} ${quota}</div>
          ${!connected && !runtime?.github_oauth_client_configured ? `<div class="runtime-note warning-note">${zh ? '维护者需要先为这个公开项目配置一次 GHOST_TALENT_GITHUB_CLIENT_ID；普通用户之后只需点击“连接 GitHub”。' : 'The maintainer must configure GHOST_TALENT_GITHUB_CLIENT_ID once for this public project; after that, normal users only click “Connect GitHub”.'}</div>` : ''}
          <div class="device-code" id="githubDeviceCode"></div>
          <div class="runtime-note" id="githubConnectState"></div>
        </section>
        <section class="preference-group">
          <h3>${zh ? '语言' : 'Language'}</h3>
          <p>${zh ? '切换界面语言。设置会保存在当前设备。' : 'Choose the interface language. The preference is saved on this device.'}</p>
          <div class="preference-actions">
            <button class="${lang === 'zh' ? 'active' : ''}" onclick="setGhostTalentLanguage('zh')">中文</button>
            <button class="${lang === 'en' ? 'active' : ''}" onclick="setGhostTalentLanguage('en')">English</button>
          </div>
        </section>
        <section class="preference-group">
          <h3>${zh ? '外观' : 'Appearance'}</h3>
          <p>${zh ? '选择浅色、深色或跟随系统。' : 'Choose light, dark, or follow your system setting.'}</p>
          <div class="preference-actions">
            <button class="${theme === 'light' ? 'active' : ''}" onclick="setGhostTalentTheme('light')">${zh ? '浅色' : 'Light'}</button>
            <button class="${theme === 'dark' ? 'active' : ''}" onclick="setGhostTalentTheme('dark')">${zh ? '深色' : 'Dark'}</button>
            <button class="${theme === 'system' ? 'active' : ''}" onclick="setGhostTalentTheme('system')">${zh ? '跟随系统' : 'System'}</button>
          </div>
        </section>
      </div>
    `);
  };
})();
