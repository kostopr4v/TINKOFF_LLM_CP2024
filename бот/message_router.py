from aiogram import Router, types, F
from aiogram.types import Message, FSInputFile
import json
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot import conn, cursor, bot
import hashlib
import fire
from interact_llama3_llamacpp import interact, SYSTEM_PROMPT
from tts_model import text2speech
from pp import get_sim

router = Router()
content = ''
query = ''

def replace_stars(input_string):
    words = input_string.split('**')
    result = ''
    for i, word in enumerate(words):
        if i % 2 == 1:
            result += '<b>' + word + '</b>'
        else:
            result += word
    return result

@router.message(Command('start'))
async def start_handler(message: Message):
    await message.answer(f"Здравствуйте, {message.chat.username}, я ИИ ассистент Тинькоффа. Чем могу быть полезен?")



async def edit_msg(message: types.Message, text):
    await message.edit_text(text)


@router.message()
async def any_message(message: Message):
    wait_msg = await message.answer('Пожалуйста, подождите. Генерирую ответ!')
    global content, query

    if message.voice != None:
        from whisper_model import transcribe_audio

        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.send_chat_action(message.chat.id, 'typing')
        await bot.download_file(file_path, f"{message.chat.id}.mp3")
        await bot.send_chat_action(message.chat.id, 'typing')
        text = transcribe_audio(f"{message.chat.id}.mp3")
        await bot.send_chat_action(message.chat.id, 'typing')
        hist = []
        hist.append({"role": "user", "content": text})
        await bot.send_chat_action(message.chat.id, 'typing')
        print(text)
        await bot.send_chat_action(message.chat.id, 'typing')
        data = get_sim(text)
        if data[0][0] <= 0.8:
          content = str(fire.Fire(interact(messages=hist)))
        else:
          content = data[0][4]
        
        content += f'\n\nПодробнее: \n{data[0][2]}\n{data[1][2]}\n{data[2][2]}'
        query = text
        await bot.send_chat_action(message.chat.id, 'typing')
        await bot.delete_message(message.chat.id, wait_msg.message_id)

        await message.answer(replace_stars(content), parse_mode='html')
        
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="👍",
            callback_data="show")
        )
        builder.add(types.InlineKeyboardButton(
            text="👎",
            callback_data="hide")
        )

        await message.answer('Озвучить ответ?', reply_markup=builder.as_markup())
    else:
        if str(message.text)[0] == '/':
            await message.answer('Неизвестная команда!')
        else:
            if len(message.text) < 2000:
                await bot.send_chat_action(message.chat.id, 'typing')
                hist = []
                hist.append({"role": "user", "content": message.text})
                await bot.send_chat_action(message.chat.id, 'typing')
                print(message.text)
                data = get_sim(message.text)
                if data[0][0] < 0.88:
                  content = str(fire.Fire(interact(messages=hist)))
                else:
                  content = data[0][4]
                
                content += f'\n\nПодробнее: \n{data[0][2]}\n{data[1][2]}\n{data[2][2]}'
                query = message.text
                await bot.send_chat_action(message.chat.id, 'typing')
                await message.answer(replace_stars(content), parse_mode='html')
                await bot.delete_message(message.chat.id, wait_msg.message_id)

                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(
                    text="👍",
                    callback_data="show")
                )
                builder.add(types.InlineKeyboardButton(
                    text="👎",
                    callback_data="hide")
                )

                await message.answer('Озвучить ответ?', reply_markup=builder.as_markup())
            else:
                await message.answer("Слишком большое сообщение. Пожалуйста, сократите количество символов в нем.")

@router.callback_query(F.data == 'like')
async def like(callback: types.CallbackQuery):
    await callback.message.answer('Мы рады, что ваш вопрос решился! Если вас интересуют другие вопросы, то вы можете меня спросить об этом!')
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    cursor.execute(f"""INSERT INTO likes(user_id, like, query, answer)
            VALUES  (?, ?, ?, ?)""", (callback.message.chat.id, 1, query, content))
    conn.commit()
   

@router.callback_query(F.data == 'dislike')
async def like(callback: types.CallbackQuery):
    await callback.message.answer('Очень жаль, что мой ответ Вас не устроил. Если вас интересуют другие вопросы, то вы можете меня спросить об этом!')
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    cursor.execute(f"""INSERT INTO likes(user_id, like, query, answer)
        VALUES  (?, ?, ?, ?)""", (callback.message.chat.id, 0, query, content))
    conn.commit()


@router.callback_query(F.data == 'show')
async def like(callback: types.CallbackQuery):
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
        wait = await callback.message.answer('Генерирую аудио!')
        text2speech(content, f"{callback.message.chat.id}.ogg")

        audio = FSInputFile(f"{callback.message.chat.id}.ogg")
        await bot.send_voice(callback.message.chat.id, audio)
        await bot.delete_message(callback.message.chat.id, wait.message_id)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="👍",
            callback_data="like")
        )
        builder.add(types.InlineKeyboardButton(
            text="👎",
            callback_data="dislike")
        )

        await callback.message.answer('Решился ли Ваш вопрос?', reply_markup=builder.as_markup())

@router.callback_query(F.data == 'hide')
async def like(callback: types.CallbackQuery):
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="👍",
            callback_data="like")
        )
        builder.add(types.InlineKeyboardButton(
            text="👎",
            callback_data="dislike")
        )

        await callback.message.answer('Решился ли Ваш вопрос?', reply_markup=builder.as_markup())