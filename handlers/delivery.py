from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Cache simples para revelar/borrar produto
_revealed: dict[tuple[int, int], bool] = {}


def entrega_text(preco: float, revelado: bool = False) -> str:
    email = "cliente@email.com" if revelado else "••••••••••••••••"
    senha = "senha123456"       if revelado else "••••••••••••••••"
    return (
        "✅ <b>Produto realizado com sucesso!</b>\n"
        "⏰ Data da compra: 31/01/2026\n"
        "📆 Vencimento: 02/03/2026\n"
        f"💰 Valor: R$ {preco:.2f}\n"
        "🎫 ID da compra: <code>81c5465d-e71e-4b43-903a-e1dc567272ea</code>\n"
        "⚜️ Serviço: CANVA PRO (no seu email)\n"
        f"📧 Email: {email}\n"
        f"🔐 Senha: {senha}\n"
        "📃 Nota: Use o botão abaixo para ativar:"
    )


def entrega_kb(pid: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔓 VER PRODUTO",             callback_data=f"show:{pid}")
    kb.button(text="🔗 CLIQUE AQUI PARA ATIVAR", url="https://example.com/ativar")
    kb.adjust(1, 1)
    return kb.as_markup()


@router.callback_query(F.data.startswith("show:"))
async def revelar_produto(cb: CallbackQuery):
    pid = cb.data.split(":", 1)[1]
    key = (cb.from_user.id, cb.message.message_id)
    atual = _revealed.get(key, False)
    novo = not atual
    _revealed[key] = novo

    preco = 18.00  # TODO: puxar do banco
    await cb.message.edit_text(
        entrega_text(preco, revelado=novo),
        reply_markup=entrega_kb(pid),
    )
    await cb.answer()
