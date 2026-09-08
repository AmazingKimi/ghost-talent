(() => {
  const originalSettingsPanels = window.settingsPanels;
  let connectTimer = null;

  function currentLanguage() {
    return localStorage.getItem('ghostTalentLang') || ((navigator.language || '').toLowerCase().startsWith('zh') ? 'zh' : 'en');
  }

  function currentTheme() {
    return localStorage.getItem('ghostTalentTheme') || 'system';
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>\"]/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;'
    }[char]));
  }

  function safeUrl(value) {
    const url = String(value || '').trim();
    return /^https:\/\//i.test(url) ? url : '';
  }

  function allCandidateRows() {
    const primary = typeof rows !== 'undefined' && Array.isArray(rows) ? rows : [];
    const watched = typeof watchRows !== 'undefined' && Array.isArray(watchRows) ? watchRows : [];
    return [...primary, ...watched];
  }

  function candidateByLogin(login) {
    return allCandidateRows().find((row) => String(row?.candidate?.login || '').toLowerCase() === String(login || '').toLowerCase());
  }

  function enhanceCandidateCards() {
    document.querySelectorAll('.card').forEach((card) => {
      if (card.dataset.profileEnhanced === '1') return;
      const loginNode = card.querySelector('.login');
      const nameNode = card.querySelector('.name');
      if (!loginNode || !nameNode) return;
      const login = loginNode.textContent.trim().replace(/^@/, '');
      const row = candidateByLogin(login);
      const profileUrl = safeUrl(row?.candidate?.profile_url || row?.dossier?.identity?.profile_url);
      if (!profileUrl) return;
      [nameNode, loginNode].forEach((node) => {
        const link = document.createElement('a');
        link.href = profileUrl;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.className = 'candidate-profile-link';
        link.innerHTML = node.innerHTML;
        node.textContent = '';
        node.appendChild(link);
      });
      card.dataset.profileEnhanced = '1';
    });
  }

  const resultsObserver = new MutationObserver(() => enhanceCandidateCards());
  const observeResults = () => {
    const results = document.getElementById('results');
    if (results) {
      resultsObserver.observe(results, { childList: true, subtree: true });
      enhanceCandidateCards();
    }
  };

  window.setGhostTalentLanguage = async function setGhostTalentLanguage(value) {
    localStorage.setItem('ghostTalentLang', value);
    if (typeof lang !== 'undefined') lang = value;
    if (typeof applyLanguage === 'function') applyLanguage();
    else document.documentElement.lang = value === 'zh' ? 'zh-CN' : 'en';
    if (typeof window.settingsPanels === 'function') await window.settingsPanels();
  };

  window.setGhostTalentTheme = async function setGhostTalentTheme(value) {
    localStorage.setItem('ghostTalentTheme', value);
    if (typeof themePref !== 'undefined') themePref = value;
    if (typeof applyTheme === 'function') applyTheme();
    else {
      const dark = value === 'dark' || (value === 'system' && window.matchMedia?.('(prefers-color-scheme: dark)').matches);
      document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    }
    if (typeof window.settingsPanels === 'function') await window.settingsPanels();
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
    const current = currentLanguage();
    const zh = current === 'zh';
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

  window.openDossier = function openDossierRich(login) {
    const row = candidateByLogin(login);
    if (!row) return;
    const zh = currentLanguage() === 'zh';
    const dossier = row.dossier || {};
    const identity = dossier.identity || row.candidate || {};
    const recommendation = dossier.recommendation || {};
    const signal = dossier.signal || {};
    const mix = dossier.evidence_mix || {};
    const profile = dossier.technical_profile || [];
    const contributions = dossier.important_contributions || dossier.best_evidence || [];
    const bestEvidence = dossier.best_evidence || [];
    const trajectory = dossier.trajectory || row.trajectory || {};
    const activity = dossier.activity || {};
    const profileUrl = safeUrl(identity.profile_url || row.candidate?.profile_url);
    const status = recommendation.status || row.recommendation_status || 'DISCOVERED';

    const labels = zh ? {
      profile: '打开 GitHub 主页 ↗', why: '为什么值得关注', technical: '技术画像', whyNow: '为什么是现在',
      evidence: '最佳外部证据', contributions: '重要贡献', mix: '证据结构', trajectory: '轨迹与活跃度',
      signal: '信号详情', risks: '证据边界与限制', noEvidence: '当前没有足够的可展示外部证据。',
      self: '自有 / 发现来源仓库', external: '外部贡献', confidence: '置信度', mainRisk: '主要风险',
      repo: '仓库', strength: '证据强度', observed: '观察时间', openEvidence: '打开原始证据 ↗'
    } : {
      profile: 'Open GitHub profile ↗', why: 'Why this candidate', technical: 'Technical profile', whyNow: 'Why now',
      evidence: 'Best external evidence', contributions: 'Important contributions', mix: 'Evidence mix', trajectory: 'Trajectory & activity',
      signal: 'Signal detail', risks: 'Evidence boundaries & limitations', noEvidence: 'No sufficiently detailed external evidence is available yet.',
      self: 'Self-owned / discovery repo', external: 'External contribution', confidence: 'Confidence', mainRisk: 'Main risk',
      repo: 'Repository', strength: 'Evidence strength', observed: 'Observed', openEvidence: 'Open source evidence ↗'
    };

    const evidenceCards = bestEvidence.length ? bestEvidence.map((item) => {
      const url = safeUrl(item.url);
      return `<article class="evidence-item">
        <div class="evidence-item-head"><strong>${escapeHtml(item.title || 'Evidence')}</strong><span class="badge ${item.evidence_strength === 'strong' ? 'good' : 'warn'}">${escapeHtml(item.evidence_strength || 'limited')}</span></div>
        <div class="small">${labels.repo}: ${escapeHtml(item.repository || '—')}${item.number ? ` · PR #${escapeHtml(item.number)}` : ''}</div>
        <p>${escapeHtml(item.interpretation || '')}</p>
        ${url ? `<a class="dossier-link" href="${url}" target="_blank" rel="noopener noreferrer">${labels.openEvidence}</a>` : ''}
      </article>`;
    }).join('') : `<p class="small">${labels.noEvidence}</p>`;

    const contributionRows = contributions.length ? contributions.map((item) => {
      const url = safeUrl(item.url);
      const facts = Array.isArray(item.evidence_facts) ? item.evidence_facts.join(' · ') : '';
      return `<div class="contribution-row">
        <div><strong>${escapeHtml(item.title || 'Contribution')}</strong><div class="small">${escapeHtml(item.repository || '—')}${item.number ? ` · PR #${escapeHtml(item.number)}` : ''}</div></div>
        <div class="small">${escapeHtml(facts || item.evidence_strength || '')}</div>
        ${url ? `<a class="dossier-link" href="${url}" target="_blank" rel="noopener noreferrer">↗</a>` : ''}
      </div>`;
    }).join('') : `<p class="small">${labels.noEvidence}</p>`;

    const limitations = Array.isArray(dossier.limitations) ? dossier.limitations : [];
    const drawer = document.getElementById('dossier');
    if (!drawer) return;
    drawer.innerHTML = `
      <div class="dossier-identity-row">
        <div>
          <h2>${escapeHtml(identity.name || identity.login || login)}</h2>
          <p class="small">@${escapeHtml(identity.login || login)} · ${labels.confidence} ${escapeHtml(identity.confidence ?? row.evidence_confidence ?? '—')}</p>
        </div>
        ${profileUrl ? `<a class="profile-cta" href="${profileUrl}" target="_blank" rel="noopener noreferrer">${labels.profile}</a>` : ''}
      </div>
      <div class="decision">
        <span class="status" data-status="${escapeHtml(status)}">${escapeHtml(status)}</span>
        <h3>${escapeHtml(recommendation.action || '')}</h3>
        <p class="small"><b>${labels.mainRisk}:</b> ${escapeHtml(recommendation.main_risk || '')}</p>
      </div>
      <div class="section"><h3>${labels.why}</h3><p>${escapeHtml(typeof reason === 'function' ? reason(row) : recommendation.action || '')}</p></div>
      <div class="section"><h3>${labels.technical}</h3>${profile.length ? profile.map((item) => `<p><b>${escapeHtml(item.term)}</b> · ${escapeHtml(item.support)} evidence · ${escapeHtml(item.external_support)} external</p>`).join('') : `<p class="small">${labels.noEvidence}</p>`}</div>
      <div class="section"><h3>${labels.whyNow}</h3><ul>${(dossier.why_now || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul></div>
      <div class="section"><h3>${labels.evidence}</h3><div class="evidence-list">${evidenceCards}</div></div>
      <div class="section"><h3>${labels.contributions}</h3><div class="contribution-list">${contributionRows}</div></div>
      <div class="section"><h3>${labels.mix}</h3><div class="mix"><div><strong>${escapeHtml(mix.self_owned_repo_pct ?? mix.self_owned_or_discovery_repo_pct ?? 0)}%</strong><span class="small">${labels.self}</span></div><div><strong>${escapeHtml(mix.external_repository_contribution_pct ?? mix.external_upstream_pct ?? 0)}%</strong><span class="small">${labels.external}</span></div></div></div>
      <div class="section"><h3>${labels.trajectory}</h3>
        <div class="trajectory-grid">
          <div><span class="small">Observations</span><strong>${escapeHtml(trajectory.observation_count ?? '—')}</strong></div>
          <div><span class="small">7d</span><strong>${escapeHtml(trajectory.d7?.status || 'building_history')}</strong></div>
          <div><span class="small">30d</span><strong>${escapeHtml(trajectory.d30?.status || 'building_history')}</strong></div>
          <div><span class="small">30d active days</span><strong>${escapeHtml(activity.active_days_30d ?? '—')}</strong></div>
        </div>
      </div>
      <div class="section"><h3>${labels.signal}</h3><p>Radar <b>${escapeHtml(signal.radar_score ?? row.radar_score)}</b> · Ghost ${escapeHtml(signal.ghost_score ?? row.ghost_score)} · External ${escapeHtml(signal.external_validation ?? row.external_validation)} · Momentum ${escapeHtml(row.momentum)} · Visibility ${escapeHtml(signal.visibility_gap ?? row.visibility_gap)}</p></div>
      <div class="section"><h3>${labels.risks}</h3>${limitations.length ? `<ul>${limitations.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : `<p class="small">—</p>`}</div>
    `;
    document.getElementById('drawer')?.classList.add('open');
  };

  window.settingsPanels = async function settingsPanelsWithPreferences() {
    if (typeof originalSettingsPanels === 'function') originalSettingsPanels();
    const panels = document.getElementById('panels');
    if (!panels) return;

    const currentLang = currentLanguage();
    const currentThemeValue = currentTheme();
    let runtime = null;
    try {
      const response = await fetch('/api/runtime');
      if (response.ok) runtime = await response.json();
    } catch (_) {}

    const zh = currentLang === 'zh';
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
            ? (zh ? `已连接 ${account}。当前 REST API 额度：${quota}。` : `Connected ${account}. Current REST API quota: ${quota}.`)
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
            <button class="${currentLang === 'zh' ? 'active' : ''}" onclick="setGhostTalentLanguage('zh')">中文</button>
            <button class="${currentLang === 'en' ? 'active' : ''}" onclick="setGhostTalentLanguage('en')">English</button>
          </div>
        </section>
        <section class="preference-group">
          <h3>${zh ? '外观' : 'Appearance'}</h3>
          <p>${zh ? '选择浅色、深色或跟随系统。' : 'Choose light, dark, or follow your system setting.'}</p>
          <div class="preference-actions">
            <button class="${currentThemeValue === 'light' ? 'active' : ''}" onclick="setGhostTalentTheme('light')">${zh ? '浅色' : 'Light'}</button>
            <button class="${currentThemeValue === 'dark' ? 'active' : ''}" onclick="setGhostTalentTheme('dark')">${zh ? '深色' : 'Dark'}</button>
            <button class="${currentThemeValue === 'system' ? 'active' : ''}" onclick="setGhostTalentTheme('system')">${zh ? '跟随系统' : 'System'}</button>
          </div>
        </section>
      </div>
    `);
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', observeResults);
  else observeResults();
})();
