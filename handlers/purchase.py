from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.product import get_produto, produto_text, produto_kb

router = Router()


def saldo_insuf_text(saldo: float, preco: float) -> str:
    faltam = preco - saldo
    return (
        "❌ <b>Saldo insuficiente!</b>\n"
        f"💰 Seu saldo: R$ {saldo:.2f}\n"
        f"💵 Valor do produto: R$ {preco:.2f}\n"
        f"📉 Faltam: R$ {faltam:.2f}\n"
        f"💡 Deseja gerar um PIX no valor de R$ {preco:.2f} para completar a compra?"
    )


def saldo_insuf_kb(pid: str, preco: float):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💠 Gerar PIX de R$ {preco:.2f}", callback_data=f"pix:{pid}:{preco:.2f}")
    kb.button(text="❌ Cancelar",                      callback_data=f"prod:{pid}")
    kb.adjust(1, 1)
    return kb.as_markup()


def pix_gerando_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⏰ AGUARDANDO PAGAMENTO", callback_data="pix:waiting")
    return kb.as_markup()


def pix_pronto_text(preco: float, recarga_id: str, saldo: float) -> str:
    return (
        "⏳ <b>Pagamento gerado</b>\n\n"
        f"💵 Valor: R$ {preco:.2f}\n"
        f"🎫 ID da recarga: <code>{recarga_id}</code>\n"
        f"💰 Saldo Atual: R$ {saldo:.2f}\n"
        "⏰ Tempo de expiração: 10 minutos\n\n"
        "(QR Code do PIX aparece aqui)"
    )


def pix_ok_kb(preco: float):
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Copiar PIX", callback_data="pix:copy")
    return kb.as_markup()


@router.callback_query(F.data.startswith("buy:"))
async def comprar(cb: CallbackQuery):
    pid = cb.data.split(":", 1)[1]
    p = get_produto(pid)
    if not p:
        await cb.answer("Produto não encontrado.", show_alert=True)
        return

    saldo = 0.0  # TODO: puxar do banco

    if saldo >= p["preco"]:
        # TODO: módulo de entrega
        await cb.answer("Fluxo de compra direta (módulo de entrega).", show_alert=True)
        return

    await cb.message.edit_text(
        saldo_insuf_text(saldo, p["preco"]),
        reply_markup=saldo_insuf_kb(pid, p["preco"]),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("pix:"))
async def pix_router(cb: CallbackQuery):
    parts = cb.data.split(":")

    # pix:copy
    if len(parts) == 2 and parts[1] == "copy":
        await cb.answer("PIX copiado!", show_alert=False)
        return

    # pix:waiting
    if len(parts) == 2 and parts[1] == "waiting":
        await cb.message.edit_text(
            "Nosso sistema viu que você não realizou o pagamento.",
        )
        await cb.answer()
        return

    # pix:<pid>:<preco>
    if len(parts) == 3:
        pid = parts[1]
        try:
            preco = float(parts[2])
        except ValueError:
            await cb.answer("Valor inválido.", show_alert=True)
            return

        await cb.message.edit_text("⏳ Gerando pagamento...")
        await cb.answer()

        recarga_id = "REC-" + cb.from_user.id.__str__()[-6:]
        await cb.message.edit_text(
            pix_pronto_text(preco, recarga_id, 0.0),
            reply_markup=pix_ok_kb(preco),
        )
        return

    await cb.answer()


@router.callback_query(F.data.startswith("buymulti:"))
async def comprar_mais_de_um(cb: CallbackQuery):
    pid = cb.data.split(":", 1)[1]
    p = get_produto(pid)
    if not p:
        await cb.answer("Produto não encontrado.", show_alert=True)
        return

    await cb.message.edit_text(
        "Quantos logins deseja comprar?\n"
        f"📦 Estoque disponível: {p['estoque']}\n"
        "💡 Digite /cancelar a qualquer momento para sair.",
    )
    await cb.answer()
