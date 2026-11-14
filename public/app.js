const state = { styles: {}, selected: 'chinese-pentatonic', composition: null };
const $ = (id) => document.getElementById(id);

function makePiano() {
  $('piano').innerHTML = Array.from({length: 18}, (_, i) => `<span class="key ${[1,3,6,8,10,13,15,17].includes(i) ? 'black' : ''}"></span>`).join('');
}
function renderStyles() {
  $('stylePicker').innerHTML = Object.entries(state.styles).map(([id, style]) => `<button class="style-option ${id === state.selected ? 'active' : ''}" data-style="${id}"><strong>${style.name}</strong><small>${style.mode}</small></button>`).join('');
  document.querySelectorAll('.style-option').forEach((button) => button.addEventListener('click', () => { state.selected = button.dataset.style; renderStyles(); const s = state.styles[state.selected]; $('tempo').value = s.tempo; syncInputs(); }));
}
function syncInputs() { $('tempoValue').textContent = $('tempo').value; $('densityValue').textContent = $('density').value; $('barsValue').textContent = $('bars').value; }
function renderComposition(data) {
  state.composition = data;
  $('compositionId').textContent = data.id;
  $('scaleName').textContent = `${data.scale} · ${data.style.mode}`;
  $('sectionSummary').textContent = data.sections.map(s => s.name).join(' · ');
  $('particleCount').textContent = data.visual.particleCount;
  const colors = data.tracks.map(t => t.color);
  const melody = data.tracks.find(t => t.role === 'melody')?.notes || [];
  const maxTime = data.bars * 4;
  $('noteField').innerHTML = melody.map((n, i) => { const left = 10 + n.start / maxTime * 84; const top = 17 + ((n.pitch - 55) % 42) / 42 * 72; const width = Math.max(1.4, n.duration / maxTime * 320); const color = colors[i % colors.length]; return `<span class="note" style="left:${left}%;top:${top}%;width:${width}%;color:${color};background:${color}"></span>`; }).join('');
  $('captions').innerHTML = data.sections.map(s => `<div class="caption"><strong>${s.name} · ${s.startBar}-${s.endBar}小节</strong>${s.caption}</div>`).join('');
  $('tracks').classList.remove('empty');
  $('tracks').innerHTML = data.tracks.map((track, idx) => { const blocks = Array.from({length: Math.min(12, Math.max(4, Math.ceil(data.bars / 4)))}, (_, i) => `<span class="track-block" style="left:${i * (100 / 12)}%;width:${100 / 15}%;color:${track.color};background:${track.color}"></span>`).join(''); return `<div class="track-row"><div class="track-name"><strong>${track.name}</strong><small>${track.instrument}</small></div><div class="track-lane">${blocks}</div><div class="track-count">${track.notes.length} 个事件</div></div>`; }).join('');
  $('trackCount').textContent = `${data.tracks.length} 个声部`;
}
async function compose() {
  const button = $('composeBtn'); button.classList.add('loading'); button.innerHTML = '<span>◌</span> 正在展开声部...';
  try { const response = await fetch('/api/compose', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({prompt: $('prompt').value, style: state.selected, tempo: $('tempo').value, density: Number($('density').value) / 100, bars: $('bars').value})}); if (!response.ok) throw new Error('compose failed'); renderComposition(await response.json()); $('serverStatus').textContent = '本地引擎已生成'; } catch (error) { $('serverStatus').textContent = '引擎连接失败'; console.error(error); } finally { button.classList.remove('loading'); button.innerHTML = '<span>✦</span> 生成我的音乐世界'; }
}
$('tempo').addEventListener('input', syncInputs); $('density').addEventListener('input', syncInputs); $('bars').addEventListener('input', syncInputs); $('composeBtn').addEventListener('click', compose); $('copyPrompt').addEventListener('click', async () => { try { await navigator.clipboard.writeText($('prompt').value); $('serverStatus').textContent = '创作提示已复制'; } catch { $('serverStatus').textContent = '请手动复制创作提示'; } });
makePiano(); syncInputs(); fetch('/api/styles').then(r => r.json()).then(styles => { state.styles = styles; renderStyles(); compose(); }).catch(() => { $('serverStatus').textContent = '请先启动本地引擎'; });
