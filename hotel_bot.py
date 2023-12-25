import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters.command import Command
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

# from config import bot_token
bot_token = os.getenv("bot_token")

import hotel_db

rooms_db = hotel_db.Room_DB()

# from bot_fsm import text_input_router, MessageState

logging.basicConfig(level=logging.INFO)
bot = Bot(token=bot_token)
text_input_router = Router()
dp = Dispatcher()
dp.include_router(text_input_router)


class MessageState(StatesGroup):
    room_id = State()
    waiting_comment = State()
    waiting_tech_comment = State()
    waiting_room_price = State()


def get_default_keyboard():
    default_keyboard = [

            [types.KeyboardButton(text="Свободные номера"),
            types.KeyboardButton(text="Нужна уборка"),
            types.KeyboardButton(text="Нужен техник")],
            [types.KeyboardButton(text="Номера"),
            types.KeyboardButton(text="Список всех помещений")],
            [types.KeyboardButton(text="Отмена")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=default_keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите"
    )
    return keyboard
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # await message.answer("Hello!")

    await message.answer("Выберите кнопкой", reply_markup=get_default_keyboard())
    # await message.reply(".", reply_markup=types.ReplyKeyboardRemove())


@dp.message(Text("Свободные номера"))
async def cmd_start(message: types.Message):
    room_buttons = list()
    for room, room_description in rooms_db.get_free_rooms_list():
        room_buttons.append([types.InlineKeyboardButton(text=f"{room_description}",
                                                        callback_data=f"room-{room}")])
    # print(room_buttons)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=room_buttons)
    await message.answer(f"Занятых номеров: {rooms_db.rooms_occuped_count()}\n"
                         f"Свободных номеров: {rooms_db.rooms_free_count()}\n"
                         f"Свободные номера:",
                         reply_markup=keyboard)


@dp.message(Text("Список всех помещений"))
async def cmd_start(message: types.Message):
    room_buttons = list()
    for room, room_description in rooms_db.get_all_rooms_list():
        # print(room, room_description)
        room_buttons.append([types.InlineKeyboardButton(text=f"{room_description}",
                                                        callback_data=f"roommode-{room}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=room_buttons)
    await message.answer(f"Все помещения отеля:",
                         reply_markup=keyboard)


@dp.message(Text("Нужен техник"))
async def need_tech(message: types.Message):
    room_buttons = list()
    for room, room_description in rooms_db.get_rooms_need_technician():
        room_buttons.append([types.InlineKeyboardButton(text=f"{room_description}",
                                                        callback_data=f"room-{room}")])
    # print(room_buttons)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=room_buttons)
    # await message.reply("Свободные номера:")
    await message.answer(f"Номеров, где нужен визит техника: {rooms_db.rooms_need_technician_count()} ", reply_markup=keyboard)


@dp.message(Text("Нужна уборка"))
async def need_cleaning(message: types.Message):
    room_buttons = list()
    for room, room_description in list(rooms_db.get_rooms_need_cleaning_list()):
        room_buttons.append([types.InlineKeyboardButton(text=f"{room_description}",
                                                        callback_data=f"room-{room}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=room_buttons)
    await message.answer(f"Номеров, где нужна уборка: {rooms_db.rooms_need_cleaning_count()}", reply_markup=keyboard)


def get_all_rooms_keyboard():
    # buttons = [
    #     [
    #         types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
    #         types.InlineKeyboardButton(text="+1", callback_data="num_incr")
    #     ],
    #     [
    #         types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")
    #     ]
    # ]

    room_buttons = list()
    for room, room_description in rooms_db.get_rooms_list():
        room_buttons.append([types.InlineKeyboardButton(text=f"{room_description}", callback_data=f"room-{room}")])
    # print(room_buttons)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=room_buttons)
    return keyboard


@dp.message(Text("Номера"))
async def room_list(message: types.Message):
    # builder = InlineKeyboardBuilder()
    # builder.add(types.InlineKeyboardButton(
    #     text="Нажми меня",
    #     callback_data="random_value")
    # )
    # for room_number in rooms_db.get_rooms_list():
    #     await message.answer(f"{room_number}", reply_markup=get_room_keyboard())
    await message.answer(f"Rooms:", reply_markup=get_all_rooms_keyboard())
    # await message.answer(
    #     "Нажмите на кнопку",
    #     reply_markup=builder.as_markup()
    # )

# from random import randint
# @dp.callback_query(Text("random_value"))
# async def send_random_value(callback: types.CallbackQuery):
#     await callback.message.answer(str(randint(1, 10)))


def get_rooms_propery_keyboard(room_id):
    room_properties_dict = rooms_db.get_room_property(room_id)
    room_buttons = list()
    for dict_key in room_properties_dict:
        property_name = dict_key
        if property_name == 'room_id':
            property_name = 'Номер'
        if property_name == 'occupied': property_name = f'{hotel_db.sign.occupied} Заселен'
        if property_name == 'need_cleaning': property_name = f'{hotel_db.sign.need_cleaning} Нужна уборка'
        if property_name == 'need_attention': property_name = f'{hotel_db.sign.need_attention} Обратить внимание'
        if property_name == 'need_repair': property_name = f'{hotel_db.sign.need_repair} Нужен специалист'
        if property_name == 'need_water_repair': property_name = f'{hotel_db.sign.need_water_repair} Нужен сантехник'
        if property_name == 'need_electric_repair': property_name = f'{hotel_db.sign.need_electric_repair} Нужен электрик'
        if room_properties_dict[dict_key] == True:
            property_value = f'Да {hotel_db.sign.yes}'
        elif room_properties_dict[dict_key] == False:
            property_value = 'Нет'
        else:
            property_value = room_properties_dict[dict_key]

        room_buttons.append([types.InlineKeyboardButton(text=f"{property_name} - {property_value}",
                                                        callback_data=f"roomchangeproperty-{room_id}-{dict_key}")])
    # room_buttons.append([types.InlineKeyboardButton(text=f"Изменить комментарий",
    #                                                 callback_data=f"roomchangecomment-{room_id}")])
    room_buttons.append(
        (types.InlineKeyboardButton(text=f"Изменить комментарий", callback_data=f"roomchangecomment-{room_id}"),
         types.InlineKeyboardButton(text=f"Удалить комментарий", callback_data=f"roomdeletecomment-{room_id}"))
    )
    room_buttons.append(
        (types.InlineKeyboardButton(text=f"Изменить тех.комментарий", callback_data=f"roomchangetechcomment-{room_id}"),
         types.InlineKeyboardButton(text=f"Удалить", callback_data=f"roomdeletetechcomment-{room_id}"))
    )
    # room_buttons.append([types.InlineKeyboardButton(text=f"Изменить комментарий технику",
    #                                                 callback_data=f"roomchangetechcomment-{room_id}")])
    # print(room_buttons)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=room_buttons)
    return keyboard


@dp.callback_query(Text(startswith="room-"))
async def room_property(callback: types.CallbackQuery):
    # user_value = user_data.get(callback.from_user.id, 0)
    room_id = callback.data.split("-")[1]
    # print(f'Request property for {room_id}')
    # await callback.message.answer((f"Rooms:", reply_markup=get_rooms_propery_keyboard(room_id))
    message_text = f'Номер {room_id}\n'
    room_comment = rooms_db.get_room_comment(room_id)
    if room_comment:
        message_text = f'{message_text}\n {room_comment}'
    room_comment_for_technician = rooms_db.get_room_comment_tech(room_id)
    if room_comment_for_technician:
        message_text = f'{message_text}\n Технику: {room_comment_for_technician}'
    await callback.message.answer(message_text, reply_markup=get_rooms_propery_keyboard(room_id))


@dp.callback_query(Text(startswith="roomchangeproperty-"))
async def roomchangeproperty(callback: types.CallbackQuery):
    # user_value = user_data.get(callback.from_user.id, 0)
    room_id, room_property  = callback.data.split("-")[1:3]
    if room_property == 'occupied':
        bools = ('не заселен', 'заселен')
        await callback.message.answer(f"Номер {room_id}\n {bools[rooms_db.change_room_occuped(room_id)]}.")
        # await bot.send_message()
    if room_property == 'need_cleaning':
        bools = ('Убран', f'{hotel_db.sign.need_cleaning} нужна уборка')
        await callback.message.answer(f"Номер {room_id}\n{bools[rooms_db.change_room_need_cleaning(room_id)]}.")
    if room_property == 'need_water_repair':
        bools = ('сантехника в порядке.', f'нужен сантехник. {hotel_db.sign.need_water_repair}')
        await callback.message.answer(f"Номер {room_id}\n{bools[rooms_db.change_room_need_waterrepair(room_id)]}.")
    if room_property == 'need_electric_repair':
        bools = ('электрика в порядка', f'нужен электрик. {hotel_db.sign.need_electric_repair}')
        await callback.message.answer(f"Номер {room_id}\n{bools[rooms_db.change_room_need_electrician(room_id)]}.")
    if room_property == 'need_repair':
        bools = ('нет задач специалисту', f'нужен специалист. {hotel_db.sign.need_repair}')
        await callback.message.answer(f"Номер {room_id}\n{bools[rooms_db.change_room_need_attention(room_id)]}.")
    if room_property == 'need_attention':
        bools = ('Не требует дополнительного внимания', f'необходимо обратить внимание {hotel_db.sign.need_attention}')
        await callback.message.answer(f"Номер {room_id}\n{bools[rooms_db.change_room_need_attention(room_id)]}.")


    # property = callback.data.split("_")[1]
    # print(f'Request property change for {room_id}')
    # await callback.message.answer((f"Rooms:", reply_markup=get_rooms_propery_keyboard(room_id))
    # await callback.message.answer(f"Room {room_id}", reply_markup=get_rooms_propery_keyboard(room_id))


@dp.callback_query(Text(startswith="roommode-"))
async def callbacks_roommode(callback: types.CallbackQuery, state: FSMContext):
    room_id = callback.data.split("-")[1]
    buttons = list()
    if rooms_db.get_room_for_rent(room_id):
        buttons.append([types.InlineKeyboardButton(text="Не сдавать", callback_data=f"roomnotforrentset-{room_id}")])
    else:
        buttons.append([types.InlineKeyboardButton(text="Cдавать", callback_data=f"roomforrentset-{room_id}")])
    buttons.append([types.InlineKeyboardButton(text="Изменить стоимость", callback_data=f"roomchangecost-{room_id}")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer(f"Номер {room_id} сдается: {rooms_db.get_room_for_rent(room_id)}\n"
                                  f"Стоимость: {rooms_db.get_room_cost(room_id)}",
                                  reply_markup=keyboard)
    # await state.update_data(room_id=room_id)
    # await state.set_state(MessageState.waiting_tech_comment)


@dp.callback_query(Text(startswith="roomforrentset-"))
async def callbacks_roomforrentset(callback: types.CallbackQuery):
    room_id = callback.data.split("-")[1]
    rooms_db.set_room_for_rent(room_id)
    await callback.message.answer(f"Комната {room_id} теперь в статусе: Сдается.")


@dp.callback_query(Text(startswith="roomnotforrentset-"))
async def callbacks_roomforrentset(callback: types.CallbackQuery):
    room_id = callback.data.split("-")[1]
    rooms_db.set_room_not_for_rent(room_id)
    await callback.message.answer(f"Комната {room_id} теперь в статусе: НЕ сдается.")


@dp.callback_query(Text(startswith="roomdeletecomment-"))
async def callbacks_roommode(callback: types.CallbackQuery):
    room_id = callback.data.split("-")[1]
    rooms_db.set_room_comment(room_id, '')
    await callback.message.answer(f"Комментарий для номера {room_id} удален.")


@dp.callback_query(Text(startswith="roomdeletetechcomment-"))
async def callbacks_roommode(callback: types.CallbackQuery):
    room_id = callback.data.split("-")[1]
    rooms_db.set_room_comment_tech(room_id, '')
    await callback.message.answer(f"Комментарий технику для номера {room_id} удален.")


@dp.callback_query(Text(startswith="roomchangecomment-"), )
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    room_id = callback.data.split("-")[1]
    await state.update_data(room_id=room_id)
    await callback.message.answer(f'Текущий комментарий: {rooms_db.get_room_comment(room_id)}'
                                  f'Введите комментарий к номеру {room_id} или нажмите кнопку "отмена"\n')
    await state.set_state(MessageState.waiting_comment)


@text_input_router.message(MessageState.waiting_comment)
async def process_language(message: Message, state: FSMContext) -> None:
    # data = await state.update_data(language=message.text)
    # room_id = await MessageState.room_id.
    data = await state.get_data()
    # print('room_id: ', data['room_id'])
    rooms_db.set_room_comment(data['room_id'], message.text)
    await state.clear()
    await message.reply(f"Установлен для номера {data['room_id']}.")


@dp.callback_query(Text(startswith="roomchangetechcomment-"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    # user_value = user_data.get(callback.from_user.id, 0)
    room_id = callback.data.split("-")[1]
    # print(f'Request property for {room_id}')
    # await callback.message.answer((f"Rooms:", reply_markup=get_rooms_propery_keyboard(room_id))
    await state.update_data(room_id=room_id)
    await callback.message.answer(f'Текущий комментарий технику:\n {rooms_db.get_room_comment(room_id)}'
                                  f'\nВведите комментарий к номеру {room_id} или нажмите кнопку "отмена"\n')
    await state.set_state(MessageState.waiting_tech_comment)


@text_input_router.message(MessageState.waiting_tech_comment)
async def process_language(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    rooms_db.set_room_comment_tech(data['room_id'], message.text)
    await state.clear()
    await message.reply(f"Установлен комментарий технику для номера {data['room_id']}.")


@dp.callback_query(Text(startswith="roomchangecost-"), )
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    room_id = callback.data.split("-")[1]
    await state.update_data(room_id=room_id)
    await callback.message.answer(f'Номер: {room_id}\n'
                                  f'Текущая стоимость: {rooms_db.get_room_cost(room_id)}\n'
                                  f' Введите стоимость номера (число) или нажмите кнопку "отмена"\n')
    await state.set_state(MessageState.waiting_room_price)


@text_input_router.message(MessageState.waiting_room_price)
async def process_language(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    try:
        rooms_db.set_room_cost(data['room_id'], int(message.text))
        await message.reply(f"Стоимость номера {data['room_id']} установлена в {int(message.text)}.")
    except Exception as e:
        print(e)
        await message.reply(f"Ошибка установки новой стоимости для номера {data['room_id']}.")
    await state.clear()


@text_input_router.message(Command("отмена"))
@text_input_router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Операция отменена.",
        # reply_markup=ReplyKeyboardRemove(),
    )



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
