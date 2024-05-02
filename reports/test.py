def filter_info(info_):
    # Создаем пустую строку для хранения отфильтрованных элементов
    filtered_str = " ".join(
        [
            # Проходим по каждому элементу списка info_
            item
            # Отбираем элементы, которые содержат хотя бы одну букву или символ "№"
            for item in info_
            if any(char.isalpha() or char == "№" for char in item)
            # Отбираем элементы, которые не содержат строки "БЕЗ" или "НДС"
            and item not in ["БЕЗ", "НДС"]
        ]
    )
    return filtered_str


def find_INN(resource, query, API_KEY):
    # Функция для поиска ИНН по запросу с использованием API Dadata
    BASE_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/"
    url = BASE_URL + resource
    headers = {
        "Authorization": "Token " + API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {"query": query}
    # Отправляем POST-запрос к API для поиска ИНН
    res = requests.post(url, data=json.dumps(data), headers=headers)
    # Возвращаем JSON-ответ
    return res.json()


def process_PDF_files(downloaded_zip_file):
    API_KEY = "e847ba51dfe5006957aca33cbd3e158f234b2bfe"
    try:
        with zipfile.ZipFile(io.BytesIO(downloaded_zip_file), "r") as zip_ref:
            results = []  # Здесь будем хранить результаты обработки
            dict_ = {}
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(".pdf"):
                    pdf_content = zip_ref.read(file_name)
                    pdf_file = io.BytesIO(pdf_content)
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_content = page.extract_text()
                            page_content = page_content.split("\n")
                            name_ = ""
                            phone_ = ""
                            address_ = ""
                            inn_ = ""
                            сompany_ = ""
                            product_ = ""
                            address__ = (
                                False  # Флаг для обозначения начала сбора адреса
                            )

                            for line in page_content:
                                if re.search(r"^ИНН:", line):
                                    inn_ = line.replace("ИНН: ", "").replace(".", "")
                                    if inn_[:-1] in dict_.keys():
                                        сompany_ = dict_[inn_[:-1]]
                                    else:
                                        name_company = find_INN(
                                            "party", inn_[:-1], API_KEY
                                        )["suggestions"][0]["value"]
                                        dict_[inn_[:-1]] = name_company
                                        сompany_ = dict_[inn_[:-1]]
                                if re.search(r"^ФИО:", line):
                                    name_ = line.replace("ФИО: ", "").replace(".", "")
                                if re.search(r"^Телефон:", line):
                                    if phone_ == "":
                                        phone_ = line.replace("Телефон: ", "")
                                if address__:
                                    address_ = (
                                        address_
                                        + " "
                                        + line.replace("Адрес: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
                                    if "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = False
                                if re.search(r"^Адрес:", line) or re.search(
                                    r"^ПВЗ:", line
                                ):
                                    if not "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = True
                                    address_ = (
                                        line.replace("Адрес: ", "")
                                        .replace(" ПВЗ: ", "")
                                        .replace("ПВЗ: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
                                if "Арт." in line:
                                    info_ = line.split(" ")
                                    if len(info_) > 2:
                                        if len(info_[2]) > 1:
                                            product_ = filter_info(info_)

                                        else:
                                            info_2 = (
                                                line.replace(")", "__")
                                                .replace("(", "__")
                                                .split("__")
                                            )
                                            product_ = filter_info(info_2)

                            result_entry = {
                                "ФИО": name_.strip(),
                                "Телефон": phone_.strip(),
                                "Адрес": address_.strip(),
                                "Продукт": product_.strip(),
                                "ИНН": inn_.strip(),
                                "Компания": сompany_.strip(),
                            }

                            results.append(result_entry)
                    except Exception as e:
                        print(f"Ошибка при чтении PDF-файла: {file_name}")
                        traceback.print_exc()

        # Преобразование результатов в формат JSON
        # json_results = json.dumps(results, ensure_ascii=False, indent=4)
        return results

    except zipfile.BadZipFile:
        print("Ошибка: Неверный zip-файл.")
        traceback.print_exc()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        traceback.print_exc()


def process_PDF_files_rar(downloaded_rar_file):
    pprint("process_PDF_files_rar")
    API_KEY = "e847ba51dfe5006957aca33cbd3e158f234b2bfe"
    try:
        with rarfile.RarFile(io.BytesIO(downloaded_rar_file), "r") as rar_ref:
            results = []  # Здесь будем хранить результаты обработки
            dict_ = {}
            pprint(rar_ref)
            for file_name in rar_ref.namelist():
                if file_name.lower().endswith(".pdf"):
                    pdf_content = rar_ref.read(file_name)
                    pdf_file = io.BytesIO(pdf_content)
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_content = page.extract_text()
                            page_content = page_content.split("\n")
                            name_ = ""
                            phone_ = ""
                            address_ = ""
                            inn_ = ""
                            сompany_ = ""
                            product_ = ""
                            address__ = (
                                False  # Флаг для обозначения начала сбора адреса
                            )

                            for line in page_content:
                                if re.search(r"^ИНН:", line):
                                    inn_ = line.replace("ИНН: ", "").replace(".", "")
                                    if inn_[:-1] in dict_.keys():
                                        сompany_ = dict_[inn_[:-1]]
                                    else:
                                        name_company = find_INN(
                                            "party", inn_[:-1], API_KEY
                                        )["suggestions"][0]["value"]
                                        dict_[inn_[:-1]] = name_company
                                        сompany_ = dict_[inn_[:-1]]
                                if re.search(r"^ФИО:", line):
                                    name_ = line.replace("ФИО: ", "").replace(".", "")
                                if re.search(r"^Телефон:", line):
                                    if phone_ == "":
                                        phone_ = line.replace("Телефон: ", "")
                                if address__:
                                    address_ = (
                                        address_
                                        + " "
                                        + line.replace("Адрес: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
                                    if "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = False
                                if re.search(r"^Адрес:", line) or re.search(
                                    r"^ПВЗ:", line
                                ):
                                    if not "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = True
                                    address_ = (
                                        line.replace("Адрес: ", "")
                                        .replace(" ПВЗ: ", "")
                                        .replace("ПВЗ: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
                                if "Арт." in line:
                                    info_ = line.split(" ")
                                    if len(info_) > 2:
                                        if len(info_[2]) > 1:

                                            product_ = filter_info(info_)

                                        else:
                                            info_2 = (
                                                line.replace(")", "__")
                                                .replace("(", "__")
                                                .split("__")
                                            )

                                            product_ = filter_info(info_2)

                            result_entry = {
                                "ФИО": name_.strip(),
                                "Телефон": phone_.strip(),
                                "Адрес": address_.strip(),
                                "Продукт": product_.strip(),
                                "ИНН": inn_.strip(),
                                "Компания": сompany_.strip(),
                            }

                            results.append(result_entry)
                    except Exception as e:
                        print(f"Ошибка при чтении PDF-файла: {file_name}")
                        traceback.print_exc()

        # Преобразование результатов в формат JSON
        # json_results = json.dumps(results, ensure_ascii=False, indent=4)
        return results

    except rarfile.BadRarFile:
        print("Ошибка: Неверный rar-файл.")
        traceback.print_exc()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        traceback.print_exc()
