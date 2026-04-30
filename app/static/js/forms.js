
function formatCurrencyValue(num){
  return new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(Number(num || 0));
}
function parseCurrency(value){
  return Number(String(value || '0').replace(/[^\d,-]/g,'').replace(/\./g,'').replace(',','.')) || 0;
}
function parsePercent(value){
  const num = Number(String(value ?? '0').replace(',', '.')) || 0;
  return num / 100;
}
function bindCurrencyMasks(){
  document.querySelectorAll('.currency').forEach(input => {
    if(input.dataset.bound) return;
    input.dataset.bound = '1';
    input.addEventListener('input', () => {
      const digits = input.value.replace(/\D/g,'');
      input.value = formatCurrencyValue(Number(digits || 0)/100);
      updateSavingsCapacity();
      updatePortfolioPreview();
    });
    if(!input.value) input.value = 'R$ 0,00';
  });
}
function calcAgeFromBirth(dateString){
  if(!dateString) return 0;
  const birth = new Date(dateString + 'T00:00:00');
  if(isNaN(birth.getTime())) return 0;
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if(m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return Math.max(age,0);
}
function updateAgesAndRetirement(){
  const age1 = calcAgeFromBirth(document.getElementById('birth1')?.value);
  if(age1) document.getElementById('age').value = age1;
  const age2 = calcAgeFromBirth(document.getElementById('birth2')?.value);
  if(age2) document.getElementById('partner_age').value = age2;
  const targetAge = Number(document.getElementById('target_age')?.value || 60);
  document.getElementById('retirement_years').value = Math.max(100-targetAge,0);
}
function sumSelectedValues(selector){
  let total = 0;
  document.querySelectorAll(selector).forEach(inp => {
    const card = inp.closest('.toggle-card');
    if(card && card.classList.contains('active')) total += parseCurrency(inp.value);
  });
  return total;
}
function updateSavingsCapacity(){
  const meetingType = document.getElementById('meetingType');
  const incomeMode = document.getElementById('incomeMode');
  const partnerIncome = (meetingType?.value === 'couple' && incomeMode?.value === 'family') ? parseCurrency(document.getElementById('partner_income')?.value) : 0;
  const totalIncome = parseCurrency(document.getElementById('monthly_income')?.value) + partnerIncome + sumSelectedValues('.income-value');
  const totalExpenses = sumSelectedValues('.expense-value');
  const incomeOut = document.getElementById('calculated_total_income');
  const expenseOut = document.getElementById('calculated_total_expenses');
  const contribution = document.getElementById('monthly_contribution');
  if(incomeOut) incomeOut.value = formatCurrencyValue(totalIncome);
  if(expenseOut) expenseOut.value = formatCurrencyValue(totalExpenses);
  if(contribution && !contribution.dataset.touched){
    contribution.value = formatCurrencyValue(Math.max(totalIncome-totalExpenses,0));
  }
}
function createToggleCard({title, desc, field, cssClass, label='Valor', dataAttr='moneyField'}){
  const card = document.createElement('div');
  card.className = `toggle-card ${cssClass || ''}`;
  card.innerHTML = `<div class="toggle-top"><input type="checkbox"><div><div class="toggle-title">${title}</div><div class="toggle-desc">${desc}</div></div></div>
  <div class="toggle-fields"><div class="field"><label>${label}</label><input class="currency ${cssClass || ''}-value" data-${dataAttr}="${field}" value="R$ 0,00"></div></div>`;
  return card;
}
function buildDynamicCards(){
  const assetDefs = [
    ['real_estate_assets','Imóveis','Residencial, comercial, praia, terreno e patrimônio familiar.'],
    ['vehicles_assets','Veículos','Carros, motos e bens móveis de alto valor.'],
    ['cash_reserves','Caixa / liquidez','Conta, poupança e curto prazo.'],
    ['invested_assets','Investimentos financeiros','Renda fixa, ações, FIIs, ETFs e demais ativos financeiros.'],
    ['international_assets','Internacional','Conta offshore, ETFs globais, BDRs e ativos em moeda forte.'],
    ['previdence_assets','Previdência','Saldo de previdência já acumulado.'],
    ['insurance_reserve_assets','Seguros resgatáveis','Produtos com reserva financeira.'],
    ['other_assets','Outros ativos','Joias, obras, crédito a receber, negócios e participações especiais.']
  ];
  const assetCards = document.getElementById('assetCards');
  if(assetCards && !assetCards.dataset.ready){
    assetCards.dataset.ready = '1';
    assetDefs.forEach(([field,title,desc]) => assetCards.appendChild(createToggleCard({field,title,desc,cssClass:'asset',dataAttr:'moneyField'})));
  }

  const portfolioDefs = [
    ['cash','Caixa / Liquidez','Conta, liquidez diária, reserva e caixa tático.'],
    ['fixed_income','Renda Fixa','CDB, Tesouro, crédito privado, pós, pré e inflação.'],
    ['equities_br','Ações Brasil','Ações locais, fundos de ações e exposição direcional Brasil.'],
    ['equities_global','Ações Exterior','ETFs internacionais, BDRs e ativos globais.'],
    ['fiis','Fundos Imobiliários','FIIs e fundos listados imobiliários.'],
    ['alternatives','Alternativos','Ouro, cripto, fundos alternativos ou estratégias especiais.'],
    ['pension','Previdência','Saldo financeiro alocado em previdência.'],
    ['others','Outros','Ativos financeiros não classificados nas demais classes.']
  ];
  const portfolioCards = document.getElementById('portfolioCards');
  if(portfolioCards && !portfolioCards.dataset.ready){
    portfolioCards.dataset.ready = '1';
    portfolioDefs.forEach(([field,title,desc]) => portfolioCards.appendChild(createToggleCard({field,title,desc,cssClass:'portfolio',dataAttr:'portfolioField', label:'Valor investido'})));
  }

  const incomeDefs = [['salario','Salário'],['prolabore','Pró-labore'],['dividendos','Dividendos'],['aluguel','Aluguel'],['renda_passiva','Renda passiva'],['outras','Outras receitas']];
  const incomeCards = document.getElementById('incomeCards');
  if(incomeCards && !incomeCards.dataset.ready){
    incomeCards.dataset.ready = '1';
    incomeDefs.forEach(([id,title]) => incomeCards.appendChild(createToggleCard({field:id,title,desc:'Fonte recorrente considerada até a idade de parada.',cssClass:'income',dataAttr:'incomeField',label:'Valor mensal'})));
  }

  const expenseDefs = [['essenciais','Essenciais'],['estilo_vida','Estilo de vida'],['saude','Saúde'],['educacao','Educação'],['moradia','Moradia'],['viagens','Viagens'],['dependentes','Dependentes'],['outras_despesas','Outras despesas']];
  const expenseCards = document.getElementById('expenseCards');
  if(expenseCards && !expenseCards.dataset.ready){
    expenseCards.dataset.ready = '1';
    expenseDefs.forEach(([id,title]) => expenseCards.appendChild(createToggleCard({field:id,title,desc:'Categoria de gasto para compor o custo de vida.',cssClass:'expense',dataAttr:'expenseField',label:'Valor mensal'})));
  }

  bindToggleCards();
  bindCurrencyMasks();
}
function bindToggleCards(){
  document.querySelectorAll('.toggle-card').forEach(card => {
    const checkbox = card.querySelector('input[type="checkbox"]');
    if(!checkbox || checkbox.dataset.bound) return;
    checkbox.dataset.bound = '1';
    checkbox.addEventListener('change', () => {
      card.classList.toggle('active', checkbox.checked);
      updateSavingsCapacity();
      updatePortfolioPreview();
    });
  });
}
function getAssetMap(){
  const assetMap = {};
  document.querySelectorAll('[data-moneyfield]').forEach(inp => {
    const card = inp.closest('.toggle-card');
    assetMap[inp.getAttribute('data-moneyfield')] = card && card.classList.contains('active') ? parseCurrency(inp.value) : 0;
  });
  return assetMap;

}
function getCurrentPortfolioPayload(){
  const payload = {
    cash:0, fixed_income:0, equities_br:0, equities_global:0, fiis:0, alternatives:0, pension:0, others:0,
    perceived_profile: document.getElementById('portfolio_perceived_profile')?.value || 'nao_sei',
    notes: document.getElementById('portfolio_notes')?.value || ''
  };
  document.querySelectorAll('[data-portfolio-field]').forEach(inp => {
    const card = inp.closest('.toggle-card');
    payload[inp.dataset.portfolioField] = card && card.classList.contains('active') ? parseCurrency(inp.value) : 0;
  });
  return payload;
}
function updatePortfolioPreview(){
  const p = getCurrentPortfolioPayload();
  const labels = {cash:'Caixa',fixed_income:'Renda Fixa',equities_br:'Ações BR',equities_global:'Exterior',fiis:'FIIs',alternatives:'Alternativos',pension:'Previdência',others:'Outros'};
  const entries = Object.entries(p).filter(([k,v]) => typeof v === 'number');
  const total = entries.reduce((a,[,v])=>a+Math.max(v,0),0);
  const filled = entries.filter(([,v])=>v>0).length;
  const maxEntry = entries.reduce((best,cur)=>cur[1]>best[1]?cur:best,['',0]);
  const totalEl = document.getElementById('portfolioTotalPreview');
  const classesEl = document.getElementById('portfolioClassesPreview');
  const concEl = document.getElementById('portfolioConcentrationPreview');
  if(totalEl) totalEl.textContent = formatCurrencyValue(total);
  if(classesEl) classesEl.textContent = String(filled);
  if(concEl) concEl.textContent = total>0 ? `${labels[maxEntry[0]] || maxEntry[0]} (${((maxEntry[1]/total)*100).toFixed(0)}%)` : '-';
}
function buildPayload(){
  const meetingType = document.getElementById('meetingType');
  const incomeMode = document.getElementById('incomeMode');
  const totalIncome = parseCurrency(document.getElementById('monthly_income').value)
    + (meetingType.value === 'couple' && incomeMode.value === 'family' ? parseCurrency(document.getElementById('partner_income').value) : 0)
    + sumSelectedValues('.income-value');
  const totalExpenses = sumSelectedValues('.expense-value');
  const assetMap = getAssetMap();

  const goals = Array.from(document.querySelectorAll('.goal-row')).map(row => ({
    name: row.querySelector('.goal-name').value || 'Objetivo',
    target_amount: parseCurrency(row.querySelector('.goal-amount').value),
    target_year: Number(row.querySelector('.goal-year').value || new Date().getFullYear())
  }));
  const life_events = Array.from(document.querySelectorAll('.event-row')).map(row => ({
    title: row.querySelector('.event-title').value || 'Evento',
    impact_amount: parseCurrency(row.querySelector('.event-amount').value),
    year: Number(row.querySelector('.event-year').value || new Date().getFullYear()),
    recurring: row.querySelector('.event-recurring').checked
  }));

  return {
    client_name: document.getElementById('client_name').value || 'Cliente',
    age: Number(document.getElementById('age').value || 35),
    dependents: document.getElementById('dependentsList').children.length,
    monthly_income: totalIncome,
    monthly_expenses: totalExpenses,
    monthly_contribution: parseCurrency(document.getElementById('monthly_contribution').value),
    invested_assets: Number(assetMap.invested_assets || 0),
    real_estate_assets: Number(assetMap.real_estate_assets || 0),
    cash_reserves: Number(assetMap.cash_reserves || 0),
    company_equity: 0,
    vehicles_assets: Number(assetMap.vehicles_assets || 0),
    previdence_assets: Number(assetMap.previdence_assets || 0),
    insurance_reserve_assets: Number(assetMap.insurance_reserve_assets || 0),
    international_assets: Number(assetMap.international_assets || 0),
    other_assets: Number(assetMap.other_assets || 0),
    target_age: Number(document.getElementById('target_age').value || 60),
    desired_monthly_income_future: parseCurrency(document.getElementById('desired_monthly_income_future').value),
    retirement_mode: document.getElementById('retirement_mode').value,
    tax_regime: document.getElementById('tax_regime').value,
    has_life_insurance: document.querySelector('input[name="hasInsurance"]:checked')?.value || 'nao',
    has_emergency_reserve: document.querySelector('input[name="emergencyReserve"]:checked')?.value || 'nao',
    has_pension: document.querySelector('input[name="hasPension"]:checked')?.value || 'nao',
    goals,
    life_events,
    assumptions:{
      simulation_years:Number(document.getElementById('simulation_years').value || 40),
      scenario_short_years:Number(document.getElementById('scenario_short_years').value || 20),
      selic_structural:parsePercent(document.getElementById('selic_structural').value || 5.5),
      selic_band_up:parsePercent(document.getElementById('selic_band_up').value || 2),
      selic_band_down:parsePercent(document.getElementById('selic_band_down').value || 1),
      inflation_assumption:parsePercent(document.getElementById('inflation_assumption').value || 5),
      retirement_years:Number(document.getElementById('retirement_years').value || 40),
      retirement_return_rate:parsePercent(document.getElementById('retirement_return_rate').value || 8),
      succession_cost_rate:parsePercent(document.getElementById('succession_cost_rate').value || 20),
      family_protection_years:Number(document.getElementById('family_protection_years').value || 10),
      income_multiple:Number(document.getElementById('income_multiple').value || 10),
      cdi_return:parsePercent(document.getElementById('cdi_return').value || 10.83),
      gold_return:parsePercent(document.getElementById('gold_return').value || 59.64),
      ntnb_return:parsePercent(document.getElementById('ntnb_return').value || -12.45),
      ntnf_return:parsePercent(document.getElementById('ntnf_return').value || -13.29),
      ibovespa_return:parsePercent(document.getElementById('ibovespa_return').value || -10.38),
      sp500_brl_return:parsePercent(document.getElementById('sp500_brl_return').value || 58.26),
      fiis_return:parsePercent(document.getElementById('fiis_return').value || -5.89),
      sophisticated_volatility:parsePercent(document.getElementById('sophisticated_volatility').value || 16)
    },
    comparison:{},
    existing_insurance:{
      provider:document.getElementById('insurance_provider')?.value || '',
      product_type:document.getElementById('insurance_product_type')?.value || '',
      coverage_amount:parseCurrency(document.getElementById('insurance_coverage_amount')?.value),
      death_coverage:parseCurrency(document.getElementById('insurance_death_coverage')?.value),
      disability_coverage:parseCurrency(document.getElementById('insurance_disability_coverage')?.value),
      serious_illness_coverage:parseCurrency(document.getElementById('insurance_serious_illness')?.value),
      dit_monthly:parseCurrency(document.getElementById('insurance_dit_monthly')?.value),
      monthly_premium:parseCurrency(document.getElementById('insurance_monthly_premium')?.value)
    },
    existing_pension:{
      provider:document.getElementById('pension_provider')?.value || '',
      plan_type:document.getElementById('pension_plan_type')?.value || 'nenhum',
      balance:parseCurrency(document.getElementById('pension_balance')?.value),
      annual_contribution:parseCurrency(document.getElementById('pension_annual_contribution')?.value),
      taxation_table:document.getElementById('pension_taxation_table')?.value || 'nenhuma'
    },
    current_portfolio:getCurrentPortfolioPayload(),
    advisor_notes:''
  };
}
