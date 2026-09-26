from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

RECARGA_MIN = 4.00
BONUS_PCT   = 10
BONUS_MIN   = 10.00

_esperando: dict[int, bool] = {}


def recarga_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="💠 PIX RÁPIDO", callback_data="rec:pix")
    kb.button(text="⬅️ VOLTAR",     callback_data="menu:home")
    kb.adjust(1, 1)
    return kb.as_markup()


def pix_pronto_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Copiar PIX",             callback_data="rec:copy")
    kb.button(text="⏰ AGUARDANDO PAGAMENTO",    callback_data="rec:waiting")
    kb.adjust(1, 1)
    return kb.as_markup()


def pos_recarga_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Comprar",     callback_data="menu:comprar")
    kb.button(text="🛒 Ver Produto", callback_data="menu:comprar")
    kb.adjust(2)
    return kb.as_markup()


@router.callback_query(F.data == "menu:recarregar")
async def abrir_recarga(cb: CallbackQuery):
    await cb.message.edit_text(
        "💠 Opte por PIX Rápido para que seu saldo seja creditado imediatamente.\n"
        "💰 Selecione uma opção para recarregar:",
        reply_markup=recarga_menu_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "rec:pix")
async def pix_rapido(cb: CallbackQuery):
    _esperando[cb.from_user.id] = True
    await cb.message.edit_text(
        "ℹ️ Informe o valor que deseja recarregar:\n"
        f"🔻 Recarga mínima: R$ {RECARGA_MIN:.2f}\n"
        "⚠️ Por favor, envie o valor que deseja recarregar agora.\n"
        "Ao realizar um depósito você declara ter lido e estar de acordo com nossos /termos\n"
        f"🎁 Bônus de recarga: {BONUS_PCT}%\n"
        f"❗ Recarga mínima para ganhar o bônus: R$ {BONUS_MIN:.2f}",
        reply_markup=ForceReply(selective=True),
    )
    await cb.answer()


@router.message(F.text)
async def receber_valor(message: Message):
    user_id = message.from_user.id
    if not _esperando.get(user_id):
        return

    txt = message.text.replace(",", ".").strip()
    try:
        valor = float(txt)
    except ValueError:
        await message.reply(
            "❌ Valor inválido. Envie apenas números.\n"
            f"🔻 Recarga mínima: R$ {RECARGA_MIN:.2f}",
            reply_markup=ForceReply(selective=True),
        )
        return

    if valor < RECARGA_MIN:
        await message.reply(
            f"❌ Valor mínimo é R$ {RECARGA_MIN:.2f}.\n"
            "Envie o valor novamente.",
            reply_markup=ForceReply(selective=True),
        )
        return

    _esperando.pop(user_id, None)

    bonus = valor * BONUS_PCT / 100 if valor >= BONUS_MIN else 0.0
    saldo_atual = 0.0  # TODO: banco
    saldo_pos   = saldo_atual + valor + bonus
    recarga_id  = f"REC{user_id}{int(valor * 100)}"

    msg = await message.answer("⏳ Gerando pagamento...")

    await msg.edit_text(
        "💠 <b>PIX Rápido gerado</b>\n\n"
        f"💵 Valor: R$ {valor:.2f}\n"
        f"🎫 ID da recarga: <code>{recarga_id}</code>\n"
        f"💰 Saldo Atual: R$ {saldo_atual:.2f}\n"
        f"🎁 Bônus à receber: R$ {bonus:.2f}\n"
        f"💸 Saldo após o pagamento: R$ {saldo_pos:.2f}\n\n"
        "(QR Code do PIX aparece aqui)",
        reply_markup=pix_pronto_kb(),
    )


@router.callback_query(F.data == "rec:copy")
async def copiar_pix(cb: CallbackQuery):
    await cb.answer("PIX copiado!", show_alert=False)


@router.callback_query(F.data == "rec:waiting")
async def aguardando(cb: CallbackQuery):
    # TODO: checar pagamento real
    pago = False
    if not pago:
        await cb.message.edit_text(
            "Nosso sistema viu que você não realizou o pagamento."
        )
        await cb.answer()
        return

    await cb.message.edit_text(
        "✅ <b>Recarga realizada com sucesso!</b>",
        reply_markup=pos_recarga_kb(),
    )
    await cb.answer()
