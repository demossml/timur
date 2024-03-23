# if message.document:
#     print(1)
#     file_info = await bot.get_file(message.document.file_id)
#     downloaded_file = await bot.download_file(file_info.file_path)

#     # Создаем бинарный объект из файла
#     file_bytes = downloaded_file.read()

#     src = message.document.file_name

#     # Сохраняем файл в MongoDB
#     session.params["inputs"][str(room)][input_name] = file_bytes

#     # Записываем имя файла (или другие метаданные, если необходимо) в сессию
#     session.params["file_metadata"] = {
#         "file_name": message.document.file_name,
#         "file_size": message.document.file_size,
#         "file_type": message.document.mime_type
#     }

#     session.state = State.INPUT
#     session.update(state=session.state)
#     # session.save()  # Необходимо сохранить сессию в базу данных MongoDB
#     await next()
