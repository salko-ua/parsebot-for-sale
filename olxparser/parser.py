import re
from ast import Await

import requests
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder
from bs4 import BeautifulSoup

from main import bot


def get_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except Exception as e:
        response = requests.get(url)
        raise (str(response) + "\n\n" + e)

class Information:
    # Парсинг 10 перших фото
    def get_photo(soup: BeautifulSoup, caption: str) -> list:
        photo = soup.find("div", class_="swiper-wrapper").find_all("img")

        list_src_photo = []
        media_group = MediaGroupBuilder(caption=caption)

        for src in photo:
            list_src_photo.append(src.get("src"))

        if len(list_src_photo) > 10:
            del list_src_photo[10:]

        for photo_url in list_src_photo:
            media_group.add_photo(media=photo_url)

        return media_group.build()

    # Парсинг головної інформації (к-ть кімнат, поверх, площа, Район)
    def get_main_information(soup: BeautifulSoup) -> [str, str, str, str]:
        # constants to check the list "tags"
        need_words_ukrainian = [
            "Кількість кімнат:",
            "Загальна площа:",
            "Поверх:",
            "Поверховість:",
        ]
        need_words_russian = [
            "Количество комнат:",
            "Общая площадь:",
            "Этаж:",
            "Этажность:",
        ]

        checklist = []
        tags = soup.find("ul", class_="css-rn93um").find_all("p")

        for need_word in need_words_russian:
            for tag in tags:
                if need_word in tag.text:
                    checklist.append(tag.text)

        for need_word in need_words_ukrainian:
            for tag in tags:
                if need_word in tag.text:
                    checklist.append(tag.text)

        try:
            if len(checklist) != 4:
                rooms = re.search(r"\d+", checklist[0]).group()
                area = re.search(r"\d+", checklist[1]).group()
                find_everything = re.search(r"\d+", checklist[2])
                flour = f"{find_everything.group()}"
            else:
                rooms = re.search(r"\d+", checklist[0]).group()
                area = re.search(r"\d+", checklist[1]).group()
                find_have = re.search(r"\d+", checklist[2])
                find_everything = re.search(r"\d+", checklist[3])
                flour = f"{find_have.group()} з {find_everything.group()}"
        except:
            rooms, area, flour = "", "", ""

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

        # we are looking for a district and a city, because
        # if there is no district, then the city is a district

        find = soup.find_all("script")
        pattern_district = re.compile(r'\\"districtName\\":\\"([^\\"]+)\\"')
        pattern_city = re.compile(r'\\"cityName\\":\\"([^\\"]+)\\"')

        for one in find:
            district = pattern_district.search(one.text)
            if district:
                break

        for one in find:
            city = pattern_city.search(one.text)
            if city:
                break

        if district:
            district = district.group(1)
        elif city:
            district = city.group(1)
        else:
            district = ""

        return rooms, flour, area, district

    def get_price(soup: BeautifulSoup) -> [str, str]:
        # parsing price from the page
        price = soup.find("h2", text=re.compile(r".*грн.*"))

        if not price:
            price = soup.find("h2", text=re.compile(r".*\$.*"))

        if not price:
            price = soup.find("h3", text=re.compile(r".*грн.*"))

        if not price:
            price = soup.find("h3", text=re.compile(r".*\$.*"))

        if not price:
            price = soup.find("h4", text=re.compile(r".*грн.*"))

        if not price:
            price = soup.find("h4", text=re.compile(r".*\$.*"))

        if not price:
            return "Суму не знайдено"

        return price.text

    def delete_words(text: str, words_to_remove: list) -> str:
        # Використовуємо регулярний вираз для визначення слова з можливими крапками
        pattern = re.compile(
            r"\b(?:" + "|".join(map(re.escape, words_to_remove)) + r")\b", re.IGNORECASE
        )
        print(text)

        # Замінюємо відповідні слова на порожні рядки
        result = pattern.sub("", text)
        print(result)

        return result

    def get_header(soup: BeautifulSoup) -> [str, str]:
        # parsing caption from the page
        header = soup.find("h4", class_="css-yde3oc")

        if not header:
            return "Заголовок не знайдено. Повідомте розробника про помилку."

        return header.text

    def get_caption(soup: BeautifulSoup) -> str:
        # parsing caption from the page
        caption = soup.find("div", class_="css-1o924a9")

        if not caption:
            return "Опис не знайдено. Повідомте розробника про помилку."

        if len(caption.text) > 800:
            return caption.text[0:800]

        return caption.text

    def create_caption(soup: BeautifulSoup) -> str:
        words = [
            "Від",
            "От",
            "я собственник",
            "я власнник",
            "посредников",
            "своя",
            "свою",
            "риелтор",
            "риелторов",
            "агентство",
            "агент",
            "маклер",
            "посредник",
            "личную",
            "хозяин",
            "собственник",
            "собственника",
            "хозяина",
            "хозяйка",
            "без комиссии",
            "агента",
            "агентства",
            "собственников",
            "посередників",
            "своя",
            "свою",
            "ріелтор",
            "ріелторів",
            "агентство",
            "агент",
            "маклер",
            "посередник",
            "посередник",
            "особисту",
            "власник",
            "власника",
            "власників",
            "хазяїнахазяйка",
            "хазяйка",
            "особисту",
            "без комісії",
            "Без рієлторів",
            "комісій",
            "Без риелторов",
            "комисий",
            "комісіЇ",
            "комисии",
        ]

        caption = Information.delete_words(Information.get_caption(soup), words)
        header = Information.delete_words(Information.get_header(soup), words)

        rooms, flour, area, district = Information.get_main_information(soup)
        money = Information.get_price(soup)

        captions = (
            f"🏡{rooms}к кв\n" f"🏢Поверх: {flour}\n" f"🔑Площа: {area}м2\n" f"📍Район: {district}\n"
        )

        main_caption = f"💳️{money}" f"\n\n{header}\n\n" f"📝Опис:\n{caption}"
        if not rooms != "":
            return main_caption
        return captions + main_caption


# Отримання всіх даних і запуск надсилання
async def get_data(message: types.Message):
    soup: BeautifulSoup = get_url(message.text)
    caption = Information.create_caption(soup)
    photo_group = Information.get_photo(soup, caption)
    new_photo_group = photo_group.copy()


    for i in range(len(photo_group)):
        try:
            message_photo = await bot.send_media_group(chat_id=-1001902595324, message_thread_id=805, media=[photo_group[i]])
            await bot.delete_message(message_id=message_photo[0].message_id, chat_id=-1001902595324)
        except Exception as e:
            new_photo_group.remove(photo_group[i])
    await message.answer_media_group(media=new_photo_group)
