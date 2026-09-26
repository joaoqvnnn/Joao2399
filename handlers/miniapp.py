from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# URL do Web App hospedado no Render
WEBAPP_URL = "https://SEU-APP.onrender.com/webapp/senha"

# user_id -> senha (mock; depois banco)
from handlers.saques import _senhas


def miniapp_kb():
    from aiogram.types import WebAppInfo
    kb = InlineKeyboardBuilder()
    kb.button(text="🔐 Abrir Mini App", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="⬅️ Voltar",         callback_data="menu:afiliados")
    kb.adjust(1, 1)
    return kb.as_markup()


@router.callback_query(F.data == "afi:senha")
async def abrir_miniapp(cb: CallbackQuery):
    await cb.message.edit_text(
        "🔐 <b>Cadastrar Senha de Saque</b>\n"
        "Abra o Mini App abaixo para cadastrar sua senha de 6 dígitos.",
        reply_markup=miniapp_kb(),
    )
    await cb.answer()


# Endpoint interno chamado pelo Mini App via API
def salvar_senha(user_id: int, senha: str) -> bool:
    if not senha.isdigit() or len(senha) != 6:
        return False
    _senhas[user_id] = senha
    return True
