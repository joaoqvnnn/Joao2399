from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus

from config import CHANNEL_ID, CHANNEL_LINK, SUPORTE_LINK

router = Router()

# user_id -> (chat_id, message_id) da mensagem do gate para editar depois
pending_gate: dict[int, tuple[int, int]] = {}

MEMBRO_OK = (
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
)


async def user_in_channel(bot, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(CHANNEL_ID, user_id)
        return m.status in MEMBRO_OK
    except Exception:
        return False


def gate_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="➡️ ENTRAR NO CANAL", url=CHANNEL_LINK)
    return kb.as_markup()


def welcome_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Comprar Produtos",   callback_data="menu:comprar")
    kb.button(text="🛒 Abrir Loja",         callback_data="menu:loja")
    kb.button(text="👤 Meu Perfil",         callback_data="menu:perfil")
    kb.button(text="💠 Recarregar Saldo",   callback_data="menu:recarregar")
    kb.button(text="👥 Afiliados",          callback_data="menu:afiliados")
    kb.button(text="🏆 Top Compradores",    callback_data="menu:top")
    kb.button(text="📩 Atendimento",        url=SUPORTE_LINK)
    kb.button(text="🤖 Sobre o Bot",        callback_data="menu:sobre")
    kb.button(text="🔎 Pesquisar Serviços", callback_data="menu:pesquisar")
    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()


def welcome_text(user, saldo: float = 0.0) -> str:
    return (
        "📡 <b>Bem-vindo à Larizinha Store!</b>\n"
        "✨ A sua central de streamings com entrega 100% automática.\n"
        "Pagou, recebeu. Sem filas, sem precisar falar com atendente, 24 horas por dia! ⚡\n\n"
        "🛡 <b>Segurança e Suporte:</b>\n"
        "Mais de 12.000 clientes já passaram por aqui.\n"
        "Participe da nossa comunidade e veja as referências\n\n"
        "● <b>Seus Dados:</b>\n"
        f"├ 👤 ID: <code>{user.id}</code>\n"
        f"└ 💰 Saldo Atual: R$ {saldo:.2f}\n\n"
        "👇 <b>COMO COMEÇAR:</b>\n"
        'Clique no botão "🛍 Comprar Produtos" abaixo para ver nosso catálogo e escolher sua tela!'
    )


@router.message(CommandStart())
async def cmd_start(message: Message, bot):
    user_id = message.from_user.id

    if not await user_in_channel(bot, user_id):
        sent = await message.answer(
            "❗ Para utilizar nosso serviço é obrigatório que você entre no nosso grupo.",
            reply_markup=gate_kb(),
        )
        pending_gate[user_id] = (sent.chat.id, sent.message_id)
        return

    sent = await message.answer(
        welcome_text(message.from_user, 0.0),
        reply_markup=welcome_kb(),
    )
    pending_gate[user_id] = (sent.chat.id, sent.message_id)


@router.chat_member()
async def on_chat_member(update: ChatMemberUpdated, bot):
    chan = str(CHANNEL_ID)
    chat_id_str = str(update.chat.id)
    chat_user = (update.chat.username or "").lstrip("@")
    if chat_id_str != chan and chat_user != chan.lstrip("@"):
        return

    user = update.new_chat_member.user
    if update.new_chat_member.status in MEMBRO_OK and user.id in pending_gate:
        chat_id, msg_id = pending_gate.pop(user.id)
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=welcome_text(user, 0.0),
                reply_markup=welcome_kb(),
            )
        except Exception:
            pass


# Placeholder — cada menu terá seu módulo próprio
@router.callback_query(F.data.startswith("menu:"))
async def menu_stub(cb: CallbackQuery):
    await cb.answer("Módulo em construção...", show_alert=False)
