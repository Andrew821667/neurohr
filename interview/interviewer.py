# -*- coding: utf-8 -*-
import logging
import time
import re
from typing import List, Dict, Any, Optional
from IPython.display import Audio, display

from hr_utils.audio_utils import google_tts
from hr_utils.api_utils import generate_answer
from hr_utils.file_utils import format_text

logger = logging.getLogger('hr_system')

def conduct_interview(resume: str, questions: List[str]):
    """
    Проводит собеседование с кандидатом.
    
    Args:
        resume: Текст резюме кандидата
        questions: Список вопросов для собеседования
        
    Returns:
        Строка с историей диалога
    """
    text_start = (f'Рекрутер: Здравствуйте! Давайте начнем собеседование. План собеседования следующий: \n'
                 f' 1. Я задам Вам несколько вопросов. \n 2. Расскажу о нашей компании и имеющейся вакансии \n'
                 f' 3. Отвечу на Ваши вопросы. \n Общайтесь пожалуйста со мной как с обычным рекрутером!')

    # Озвучивание приветствия
    audio_file = google_tts(text_start.replace("Рекрутер:", ""))
    if audio_file:
        display(Audio(audio_file))
        time.sleep(1)

    print(text_start, '\n')

    # Сохранение резюме и истории диалога
    interview_summary = [f"Резюме:\n{resume}\n", "Интервью:\n"]

    # Получение ответов на вопросы
    interview_summary.extend(ask_questions(questions))

    logger.info("Собеседование успешно проведено")

    # Возвращаем резюме и историю диалога в текстовом виде
    return "\n".join(interview_summary)

def ask_questions(questions: List[str]):
    """
    Проводит диалог, задавая вопросы из списка и получая ответы пользователя.
    
    Args:
        questions: Список вопросов
    
    Returns:
        Список строк с историей диалога
    """
    responses = []

    for question in questions:
        try:
            # Очистка номера вопроса для озвучивания
            clean_question = re.sub(r'^\d+\.', '', question)

            # Озвучивание вопроса
            audio_file = google_tts(clean_question)
            if audio_file:
                display(Audio(audio_file))
                time.sleep(1)  # Пауза для корректного отображения

            # Вывод вопроса
            print(format_text(f"Рекрутер: {question}"), '\n')

            # Получение ответа пользователя
            answer = input("Кандидат: ")
            formatted_answer = format_text(f"Кандидат: {answer}")

            # Добавление истории диалога в список
            responses.append(f"{question}\n\n{formatted_answer}\n\n")
            print('\n')
        except Exception as e:
            error_msg = f"Ошибка при обработке вопроса: {str(e)}"
            logger.error(error_msg)
            print(error_msg)

    logger.info(f"Задано {len(questions)} вопросов, получены ответы")
    return responses

def ask_additional_questions(questions):
    """
    Задает дополнительные вопросы, полученные после анализа ответов.
    
    Args:
        questions: Строка или список с вопросами
        
    Returns:
        Список строк с историей диалога
    """
    # Преобразуем вопросы в список, если передана строка
    if isinstance(questions, str):
        question_list = [q.strip() for q in questions.split('\n') if q.strip() and re.match(r'^\d+\.', q.strip())]
    else:
        question_list = questions
        
    # Задаем вопросы и получаем ответы
    responses = ask_questions(question_list)
    
    logger.info(f"Задано {len(question_list)} дополнительных вопросов")
    return responses

def present_company_and_vacancy(company_description: str):
    """
    Представляет информацию о компании и вакансии.
    
    Args:
        company_description: Описание компании и вакансии
    """
    text_presentation = f'Рекрутер: Спасибо, что ответили на все дополнительные вопросы. Теперь я хочу подробнее рассказать Вам о нашей организации. Нажмите Enter, когда будете готовы.'
    print(format_text(text_presentation), '\n')
    input()
    print(format_text(company_description), '\n\n')
    
    logger.info("Представлена информация о компании и вакансии")

