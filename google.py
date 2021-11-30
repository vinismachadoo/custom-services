import gspread
import os
import pandas as pd
import gspread_dataframe
from singleton import Singleton
from typing import Optional


class GoogleService:
    def __init__(self, map_name_to_id: bool = False):

        if not os.environ.get("GOOGLE_API_CREDENTIALS"):
            raise ValueError("you must provide a GOOGLE_API_CREDENTIALS enviroment variable")
        self.google_credentials = os.environ.get("GOOGLE_API_CREDENTIALS")
        self.sheets_authorizer = self.get_sheets_authorizer()
        self.sheet = None
        if map_name_to_id:
            if not os.environ.get("ID_SHEETS_MAP"):
                raise ValueError("you must provide a ID_SHEETS_MAP enviroment variable")
            self.id_sheet_id_map = os.environ.get("ID_SHEETS_MAP")
            self.map_name_to_id = self.get_sheets_id_map()

    def get_sheets_authorizer(self):
        credentials = {
            key_value.split(":")[0]: ":".join(key_value.split(":")[1:])
            for key_value in self.google_credentials.split(",")
        }
        credentials["private_key"] = credentials["private_key"].replace("\\n", "\n")
        return gspread.service_account_from_dict(credentials)

    def get_sheets_id_map(self):
        todos_ids_sheets = self.sheets_authorizer.open_by_key(self.id_sheet_id_map).get_worksheet(0)
        todos_ids_records = todos_ids_sheets.get_all_records()
        # this will return a dict like {..., "name":"id"}
        return {list(rec.values())[0]: list(rec.values())[1] for rec in todos_ids_records}


class GoogleSheets(GoogleService, metaclass=Singleton):
    def open(self, fileid: Optional[str] = None, filename: Optional[str] = None, by_worksheet_name: bool = False):
        if not self.sheet:
            if not fileid and not filename:
                raise ValueError("expected either fileid or filename, got 'NoneType'")
            elif fileid and filename:
                if not fileid == self.map_name_to_id[filename]:
                    raise ValueError(
                        "filename and fileid are not compatible. you should provide just one of them in this case"
                    )
            elif filename:
                fileid = self.map_name_to_id[filename]
            if by_worksheet_name:
                self.sheet = self.sheets_authorizer.open_by_key(fileid).worksheet(by_worksheet_name)
                return pd.DataFrame(self.sheet.get_all_records())
            self.sheet = self.sheets_authorizer.open_by_key(fileid).get_worksheet(0)
            return pd.DataFrame(self.sheet.get_all_records())
        else:
            raise Exception("You never closed a file")

    def push(self, list_values):
        if self.sheet:
            self.sheet.append_row(list_values)
        else:
            raise Exception("You never opened a file")

    def clear(self):
        if self.sheet:
            self.sheet.clear()
        else:
            raise Exception("You never opened a file")

    def update(self, new_dataframe):
        if self.sheet:
            gspread_dataframe.set_with_dataframe(self.sheet, new_dataframe)
        else:
            raise Exception("You never opened a file")

    def close(self):
        if self.sheet:
            self.sheet = None
        else:
            raise Exception("You never opened a file")
