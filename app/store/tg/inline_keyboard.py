from typing import DefaultDict
from collections import defaultdict

from store.tg.dcs import InlineKeyboardButton, InlineKeyboardMarkup


class InlineKeyboard:
    def __init__(self, callback_data_prefix: str = ""):
        self._buttons: dict[int, dict[int, InlineKeyboardButton]] = defaultdict(dict)
        self._callback_data_prefix = callback_data_prefix

    def __getitem__(self, row_index: int) -> dict[int, InlineKeyboardButton]:
        return self._buttons[row_index]

    def set_callback_data_prefix(self, prefix: str) -> None:
        self._callback_data_prefix = prefix

    # noinspection PyArgumentList
    def to_reply_markup(self) -> InlineKeyboardMarkup:
        tg_buttons_list: DefaultDict[int, list[InlineKeyboardButton]] = defaultdict(list)
        for row, _ in enumerate(self._buttons):
            row_dict = self._buttons[row]
            for column in row_dict:
                button = row_dict[column]
                tg_buttons_list[row].append(button)

        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=tg_buttons_list.values())
        return InlineKeyboardMarkup.Schema().dump(inline_keyboard)
