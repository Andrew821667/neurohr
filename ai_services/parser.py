# -*- coding: utf-8 -*-
import logging
from typing import Type, Dict, Any, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel

from hr_utils.api_utils import generate_answer

logger = logging.getLogger('hr_system')

def to_dict_parser(text: str, parser_class: Type[BaseModel], model: str = 'gpt-3.5-turbo') -> Dict[str, Any]:
    """
    Парсит текст с использованием модели LLM и заданного парсера.
    
    Args:
        text: Текст для парсинга
        parser_class: Класс парсера (например, Vacancy или Resume)
        model: Имя модели для генерации текста (по умолчанию 'gpt-3.5-turbo')
        
    Returns:
        Словарь с распарсенными данными
    """
    try:
        # Экземпляр JsonOutputParser
        parser = JsonOutputParser(pydantic_object=parser_class)

        # Создаем шаблон промпта
        prompt = PromptTemplate(
            input_variables=["query"],
            template="Follow the instructions:\n{format_instructions}\n{query}\n",
            partial_variables={"format_instructions": parser.get_format_instructions()})

        # Создаем цепочку: шаблон -> модель -> парсер
        llm = ChatOpenAI(model=model, temperature=0)
        chain = prompt | llm | parser

        # Вызываем цепочку для парсинга текста
        result = chain.invoke({"query": text})

        logger.info(f"Успешный парсинг с использованием {parser_class.__name__}")
        return result
    except Exception as e:
        error_msg = f"Ошибка при парсинге текста: {str(e)}"
        logger.error(error_msg)
        return {}

def analyze_text_with_prompt(text: str, system_prompt: str, user_prompt: str, 
                            model: str = 'gpt-3.5-turbo', temp: float = 0.1) -> str:
    """
    Анализирует текст с использованием заданных промптов.
    
    Args:
        text: Текст для анализа
        system_prompt: Системный промпт для модели
        user_prompt: Шаблон пользовательского промпта
        model: Имя модели (по умолчанию 'gpt-3.5-turbo')
        temp: Температура генерации (по умолчанию 0.1)
        
    Returns:
        Результат анализа текста
    """
    try:
        # Формируем полный пользовательский промпт с текстом
        full_user_prompt = f"{user_prompt}\n\nТЕКСТ ДЛЯ АНАЛИЗА:\n{text}"
        
        # Генерируем ответ
        response = generate_answer(
            prompt_system=system_prompt,
            prompt_user=full_user_prompt,
            model=model,
            temp=temp
        )
        
        logger.info("Успешный анализ текста")
        return response
    except Exception as e:
        error_msg = f"Ошибка при анализе текста: {str(e)}"
        logger.error(error_msg)
        return f"Произошла ошибка при анализе: {str(e)}"
