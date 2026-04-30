
function renderScenarioChart(series){
  const canvas = document.getElementById('scenarioCanvas');
  if(!canvas || !series) return;
  Atlas.lastScenarioSeries = series;
  const ctx = canvas.getContext('2d');
  const W = canvas.width = canvas.parentElement.clientWidth - 32;
  const H = canvas.height = 240;
  ctx.clearRect(0,0,W,H);
  const colors = {'Conservador':'#84CC16','Moderado':'#F59E0B','Sofisticado':'#2563EB'};
  const all = Object.values(series).flat();
  if(!all.length) return;
  const min = Math.min(...all) * 0.95;
  const max = Math.max(...all) * 1.05;
  const keys = Object.keys(series);
  const count = series[keys[0]].length;
  ctx.strokeStyle = '#dbe5f0'; ctx.lineWidth = 1;
  for(let i=0;i<5;i++){
    const y = 20 + i*((H-40)/4);
    ctx.beginPath(); ctx.moveTo(40,y); ctx.lineTo(W-10,y); ctx.stroke();
  }
  keys.forEach(name => {
    ctx.beginPath();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = colors[name] || '#0f4c81';
    series[name].forEach((val, idx) => {
      const x = 40 + idx*((W-60)/(count-1));
      const y = H-20 - ((val-min)/(max-min || 1))*(H-40);
      if(idx===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    });
    ctx.stroke();
  });
}
window.addEventListener('resize', () => {
  if(Atlas.lastScenarioSeries) renderScenarioChart(Atlas.lastScenarioSeries);
});
