from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.start import welcome_kb, welcome_text

router = Router()

# Módulo 3 — Catálogo (mock; depois troca por banco)
PRODUTOS = [
    {"id": "canva",     "nome": "CANVA PRO (6 MESES)",        "preco": 18.00},
    {"id": "disney",    "nome": "Disney+ Plano Padrão",       "preco": 2.90},
    {"id": "globo",     "nome": "GLOBO + CS + PREMIERE + TELECINE…", "preco": 0.00},
    {"id": "globoplay", "nome": "GLOBOPLAY + CANAIS",         "preco": 3.90},
    {"id": "hbo",       "nome": "HBO MAX",                    "preco": 8.00},
    {"id": "iptv_elite","nome": "IPTV Elite: +30k Conteúdos e Canais…", "preco": 0.00},
    {"id": "iptv_rev",  "nome": "IPTV REVENDA (10 CREDITOS)", "preco": 0.00},
    {"id": "iptv_std",  "nome": "IPTV Standard: Canais Aberto e Fechado…", "preco": 0.00},
    {"id": "netflix",   "nome": "NETFLIX 4K PREMIUM",         "preco": 14.90},
    {"id": "p2p",       "nome": "P2P ANTI-TRAVAMENTO",        "preco": 20.00},
    {"id": "sky",       "nome": "SKY + Hbo + Paramount + Premiere…", "preco": 0.00},
]


def catalog_text(saldo: float) -> str:
    return (
        "⚡ <b>Lari Contas | Catálogo de Serviços</b>\n"
        "────────────────────────\n"
        f"💰 | Saldo da Carteira: R$ {saldo:.2f}\n"
        "⬇️ Selecione uma categoria abaixo para ver nossos planos:"
    )


def catalog_kb():
    kb = InlineKeyboardBuilder()
    for p in PRODUTOS:
        label = p["nome"]
        if p["preco"] > 0:
            label += f" — R$ {p['preco']:.2f}"
        kb.button(text=label, callback_data=f"prod:{p['id']}")
    kb.button(text="⬅️ VOLTAR", callback_data="menu:home")
    kb.adjust(*([1] * len(PRODUTOS)), 1)
    return kb.as_markup()


@router.callback_query(F.data.in_({"menu:comprar", "menu:loja"}))
async def abrir_catalogo(cb: CallbackQuery):
    # TODO: puxar saldo real do banco
    saldo = 0.0
    await cb.message.edit_text(
        catalog_text(saldo),
        reply_markup=catalog_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "menu:home")
async def voltar_home(cb: CallbackQuery):
    await cb.message.edit_text(
        welcome_text(cb.from_user, 0.0),
        reply_markup=welcome_kb(),
    )
    await cb.answer()
