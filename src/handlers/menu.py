from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, message

from src.control_db import Database
from src.keyboards.menu import about, buy_premium, continue_premium, hide_kb
from src.keyboards.setting import send_settings 
from src.keyboards.premium import back

router = Router()

class SendFAQ(StatesGroup):
    send_message = State()
    change_group = State()
    change_template = State()


@router.message(Command("about"))
@router.message(F.text == "Інформація 🧾")
async def informations(message: Message):
    await message.delete()
    await message.answer("Що вас цікавить ?", reply_markup=about())


async def send_about_information(query: CallbackQuery, text: str) -> None:
    try:
        await query.message.edit_text(
            text=text, parse_mode="HTML", reply_markup=about()
        )
    except Exception as e:
        print(f"SEND ABOUT INFORMATION: {e}\n USER STUPID PRESS THE SAME BUTTON")
        await query.answer(f"Ви уже переглядаєте {query.data}")


@router.callback_query(F.data == "Контакти 📱")
@router.callback_query(F.data == "Поради користування ❤️")
@router.callback_query(F.data == "Про нас 👥")
@router.callback_query(F.data == "Тариф 💸")
@router.callback_query(F.data == "Договір Оферти 📑")
@router.callback_query(F.data == "Політика конфід. 🔐")
async def about_information(query: CallbackQuery):
    privacy_policy = (
        "Політика конфіденційності\n"
        "\n"
        "Останнє оновлення: 22.12.2023\n"
        "\n"
        "Ця політика конфіденційності пояснює, як ми збираємо, використовуємо та захищаємо особисту інформацію, яку ви надаєте нам через телеграм бота Опис та фото обʼєкта. Ми рекомендуємо вам уважно ознайомитися з цією політикою, щоб зрозуміти, як ми обробляємо ваші дані.\n"
        "\n"
        "1. Збирання даних\n"
        "Ми можемо збирати такі дані від користувачів:\n"
        "Ваш Телеграм ID\n"
        "Username користувача (за наявності)\n"
        "Ім'я та прізвище в Телеграм (First Name, Second Name)\n"
        "\n"
        "Ми не збираємо і ніяк не зберігаємо вашу переписку з ботом.\n"
        "\n"
        "2. Мета збору даних\n"
        "Ми збираємо ці дані для надання зручного та адекватного функціонування нашого бота. Ця інформація допомагає нам персоналізувати послуги та поліпшити ваш досвід користувача.\n"
        "\n"
        "3. Збереження даних\n"
        "Термін збереження цих даних не регламентується і може залежати від вашої активності в боті. Ми зберігаємо дані стійко та використовуємо їх лише для цілей, зазначених у розділі 2 цієї політики.\n"
        "\n"
        "4. Обмін і передача даних\n"
        "Ми не передаємо ваші особисті дані третім особам. Інформація, яку ви надаєте через нашого бота, залишається конфіденційною і використовується тільки для цілей, зазначених у розділі 2.\n"
        "\n"
        "5. Права користувача\n"
        "Користувач має право на:\n"
        "Доступ до ваших особистих даних\n"
        "\n"
        "6. Зміни політики конфіденційності\n"
        "Ми можемо оновлювати цю політику конфіденційності без попередження. Останнє оновлення завжди відображається у верхній частині цього документа.\n"
        "\n"
        "7. Контактна інформація\n"
        "Якщо у вас є питання, скарги або запити щодо цієї політики конфіденційності, будь ласка, зв'яжіться з нами за адресою електронної пошти: primehouse.kh@gmail.com\n"
        "\n"
        "Ця політика конфіденційності була останнього разу оновлена 22.12.2023\n"
    )

    offer_contract = (
        "ДОГОВІР ОФЕРТИ\n"
        "\n"
        "1. Загальні положення\n"
        "\n"
        '1.1. Цей Договір оферти (далі - "Договір") є публічною пропозицією власника телеграм бота Опис та фото обʼєкта , з однієї сторони, і будь-якого користувача (далі - "Користувач"), з іншої сторони, укласти угоду на умовах, викладених у цьому Договорі.\n'
        "\n"
        '1.2. Користувач погоджується з умовами цього Договору шляхом використання телеграм бота "Опис та фото обʼєкта".\n'
        "\n"
        "2. Умови використання\n"
        "\n"
        '2.1. Користувач зобов\'язується використовувати телеграм бота "Опис та фото обʼєкта" згідно з його призначенням і не порушувати законодавство та правила користування.\n'
        "\n"
        "2.2. Власник бота залишає за собою право в будь-який час внести зміни до функціональності бота та умов його використання. Користувач буде повідомлений про такі зміни.\n"
        "\n"
        "2.3. Користувач несе відповідальність за безпеку свого облікового запису та зобов'язується не розголошувати свої облікові дані третім особам.\n"
        "\n"
        "3. Власність і авторські права\n"
        "\n"
        '3.1. Весь вміст телеграм бота "Опис та фото обʼєкта", включаючи тексти, зображення, відео та інше, захищений авторськими правами. Використання матеріалів з бота можливе лише з дозволу власника.\n'
        "\n"
        "4. Відповідальність\n"
        "\n"
        "4.1. Власник бота не несе відповідальності за будь-які збитки або шкоди, спричинені Користувачеві в результаті використання бота.\n"
        "\n"
        "5. Заключні положення\n"
        "\n"
        "5.1. Цей Договір регулює відносини між власником бота та Користувачем і підлягає тлумаченню відповідно до законодавства, що діє на території України.\n"
        "\n"
        '5.2. Цей Договір набирає чинності з моменту початку використання Користувачем телеграм бота "Опис та фото обʼєкта".\n'
        "\n"
        "5.3. Зміни і доповнення до цього Договору мають бути внесені в письмовій формі та підписані обома сторонами.\n"
        "\n"
        "6. Повернення коштів.\n"
        "При виникненні непередбачуваних ситуацій або форс-мажорів, кошти за підписку на Telegram-бот не повертаються.\n"
        "\n"
        "7. Реквізити сторін:\n"
        "\n"
        "Продавець:\n"
        "ФОП Магировська Марія Тарасівна\n"
        "Україна, 84511, Донецька обл., Бахмутський р-н, місто Бахмут, вулиця Незалежності, будинок 18, квартира 417-418\n"
        "Код: 3521001888\n"
        "Р/р UA573515330000026004015902981\n"
        "ПриватБанк\n"
    )

    tariff = (
        "Тариф 📑\n"
        "Ціна тарифу - 300 грн 💸\n"
        "Термін дії - 1 місяць 🕐\n"
        "Подовжити тариф можна в будь який час 🤝\n"
    )

    about_us = (
        "Про Нас 👤\n"
        "\n"
        'Бот-помічник "Опис та фото обʼєкта". Створений для агенцій нерухомості.\n'
        "Допомагає автоматизувати роботу та генерую рекламні пости обʼєктів аренди та продажу.\n"
    )

    usage_tips = (
        "Поради Користування ❤️\n"
        "\n"
        "Все просто! Кидаєте боту посилання з ОЛХ ( обовʼязково це посилання повинно бути зі сторінки сайту з продажу чи оренди нерухомості)\n"
        "Бот у відповідь вам надсилає готовий пост с фото та описом. Ви цей пост вже надсилаєте своєму клієнту!\n"
    )

    contacts = (
        "Контакти 📱\n"
        "\n"
        "З приводу пропозицій, скарг або комерційних питань:\n"
        "Телеграм - @realtor_057\n"
        "Пошта - primehouse.kh@gmail.com\n"
    )

    dict_chose = {
        "Політика конфід. 🔐": privacy_policy,
        "Договір Оферти 📑": offer_contract,
        "Тариф 💸": tariff,
        "Про нас 👥": about_us,
        "Поради користування ❤️": usage_tips,
        "Контакти 📱": contacts,
    }

    await send_about_information(query, dict_chose[query.data])


