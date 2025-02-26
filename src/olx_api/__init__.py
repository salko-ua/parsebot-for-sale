import re
import requests
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder
from bs4 import BeautifulSoup
from bs4.element import Tag
from src.keyboards.parsing_edit import edit_parse_advert


class Parser:
    def __init__(self, url):
        self.url = url
        self.response = requests.get(url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        self.images = []
        self.amount_of_rooms = ""
        self.floor = ""
        self.area = ""
        self.district = ""
        self.price = ""
        self.header = ""
        self.caption = ""
        self.template = ""
        self.full_caption = ""

    def update_amount_of_rooms(self, update_to: str) -> None:
        self.amount_of_rooms = update_to
        self.update_full_caption()

    def update_floor(self, update_to: str) -> None:
        self.floor = update_to
        self.update_full_caption()

    def update_area(self, update_to: str) -> None:
        self.area = update_to
        self.update_full_caption()

    def update_district(self, update_to: str) -> None:
        self.district = update_to
        self.update_full_caption()

    def update_price(self, update_to: str) -> None:
        self.price = update_to
        self.update_full_caption()

    def update_header(self, update_to: str) -> None:
        self.header = update_to
        self.update_full_caption()

    def update_caption(self, update_to: str) -> None:
        self.caption = update_to
        self.update_full_caption()

    def update_template(self, update_to: str) -> None:
        self.template = update_to
        self.update_full_caption()

    def delete_words(self, text: str, words_to_remove: list) -> str:
        # Використовуємо регулярний вираз для визначення слова з можливими крапками
        pattern = re.compile(
            r"\b(?:" + "|".join(map(re.escape, words_to_remove)) + r")\b", re.IGNORECASE
        )

        # Замінюємо відповідні слова на порожні рядки
        result = pattern.sub("", text)

        return result

    def reset_header(self) -> None:
        # parsing caption from the page
        header_parent = self.soup.find("div", {"data-testid": "ad_title"})
        if header_parent and isinstance(header_parent, Tag):
            header = header_parent.find(lambda tag: tag.name not in ["style", "script"])
            header = header.text if header else None
        else:
            header = None

        if not header:
            self.header = "Заголовок не знайдено. Повідомте розробника про помилку."
            return None

        self.header = header
        self.update_full_caption()

    def reset_caption(self) -> None:
        # parsing caption parent
        full_caption = self.soup.find("div", {"data-testid": "ad_description"})

        # get caption if he is exist
        if full_caption and isinstance(full_caption, Tag):
            caption = full_caption.find("div")
            caption = caption.text if caption else None
        else:
            caption = None

        if caption is None:
            self.caption = "Опис не знайдено."
            return

        if len(caption) > 800:
            self.caption = caption[0:800]
            return

        self.caption = "📝Опис:\n" + caption
        self.update_full_caption()

    def reset_price(self) -> None:
        # parsing price from the page

        price_parent = self.soup.find("div", {"data-testid": "ad-price-container"})
        if price_parent and isinstance(price_parent, Tag):
            price = price_parent.find(lambda tag: tag.name not in ["style", "script"])
            price = price.text if price else None
        else:
            price = None

        if not price:
            self.price = "Суму не знайдено"
            return

        self.price = price
        self.update_full_caption()

    # Parse main information like (amount of rooms, floor, area, region)
    def reset_main_information(self) -> None:
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

        # find all span tags in div
        div_with_tags = self.soup.find("div", class_="css-41yf00")
        if div_with_tags and isinstance(div_with_tags, Tag):
            tags = div_with_tags.find_all("p")
        else:
            tags = []

        # check for matches
        for need_word in need_words_russian:
            for tag in tags:
                if need_word in tag.text:
                    checklist.append(tag.text)

        for need_word in need_words_ukrainian:
            for tag in tags:
                if need_word in tag.text:
                    checklist.append(tag.text)

        # TODO переробити принцип
        try:
            if len(checklist) != 4:
                rooms = re.search(r"\d+", checklist[0]).group()
                area = re.search(r"\d+", checklist[1]).group()
                find_everything = re.search(r"\d+", checklist[2])
                floor = f"{find_everything.group()}"
            else:
                rooms = re.search(r"\d+", checklist[0]).group()
                area = re.search(r"\d+", checklist[1]).group()
                find_have = re.search(r"\d+", checklist[2])
                find_everything = re.search(r"\d+", checklist[3])
                floor = f"{find_have.group()} з {find_everything.group()}"
        except:
            rooms, area, floor = "", "", ""

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

        # we are looking for a district and a city, because
        # if there is no district, then the city is a district

        # TODO можливо можна шукати одразу в find?
        find = self.soup.find_all("script")
        pattern_district = re.compile(r'\\"districtName\\":\\"([^\\"]+)\\"')
        pattern_city = re.compile(r'\\"cityName\\":\\"([^\\"]+)\\"')
        district, city = "", ""

        for one in find:
            district = pattern_district.search(one.text)
            city = pattern_city.search(one.text)
            if district and city:
                break

        if district:
            district = district.group(1)
        elif city:
            district = city.group(1)
        else:
            district = ""

        self.amount_of_rooms = rooms
        self.floor = floor
        self.area = area
        self.district = district
        self.update_full_caption()

    # Parse first 10 photo
    def reset_photo(self) -> None:
        # find all images tags in div
        wrapper = self.soup.find("div", class_="swiper-wrapper")
        if wrapper and isinstance(wrapper, Tag):
            images = wrapper.find_all("img")
        else:
            images = []

        # list with photo urls
        list_src_photo = []
        media_group = MediaGroupBuilder(caption=self.full_caption)

        # add urls to list
        for src in images:
            list_src_photo.append(src.get("src"))

        # if images more then 10 cut to 10
        if len(list_src_photo) > 10:
            del list_src_photo[10:]

        # add images_url to media_group
        for photo_url in list_src_photo:
            media_group.add_photo(media=photo_url)

        # save images
        self.images = media_group.build()

    def update_full_caption(self) -> None:
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
            "ріелтор",
            "ріелторів",
            "агентство",
            "маклер",
            "посередник",
            "посередник",
            "особисту",
            "власник",
            "власника",
            "власників",
            "хазяїн",
            "хазяйка",
            "особисту",
            "без комісії",
            "без рієлторів",
            "комісій",
            "Без риелторов",
            "комисий",
            "комісіЇ",
            "комисии",
        ]

        self.caption = self.delete_words(self.caption, words)
        self.header = self.delete_words(self.header, words)

        captions = (
            f"🏡{self.amount_of_rooms}к кв\n"
            f"🏢Поверх: {self.floor}\n"
            f"🔑Площа: {self.area}м2\n"
            f"📍Район: {self.district}\n"
        )
        header = f"\n\n{self.header}" if self.header != "" else ""
        caption = f"\n\n{self.caption}" if self.caption != "" else ""
        main_caption = f"💳️{self.price}" f"{header}" f"{caption}"
        end = f"\n\n{self.template}" if self.template != "" else ""
        self.full_caption = captions + main_caption + end
        self.reset_photo()

    def reset_all(self) -> None:
        self.reset_header()
        self.reset_caption()
        self.reset_price()
        self.reset_main_information()
        self.update_full_caption()


# Отримання всіх даних і запуск надсилання
async def get_data(message: types.Message) -> Parser:
    parser = Parser(url=message.text)
    parser.reset_all()
    print(parser.full_caption)

    # check photo is alright
    new_list = parser.images.copy()

    for index in range(len(parser.images)):
        try:
            message_photo = await message.bot.send_media_group(
                chat_id=-1001902595324,
                message_thread_id=805,
                media=[parser.images[index]],
            )
            await message.bot.delete_message(
                message_id=message_photo[0].message_id, chat_id=-1001902595324
            )
        except:
            new_list.remove(parser.images[index])
    parser.images = new_list

    await message.answer_photo(
        photo=parser.images[0].media,
        caption=parser.full_caption,
        reply_markup=edit_parse_advert(),
    )
    return parser
