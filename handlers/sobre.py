from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def sobre_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ VOLTAR", callback_data="menu:home")
    return kb.as_markup()


@router.callback_query(F.data == "menu:sobre")
async def abrir_sobre(cb: CallbackQuery):
    await cb.message.edit_text(
        "🤖 <b>Sobre o Bot</b>\n\n"
        "📡 <b>Larizinha Store</b>\n"
        "Central de streamings com entrega 100% automática.\n\n"
        "👨‍💻 <b>Desenvolvedor:</b> —\n"
        "📩 <b>Contato:</b> @suporte_laricontas\n"
        "🌐 <b>Versão:</b> 1.0.0\n"
        "⚙️ <b>Tecnologia:</b> Python + aiogram\n\n"
        "🛡 Entrega automática 24h por dia.",
        reply_markup=sobre_kb(),
    )
    await cb.answer()
