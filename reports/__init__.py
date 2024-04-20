# reports/__init__.py

from reports import download_data
from reports import upload_data_
from reports import info_bd
from reports import get_salary
from reports import get_order

# from reports import upload_data

from reports import pdf_to_xls
from bd.model import Session

user_id = [49089990677]
timur_id = [301477504, 490899906]


def get_reports(session: Session):
    if session.user_id in user_id:
        return {
            "info_bd": info_bd,
            "upload_data": upload_data_,
            "pdf_to_xls": pdf_to_xls,
            "get_salary": get_salary,
            "get_order": get_order,
        }
    elif session.user_id in timur_id:
        return {
            "pdf_to_xls": pdf_to_xls,
            "get_salary": get_salary,
            "get_order": get_order,
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
    "get_salary": get_salary,
    "get_order": get_order,
}
