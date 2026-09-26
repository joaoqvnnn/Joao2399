import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import (
    start,
    catalog,
    product,
    purchase,
    delivery,
    profile,
    history,
    gift,
    alterar_dados,
    recarga,
    afiliados,
    saques,
    miniapp,
    search,
    ranking,
    sobre,
)


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(product.router)
    dp.include_router(purchase.router)
    dp.include_router(delivery.router)
    dp.include_router(profile.router)
    dp.include_router(history.router)
    dp.include_router(afiliados.router)
    dp.include_router(saques.router)
    dp.include_router(miniapp.router)
    dp.include_router(ranking.router)
    dp.include_router(sobre.router)
    dp.include_router(gift.router)
    dp.include_router(alterar_dados.router)
    dp.include_router(recarga.router)
    dp.include_router(search.router)

    print("Bot iniciado.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
