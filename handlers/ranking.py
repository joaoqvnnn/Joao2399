from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Mock — depois troca por banco
RANKINGS = {
    "servicos": [
        ("Trabalho", 12), ("João Oliveira", 9), ("T", 7), ("Lucas", 5),
    ],
    "recargas": [
        ("Maria", 20), ("Trabalho", 15), ("Ana", 10), ("João", 6),
    ],
    "compras": [
        ("Trabalho", 30), ("João Oliveira", 22), ("T", 18), ("Lucas", 11),
    ],
    "gift": [
        ("Ana", 5), ("Maria", 3), ("Trabalho", 2), ("T", 1),
    ],
    "saldo": [
        ("Investidor", 500.0), ("Maria", 320.0), ("Trabalho", 180.0), ("T", 95.0),
    ],
}

FILTROS = ["servicos", "recargas", "compras", "gift", "saldo"]
LABELS = {
    "servicos": "Serviços",
    "recargas": "Recargas",
    "compras":  "Compras",
    "gift":     "Gift card",
    "saldo":    "Saldo",
}


def ranking_text(filtro: str) -> str:
    linhas = [f"🏆 <b>Ranking dos usuários que mais compraram (deste mês)</b>"]
    medalhas = ["🥇", "🥈", "🥉"]
    itens = RANKINGS.get(filtro, [])
    for i, (nome, val) in enumerate(itens):
        pos = i + 1
        m = medalhas[i] if i < 3 else f"{pos}º)"
        if filtro == "saldo":
            linhas.append(f"{pos}º) {nome} — R$ {val:.2f} {m if i < 3 else ''}".rstrip())
        else:
            linhas.append(f"{pos}º) {nome} {m if i < 3 else ''}".rstrip())
    if not itens:
        linhas.append("Sem dados no momento.")
    return "\n".join(linhas)


def ranking_kb(filtro_ativo: str):
    kb = InlineKeyboardBuilder()
    for f in FILTROS:
        check = "✅" if f == filtro_ativo else "▫️"
        kb.button(text=f"{check} {LABELS[f]}", callback_data=f"rank:{f}")
    kb.button(text="⬅️ VOLTAR", callback_data="menu:home")
    kb.adjust(1, 1, 1, 1, 1, 1)
    return kb.as_markup()


@router.callback_query(F.data == "menu:top")
async def abrir_ranking(cb: CallbackQuery):
    filtro = "servicos"
    await cb.message.edit_text(
        ranking_text(filtro),
        reply_markup=ranking_kb(filtro),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("rank:"))
async def trocar_filtro(cb: CallbackQuery):
    filtro = cb.data.split(":", 1)[1]
    if filtro not in LABELS:
        await cb.answer()
        return
    await cb.message.edit_text(
        ranking_text(filtro),
        reply_markup=ranking_kb(filtro),
    )
    await cb.answer()
