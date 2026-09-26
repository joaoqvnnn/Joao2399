from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.catalog import PRODUTOS

router = Router()

DESCRICOES = {
    "canva": {
        "titulo": "CANVA PRO (6 MESES)",
        "preco": 18.00,
        "estoque": 3,
        "vendidas": 239,
        "vendo": 14,
        "garantia": "180 dias",
        "descricao": (
            "LEIA A DESCRIÇÃO DO PRODUTO\n"
            "Após a compra, enviaremos o e-mail e a senha.\n"
            "✅ Assinatura de 6 meses\n"
            "✅ Funciona 24 horas por dia, sem interrupções\n"
            "✅ Renovação automática\n"
            "✅ Conta privada\n"
            "✅ Plano CANVA EDUCATION\n"
            "🔥🔥🔥 Garantia total 🔥🔥🔥"
        ),
    },
}


def get_produto(pid: str):
    base = next((p for p in PRODUTOS if p["id"] == pid), None)
    if not base:
        return None
    extra = DESCRICOES.get(pid, {})
    return {
        "id": pid,
        "titulo": extra.get("titulo", base["nome"]),
        "preco": extra.get("preco", base["preco"]),
        "estoque": extra.get("estoque", 0),
        "vendidas": extra.get("vendidas", 0),
        "vendo": extra.get("vendo", 0),
        "garantia": extra.get("garantia", "—"),
        "descricao": extra.get("descricao", "Sem descrição cadastrada."),
    }


def produto_text(p: dict, saldo: float) -> str:
    return (
        "🔥 <b>OPORTUNIDADE EXCLUSIVA</b> 🔥\n"
        f"🚀 <b>{p['titulo']}</b>\n"
        "🟢 DISPONÍVEL AGORA\n"
        f"├ 💵 Preço: R$ {p['preco']:.2f}\n"
        f"├ 💰 Seu Saldo: R$ {saldo:.2f}\n"
        f"└ 📦 Estoque: {p['estoque']}\n"
        "📝 <b>Descrição:</b>\n"
        f"{p['descricao']}\n"
        "📊 <b>Estatísticas em tempo real:</b>\n"
        f"⚡️ Já foram vendidas {p['vendidas']} unidades!\n"
        f"👀 {p['vendo']} pessoas estão vendo isso agora.\n"
        f"🛡 Garantia: {p['garantia']}\n"
        "✅ Compra segura. Ao adquirir, concorda com /termos"
    )


def produto_kb(pid: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 COMPRAR",             callback_data=f"buy:{pid}")
    kb.button(text="🛒 Comprar mais de um",  callback_data=f"buymulti:{pid}")
    kb.button(text="⬅️ VOLTAR",              callback_data="menu:comprar")
    kb.adjust(1, 1, 1)
    return kb.as_markup()


@router.callback_query(F.data.startswith("prod:"))
async def abrir_produto(cb: CallbackQuery):
    pid = cb.data.split(":", 1)[1]
    p = get_produto(pid)
    if not p:
        await cb.answer("Produto não encontrado.", show_alert=True)
        return

    # TODO: puxar saldo real do banco
    saldo = 0.0
    await cb.message.edit_text(
        produto_text(p, saldo),
        reply_markup=produto_kb(pid),
    )
    await cb.answer()
