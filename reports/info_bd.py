from arrow import utcnow, get
from bd.model import Session, Clients, PDFFile
from .util import json_to_xls_format_change, he_she_item
from pprint import pprint
import io


name = "🗄️ Database information ➡️"
desc = "Загружает данне"
mime = "text"


def get_inputs(session: Session):
    return {}


def generate(session: Session):

    clients = Clients.objects().order_by("closeDate")

    data_list = he_she_item(clients)

    man = len(data_list[0])
    woman = len(data_list[1])
    report_data = [
        {
            "🙎‍♂️ man:".upper(): f"{man} client",
            "🙎‍♀️ woman:".upper(): f"{woman}client",
            "👫 Total:".upper(): f"{man + woman} clients",
        }
    ]

    return report_data
