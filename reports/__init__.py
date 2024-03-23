# reports/__init__.py

from reports import download_data
from reports import upload_data
from reports import pdf_to_xls
from bd.model import Session

user_id = [490899906, 301477504]


def get_reports(session: Session):
    # if session.user_id in user_id:
    return {
        # "download_data": download_data,
        # "upload_data": upload_data,
        "pdf_to_xls": pdf_to_xls,
    }


reports = {
    "download_data": download_data,
    "upload_data": upload_data,
    "pdf_to_xls": pdf_to_xls,
}
