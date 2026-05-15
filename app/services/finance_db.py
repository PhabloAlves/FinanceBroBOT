from sqlalchemy import select, delete, exists
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db.database import AsyncSessionLocal
from app.db.models import User, MonthlyIncome, Transaction
from datetime import datetime
import calendar


async def user_exists(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(exists().where(User.telegram_user_id == user_id)))
        return result.scalar()


async def create_user(user_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            pg_insert(User).values(telegram_user_id=user_id).on_conflict_do_nothing()
        )
        await session.commit()


async def save_transaction(data: dict, user_id: int):
    async with AsyncSessionLocal() as session:
        if not await user_exists(user_id):
            await create_user(user_id)
        session.add(Transaction(
            telegram_user_id=user_id,
            data=data.get("data"),
            categoria=data.get("categoria"),
            tipo=data.get("tipo"),
            descricao=data.get("descricao"),
            valor=data.get("valor"),
            forma_pagamento=data.get("forma_pagamento"),
        ))
        await session.commit()
    return {"ok": True}


async def set_renda(monthly_income, user_id: int):
    mes_atual = datetime.now().strftime("%m/%Y")
    async with AsyncSessionLocal() as session:
        if not await user_exists(user_id):
            await create_user(user_id)
        await session.execute(
            pg_insert(MonthlyIncome)
            .values(telegram_user_id=user_id, month=mes_atual, amount=float(monthly_income))
            .on_conflict_do_update(
                index_elements=["telegram_user_id", "month"],
                set_={"amount": float(monthly_income)}
            )
        )
        await session.commit()
    return {"ok": True}


async def clear_data(user_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Transaction).where(Transaction.telegram_user_id == user_id))
        await session.execute(delete(MonthlyIncome).where(MonthlyIncome.telegram_user_id == user_id))
        await session.commit()


async def get_resume(user_id: int) -> str:
    mes_atual = datetime.now().strftime("%m/%Y")
    hoje = datetime.now()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MonthlyIncome.amount).where(
                MonthlyIncome.telegram_user_id == user_id,
                MonthlyIncome.month == mes_atual
            )
        )
        renda = float(result.scalar() or 0)

        result = await session.execute(
            select(Transaction).where(
                Transaction.telegram_user_id == user_id,
                Transaction.data.like(f"%/{mes_atual}")
            )
        )
        transacoes = result.scalars().all()

    total_despesas = sum(float(t.valor) for t in transacoes if t.tipo == "despesa")
    total_receitas = sum(float(t.valor) for t in transacoes if t.tipo == "receita")
    saldo_atual = renda + total_receitas - total_despesas

    ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)[1]
    dias_restantes = (hoje.replace(day=ultimo_dia_num) - hoje).days + 1
    sugestao_diaria = saldo_atual / dias_restantes if dias_restantes > 0 else 0
    sugestao_diaria = sugestao_diaria if sugestao_diaria >= 0 else 0

    linhas = [f"📊 Resumo de {mes_atual}\n"]
    linhas.append(f"💰 Renda mensal: R$ {renda:.2f}")
    linhas.append(f"🔴 Total despesas: R$ {total_despesas:.2f}")
    linhas.append(f"🟢 Total receitas: R$ {total_receitas:.2f}")
    linhas.append(f"💵 Saldo atual: R$ {saldo_atual:.2f}")
    linhas.append(f"📆 Dias restantes no mês: {dias_restantes}")
    linhas.append(f"💡 Sugestão por dia: R$ {sugestao_diaria:.2f}\n")

    categorias: dict = {}
    for t in transacoes:
        if t.tipo == "despesa":
            cat = t.categoria or "Outros"
            categorias[cat] = categorias.get(cat, 0) + float(t.valor)

    if categorias:
        linhas.append("🗂 Por categoria:")
        for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            linhas.append(f"  • {cat}: R$ {valor:.2f}")

    return "\n".join(linhas)


async def get_daily_summary(user_id: int) -> str:
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    mes_atual = datetime.now().strftime("%m/%Y")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Transaction).where(
                Transaction.telegram_user_id == user_id,
                Transaction.data == hoje_str
            )
        )
        do_dia = result.scalars().all()

        if not do_dia:
            return f"Nenhum lançamento registrado hoje ({hoje_str})."

        result = await session.execute(
            select(MonthlyIncome.amount).where(
                MonthlyIncome.telegram_user_id == user_id,
                MonthlyIncome.month == mes_atual
            )
        )
        renda = float(result.scalar() or 0)

        result = await session.execute(
            select(Transaction).where(
                Transaction.telegram_user_id == user_id,
                Transaction.data.like(f"%/{mes_atual}")
            )
        )
        do_mes = result.scalars().all()

    total_dia_despesas = sum(float(t.valor) for t in do_dia if t.tipo == "despesa")
    total_dia_receitas = sum(float(t.valor) for t in do_dia if t.tipo == "receita")
    total_mes_despesas = sum(float(t.valor) for t in do_mes if t.tipo == "despesa")
    total_mes_receitas = sum(float(t.valor) for t in do_mes if t.tipo == "receita")
    saldo_atual = renda + total_mes_receitas - total_mes_despesas

    linhas = [f"📅 Resumo do dia {hoje_str}\n"]
    for t in do_dia:
        emoji = "🔴" if t.tipo == "despesa" else "🟢"
        linhas.append(f"{emoji} {t.descricao} | {t.categoria} | R$ {float(t.valor):.2f} | {t.forma_pagamento}")

    linhas.append(f"\n📊 Hoje")
    linhas.append(f"  🔴 Despesas: R$ {total_dia_despesas:.2f}")
    linhas.append(f"  🟢 Receitas: R$ {total_dia_receitas:.2f}")
    linhas.append(f"\n📆 Mês")
    linhas.append(f"  🔴 Despesas: R$ {total_mes_despesas:.2f}")
    linhas.append(f"  🟢 Receitas: R$ {total_mes_receitas:.2f}")
    linhas.append(f"  💵 Saldo atual: R$ {saldo_atual:.2f}")

    return "\n".join(linhas)


async def get_all_users() -> list[int]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.telegram_user_id))
        return result.scalars().all()