from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import Tuple, Dict

import settings


@dataclass
class Mark:
    """ Describes single mark
    """
    value: str
    date: datetime.date

    MARK_RE = re.compile(r"(<span class=\"ocena\">)?(?P<mark>\d\.\d)(</span>)?<br>(<span class=\"ocena\">)"
                         r"?(?P<date_day>\d{2})\.(?P<date_month>\d{2})\.(?P<date_year>\d{2})(</span>)?")

    @classmethod
    def parse(cls, inner_html: str) -> Mark or None:
        """ Prases mark from string from table
        :param inner_html: Content of table cell containing mark
        :return: Mark
        """
        if inner_html == '&nbsp;':
            return None

        re_match = cls.MARK_RE.match(inner_html)
        if not re_match:
            raise ValueError('Given inner HTML does not match mark format')

        return Mark(
            value=re_match['mark'],
            date=datetime.date(
                year=int(re_match['date_year']) + 2000,
                month=int(re_match['date_month']),
                day=int(re_match['date_day'])
            )
        )


class WUClient:
    """ Client for retrieving data from Wirtualna Uczelnia
    """

    LOGIN_FIELD_ID = 'ctl00_ctl00_ContentPlaceHolder_MiddleContentPlaceHolder_txtIdent'
    PASSWORD_FIELD_ID = 'ctl00_ctl00_ContentPlaceHolder_MiddleContentPlaceHolder_txtHaslo'
    LOGIN_BUTTON_ID = 'ctl00_ctl00_ContentPlaceHolder_MiddleContentPlaceHolder_butLoguj'

    MARKS_URL = '/OcenyP.aspx'
    MARKS_TABLE_ID = 'ctl00_ctl00_ContentPlaceHolder_RightContentPlaceHolder_dgDane'
    MARKS_TABLE_ROW_CLASS = 'gridDane'

    def __init__(self, url: str, wu_user: Tuple[str, str]):
        """ Creates WU client session
        :param url: Address of WU service
        :param wu_user: Tuple containing username and password
        """
        self._url = url

        # get WU main page
        self._driver = settings.SELENIUM_DRIVER()
        self._driver.get(url)

        # log in to WU
        login, password = wu_user

        login_field = self._driver.find_element_by_id(self.LOGIN_FIELD_ID)
        login_field.send_keys(login)

        password_field = self._driver.find_element_by_id(self.PASSWORD_FIELD_ID)
        password_field.send_keys(password)

        login_button = self._driver.find_element_by_id(self.LOGIN_BUTTON_ID)
        login_button.click()

    def get_marks(self) -> Dict[Dict[Mark]]:
        """ Retrieves marks for current semester
        :return: dictionary of subjects containing dictionary of marks
        """
        self._driver.get(self._url + self.MARKS_URL)

        marks_table = self._driver.find_element_by_id(self.MARKS_TABLE_ID)
        marks_table_body = marks_table.find_element_by_tag_name('tbody')
        marks_table_rows = marks_table_body.find_elements_by_class_name(self.MARKS_TABLE_ROW_CLASS)
        marks = {}
        for row in marks_table_rows:
            marks_table_row_cells = row.find_elements_by_tag_name('td')

            subject_name = marks_table_row_cells[0].get_attribute('innerHTML')
            mark_type_str = marks_table_row_cells[2].get_attribute('innerHTML')
            final_mark = Mark.parse(marks_table_row_cells[4].get_attribute('innerHTML'))

            if final_mark:
                if subject_name not in marks:
                    marks[subject_name] = {}
                marks[subject_name][mark_type_str] = final_mark

        return marks
