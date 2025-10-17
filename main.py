from pathlib import Path
import ast
import os
import requests

# Список блок папок
IGNORED_DIRS = {
    '.venv', 'venv', 'env', '__pycache__', '.git', '.hg', '.svn',
    'node_modules', 'dist', 'build', '.tox', '.pytest_cache'
}

def should_skip_path(path: Path, ignored_dirs: set) -> bool:
    return any(part in ignored_dirs for part in path.parts)

my_directory = Path("Projects")

# Фильтруем только корневые папки 
folders = [
    item for item in my_directory.iterdir()
    if item.is_dir()
    and item.name not in IGNORED_DIRS
    and not item.name.startswith('.')
]

# Удаляю файл с библиотеками если он есть чтоб не было старых сохранений
try:
    os.remove("report_file/libraries.txt")    
except FileNotFoundError:
    pass


with open("report_file/libraries.txt","a",encoding="utf-8") as file: # Запись в libraries.txt использованных библиотек в проектах

    # Считывание requirements
    for folder in folders:
        req_file = folder / "requirements.txt"
        
        if req_file.exists():
            file.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            file.write(f"\nFolder: {folder} \n")
            file.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

            with open(req_file, "r", encoding="utf-8") as f:
                for line in f:
                    package = line.split("=")[0].strip()
                    if package:
                        file.writelines(f"{package}\n")


# Теперь обрабатываем ВСЕ папки на наличие .py файлов
with open("report_file/report.txt", "w", encoding="utf-8") as report_file:
    for folder in folders: 
        # Фильтруем ВСЕ пути, содержащие venv и др.
        py_files = [
            f for f in folder.rglob("*.py")
            if not should_skip_path(f, IGNORED_DIRS)
        ]
        # Проверка файлов на синтаксические ошибки
        for py_file in py_files:
            try:
                parsed_ast = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError as e:
                print(f"Syntax error in {py_file}: {e}")
                continue

            class_counter = 0
            func_counter = 0
            args_counter = 0

            report_file.write(f"-------------------------------------------------------------------------------------------------------------------------------------\nFile name: {py_file}\n")
            print(f"-------------------------------------------------------------------------------\nFile name: {py_file}")

            
            for node in ast.walk(parsed_ast):
                # Поиск классов
                if isinstance(node, ast.ClassDef):
                    class_counter += 1
                    report_file.write(f"Class name: {node.name}\n")
                    print(f"Class name: {node.name}")
                # Поиск функций и аргументов
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_counter += 1
                    args = [arg.arg for arg in node.args.args]
                    args_str = ", ".join(args) if args else "None args"
                    args_counter += len(args)  

                    report_file.write(f"Function name: {node.name}\n")
                    report_file.write(f"Args: {args_str}\n")
                    print(f"Function name: {node.name}")
                    print(f"Args: {args_str}")

            # Запись в файл репорт
            summary = f"functions: {func_counter}, classes: {class_counter}, function arguments: {args_counter}"
            print(summary)
            report_file.write(summary + "\n")
