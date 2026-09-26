from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# user_id -> True enquanto espera número
_esperando: dict[int, bool] = {}


def alterar_kb(whatsapp: str = "—"):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"📱 WhatsApp: {whatsapp}", callback_data="alt:whatsapp")
    kb.button(text="⬅️ Voltar",                  callback_data="menu:perfil")
    kb.adjust(1, 1)
    return kb.as_markup()


def voltar_perfil_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Voltar", callback_data="menu:perfil")
    return kb.as_markup()


@router.callback_query(F.data == "perfil:alterar")
async def abrir_alterar(cb: CallbackQuery):
    # TODO: puxar whatsapp do banco
    await cb.message.edit_text(
        "✏️ <b>Alterar Dados</b>\n"
        "Selecione o dado que deseja alterar:",
        reply_markup=alterar_kb("—"),
    )
    await cb.answer()


@router.callback_query(F.data == "alt:whatsapp")
async def pedir_whatsapp(cb: CallbackQuery):
    _esperando[cb.from_user.id] = True
    await cb.message.edit_text(
        "📱 Envie seu número de WhatsApp\n"
        "Formato: DDD + Número (apenas números)\n"
        "Exemplo: 11999998888\n"
        '⚠️ Envie "remover" para remover o número cadastrado.',
        reply_markup=ForceReply(selective=True),
    )
    await cb.answer()


@router.message(F.text)
async def receber_whatsapp(message: Message):
    user_id = message.from_user.id
    if not _esperando.get(user_id):
        return

    if message.text.startswith("/start"):
        await message.reply(
            "❌ Número inválido!\n"
            "Formato: DDD + Número (apenas números)\n"
            "Exemplo: 11999998888",
            reply_markup=ForceReply(selective=True),
        )
        return

    _esperando.pop(user_id, None)
    texto = message.text.strip().lower()

    if texto == "remover":
        # TODO: remover do banco
        await message.answer(
            "✅ WhatsApp removido com sucesso.",
            reply_markup=voltar_perfil_kb(),
        )
        return

    if not texto.isdigit() or len(texto) < 10:
        _esperando[user_id] = True
        await message.reply(
            "❌ Número inválido!\n"
            "Formato: DDD + Número (apenas números)\n"
            "Exemplo: 11999998888",
            reply_markup=ForceReply(selective=True),
        )
        return

    # TODO: salvar no banco
    await message.answer(
        f"✅ WhatsApp atualizado com sucesso!\n📱 {texto}",
        reply_markup=voltar_perfil_kb(),
    )