def handle_candidate_questions(candidate_position: str, db_hr_answers, 
                              model: str = 'gpt-3.5-turbo', temp: float = 0.3):
    """
    Отвечает на вопросы кандидата о компании и вакансии.
    
    Args:
        candidate_position: Позиция кандидата
        db_hr_answers: Векторная база данных с ответами HR
        model: Модель для генерации ответов (по умолчанию 'gpt-3.5-turbo')
        temp: Температура генерации (по умолчанию 0.3)
    """
    prompt_candidate_questions = f"""
    Ты являешься опытным рекрутером, который проводит собеседование на позицию {candidate_position}.
    Ты хорошо знаешь компанию, её ценности, процессы и требования к сотрудникам.
    Твоя задача - дать кандидату информативные, точные и честные ответы на вопросы о компании и вакансии.
    Отвечай кратко, но полно, в дружелюбном и профессиональном тоне.
    Если вопрос не относится к вакансии или компании, вежливо направь разговор обратно к теме собеседования.
    Если ты не знаешь точного ответа, не выдумывай информацию - лучше признай, что необходимо уточнить детали.
    """

    query_candidate_questions_template = """
    ИНСТРУКЦИИ:

    1. Используй предоставленную Базу знаний для ответа на вопрос кандидата
    2. Выбирай информацию только для позиции {candidate_position} или универсальную для всех позиций
    3. Игнорируй информацию, относящуюся к другим должностям
    4. Формируй ответ полными, развернутыми предложениями
    5. Не используй формальные обозначения типа "Ответ:"
    6. Если в базе знаний нет релевантной информации, дай общий ответ на основе типичных практик рекрутинга
    7. Если вопрос не относится к профессиональной сфере, вежливо скажи, что это не имеет отношения к текущему собеседованию

    ВОПРОС КАНДИДАТА:
    {candidate_question}
    """

    text_candidate_questions = f'Рекрутер: Если у Вас остались какие-либо вопросы, задайте их, пожалуйста, и я постараюсь ответить. Если вопросов нет, просто напишите "вопросов нет", и мы завершим наше собеседование.'
    print(format_text(text_candidate_questions), '\n\n')

    while True:
        candidate_question = input("Кандидат: ")
        print()

        if candidate_question.strip().lower() == 'вопросов нет':
            print("Рекрутер: Спасибо за собеседование! Желаем Вам удачи!")
            break

        try:
            # Формирование полного вопроса с позицией
            full_question = f'Вопрос к позиции: {candidate_position}: {candidate_question}'

            # Формирование запроса с промптом
            query_template = query_candidate_questions_template.format(
                candidate_position=candidate_position,
                candidate_question=candidate_question
            )

            # Поиск похожих документов в базе знаний
            docs = db_hr_answers.similarity_search(full_question, k=3)

            # Формирование контекста из найденных документов
            message_content = '\n '.join([f'\nChank {i+1}:\n' +
                                        doc.page_content + '\n' for i, doc in enumerate(docs)])
            message_content = re.sub(r'\n{2}', ' ', message_content)

            # Добавление контекста к запросу
            query_with_context = f'# База знаний для ответов: \n{message_content} \n# {query_template}'

            # Генерация ответа
            answer = generate_answer(prompt_candidate_questions, query_with_context, model=model, temp=temp)

            # Озвучивание ответа
            audio_file = google_tts(answer)
            if audio_file:
                display(Audio(audio_file))
                time.sleep(1)

            print("Рекрутер: " + format_text(answer))
            print()
        except Exception as e:
            error_msg = f"Ошибка при обработке вопроса: {str(e)}"
            logger.error(error_msg)
            print("Рекрутер: Извините, я не могу ответить на этот вопрос. Попробуйте задать другой вопрос.")
            
    logger.info("Завершен этап ответов на вопросы кандидата")
