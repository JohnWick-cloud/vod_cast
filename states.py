from aiogram.dispatcher.filters.state import StatesGroup, State

class Audio1(StatesGroup):
    photo = State()
    caption = State()
    file = State()
    done = State()

class Audio2(StatesGroup):
    photo = State()
    caption = State()
    audio = State()
    file = State()