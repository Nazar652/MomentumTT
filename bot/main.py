from telebot import async_telebot
from telebot import types
import requests
import asyncio
import aiohttp

from config import *

bot = async_telebot.AsyncTeleBot(TOKEN)


cryptocurrencies = [
    'BTC', 'ETH', 'USDT', 'UAH', 'SOL',
    'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE'
]


async def create_user(data: dict) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{URL}/users/', data=data) as response:
            return response.status


async def get_user(user_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{URL}/users/{user_id}') as response:
            return await response.json()


async def create_state(data: dict) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{URL}/states/', data=data) as response:
            return response.status


async def get_state(user_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{URL}/states/?user={user_id}') as response:
            return (await response.json())[0]


async def update_state(user_id: int, data: dict) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.patch(f'{URL}/states/update-by-user/?user={user_id}', data=data) as response:
            return await response.json()


async def create_account(data: dict) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{URL}/accounts/', data=data) as response:
            return response.status


def check_state(user_id: int, state: str | list) -> bool:
    current_state = requests.get(f'{URL}/states/?user={user_id}').json()[0]['state']
    return current_state in state


async def send_menu(user_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=5)
    keyboard.row(*cryptocurrencies[:5])
    keyboard.row(*cryptocurrencies[5:])
    await bot.send_message(user_id, 'Головне меню. Тут ви можете обрати криптовалюту', reply_markup=keyboard)


async def send_currency(currency, chat_id):
    d_to_c, c_to_d = await get_exchange(currency)
    d_to_c_formatted = f"{d_to_c:.20f}".rstrip('0')
    c_to_d_formatted = f"{c_to_d:.20f}".rstrip('0')
    text = f'Курс USD до {currency}: <code>{d_to_c_formatted}</code>\n'
    text += f'Курс {currency} до USD: <code>{c_to_d_formatted}</code>\n'
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(f'Купівля {currency}')
    keyboard.add(f'Продаж {currency}')
    keyboard.add(f'Назад')
    await bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=keyboard)


async def get_exchange(currency: str, dtc=True, ctd=True) -> list:
    resp = []
    async with aiohttp.ClientSession() as session:
        if dtc:
            async with session.get(f'https://api.coinbase.com/v2/exchange-rates?currency=USD') as response:
                resp.append(float((await response.json())['data']['rates'][currency]))
        if ctd:
            async with session.get(f'https://api.coinbase.com/v2/exchange-rates?currency={currency}') as response:
                resp.append(float((await response.json())['data']['rates']['USD']))
    return resp


@bot.message_handler(commands=['start'], chat_types=['private'])
async def start(m):
    response = requests.get(f'{URL}/users/{m.from_user.id}')
    if response.status_code == 404:
        await bot.send_message(m.chat.id, f"Вітаю {m.from_user.first_name}!")
        await create_user(data={
            'first_name': m.from_user.first_name,
            'surname': m.from_user.last_name,
            'username': m.from_user.username,
            'identifier': m.from_user.id,
        })
        await create_state(data={
            'state': 'START',
            'user': m.from_user.id
        })

    await bot.send_message(m.chat.id, f"Перевіряємо чи є у вас обліковий запис")
    response_data = requests.get(f'{URL}/accounts/?user={m.from_user.id}').json()
    if response_data:
        await bot.send_message(m.chat.id, f"Обліковий запис знайдено!")
        await send_menu(m.from_user.id)
        await update_state(m.from_user.id, {'state': 'MENU'})
    else:
        await bot.send_message(m.chat.id, f"У вас відсутній обліковий запис. Зараз створимо!")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Поділитись номером телефону', request_contact=True))
        await bot.send_message(m.chat.id,
                               "Для реєстрації вам потрібно надіслати номер телефону. Натисніть кнопку для цього",
                               reply_markup=markup)


@bot.message_handler(content_types=['contact'], func=lambda m: check_state(m.from_user.id, 'START'))
async def sign_up(m):
    phone_number = m.contact.phone_number

    await create_account(data={
        'phone_number': phone_number,
        'user': m.from_user.id,
    })
    await bot.send_message(m.chat.id, f"Обліковий запис створено!")
    await send_menu(m.from_user.id)
    await update_state(m.from_user.id, {'state': 'MENU'})


@bot.message_handler(func=lambda m: m.text in cryptocurrencies and check_state(m.from_user.id, 'MENU'))
async def handle_cryptocurrency(m):
    await send_currency(m.text, m.chat.id)
    await update_state(m.from_user.id, {'state': 'CURRENCY', 'data': m.text})


@bot.message_handler(func=lambda m: check_state(m.from_user.id, 'CURRENCY'))
async def cryptocurrency_menu(m):
    command = m.text.split()[0]
    if command == "Назад":
        await send_menu(m.from_user.id)
        await update_state(m.from_user.id, {'state': 'MENU', 'data': None})
        return
    state = await get_state(m.from_user.id)
    if command == "Купівля":
        await bot.send_message(m.chat.id,
                               f'Надішліть суму {state["data"]} яку ви хочете купити. Надішліть її у вигляді числа '
                               f'через крапку.\n Наприклад:\n<code>10.0</code>\n<code>13.12</code>\n<code>23.56</code>',
                               reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
        await update_state(m.from_user.id, {'state': 'BUY'})
    elif command == "Продаж":
        await bot.send_message(m.chat.id,
                               f'Надішліть суму {state["data"]} яку ви хочете продати. Надішліть її у вигляді числа '
                               f'через крапку.\n Наприклад:\n<code>10.0</code>\n<code>13.12</code>\n<code>23.56</code>',
                               reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
        await update_state(m.from_user.id, {'state': 'SELL'})


@bot.message_handler()
async def cryptocurrency_buy(m):
    state = await get_state(m.from_user.id)
    if 'BUY' in state['state'] or 'SELL' in state['state']:
        try:
            amount = float(m.text)
        except TypeError:
            await bot.send_message(m.chat.id,
                                   f'Ви надіслали неправильне число, надішліть по прикладу з повідомлення вище')
            return

        currency = state['data']
        if state['state'] == 'BUY':
            c_to_d = (await get_exchange(currency, dtc=False))[0]
            formatted_amount = f"{c_to_d*amount:.20f}".rstrip('0')
            await bot.send_message(m.chat.id,
                                   f'По поточному курсу для купівлі <code>{amount}</code> {currency} треба '
                                   f'<code>{formatted_amount}</code> USD', parse_mode='HTML')
        elif state['state'] == 'SELL':
            d_to_c = (await get_exchange(currency, ctd=False))[0]
            formatted_amount = f"{d_to_c*amount:.20f}".rstrip('0')
            await bot.send_message(m.chat.id,
                                   f'По поточному курсу при продажу <code>{amount}</code> {currency} ви отримаєте '
                                   f'<code>{formatted_amount}</code> USD', parse_mode='HTML')

        await send_currency(currency, m.chat.id)
        await update_state(m.from_user.id, {'state': 'CURRENCY'})


if __name__ == '__main__':
    asyncio.run(bot.polling())
