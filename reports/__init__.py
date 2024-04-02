# reports/__init__.py

from reports import download_data
from reports import upload_data_
from reports import info_bd

# from reports import upload_data

from reports import pdf_to_xls
from bd.model import Session

user_id = [490899906, 301477504]


def get_reports(session: Session):
    if session.user_id in user_id:
        return {
            "info_bd": info_bd,
            "upload_data": upload_data_,
            "pdf_to_xls": pdf_to_xls,
        }
    else:
        return {
            "pdf_to_xls": pdf_to_xls,
        }


reports = {
    "download_data": download_data,
    "upload_data": upload_data_,
    "pdf_to_xls": pdf_to_xls,
    "info_bd": info_bd,
}
