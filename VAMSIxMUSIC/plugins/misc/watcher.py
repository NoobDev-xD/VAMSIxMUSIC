from pyrogram import filters
from pyrogram.types import Message

from VAMSIxMUSIC import nand
from VAMSIxMUSIC.core.call import Shruti

welcome = 20
close = 30


@nand.on_message(filters.video_chat_started, group=welcome)
@nand.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await Shruti.stop_stream_force(message.chat.id)
