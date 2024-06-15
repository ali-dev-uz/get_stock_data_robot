from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Launch the bot"),
            types.BotCommand("referrals", "Invitations for your friends"),

        ]
    )
