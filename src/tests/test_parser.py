from src.olx_api import Parser

s = Parser(
    url="https://www.olx.ua/d/uk/obyavlenie/kvartira-podobo-pogodinno-dlya-1-4h-osb-poruch-z-opernim-teatrom-IDUE39U.html"
)
s.reset_all()
print(s.images)
