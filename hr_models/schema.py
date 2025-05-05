# -*- coding: utf-8 -*-
from langchain_core.pydantic_v1 import BaseModel, Field

class Vacancy(BaseModel):
    """Класс для структурирования данных вакансии при парсинге."""
    position: str = Field(
        description = 'Найди в тексте вакансии название должности (позиции). Иначе, выведи ответ: None')
    skills: str = Field(
        description = 'Найди в тексте вакансии все указанные навыки. Иначе, выведи ответ: None')
    requirements: str = Field(
        description = 'Найди в тексте вакансии все указанные требования. Иначе, выведи ответ: None')
    responsibilities: str = Field(
        description = 'Найди в тексте вакансии все указанные обязанности. Иначе, выведи ответ: None')

class Resume(BaseModel):
    """Класс для структурирования данных резюме при парсинге."""
    position: str = Field(
        description = 'Найди в тексте резюме название должности (позиции). Иначе, выведи ответ: None')
    skills: str = Field(
        description = 'Найди в тексте резюме все указанные навыки (стек). Иначе, выведи ответ: None')
    experience: str = Field(
        description = 'Найди в тексте резюме описание прошлого опыта с описанием деятельности. Иначе, выведи ответ: None')
