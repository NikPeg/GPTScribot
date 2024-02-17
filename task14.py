def count_words_in_file(file_path: str) -> int | None:
    try:
        with open(file_path, "r") as file:
            text = file.read()
            words = text.split()
            return len(words)
    except FileNotFoundError:
        print(f"Ошибка: файл {file_path} не найден.")
        return None
