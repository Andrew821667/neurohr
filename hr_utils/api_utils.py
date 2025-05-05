# -*- coding: utf-8 -*-
import os
import openai
import logging
from dotenv import load_dotenv

logger = logging.getLogger('hr_system')

# Загрузка переменных окружения
load_dotenv()

# Установка API-ключа OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    logger.warning("OPENAI_API_KEY не найден в переменных окружения!")

def print_tokens_count_and_price(completion, model):
    """
    Рассчитывает количество токенов и стоимость запроса к API OpenAI.
    
    Args:
        completion: Ответ от API OpenAI
        model: Название используемой модели
    """
    # Цены на токены в долларах за 1 миллион токенов
    model_prices = {
        "gpt-4o": {"input": 5, "output": 15},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }

    if model in model_prices:
        input_price = model_prices[model]["input"]
        output_price = model_prices[model]["output"]
    else:
        print(f"Неизвестная модель: {model}, используются цены для gpt-4o-mini")
        input_price, output_price = 0.15, 0.60

    price = input_price * completion.usage.prompt_tokens / 1e6 +             output_price * completion.usage.completion_tokens / 1e6

    message = (f'Использовано токенов: {completion.usage.prompt_tokens} (ввод) + '
               f'{completion.usage.completion_tokens} (вывод) = '
               f'{completion.usage.total_tokens} (всего). '
               f'*** {model} *** $ {round(price, 5)}')

    print(message)
    return message

def generate_answer(prompt_system, prompt_user, prompt_assistant='', model='gpt-3.5-turbo', temp=0.1):
    """
    Генерирует ответ с использованием API OpenAI.
    
    Args:
        prompt_system: Системный промпт
        prompt_user: Пользовательский промпт
        prompt_assistant: Предыдущий ответ ассистента (по умолчанию пустая строка)
        model: Модель OpenAI (по умолчанию 'gpt-3.5-turbo')
        temp: Температура генерации (по умолчанию 0.1)
        
    Returns:
        Текст ответа от модели
    """
    messages = [
        {"role": "system", "content": prompt_system}
    ]

    # Добавляем предыдущий ответ ассистента, если он есть
    if prompt_assistant:
        messages.append({"role": "assistant", "content": prompt_assistant})

    messages.append({"role": "user", "content": prompt_user})

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
        )
        # Вывод количества используемых токенов и стоимость
        tokens_info = print_tokens_count_and_price(response, model=model)
        logger.info(f"Запрос к API OpenAI успешен. {tokens_info}")
        
        return response.choices[0].message.content
    except Exception as e:
        error_msg = f"Ошибка при запросе к API OpenAI: {str(e)}"
        logger.error(error_msg)
        return f"Произошла ошибка: {str(e)}"
