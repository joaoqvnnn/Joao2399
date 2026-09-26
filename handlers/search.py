from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ForceReply
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.catalog import PRODUTOS

router = Router()

_esperando: dict[int, bool] = {}


def buscar(termo: str):
    t = termo.lower().strip()
    for p in PRODUTOS:
        if t in p["nome"].lower():
            return p
    return None


def resultado_kb(pid: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Comprar",  callback_data=f"buy:{pid}")
    kb.button(text="❌ Cancelar", callback_data="menu:home")
    kb.adjust(1, 1)
    return kb.as_markup()


@router.callback_query(F.data == "menu:pesquisar")
async def abrir_pesquisa(cb: CallbackQuery):
    _esperando[cb.from_user.id] = True
    await cb.message.edit_text(
        "🔎 <b>Como procurar um serviço?</b>\n"
        "Digite: <code>procurar &lt;nome do serviço&gt;</code>",
        reply_markup=ForceReply(selective=True),
    )
    await cb.answer()


@router.message(F.text)
async def receber_termo(message: Message):
    user_id = message.from_user.id
    if not _esperando.get(user_id):
        return

    texto = (message.text or "").strip()
    if not texto.lower().startswith("procurar"):
        await message.reply(
            "🔎 Digite: <code>procurar &lt;nome do serviço&gt;</code>",
            reply_markup=ForceReply(selective=True),
        )
        return

    termo = texto[len("procurar"):].strip()
    _esperando.pop(user_id, None)

    p = buscar(termo) if termo else None
    if not p:
        await message.answer(f'❌ Nenhum serviço encontrado com "{termo}"')
        return

    await message.answer(
        f"🎯 <b>{p['nome']}</b>\n"
        f"💵 R$ {p['preco']:.2f}\n"
        'Para comprar, clique no botão "🛒 Comprar" abaixo ou abra o painel do serviço.',
        reply_markup=resultado_kb(p["id"]),
    )
