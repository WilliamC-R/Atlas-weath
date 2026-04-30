# Atlas Wealth

Versão modular com front, backend e PDF integrados.

## Como rodar localmente no Windows

```powershell
.\start.bat
```

Ou manualmente:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Abra:

```text
http://127.0.0.1:8000
```

## Estrutura do front

- `app/templates/base.html`: layout principal
- `app/templates/index.html`: shell que inclui as abas
- `app/templates/partials/`: uma aba por arquivo
- `app/static/css/`: CSS separado por camada
- `app/static/js/`: JS separado por responsabilidade

## Abas

1. Pessoas e família
2. Patrimônio
3. Carteira atual
4. Receitas
5. Custos e poupança
6. Objetivos
7. Proteção e previdência
8. Resumo do plano
9. Cenários

## Funcionalidades

- Patrimônio completo com blocos selecionáveis
- Carteira atual com diagnóstico, risco, perfil e nota
- Receitas sem datas manuais
- Capacidade de poupança calculada e editável
- Proteção e previdência com sim/não e recomendação automática
- Cenários conservador, moderado e sofisticado
- PDF com diagnóstico, carteira, proteção, cenários e recomendações
