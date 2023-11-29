from ast import Await
import re
import requests
from main import bot
from aiogram import types
from bs4 import BeautifulSoup

def get_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

class Information():
    # Парсинг 10 перших фото
    def get_photo(soup: BeautifulSoup, a_lot_of: bool) -> list | types.URLInputFile:
        photo = soup.find("div", class_="swiper-wrapper").find_all("img")

        list_src_photo = []
        media_group = [] 

        for src in photo:
            list_src_photo.append(src.get("src"))

        if len(list_src_photo) > 10:
            del list_src_photo[10:]
       
        for photo_url in list_src_photo:
            media_group.append(types.InputMediaPhoto(media=photo_url))

        first_photo = types.URLInputFile(str(list_src_photo[0]))
        
        if not a_lot_of:
            return first_photo
        
        return media_group
    
    # Парсинг головної інформації (к-ть кімнат, поверх, площа, Район)
    def get_main_information(soup: BeautifulSoup) -> [str, str, str, str]:
        # constants to check the list "tags"
        NEED_WORDS_UKRAINIAN = ["Кількість кімнат:",
                                "Загальна площа:","Поверх:", "Поверховість:"]
        NEED_WORDS_RUSSIAN = ["Количество комнат:", "Общая площадь:",
                              "Этаж:", "Этажность:"]

        checklist = []
        tags = soup.find("ul", class_="css-sfcl1s").find_all("p")

        for need_word in NEED_WORDS_RUSSIAN:
            for tag in tags:
                if need_word in tag.text:
                    checklist.append(tag.text)
        
        for need_word in NEED_WORDS_UKRAINIAN:
            for tag in tags:
                if need_word in tag.text:
                    checklist.append(tag.text)
        
        find_rooms = re.search(r"\d+", checklist[0])
        find_area = re.search(r"\d+", checklist[1])
        find_have = re.search(r"\d+", checklist[2])
        find_everything = re.search(r"\d+", checklist[3])
        
        rooms = find_rooms.group()
        area = find_area.group()
        flour = f"{find_have.group()} з {find_everything.group()}"

        #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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
        price = soup.find("h2", text=re.compile(r'.*грн.*'))
    
        if not price:
            price = soup.find("h3", text=re.compile(r'.*грн.*'))

        if not price:
            price = soup.find("h4", text=re.compile(r'.*грн.*'))

        if not price:
            return "Суму не знайдено", "#0грн"
        
        without_space = "".join(price.text.split())
        price = int((re.search(r"\d+", without_space)).group())

        return price
    
    def get_header(soup: BeautifulSoup) -> [str, str]:
        # parsing caption from the page
        header = soup.find("h4", class_="css-1juynto")

        if not header:
            return None

        return header.text

    def get_caption(soup: BeautifulSoup) -> str:
        # parsing caption from the page
        caption = soup.find("div", class_="css-1t507yq er34gjf0")

        if not caption:
            return "Описание не найдено"

        if len(caption.text) > 800:
           return caption.text[0:800]

        return caption.text

    def create_caption(soup: BeautifulSoup) -> str:
        caption = Information.get_caption(soup)
        header = Information.get_header(soup)

        rooms, flour, area, district = Information.get_main_information(soup)
        money = Information.get_price(soup)

        main_caption = (f"🏡{rooms}к кв\n"
            f"🏢Поверх: {flour}\n"
            f"🔑Площа: {area}м2\n"
            f'📍Район: {district}\n'
            f"💳️{money} грн"
            f"\n\n{header}\n\n"
            f"📝Опис: {caption}")

        return main_caption
    


# Отримання всіх даних і запуск надсилання
async def get_data(message: types.Message):
    soup: BeautifulSoup = get_url(message.text)
    photo_group = Information.get_photo(soup, True)
    caption = Information.create_caption(soup)

    message_photo = await message.answer_media_group(media=photo_group)
    await bot.edit_message_caption(message_id=message_photo[0].message_id,
                                   chat_id=message.chat.id,
                                   caption=caption)



