from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def perfil_text(user, saldo: float = 0.0, whatsapp: str = "—") -> str:
    return (
        "👤 <b>Meu perfil</b>\n"
        "🔍 Veja aqui os detalhes da sua conta:\n"
        "- 👤 <b>Informações:</b>\n"
        f"🆔 ID da Carteira: <code>{user.id}</code>\n"
        f"💰 Saldo Atual: R$ {saldo:.2f}\n"
        f"📲 Seu Whatsapp: {whatsapp}\n"
        "─── 📊 <b>Suas Movimentações:</b>\n"
        "ー 🛒 Compras Realizadas: 0\n"
        "ー 💰 Total Gasto Em Compras: R$ 0,00\n"
        "ー 💠 Pix Inseridos: R$ 0,00\n"
        "ー 🎁 Gifts Resgatados: R$ 0,00"
    )


def perfil_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📜 Histórico de Compras", callback_data="perfil:historico")
    kb.button(text="🎁 Resgatar Gift Card",   callback_data="perfil:gift")
    kb.button(text="✏️ Alterar dados",        callback_data="perfil:alterar")
    kb.button(text="⬅️ VOLTAR",               callback_data="menu:home")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()


@router.callback_query(F.data == "menu:perfil")
async def abrir_perfil(cb: CallbackQuery):
    # TODO: puxar saldo e whatsapp do banco
    await cb.message.edit_text(
        perfil_text(cb.from_user, 0.0, "—"),
        reply_markup=perfil_kb(),
    )
    await cb.answer()
