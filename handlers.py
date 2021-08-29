from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from bot import dp
from aiogram.dispatcher import FSMContext
import fucking_messages as fm
from states import Form
from models import db, User, Word


@dp.message_handler(commands=['start'])
async def handle_command_start(message: Message) -> None:
    if not User.select().where(User.external_id == message.from_user.id).exists():
        User.create(external_id=message.from_user.id)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(fm.add_new_word_button)]
        ],
        resize_keyboard=True
    )

    await message.answer(fm.start, reply_markup=markup)


@dp.message_handler(commands=['help'])
async def handle_command_help(message: Message) -> None:
    await message.answer(fm.help)


@dp.message_handler(text=[fm.add_new_word_button])
async def handle_button_add_new_word(message: Message) -> None:
    await Form.word.set()
    await message.answer(fm.add_answer, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=Form.word)
async def handle_word(message: Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['word'] = message.text
    await Form.next()
    await message.answer(fm.next_state)


@dp.message_handler(state=Form.translation)
async def handle_translation(message: Message, state: FSMContext) -> None:
    user = User.select().where(User.external_id == message.from_user.id).get()
    word = (await state.get_data())['word']
    Word.create(user=user, word=word, translation=message.text)
    await message.answer(fm.save_word)
    await state.finish()


@dp.message_handler(commands=['list'])
async def handle_word_list(message: Message):
    words = Word.select().where(Word.user == User.select().where(User.external_id == message.from_user.id).get())
    await message.answer('\n'.join([f'{word.word} - {word.translation}' for word in words]))
