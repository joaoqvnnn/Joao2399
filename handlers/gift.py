from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# user_id -> True enquanto espera o código
_esperando: dict[int, bool] = {}

# Mock — depois troca por banco
GIFTS_VALIDOS = {
    "ABC123XYZ456": {"tipo": "saldo",   "valor": 10.0, "produto": None},
    "PRODUTOCANVA": {"tipo": "produto", "valor": 0.0,  "produto": "canva"},
}


def gift_pedir_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Cancelar", callback_data="gift:cancelar")
    kb.adjust(1)
    return kb.as_markup()


def gift_ok_kb(produto_id: str | None):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Usar", callback_data=f"gift:usar:{produto_id or 'saldo'}")
    kb.adjust(1)
    return kb.as_markup()


@router.callback_query(F.data == "perfil:gift")
async def abrir_gift(cb: CallbackQuery):
    _esperando[cb.from_user.id] = True
    await cb.message.edit_text(
        "🎁 <b>RESGATAR GIFT CARD</b>\n"
        "Digite o código do seu gift card abaixo:\n"
        "Exemplo: ABC123XYZ456",
        reply_markup=gift_pedir_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "gift:cancelar")
async def cancelar_gift(cb: CallbackQuery):
    _esperando.pop(cb.from_user.id, None)
    from handlers.profile import perfil_text, perfil_kb
    await cb.message.edit_text(
        perfil_text(cb.from_user, 0.0, "—"),
        reply_markup=perfil_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("gift:usar:"))
async def usar_gift(cb: CallbackQuery):
    destino = cb.data.split(":", 2)[2]
    if destino == "saldo":
        await cb.message.edit_text(
            "🎁 Gift Card resgatado! Saldo creditado na sua carteira."
        )
    else:
        from handlers.product import get_produto, produto_text, produto_kb
        p = get_produto(destino)
        if not p:
            await cb.answer("Produto do gift não encontrado.", show_alert=True)
            return
        await cb.message.edit_text(
            produto_text(p, 0.0),
            reply_markup=produto_kb(destino),
        )
    await cb.answer()


@router.message(F.text)
async def receber_codigo(message: Message):
    user_id = message.from_user.id
    if not _esperando.get(user_id):
        return

    codigo = (message.text or "").strip().upper()
    _esperando.pop(user_id, None)

    gift = GIFTS_VALIDOS.get(codigo)
    if not gift:
        sent = await message.answer("Gift não encontrado.")
        # edita a mensagem? Aqui é mensagem nova do user — só respondemos
        return

    destino = gift.get("produto")
    texto = (
        "🎁 <b>Gift Card resgatado!</b>\n\n"
        + (
            f"Você ganhou R$ {gift['valor']:.2f} em saldo."
            if gift["tipo"] == "saldo"
            else "Você ganhou acesso a um produto."
        )
    )
    await message.answer(texto, reply_markup=gift_ok_kb(destino))