@router.message(F.text == "Підписка 👑")
async def premium(message: Message, text=None):
    await message.delete()
    db = await Database.setup()
    telegram_id = message.from_user.id

    if not await db.telegram_id_premium_exists(telegram_id):
        await message.answer(
            text=(
                f"Інформація про вашу підписку 👑:\n"
                f"Підписка: Не активна ❌\n"
                f"Ви ні разу не купували підписку."
            ),
            reply_markup=buy_premium(),
        )
        return

    is_premium = await db.is_premium_user(telegram_id)
    expiration_date = await db.get_expiration_date(telegram_id)
    bought_premium = await db.get_bought_premium(telegram_id)
    date_purchase = await db.get_date_purchase(telegram_id)

    if is_premium:
        text = (
            f"Інформація про вашу підписку 👑:\n"
            f"Підписка: Активна ✅\n"
            f"Купував підписку: {bought_premium} раз\n\n"
            f"Дія підписки до: <b>{date_purchase}-{expiration_date}</b>"
        )
    elif not is_premium:
        text = (
            f"Інформація про вашу підписку 👑:\n"
            f"Підписка: Не активна ❌\n"
            f"Купував підписку: {bought_premium} раз\n\n"
            f"Закінчилась: <b>{expiration_date}</b>"
        )

    await message.answer(text, parse_mode="HTML", reply_markup=continue_premium())


