from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

router = Router()

WEBAPP_URL = "https://SEU-APP.onrender.com/webapp/senha.html"

from handlers.saques import _senhas


def miniapp_kb():
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


@router.message(F.web_app_data)
async def receber_webapp(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("❌ Dados inválidos do Mini App.")
        return

    tipo = data.get("tipo")

    if tipo == "senha_saque":
        senha = str(data.get("senha", ""))
        if not senha.isdigit() or len(senha) != 6:
            await message.answer("❌ Senha inválida. Use 6 dígitos.")
            return
        _senhas[message.from_user.id] = senha
        await message.answer(
            "✅ Senha de saque cadastrada com sucesso!\n"
            "Você já pode realizar saques no programa de afiliados."
        )
        return

    if tipo == "codigo_recuperacao":
        # 📌 Aqui entra seu backend real de envio de e-mail
        # Ex.: SMTP, SendGrid, Resend, etc.
        email = data.get("email", "")
        # gera e envia o código real (guarde em cache/DB com expiração)
        await message.answer(
            f"📧 Enviamos um código para {email}.\n"
            "Verifique sua caixa de entrada e a pasta de SPAM."
        )
        return

    await message.answer("❌ Ação desconhecida.")
