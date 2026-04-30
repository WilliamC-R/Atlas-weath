
function setText(id, text){
  const el = document.getElementById(id);
  if(el) el.textContent = text;
}
function bindNavigation(){
  const navButtons = document.querySelectorAll('.nav-btn');
  const panels = document.querySelectorAll('.panel');
  navButtons.forEach(btn => btn.addEventListener('click', () => {
    navButtons.forEach(b => b.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('panel-' + btn.dataset.panel).classList.add('active');
  }));
}
function bindConditionalBlocks(){
  const meetingType = document.getElementById('meetingType');
  const partnerSection = document.getElementById('partnerSection');
  meetingType.addEventListener('change', () => partnerSection.classList.toggle('hidden', meetingType.value !== 'couple'));

  document.querySelectorAll('input[name="hasInsurance"]').forEach(r => r.addEventListener('change', () => {
    document.getElementById('insuranceFields').classList.toggle('hidden', document.querySelector('input[name="hasInsurance"]:checked')?.value !== 'sim');
  }));
  document.querySelectorAll('input[name="hasPension"]').forEach(r => r.addEventListener('change', () => {
    document.getElementById('pensionFields').classList.toggle('hidden', document.querySelector('input[name="hasPension"]:checked')?.value !== 'sim');
  }));

  ['birth1','birth2','target_age'].forEach(id => document.getElementById(id)?.addEventListener('change', updateAgesAndRetirement));
  ['monthly_income','partner_income'].forEach(id => document.getElementById(id)?.addEventListener('input', updateSavingsCapacity));
  document.getElementById('incomeMode')?.addEventListener('change', updateSavingsCapacity);
  const contribution = document.getElementById('monthly_contribution');
  contribution?.addEventListener('input', () => contribution.dataset.touched = '1');
}
function bindDynamicButtons(){
  document.getElementById('addDependentBtn')?.addEventListener('click', () => {
    const list = document.getElementById('dependentsList');
    const idx = list.children.length + 1;
    const wrapper = document.createElement('div');
    wrapper.className = 'dependent-item';
    wrapper.innerHTML = `<div style="display:flex;justify-content:space-between;gap:12px;align-items:center"><h5>Dependente ${idx}</h5><button type="button" class="btn btn-ghost remove">Remover</button></div>
    <div class="grid-3"><div class="field"><label>Nome</label><input></div><div class="field"><label>Idade</label><input type="number" value="0"></div><div class="field"><label>Observação</label><input></div></div>`;
    list.appendChild(wrapper);
    wrapper.querySelector('.remove').addEventListener('click', () => wrapper.remove());
  });

  document.getElementById('addGoalBtn')?.addEventListener('click', () => {
    const list = document.getElementById('goalsList');
    const row = document.createElement('div');
    row.className = 'dynamic-item goal-row';
    row.innerHTML = `<div class="grid-4"><div class="field"><label>Objetivo</label><input class="goal-name" placeholder="Aposentadoria, viagem, carro..."></div><div class="field"><label>Valor</label><input class="currency goal-amount" value="R$ 0,00"></div><div class="field"><label>Ano</label><input class="goal-year" type="number" value="${new Date().getFullYear()+5}"></div><div class="field"><label>Ação</label><button type="button" class="btn btn-ghost remove">Remover</button></div></div>`;
    list.appendChild(row); bindCurrencyMasks();
    row.querySelector('.remove').addEventListener('click', () => row.remove());
  });

  document.getElementById('addLifeEventBtn')?.addEventListener('click', () => {
    const list = document.getElementById('lifeEventsList');
    const row = document.createElement('div');
    row.className = 'dynamic-item event-row';
    row.innerHTML = `<div class="grid-4"><div class="field"><label>Evento</label><input class="event-title" placeholder="Faculdade, compra, herança..."></div><div class="field"><label>Impacto</label><input class="currency event-amount" value="R$ 0,00"></div><div class="field"><label>Ano</label><input class="event-year" type="number" value="${new Date().getFullYear()+1}"></div><div class="field"><label>Recorrente?</label><label><input class="event-recurring" type="checkbox"> Sim</label><button type="button" class="btn btn-ghost remove">Remover</button></div></div>`;
    list.appendChild(row); bindCurrencyMasks();
    row.querySelector('.remove').addEventListener('click', () => row.remove());
  });
}
function renderPlan(data){
  Atlas.lastPlan = data;
  setText('outCurrentNetWorth', formatCurrencyValue(data.summary.current_net_worth));
  setText('outFutureValue', formatCurrencyValue(data.summary.future_value));
  setText('outTargetCapital', formatCurrencyValue(data.summary.retirement_target_capital));
  setText('outCapitalGap', formatCurrencyValue(data.summary.capital_gap));
  setText('outProtectionNeeded', formatCurrencyValue(data.summary.protection_capital_needed));
  setText('outCurrentCoverage', formatCurrencyValue(data.summary.current_insurance_coverage));
  setText('outProtectionGap', formatCurrencyValue(data.summary.protection_gap));
  setText('outThermometerStatus', data.summary.thermometer_status);
  document.getElementById('thermoBar').style.width = `${Math.min(data.summary.goal_readiness_percent,100)}%`;
  setText('thermoPercent', `${data.summary.goal_readiness_percent.toFixed(1)}%`);
  setText('thermoRemaining', `${data.summary.remaining_percent.toFixed(1)}% restante`);
  document.getElementById('actionPlanList').innerHTML = data.action_plan.map(item => `<li>${item}</li>`).join('');
  setText('pensionRecommendation', data.summary.pension_recommendation);

  if(data.portfolio_diagnosis){
    setText('outPortfolioTotal', formatCurrencyValue(data.portfolio_diagnosis.total));
    setText('outPortfolioProfile', data.portfolio_diagnosis.identified_profile);
    setText('outPortfolioScore', `${data.portfolio_diagnosis.investor_score.toFixed(0)} / 100`);
    setText('outPortfolioRisk', `${(data.portfolio_diagnosis.risk_score * 100).toFixed(1)}%`);
    document.getElementById('portfolioDiagnosticsList').innerHTML = data.portfolio_diagnosis.diagnostics.map(item => `<li>${item}</li>`).join('');
    document.getElementById('portfolioRecommendationsList').innerHTML = data.portfolio_diagnosis.recommendations.map(item => `<li>${item}</li>`).join('');
    document.getElementById('portfolioComparisonTable').innerHTML = `<thead><tr><th>Classe</th><th style="text-align:right">Atual</th><th style="text-align:right">Referência Atlas</th></tr></thead><tbody>${data.portfolio_diagnosis.comparison_table.map(row => `<tr><td>${row.classe}</td><td style="text-align:right">${(row.atual*100).toFixed(1)}%</td><td style="text-align:right">${(row.referencia_atlas*100).toFixed(1)}%</td></tr>`).join('')}</tbody>`;
  }

  const pdfButton = document.getElementById('pdfButton');
  pdfButton.href = `/api/plans/${data.id}/pdf`;
  pdfButton.classList.remove('hidden');

  const scenarioCards = document.getElementById('scenarioCards');
  scenarioCards.innerHTML = data.scenario_projection.portfolio_cards.map(card => `<div class="scenario-card"><h4>${card.name}</h4><div class="small">${card.level}</div><div style="margin-top:10px;font-weight:700">Horizonte curto: ${formatCurrencyValue(card.value_10y)}</div><div style="font-weight:700">Horizonte principal: ${formatCurrencyValue(card.value_20y)}</div><div class="small" style="margin-top:8px">Retorno médio: ${(card.expected_return*100).toFixed(1)}% | Volatilidade: ${(card.volatility*100).toFixed(1)}%</div></div>`).join('');
  renderScenarioChart(data.scenario_projection.series);

  document.querySelector('[data-panel="resumo"]').click();
}
function bindSubmit(){
  document.getElementById('atlasForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = buildPayload();
    const res = await fetch('/api/plans', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    if(!res.ok){
      const err = await res.json().catch(()=>({detail:'Erro ao gerar plano'}));
      alert(Array.isArray(err.detail) ? err.detail.map(i => i.msg).join('\\n') : (err.detail || 'Erro ao gerar plano'));
      return;
    }
    const data = await res.json();
    renderPlan(data);
  });
}
document.addEventListener('DOMContentLoaded', () => {
  bindNavigation();
  buildDynamicCards();
  bindConditionalBlocks();
  bindDynamicButtons();
  bindSubmit();
  bindCurrencyMasks();
  updateAgesAndRetirement();
  updateSavingsCapacity();
  updatePortfolioPreview();
});
