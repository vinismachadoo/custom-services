import requests
import io
import os
import pandas as pd
from typing import Optional, Union, Sequence
from singleton import Singleton


class TelegramBot(metaclass=Singleton):
    def __init__(self, telegrambot_api_key: str):
        self.telegrambot_api_key = telegrambot_api_key

    def send_message(self, text: str, chat_id: Union[str, int], parse_mode: Optional[str] = None) -> None:

        if not parse_mode:
            requests.get(
                f"https://api.telegram.org/bot{self.telegrambot_api_key}/sendMessage?chat_id={chat_id}&text={text}"
            )
            return

        if not parse_mode in ["MarkdownV2", "HTML"]:
            raise ValueError("parse_mode must be MarkdownV2 or HTML")

        requests.get(
            f"https://api.telegram.org/bot{self.telegrambot_api_key}/sendMessage?chat_id={chat_id}&text={text}&parse_mode={parse_mode}"
        )

    def send_csv(self, worksheet: pd.DataFrame, filename: str, chat_id: Union[str, int]) -> None:
        strIO = io.StringIO()
        excel_writer = pd.ExcelWriter(strIO)
        worksheet.to_csv(excel_writer, encoding="utf-8", sep=";", index=False)
        strIO.getvalue()
        strIO.seek(0)
        strIO.name = f"{filename}.csv"

        requests.get(
            f"https://api.telegram.org/bot{self.telegrambot_api_key}/sendDocument?chat_id={chat_id}",
            files={"document": strIO},
        )

    def send_excel(
        self,
        worksheets: Union[Sequence[pd.DataFrame], pd.DataFrame],
        filename: str,
        chat_id: Union[str, int],
        multiple_worksheets: bool = False,
        worksheet_names: Optional[Union[Sequence[str], str]] = None,
    ) -> None:

        if multiple_worksheets:
            if not isinstance(worksheets, list) or not isinstance(worksheet_names, list):
                raise TypeError(
                    "to work with multiple worksheets, you must specify worksheets and worksheet names of type list"
                )
            else:
                strIO = io.BytesIO()
                excel_writer = pd.ExcelWriter(strIO)
                for worksheet, worksheet_name in zip(worksheets, worksheet_names):
                    worksheet.to_excel(excel_writer, sheet_name=worksheet_name, index=False)

        else:
            if not isinstance(worksheets, pd.DataFrame) or not isinstance(worksheet_names, str):
                raise TypeError("to work with single worksheet, worksheets and worksheet names must be of type str")
            else:
                strIO = io.BytesIO()
                excel_writer = pd.ExcelWriter(strIO)
                worksheets.to_excel(excel_writer, index=False)

        excel_writer.save()
        strIO.getvalue()
        strIO.seek(0)
        strIO.name = f"{filename}.xlsx"

        requests.get(
            f"https://api.telegram.org/bot{self.telegrambot_api_key}/sendDocument?chat_id={chat_id}",
            files={"document": strIO},
        )

    def send_pdf(self, content: bytes, filename: str, chat_id: Union[str, int]) -> None:
        strIO = io.BytesIO(content)
        strIO.seek(0)
        strIO.name = f"{filename}.pdf"

        requests.get(
            f"https://api.telegram.org/bot{self.telegrambot_api_key}/sendDocument?chat_id={chat_id}",
            files={"document": strIO},
        )
