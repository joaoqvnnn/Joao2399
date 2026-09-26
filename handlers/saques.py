from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ForceReply, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

SAQUE_MINIMO = 20.0

# Mock
_chaves: dict[int, dict] = {}
_senhas: dict[int, str] = {}
_saques: dict[int, list] = {}
_esperando_chave: dict[int, str] = {}
_esperando_senha: dict[int, bool] = {}


def tipo_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📧 Email",         callback_data="saq:tipo:email")
    kb.button(text="🆔 CPF",           callback_data="saq:tipo:cpf")
    kb.button(text="📱 Telefone",      callback_data="saq:tipo:tel")
    kb.button(text="🔑 Chave Aleatória", callback_data="saq:tipo:rand")
    kb.button(text="⬅️ Voltar",        callback_data="menu:afiliados")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()


def confirmar_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Confirmar Chave PIX", callback_data="saq:confirmar")
    kb.button(text="✏️ Editar Chave PIX",    callback_data="saq:editar")
    kb.button(text="❌ Cancelar",            callback_data="menu:afiliados")
    kb.adjust(1, 1, 1)
    return kb.as_markup()


def sacar_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Sacar", callback_data="saq:sacar")
    kb.adjust(1)
    return kb.as_markup()


def pdf_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📄 PDF", callback_data="saq:pdf")
    kb.adjust(1)
    return kb.as_markup()


@router.callback_query(F.data == "afi:saques")
async def abrir_saques(cb: CallbackQuery):
    await cb.message.edit_text(
        "💸 <b>Você deseja sacar?</b>\n"
        "Para que possamos realizar seu saque, selecione o tipo de chave PIX:",
        reply_markup=tipo_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("saq:tipo:"))
async def escolher_tipo(cb: CallbackQuery):
    tipo = cb.data.split(":", 2)[2]
    _esperando_chave[cb.from_user.id] = tipo
    nomes = {"email": "Email", "cpf": "CPF", "tel": "Telefone", "rand": "Chave Aleatória"}
    await cb.message.edit_text(
        f"Cadastre o seu {nomes.get(tipo, 'chave')} como chave de saque:",
        reply_markup=ForceReply(selective=True),
    )
    await cb.answer()


@router.message(F.text)
async def receber_chave(message: Message):
    user_id = message.from_user.id
    tipo = _esperando_chave.get(user_id)
    if not tipo:
        return

    _esperando_chave.pop(user_id, None)
    chave = message.text.strip()

    _chaves[user_id] = {
        "tipo": tipo,
        "chave": chave,
        "nome": "NOME COMPLETO",
        "banco": "NOME DO BANCO",
    }

    c = _chaves[user_id]
    await message.answer(
        "Confirma essa é sua chave?\n"
        f"👤 Nome: {c['nome']}\n"
        f"🏦 Banco: {c['banco']}\n"
        f"🆔 {tipo.upper()}: {chave}",
        reply_markup=confirmar_kb(),
    )


@router.callback_query(F.data == "saq:editar")
async def editar_chave(cb: CallbackQuery):
    await cb.message.edit_text(
        "💸 Selecione o tipo de chave PIX:",
        reply_markup=tipo_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "saq:confirmar")
async def confirmar_chave(cb: CallbackQuery):
    saldo = 0.0  # TODO: banco
    await cb.message.edit_text(
        f"💰 Você possui R$ {saldo:.2f} disponível para saque.\n"
        f"💵 Saque mínimo: R$ {SAQUE_MINIMO:.2f}",
        reply_markup=sacar_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "saq:sacar")
async def pedir_senha(cb: CallbackQuery):
    if cb.from_user.id not in _senhas:
        await cb.message.edit_text(
            "❌ Você ainda não cadastrou uma senha de saque.\n"
            "Cadastre no botão 🔐 Cadastrar Senha de Saque.",
        )
        await cb.answer()
        return

    _esperando_senha[cb.from_user.id] = True
    await cb.message.edit_text(
        "🔐 Digite sua senha de 6 dígitos para confirmar o saque:",
        reply_markup=ForceReply(selective=True),
    )
    await cb.answer()


@router.message(F.text)
async def receber_senha(message: Message):
    user_id = message.from_user.id
    if not _esperando_senha.get(user_id):
        return

    senha = (message.text or "").strip()

    try:
        await message.delete()
    except Exception:
        pass

    if not senha.isdigit() or len(senha) != 6:
        await message.answer("❌ Senha incorreta!")
        return

    if _senhas.get(user_id) and _senhas[user_id] != senha:
        await message.answer("❌ Senha incorreta!")
        return

    _esperando_senha.pop(user_id, None)

    msg = await message.answer("⏳ Pagamento em processamento…")

    await msg.edit_text(
        "✅ <b>Pagamento realizado com sucesso!</b>\n"
        "Comprovante disponível abaixo.",
        reply_markup=pdf_kb(),
    )


@router.callback_query(F.data == "saq:pdf")
async def gerar_pdf(cb: CallbackQuery):
    from fpdf import FPDF
    import io

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Extrato do Bot", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Larizinha Store — @seubot", ln=True, align="C")
    pdf.ln(5)

    lista = _saques.get(cb.from_user.id, [])
    if not lista:
        pdf.cell(0, 8, "Você não possui saques.", ln=True)
    else:
        for s in lista:
            pdf.cell(0, 8, f"{s['data']} - R$ {s['valor']:.2f} - {s['status']}", ln=True)

    buf = pdf.output(dest="S")
    if isinstance(buf, str):
        buf = buf.encode("latin-1")

    await cb.message.answer_document(
        BufferedInputFile(buf, filename="extrato.pdf")
    )
    await cb.answer()
