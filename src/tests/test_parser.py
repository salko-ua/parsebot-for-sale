from src.olx_api import Parser

s = Parser(url="https://www.olx.ua/d/uk/obyavlenie/vrodvushka-vidova-tsentr-msta-novobud-IDXoFpt.html?reason=extended_search_no_results_last_resort")
print(s.create_caption())