@router.message(F.text == "Посилання 🔗")
async def faq(message: Message):
    await message.delete()
    db = await Database.setup()

    if not await db.is_premium_user(message.from_user.id):
        await message.answer("Придбайте підписку, щоб переглядати останні посилання 😕")
        return

    urls = await db.see_urls(message.from_user.id)
    if len(urls) > 0:
        text = "Останні 10 посилань: \n"
        s = 1
        for url in urls:
            text += f"{s}. {url[0]}\n"
            s += 1
    else:
        text = "Ви не зпарсили жодного поста 😐"

    await message.answer(text, disable_web_page_preview=True, reply_markup=hide_kb())


@router.message(F.text == "Зворт зв`язок 👤")
async def information(message: Message, state: FSMContext):
    await message.delete()

    message = await message.answer(
        "Напишіть нижче питання, і воно буде відправлене до адміна\nАбо напишіть йому особисто @realtor_057",
        reply_markup=back(),
    )
    await state.set_state(SendFAQ.send_message)
    await state.update_data(message=message)


@router.callback_query(F.data == "Відмінити ❌", SendFAQ.send_message)
async def faq_back(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.delete()


@router.message(SendFAQ.send_message)
async def faq_back(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    messages: Message = data["message"]

    await state.clear()
    text_from_user = (
        f"Користувач @{message.from_user.username} {message.from_user.id}\n"
        "Надіслав повідомлення: \n"
        f"{message.text}"
    )

    await bot.send_message(-1001902595324, message_thread_id=348, text=text_from_user)

    await messages.delete()
    await message.answer("Повідомлення успішно надіслано ✅\nОчікуйте на відповідь 🕐")

@router.message(F.text == "Налаштування ⚙️")
async def settings(message: Message):
    db = await Database.setup()

    await message.delete()
    await message.answer("Що вас цікавить ?", reply_markup=send_settings())

@router.message(Command("add"))
@router.message(F.text == "Додати бота")
async def change_group(message: Message, state: FSMContext):
    db = await Database.setup()
    group_id = message.chat.id
    print(group_id)

    await db.update_group_id(telegram_id=message.from_user.id, group_id=message.text)
    await state.clear()
    await message.answer("Групу додано ✅")



@router.callback_query(F.data == "Змінити шаблон")
async def change_group(query: CallbackQuery, state: FSMContext):
    await query.answer("Надішліть шаблон текстом", show_alert=True)

    await state.set_state(SendFAQ.change_template)

@router.message(F.text, SendFAQ.change_template)
async def change_group_id(message: Message, state: FSMContext):
    db = await Database.setup()

    await db.update_template(telegram_id=message.from_user.id, template=message.text)
    await state.clear()
    await message.answer("Шаблон додано ✅")
