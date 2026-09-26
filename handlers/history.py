from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Mock — depois troca por banco
COMPRAS: list[dict] = []
POR_PAGINA = 1


def paginar(itens: list, pagina: int):
    total = max(1, (len(itens) + POR_PAGINA - 1) // POR_PAGINA)
    pagina = max(1, min(pagina, total))
    ini = (pagina - 1) * POR_PAGINA
    return itens[ini:ini + POR_PAGINA], pagina, total


def compra_bloco(c: dict) -> str:
    return (
        "📦 <b>Compras:</b> 1\n"
        f"⏰ Data da compra: {c['data']}\n"
        f"📆 Vencimento: {c['venc']}\n"
        f"💰 Valor: R$ {c['valor']:.2f}\n"
        f"🎫 ID da compra: <code>{c['id']}</code>\n"
        f"⚜️ Serviço: {c['servico']}\n"
        f"📧 Email: {c.get('email', 'N/A')}\n"
        f"🔐 Senha: {c.get('senha', 'N/A')}\n"
        "📃 Nota: Use o link abaixo para ativar:"
    )


def vazio_text() -> str:
    return (
        "Você não tem compras no bot.\n"
        "Quando comprar alguma conta, as informações dela ficarão exibidas aqui."
    )


def vazio_ativas_text() -> str:
    return "Você não tem compras ativas (não vencidas) no bot."


def kb_vazio():
    kb = InlineKeyboardBuilder()
    kb.button(text="🟢 Apenas Ativas", callback_data="hist:ativas")
    kb.adjust(1)
    return kb.as_markup()


def kb_vazio_ativas():
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Ver Todas", callback_data="hist:todas")
    kb.adjust(1)
    return kb.as_markup()


def kb_lista(pagina: int, total: int, ativas: bool = False):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 CLIQUE AQUI PARA ATIVAR", url="https://example.com/ativar")
    nav = []
    if pagina < total:
        nav.append(("⏩ Avançar >>", f"hist:page:{pagina + 1}:{'1' if ativas else '0'}"))
    if pagina > 1:
        nav.append(("⏪ Voltar <<", f"hist:page:{pagina - 1}:{'1' if ativas else '0'}"))
    for txt, data in nav:
        kb.button(text=txt, callback_data=data)
    if ativas:
        kb.button(text="📋 Ver Todas", callback_data="hist:todas")
    else:
        kb.button(text="🟢 Apenas Ativas", callback_data="hist:ativas")
    kb.button(text="⬅️ VOLTAR", callback_data="menu:perfil")
    kb.adjust(1, 2, 1, 1)
    return kb.as_markup()


@router.callback_query(F.data == "perfil:historico")
async def abrir_historico(cb: CallbackQuery):
    if not COMPRAS:
        await cb.message.edit_text(vazio_text(), reply_markup=kb_vazio())
        await cb.answer()
        return
    itens, pagina, total = paginar(COMPRAS, 1)
    texto = "\n\n".join(compra_bloco(c) for c in itens)
    texto += f"\n\n📄 {pagina}/{total}"
    await cb.message.edit_text(texto, reply_markup=kb_lista(pagina, total))
    await cb.answer()


@router.callback_query(F.data == "hist:ativas")
async def apenas_ativas(cb: CallbackQuery):
    ativas = [c for c in COMPRAS if c.get("ativa", True)]
    if not ativas:
        await cb.message.edit_text(vazio_ativas_text(), reply_markup=kb_vazio_ativas())
        await cb.answer()
        return
    itens, pagina, total = paginar(ativas, 1)
    texto = "\n\n".join(compra_bloco(c) for c in itens)
    texto += f"\n\n📄 {pagina}/{total}"
    await cb.message.edit_text(texto, reply_markup=kb_lista(pagina, total, ativas=True))
    await cb.answer()


@router.callback_query(F.data == "hist:todas")
async def ver_todas(cb: CallbackQuery):
    if not COMPRAS:
        await cb.message.edit_text(vazio_text(), reply_markup=kb_vazio())
        await cb.answer()
        return
    itens, pagina, total = paginar(COMPRAS, 1)
    texto = "\n\n".join(compra_bloco(c) for c in itens)
    texto += f"\n\n📄 {pagina}/{total}"
    await cb.message.edit_text(texto, reply_markup=kb_lista(pagina, total))
    await cb.answer()


@router.callback_query(F.data.startswith("hist:page:"))
async def trocar_pagina(cb: CallbackQuery):
    _, _, pag, ativ = cb.data.split(":")
    pagina = int(pag)
    ativas = ativ == "1"
    lista = [c for c in COMPRAS if c.get("ativa", True)] if ativas else COMPRAS
    if not lista:
        await cb.message.edit_text(vazio_text(), reply_markup=kb_vazio())
        await cb.answer()
        return
    itens, pagina, total = paginar(lista, pagina)
    texto = "\n\n".join(compra_bloco(c) for c in itens)
    texto += f"\n\n📄 {pagina}/{total}"
    await cb.message.edit_text(texto, reply_markup=kb_lista(pagina, total, ativas=ativas))
    await cb.answer()
