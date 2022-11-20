from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING

from resources.quiz.schemas import AnswerCreateSchema
from store import TgAccessor
from store.tg.dcs import Message, InlineKeyboardButton, CallbackQuery
from store.tg.inline_keyboard import InlineKeyboard

if TYPE_CHECKING:
    from web.app import Application


class QuizGame:
    def __init__(self, app: Application, bot: TgAccessor):
        self.app = app
        bot.register_command_handler("/start", self.start_bot_router)
        bot.register_query_handler("start", self.start_bot_callback)

        bot.register_command_handler("/set_lang", self.set_language_router)
        bot.register_query_handler("set_lang", self.answer_after_chose_language)

        bot.register_command_handler("/start_play", self.start_play_router)
        bot.register_query_handler("answer_to_question", self.check_answer_callback)
        bot.register_query_handler(
            "start_play_set_lang", self.start_play_after_set_lang_callback
        )

    async def set_language_router(self, message: Message) -> None:
        await self._show_languages(
            prefix="set_lang", message=message, need_create_user=False
        )

    async def start_bot_router(self, message: Message) -> None:
        await self._show_languages(
            prefix="start", message=message
        )

    async def _show_languages(
            self, prefix: str, message: Message, need_create_user: bool = True
    ) -> None:
        if need_create_user:
            await self.app.store.user.create_user(
                tg_id=message.from_.id,
                username=message.from_.username
            )
        languages = await (
            self.app.store.quiz.programming_language_service
            .get_programming_languages()
        )
        if not languages:
            await self.app.store.tg.tg_client.send_message(
                message.chat.id,
                "We don't have programming languages...."
            )
            return
        keyboard = InlineKeyboard()
        languages_data = deque(languages.result)
        column = 0
        while languages_data:
            for row in range(2):
                if not languages_data:
                    break
                lang_id, lang_title = languages_data.popleft()
                keyboard[column][row] = InlineKeyboardButton.Schema().load({
                    "text": lang_title,
                    "callback_data": f"{prefix} {lang_id}"
                })
            column += 1

        await self.app.store.tg.tg_client.send_message(
            message.chat.id,
            "Choose a programming language...",
            reply_markup=keyboard.to_reply_markup()
        )

    # noinspection PyArgumentList
    async def get_new_question_info(
            self, language: str, user_id: int, chat_id: int
    ) -> None | dict:
        quiz_question = await (
            self.app.store.quiz.get_first_unanswered_quiz_for_user(
                int(language), user_id
            )
        )
        if not quiz_question:
            await self.app.store.tg.tg_client.send_message(
                chat_id,
                "You have answered all the questions!"
            )
            return
        question_id, title, _ = quiz_question.question
        answers = [
            AnswerCreateSchema(
                id=answer_id,
                title=title,
                is_correct=is_correct,
                question=question
            ) for answer_id, title, is_correct, question in quiz_question.answers
        ]
        keyboard = InlineKeyboard()
        for count, answer in enumerate(answers):
            keyboard[count][0] = InlineKeyboardButton.Schema().load({
                "text": answer.title,
                "callback_data": (
                    f"answer_to_question {language} {question_id} {answer.id} {answer.is_correct}"
                )
            })

        return {
            "title": title,
            "keyboard": keyboard.to_reply_markup()
        }

    async def start_play_router(self, message: Message) -> None:
        user_id, *_, language = await (
            self.app.store.user.get_user(message.from_.id)
        )
        if not language:
            return await self._show_languages(
                message=message,
                need_create_user=False,
                prefix="start_play_set_lang"
            )

        if question_info := await self.get_new_question_info(language, user_id, message.chat.id):
            await self.app.store.tg.tg_client.send_message(
                message.chat.id,
                question_info["title"],
                reply_markup=question_info["keyboard"]
            )

    async def edit_message(
            self, chat_id: int | str, message_id: int, language: str, user_id: int
    ) -> None:
        if question_info := await self.get_new_question_info(language, user_id, chat_id):
            await self.app.store.tg.tg_client.edit_message(
                message_id=message_id,
                chat_id=chat_id,
                text=question_info["title"],
                reply_markup=question_info["keyboard"]
            )

    async def check_answer_callback(self, data: CallbackQuery) -> None:
        language, question_id, answer_id, is_correct = data.data.split()
        is_correct = False if is_correct == "False" else True
        question_id, answer_id = int(question_id), int(answer_id)

        await self.app.store.user.set_question_status_to_user(
            user_id=data.from_.id,
            question_id=question_id,
            is_correct=is_correct
        )
        if is_correct:
            await self.app.store.tg.tg_client.answer_callback_query(
                callback_query_id=data.id,
                text="Right!"
            )
        else:
            await self.app.store.tg.tg_client.answer_callback_query(
                callback_query_id=data.id,
                text="Wrong! Try it another time."
            )

        await self.edit_message(
            message_id=data.message.message_id,
            language=language,
            chat_id=data.message.chat.id,
            user_id=data.from_.id
        )

    async def answer_after_chose_language(self, data: CallbackQuery) -> None:
        _, language = await (
            self.app.store.quiz.programming_language_service
            .get_programming_language(int(data.data))
        )
        if not language:
            self.app.logger.error(f"Language with id: {data.data} not found")
            return

        *_, user_lang = await self.app.store.user.get_user(data.from_.id)
        if user_lang != int(data.data):
            await self.app.store.user.change_user_language(data.from_.id, int(data.data))
        await self.app.store.tg.tg_client.answer_callback_query(
            callback_query_id=data.id,
            text=f"You have chosen {language}."
        )

    async def start_bot_callback(self, data: CallbackQuery) -> None:
        await self.answer_after_chose_language(data)

    async def start_play_after_set_lang_callback(self, data: CallbackQuery) -> None:
        await self.answer_after_chose_language(data)
        language = data.data
        user_id = data.from_.id
        chat_id = data.message.chat.id

        if question_info := await self.get_new_question_info(language, user_id, chat_id):
            await self.app.store.tg.tg_client.send_message(
                chat_id,
                question_info["title"],
                reply_markup=question_info["keyboard"]
            )
