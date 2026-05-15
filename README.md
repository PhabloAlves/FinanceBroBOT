# FinanceBro

<img width="640" height="640" alt="image" src="https://github.com/user-attachments/assets/96fde878-88e1-4e07-84eb-56954c32a65f" />

Bot do Telegram para controle financeiro pessoal. Envie uma mensagem descrevendo um gasto ou receita e o bot extrai os dados automaticamente com IA e salva.

## Acesse o Bot

O bot está disponível no Telegram: [@SchokFinanceBot](https://t.me/SchokFinanceBot)

## Como funciona

1. Você envia uma mensagem pro bot: _"gastei 50 reais no mercado no pix"_
2. A IA (Gemini) identifica categoria, tipo, valor e forma de pagamento
3. Os dados são salvos automaticamente no banco de dados
4. Todo dia às 23:59 você recebe um resumo do dia e do mês pelo Telegram

## Tecnologias

- **FastAPI** — servidor web e webhook
- **Google Gemini** — extração de dados das mensagens
- **Supabase** — banco de dados para armazenamento dos lançamentos
- **APScheduler** — agendamento do resumo diário
- **Render** — hospedagem da API em produção

## Infraestrutura

- API: hospedada no [Render](https://render.com)
- Banco de dados: gerenciado pelo [Supabase](https://supabase.com)
