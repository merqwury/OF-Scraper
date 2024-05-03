from textual.containers import Horizontal
from textual.widgets import (
    Checkbox,
    SelectionList

)
from ofscraper.classes.table.status import status
from ofscraper.classes.table.fields.selectfield import SelectField


class MediaField(SelectField):
    def __init__(self, name: str) -> None:
        name=name.lower()
        super().__init__(name=name, classes="container")
        self.filter_name = name

    def compose(self):
        yield SelectionList(*[("Audios","audios",True),("Images","images",True),("Videos","video",True)])


