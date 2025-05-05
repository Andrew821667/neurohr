# -*- coding: utf-8 -*-
import os
import logging
from gtts import gTTS
from IPython.display import Audio

logger = logging.getLogger('hr_system')

def google_tts(text, lang='ru', slow=False, output_dir='./audio'):
    """
    Преобразует текст в речь с использованием Google Text-to-Speech.
    
    Args:
        text: Текст для преобразования в речь
        lang: Язык (по умолчанию 'ru')
        slow: Флаг медленного произношения (по умолчанию False)
        output_dir: Директория для сохранения аудиофайлов
        
    Returns:
        Путь к созданному аудиофайлу
    """
    try:
        # Убираем префикс "Рекрутер: " из текста, если он есть
        if text.startswith("Рекрутер: "):
            text = text[10:]

        # Создаем директорию, если она не существует
        os.makedirs(output_dir, exist_ok=True)
            
        # Создаем объект gTTS
        tts = gTTS(text=text, lang=lang, slow=slow)

        # Путь для сохранения файла
        output_file = os.path.join(output_dir, "audio.mp3")

        # Сохраняем аудио в файл
        tts.save(output_file)
        
        logger.info(f"Аудио успешно создано: {output_file}")
        return output_file
    except Exception as e:
        error_msg = f"Ошибка при создании аудио: {str(e)}"
        logger.error(error_msg)
        return None
