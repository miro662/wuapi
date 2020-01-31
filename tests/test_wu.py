import datetime

from wu import Mark

class TestMark:
    def test_mark_parse_correctly_parses_lack_of_mark(self):
        inner_html = '&nbsp;'
        mark = Mark.parse(inner_html)
        assert mark is None

    def test_mark_parse_correctly_parses_mark(self):
        inner_html = '4.5<br>23.01.20'
        mark = Mark.parse(inner_html)
        assert type(mark) is Mark
        assert mark.value == '4.5'
        assert mark.date == datetime.date(year=2020, month=1, day=23)

    def test_mark_parse_correctly_parses_span_mark(self):
        inner_html = '<span class="ocena">4.0</span><br><span class="ocena">16.02.20</span>'
        mark = Mark.parse(inner_html)
        assert type(mark) is Mark
        assert mark.value == '4.0'
        assert mark.date == datetime.date(year=2020, month=2, day=16)
