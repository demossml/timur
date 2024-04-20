import PyPDF2
import xlsxwriter
import time
import os
import re
import json
import requests
from pprint import pprint

#Сюда API токен с сайта
API_KEY = 'e847ba51dfe5006957aca33cbd3e158f234b2bfe'
#базовый URL для запросов
BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/'


def find_INN(resource, query):
    url = BASE_URL + resource
    headers = {
        'Authorization': 'Token ' + API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'query': query
    }
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json()

workbook = xlsxwriter.Workbook('results_' + str(int(time.time())) + '.xlsx')
worksheet = workbook.add_worksheet()

pdfs = os.listdir("pdf")
_name = []
_phone = []
row = 1
dict_ = {}

for i0 in pdfs:
    print(i0, "FOUND")
    if '.pdf' in i0.lower():
        with open("pdf/" + i0, "rb") as pdf_file:

            read_pdf = PyPDF2.PdfReader(pdf_file)
            # pprint(type(read_pdf))
            number_of_pages = len(read_pdf.pages)

            worksheet.write(0, 0, "ФИО")
            worksheet.write(0, 1, "Телефон")
            worksheet.write(0, 2, "Адрес")
            worksheet.write(0, 3, "Продукт")
            worksheet.write(0, 4, "ИНН")
            worksheet.write(0, 5, "Компания")

            for i in range(number_of_pages):
                page = read_pdf.pages[i]
                page_content = page.extract_text()
                page_content = page_content.split("\n")
                name_ = ''
                phone_ = ''
                name_t_ = ''
                address_ = ''
                inn_ = ''
                сompany_ = ''

                max_amount = 0
                address__ = False


                for i2 in page_content:
                    if re.search(r'^ИНН:', i2):
                        inn_ = i2.replace('ИНН: ', '').replace('.', "")
                        # pprint(inn_[:-1])
                        if inn_[:-1] in dict_.keys():
                            # pprint(2)
                            сompany_ = dict_[inn_[:-1]]
                        else:
                            # pprint(1)
                            name_сompany = find_INN('party', inn_[:-1])['suggestions'][0]['value']
                            dict_[inn_[:-1]] = name_сompany
                            сompany_ = dict_[inn_[:-1]]

                        # pprint(dict_)
                    if re.search(r'^ФИО:', i2):
                        name_ = i2.replace('ФИО: ', '').replace('.', "")
                    if re.search(r'^Телефон:', i2):
                        if phone_ == '':
                            phone_ = i2.replace('Телефон: ', '')
                    if address__:
                        address_ = address_ + " " + i2.replace('Адрес: ', '').replace(' ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ', '')
                        if 'ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ' in i2:
                            address__ = False
                    if re.search(r'^Адрес:', i2):
                        if not 'ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ' in i2:
                            address__ = True
                        address_ = i2.replace('Адрес: ', '').replace(' ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ', '')
                    if re.search(r'^ПВЗ:', i2):
                        if not 'ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ' in i2:
                            address__ = True
                        address_ = i2.replace('ПВЗ: ', '').replace(' ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ', '')
                    if 'Арт.' in i2:
                        info_ = i2.split(" ")
                        if len(info_) > 2:
                            if len(info_[2]) > 1:
                                name_t_ = info_[2]
                            else:
                                info_2 = i2.replace(')', '__').replace('(', '__').split('__')
                                name_t_ = info_2[2]
                    if phone_ not in _phone:
                        _name.append(name_)
                        _phone.append(phone_)
                        worksheet.write(row, 0, name_)
                        worksheet.write(row, 1, phone_)
                        worksheet.write(row, 2, address_)
                        worksheet.write(row, 3, name_t_)
                        worksheet.write(row, 4, inn_)
                        worksheet.write(row, 5, сompany_)
                        row += 1
                    else:
                        pass
workbook.close()
