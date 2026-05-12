# FinanceBro

Bot do Telegram para controle financeiro pessoal. Envie uma mensagem descrevendo um gasto ou receita e o bot extrai os dados automaticamente com IA e salva na sua planilha do Google Sheets.

## Como funciona

1. Você envia uma mensagem pro bot: _"gastei 50 reais no mercado no pix"_
2. A IA (Gemini) identifica categoria, tipo, valor e forma de pagamento
3. Os dados são salvos automaticamente na planilha
4. Todo dia às 23:59 você recebe um resumo do dia e do mês pelo Telegram

## Tecnologias

- **FastAPI** — servidor web e webhook
- **Google Gemini** — extração de dados das mensagens
- **Google Sheets** — armazenamento dos lançamentos
- **APScheduler** — agendamento do resumo diário
- **ngrok** — exposição local para o webhook (desenvolvimento)
