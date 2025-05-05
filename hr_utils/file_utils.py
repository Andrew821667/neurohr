# -*- coding: utf-8 -*-
import os
import json
import PyPDF2
from io import BytesIO
import rarfile
import logging
from datetime import datetime
import textwrap

logger = logging.getLogger('hr_system')

def format_text(text, width=120):
    """
    Форматирует текст с разбивкой на абзацы с заданной шириной строки.
    
    Args:
        text: Исходный текст для форматирования
        width: Максимальная ширина строки (по умолчанию 120)
        
    Returns:
        Отформатированный текст
    """
    paragraphs = str(text).split('\n')
    formatted_paragraphs = []
    for paragraph in paragraphs:
        formatted_paragraph = textwrap.fill(paragraph, width)
        formatted_paragraphs.append(formatted_paragraph)
    return '\n'.join(formatted_paragraphs)

def add_log_file(text, title='', log_file=None, path='./data'):
    """
    Записывает логи в файл с временной меткой.
    
    Args:
        text: Текст для записи в лог
        title: Заголовок лога
        log_file: Путь к файлу логов (если не указан, используется путь по умолчанию)
        path: Директория для логов (по умолчанию './data')
    """
    if log_file is None:
        log_file = os.path.join(path, 'log.txt')

    time_now = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    with open(log_file, "a", encoding='utf-8') as file:
        file.write(f'\n\n{time_now}. {title}.\n\n{format_text(text)}')
    print(f"Запись в лог: {title}")

def read_pdf(pdf_file):
    """
    Извлекает текст из PDF файла.
    
    Args:
        pdf_file: Путь к PDF файлу
        
    Returns:
        Извлеченный текст
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ' '.join([page.extract_text() for page in reader.pages if page.extract_text()])
        logger.info(f"PDF успешно прочитан: {pdf_file}")
        return text
    except Exception as e:
        error_msg = f"Ошибка при чтении PDF {pdf_file}: {str(e)}"
        logger.error(error_msg)
        return ""

def unrar(path):
    """
    Распаковывает все RAR-архивы в указанной папке.
    
    Args:
        path: Путь к папке с архивами
    """
    try:
        extracted_files = []
        for rar in os.listdir(path):
            if rar.endswith('.rar'):
                filepath = os.path.join(path, rar)
                with rarfile.RarFile(filepath) as opened_rar:
                    file_list = opened_rar.namelist()
                    opened_rar.extractall(path)
                    extracted_files.extend(file_list)
                print(f"Распакован архив: {rar}")

        if extracted_files:
            logger.info(f"Распакованные файлы: {', '.join(extracted_files)}")
        else:
            print("RAR-архивы не найдены")
    except Exception as e:
        error_msg = f"Ошибка при распаковке архивов: {str(e)}"
        logger.error(error_msg)
