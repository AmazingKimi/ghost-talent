(() => {
  const originalSettingsPanels = window.settingsPanels;

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
    const tokenText = runtime?.github_token_configured
      ? (zh ? 'GitHub Token：已配置' : 'GitHub Token: configured')
      : (zh ? 'GitHub Token：未配置' : 'GitHub Token: not configured');

    panels.insertAdjacentHTML('afterbegin', `
      <div class="settings-preferences">
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
          <div class="runtime-note">${tokenText}</div>
        </section>
      </div>
    `);
  };
})();
