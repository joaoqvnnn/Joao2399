from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Mock — depois troca por banco
_filiados: set[int] = set()

COMISSAO_PCT  = 20.0
SAQUE_MINIMO  = 20.0
META_NIVEL    = 5
NOME_BOT      = "seubot"


def afiliado_inativo_text() -> str:
    return (
        "💰 <b>PROGRAMA DE AFILIADOS</b>\n"
        "⚙️ Status: ❌ Inativo\n"
        f"🧲 Comissão: {COMISSAO_PCT:.1f}%\n"
        f"💰 Saque mínimo: R$ {SAQUE_MINIMO:.2f}\n"
        "ℹ️ INFO: Seus indicados continuarão gerando comissão para sempre."
    )


def afiliado_ativo_text(user_id: int,
                        indicacoes: int = 0,
                        total_ganho: float = 0.0) -> str:
    media = total_ganho / indicacoes if indicacoes else 0.0
    restantes = max(0, META_NIVEL - indicacoes)
    return (
        "💰 <b>PROGRAMA DE AFILIADOS</b>\n"
        "⚙️ Status: ✅ Ativo\n"
        f"🧲 Sua comissão: {COMISSAO_PCT:.1f}% (de todas recargas do indicado)\n"
        f"👥 Indicações: {indicacoes}\n"
        f"🪙 Total ganho: R$ {total_ganho:.2f}\n"
        f"📊 Média: R$ {media:.2f}\n"
        f"💰 Saque mínimo: R$ {SAQUE_MINIMO:.2f}\n"
        "🌱| Nível: Iniciante\n"
        f"🎯 Próxima meta: {META_NIVEL} ({restantes} restantes)\n"
        "ℹ️ INFO: Seus indicados continuarão gerando comissão para sempre.\n"
        "A comissão pode ser alterada a qualquer momento, fique atento aos avisos.\n"
        "🔗 Seu link:\n"
        f"https://t.me/{NOME_BOT}?start=893Hist{user_id}"
    )


def inativo_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Me Filiar", callback_data="afi:filiar")
    kb.button(text="⬅️ Voltar",    callback_data="menu:home")
    kb.adjust(1, 1)
    return kb.as_markup()


def ativo_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📜 Saque",                     callback_data="afi:hist_saque")
    kb.button(text="💸 Saques",                    callback_data="afi:saques")
    kb.button(text="🔐 Cadastrar Senha de Saque",  callback_data="afi:senha")
    kb.button(text="⬅️ Voltar",                    callback_data="menu:home")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()


@router.callback_query(F.data == "menu:afiliados")
async def abrir_afiliados(cb: CallbackQuery):
    if cb.from_user.id in _filiados:
        await cb.message.edit_text(
            afiliado_ativo_text(cb.from_user.id),
            reply_markup=ativo_kb(),
        )
    else:
        await cb.message.edit_text(
            afiliado_inativo_text(),
            reply_markup=inativo_kb(),
        )
    await cb.answer()


@router.callback_query(F.data == "afi:filiar")
async def me_filiar(cb: CallbackQuery):
    _filiados.add(cb.from_user.id)
    await cb.message.edit_text(
        afiliado_ativo_text(cb.from_user.id),
        reply_markup=ativo_kb(),
    )
    await cb.answer("Você agora é um afiliado!", show_alert=False)
