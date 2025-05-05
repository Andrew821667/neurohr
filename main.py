# -*- coding: utf-8 -*-
"""
НейроHR - система для проведения собеседований с использованием нейросетей

Основной модуль приложения, обеспечивающий взаимодействие между компонентами системы.
"""

import os
import logging
import argparse
from datetime import datetime
import json
from typing import Dict, Any, List, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hr_system.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('hr_system')

# Импорт утилит
from hr_utils.file_utils import read_pdf, unrar, format_text
from hr_utils.api_utils import generate_answer
from hr_utils.audio_utils import google_tts

# Импорт моделей данных
from hr_models.schema import Vacancy, Resume
from hr_models.document_store import DocumentStore

# Импорт AI сервисов
from ai_services.parser import to_dict_parser, analyze_text_with_prompt
from ai_services.vector_store import create_vector_db, load_vector_db, similarity_search, db_from_markdown_file

# Импорт модулей интервью
from interview.question_generator import load_general_questions, select_questions_for_position, generate_additional_questions
from interview.interviewer import conduct_interview, ask_questions, ask_additional_questions, present_company_and_vacancy, handle_candidate_questions
from interview.assessment import define_key_requirements, generate_final_assessment, save_assessment_report

class HRSystem:
    """
    Основной класс системы НейроHR, обеспечивающий функциональность по проведению собеседований.
    """
    
    def __init__(self, data_path: str = "./data"):
        """
        Инициализация системы НейроHR.
        
        Args:
            data_path: Путь к директории с данными
        """
        self.data_path = data_path
        self.document_store = DocumentStore(base_path=data_path)
        self.model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        
        # Инициализация системы
        logger.info(f"Инициализация системы НейроHR (путь к данным: {data_path})")
        
    def process_pdf_files(self):
        """
        Обрабатывает PDF-файлы вакансий и резюме, создает векторные базы данных.
        """
        logger.info("Начинаю обработку PDF-файлов...")
        
        # Проверяем наличие файлов
        vacancies_pdf_files = [f for f in os.listdir(self.document_store.vacancies_pdf_path) if f.endswith('.pdf')]
        resumes_files = [f for f in os.listdir(self.document_store.resumes_pdf_path) if f.endswith('.pdf')]
        
        print(f"Найдено {len(vacancies_pdf_files)} PDF-файлов вакансий")
        print(f"Найдено {len(resumes_files)} PDF-файлов резюме")
        
        # Обработка вакансий
        if vacancies_pdf_files:
            print("
Парсинг PDF-файлов вакансий...")
            self._process_vacancy_files()
        
        # Обработка резюме
        if resumes_files:
            print("
Парсинг PDF-файлов резюме...")
            self._process_resume_files()
        
        print("
Обработка PDF-файлов завершена!")
    
    def _process_vacancy_files(self):
        """
        Обрабатывает PDF-файлы вакансий и создает векторную базу.
        """
        chunks_vacancies = []
        
        for file in os.listdir(self.document_store.vacancies_pdf_path):
            if file.endswith('.pdf'):
                try:
                    # Полный путь к файлу
                    file_path = os.path.join(self.document_store.vacancies_pdf_path, file)
                    
                    # Чтение PDF и преобразование в текст
                    vacancy_text = read_pdf(file_path)
                    if not vacancy_text:
                        print(f"Пустой текст в файле: {file}")
                        continue
                    
                    # Парсинг текста вакансии
                    vacancy_id = file.split('.')[0]  # Имя файла без расширения .pdf
                    
                    # Парсинг текста с использованием LLM
                    dict_vacancy = to_dict_parser(vacancy_text, parser_class=Vacancy, model=self.model)
                    
                    # Добавление дополнительных полей
                    dict_vacancy['id'] = vacancy_id
                    dict_vacancy['vacancy'] = vacancy_text
                    
                    # Сохранение в хранилище документов
                    self.document_store.save_document_json(dict_vacancy, vacancy_id, 'vacancy')
                    
                    # Получение чанка для векторной базы
                    chunk = self.document_store.document_to_chunk(vacancy_id, 'vacancy')
                    if chunk:
                        chunks_vacancies.append(chunk)
                    
                    print(f"Обработана вакансия: {file}")
                except Exception as e:
                    error_msg = f"Ошибка при обработке файла {file}: {str(e)}"
                    logger.error(error_msg)
                    print(error_msg)
        
        # Создание векторной базы данных вакансий
        if chunks_vacancies:
            try:
                db_vacancies = create_vector_db(
                    chunks_vacancies, 
                    save_path=self.document_store.db_path, 
                    index_name='db_vacancies'
                )
                print(f"Создана векторная база данных из {len(chunks_vacancies)} вакансий")
            except Exception as e:
                error_msg = f"Ошибка при создании векторной базы вакансий: {str(e)}"
                logger.error(error_msg)
                print(error_msg)
    
    def _process_resume_files(self):
        """
        Обрабатывает PDF-файлы резюме и создает векторную базу.
        """
        chunks_resumes = []
        
        for file in os.listdir(self.document_store.resumes_pdf_path):
            if file.endswith('.pdf'):
                try:
                    # Полный путь к файлу
                    file_path = os.path.join(self.document_store.resumes_pdf_path, file)
                    
                    # Чтение PDF и преобразование в текст
                    resume_text = read_pdf(file_path)
                    if not resume_text:
                        print(f"Пустой текст в файле резюме: {file}")
                        continue
                    
                    # Парсинг текста резюме
                    resume_id = file.split('.')[0]  # Имя файла без расширения .pdf
                    
                    # Парсинг текста с использованием LLM
                    dict_resume = to_dict_parser(resume_text, parser_class=Resume, model=self.model)
                    
                    # Добавление дополнительных полей
                    dict_resume['id'] = resume_id
                    dict_resume['resume'] = resume_text
                    
                    # Сохранение в хранилище документов
                    self.document_store.save_document_json(dict_resume, resume_id, 'resume')
                    
                    # Получение чанка для векторной базы
                    chunk = self.document_store.document_to_chunk(resume_id, 'resume')
                    if chunk:
                        chunks_resumes.append(chunk)
                    
                    print(f"Обработано резюме: {file}")
                except Exception as e:
                    error_msg = f"Ошибка при обработке файла резюме {file}: {str(e)}"
                    logger.error(error_msg)
                    print(error_msg)
        
        # Создание векторной базы данных резюме
        if chunks_resumes:
            try:
                db_resumes = create_vector_db(
                    chunks_resumes, 
                    save_path=self.document_store.db_path, 
                    index_name='db_resumes'
                )
                print(f"Создана векторная база данных из {len(chunks_resumes)} резюме")
            except Exception as e:
                error_msg = f"Ошибка при создании векторной базы резюме: {str(e)}"
                logger.error(error_msg)
                print(error_msg)
    
    def search_resumes_for_vacancy(self, vacancy_id: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Поиск подходящих резюме под указанную вакансию.
        
        Args:
            vacancy_id: Идентификатор вакансии
            k: Количество результатов (по умолчанию 3)
            
        Returns:
            Список результатов поиска
        """
        try:
            # Загрузка данных вакансии
            vacancy_data = self.document_store.load_document_json(vacancy_id, 'vacancy')
            if not vacancy_data:
                raise ValueError(f"Вакансия с ID {vacancy_id} не найдена")
            
            # Загрузка векторной базы резюме
            db_resumes = load_vector_db(
                load_path=self.document_store.db_path,
                index_name='db_resumes'
            )
            
            if not db_resumes:
                raise ValueError("Не удалось загрузить векторную базу резюме")
            
            # Поиск подходящих резюме
            scores, resume_ids = similarity_search(vacancy_data['vacancy'], db_resumes, k=k)
            
            # Формирование результатов
            results = []
            for i, (score, resume_id) in enumerate(zip(scores, resume_ids), 1):
                resume_data = self.document_store.load_document_json(resume_id, 'resume')
                results.append({
                    'position': i,
                    'resume_id': resume_id,
                    'score': score,
                    'position_title': resume_data.get('position', 'Не указана'),
                    'skills': resume_data.get('skills', 'Не указаны')
                })
            
            return results
        except Exception as e:
            error_msg = f"Ошибка при поиске резюме для вакансии {vacancy_id}: {str(e)}"
            logger.error(error_msg)
            print(error_msg)
            return []
    
    def search_vacancies_for_resume(self, resume_id: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Поиск подходящих вакансий под указанное резюме.
        
        Args:
            resume_id: Идентификатор резюме
            k: Количество результатов (по умолчанию 3)
            
        Returns:
            Список результатов поиска
        """
        try:
            # Загрузка данных резюме
            resume_data = self.document_store.load_document_json(resume_id, 'resume')
            if not resume_data:
                raise ValueError(f"Резюме с ID {resume_id} не найдено")
            
            # Загрузка векторной базы вакансий
            db_vacancies = load_vector_db(
                load_path=self.document_store.db_path,
                index_name='db_vacancies'
            )
            
            if not db_vacancies:
                raise ValueError("Не удалось загрузить векторную базу вакансий")
            
            # Поиск подходящих вакансий
            scores, vacancy_ids = similarity_search(resume_data['resume'], db_vacancies, k=k)
            
            # Формирование результатов
            results = []
            for i, (score, vacancy_id) in enumerate(zip(scores, vacancy_ids), 1):
                vacancy_data = self.document_store.load_document_json(vacancy_id, 'vacancy')
                results.append({
                    'position': i,
                    'vacancy_id': vacancy_id,
                    'score': score,
                    'position_title': vacancy_data.get('position', 'Не указана'),
                    'company': vacancy_data.get('company', 'Не указана')
                })
            
            return results
        except Exception as e:
            error_msg = f"Ошибка при поиске вакансий для резюме {resume_id}: {str(e)}"
            logger.error(error_msg)
            print(error_msg)
            return []
    
    def conduct_interview(self, resume_id: str, vacancy_id: str) -> str:
        """
        Проводит собеседование с кандидатом.
        
        Args:
            resume_id: Идентификатор резюме
            vacancy_id: Идентификатор вакансии
            
        Returns:
            Путь к файлу с оценкой кандидата
        """
        try:
            # Загрузка данных резюме и вакансии
            resume_data = self.document_store.load_document_json(resume_id, 'resume')
            vacancy_data = self.document_store.load_document_json(vacancy_id, 'vacancy')
            
            if not resume_data or not vacancy_data:
                raise ValueError("Не удалось загрузить данные резюме или вакансии")
            
            # Определение позиции кандидата
            candidate_position = vacancy_data.get('position', 'Специалист')
            company_name = vacancy_data.get('company', 'компания')
            resume_text = resume_data.get('resume', '')
            vacancy_text = vacancy_data.get('vacancy', '')
            
            # Загрузка общих вопросов
            questions_file = os.path.join(self.document_store.add_data_path, 'general_questions.json')
            try:
                general_questions = load_general_questions(questions_file)
            except Exception:
                # Создаем базовый набор вопросов, если файл не найден
                general_questions = {
                    'Python_Dev': [
                        "1. Расскажите о вашем опыте работы с Python.",
                        "2. Какие фреймворки Python вы использовали?",
                        "3. Расскажите о наиболее сложном проекте.",
                        "4. Как вы организуете код?",
                        "5. Какие инструменты тестирования вы использовали?"
                    ],
                    'Head_of_sales': [
                        "1. Расскажите о вашем опыте управления продажами.",
                        "2. Какие методики повышения эффективности продаж вы использовали?",
                        "3. Как вы мотивируете команду?",
                        "4. Расскажите о успешном проекте по увеличению продаж.",
                        "5. Как вы работаете с ключевыми клиентами?"
                    ],
                    'HR_Director': [
                        "1. Расскажите о вашем опыте в HR.",
                        "2. Какие методики оценки персонала вы использовали?",
                        "3. Как вы строите адаптацию новых сотрудников?",
                        "4. Расскажите о сложном HR-проекте.",
                        "5. Как вы работаете с корпоративной культурой?"
                    ]
                }
                
                # Сохраняем для будущего использования
                os.makedirs(self.document_store.add_data_path, exist_ok=True)
                with open(questions_file, 'w', encoding='utf-8') as f:
                    json.dump(general_questions, f, ensure_ascii=False, indent=2)
            
            # Выбор вопросов для позиции
            questions = select_questions_for_position(candidate_position, general_questions)
            
            print(f"
=== Начало собеседования для кандидата на позицию {candidate_position} ===
")
            
            # Проведение первой части собеседования
            interview_summary = conduct_interview(resume_text, questions)
            
            # Генерация дополнительных вопросов
            print("
=== Анализ ответов и генерация дополнительных вопросов ===
")
            additional_questions = generate_additional_questions(
                interview_summary, 
                vacancy_text, 
                candidate_position, 
                model='gpt-4o'
            )
            
            # Проведение второй части собеседования
            print("
=== Продолжение собеседования с дополнительными вопросами ===
")
            additional_responses = ask_additional_questions(additional_questions)
            
            # Объединение результатов собеседования
            full_interview = interview_summary + "

Дополнительные вопросы и ответы:

" + "
".join(additional_responses)
            
            # Презентация компании и вакансии
            print("
=== Презентация компании и вакансии ===
")
            company_description = f"""
            О компании "{company_name}"
            
            Компания "{company_name}" - одна из ведущих компаний в своей отрасли. Мы стремимся к инновациям и постоянному развитию, создавая продукты и услуги высокого качества. Наша команда состоит из квалифицированных специалистов, которые ценят профессионализм, творческий подход и взаимное уважение.
            
            О вакансии "{candidate_position}"
            
            Мы ищем талантливого специалиста на позицию "{candidate_position}".
            
            Требуемые навыки:
            {vacancy_data.get('skills', 'Различные профессиональные навыки в зависимости от опыта кандидата')}
            
            Мы предлагаем:
            - Официальное трудоустройство согласно ТК РФ
            - Конкурентную заработную плату
            - Возможности для профессионального роста и развития
            - Дружный коллектив и комфортные условия работы
            - Современный офис в удобном месте
            
            Присоединяйтесь к нашей команде и развивайтесь вместе с нами!
            """
            
            present_company_and_vacancy(company_description)
            
            # Ответы на вопросы кандидата
            print("
=== Ответы на вопросы кандидата ===
")
            
            # Загрузка или создание базы данных с ответами HR
            hr_answers_file = os.path.join(self.document_store.add_data_path, 'hr_answers.txt')
            try:
                db_hr_answers = db_from_markdown_file(
                    hr_answers_file,
                    save_path=self.document_store.db_path,
                    index_name='db_hr_answers'
                )
            except Exception as e:
                # Если файл не найден или произошла ошибка, создаем базовый файл
                basic_hr_answers = f"""
                # Ответы HR на вопросы кандидатов
                
                # Ответы HR для позиции: {candidate_position}
                
                ## О компании
                Наша компания {company_name} - один из лидеров в своей отрасли. Мы стремимся к инновациям и постоянному развитию, создавая продукты и услуги высокого качества. Наша команда состоит из квалифицированных специалистов, которые ценят профессионализм, творческий подход и взаимное уважение.
                
                ## О позиции {candidate_position}
                Мы ищем талантливого специалиста на позицию {candidate_position}. Требуемые навыки: {vacancy_data.get('skills', 'различные профессиональные навыки в зависимости от опыта кандидата')}.
                
                ## Процесс трудоустройства
                Процесс трудоустройства включает первичное собеседование с HR, техническое собеседование и финальную встречу с руководителем. После успешного прохождения всех этапов мы делаем предложение о работе.
                
                ## Выплаты и льготы
                Мы предлагаем конкурентную заработную плату, официальное трудоустройство, ДМС, корпоративное обучение и другие бенефиты для сотрудников.
                """
                
                with open(hr_answers_file, 'w', encoding='utf-8') as f:
                    f.write(basic_hr_answers)
                
                db_hr_answers = db_from_markdown_file(
                    hr_answers_file,
                    save_path=self.document_store.db_path,
                    index_name='db_hr_answers'
                )
            
            handle_candidate_questions(candidate_position, db_hr_answers, model='gpt-4o')
            
            # Определение ключевых требований
            print("
=== Определение ключевых требований к кандидату ===
")
            key_requirements = define_key_requirements(vacancy_text, candidate_position)
            
            # Генерация итоговой оценки
            print("
=== Генерация итоговой оценки кандидата ===
")
            assessment = generate_final_assessment(
                full_interview, 
                vacancy_text, 
                key_requirements, 
                candidate_position, 
                company_name
            )
            
            # Сохранение оценки в файл
            assessment_file = save_assessment_report(
                assessment, 
                candidate_position, 
                resume_id, 
                company_name, 
                'Локальная база', 
                self.data_path
            )
            
            print(f"
=== Собеседование завершено! ===
")
            print(f"Итоговая оценка сохранена в файл: {assessment_file}")
            
            return assessment_file
        except Exception as e:
            error_msg = f"Ошибка при проведении собеседования: {str(e)}"
            logger.error(error_msg)
            print(error_msg)
            return None

# Основная функция для запуска системы из командной строки
def main():
    """Основная функция для запуска системы из командной строки."""
    
    parser = argparse.ArgumentParser(description='НейроHR - система для проведения собеседований')
    parser.add_argument('--data-path', type=str, default='./data', help='Путь к директории с данными')
    parser.add_argument('--action', type=str, choices=['process', 'search-resumes', 'search-vacancies', 'interview'],
                       required=True, help='Действие для выполнения')
    parser.add_argument('--resume-id', type=str, help='ID резюме для поиска вакансий или собеседования')
    parser.add_argument('--vacancy-id', type=str, help='ID вакансии для поиска резюме или собеседования')
    parser.add_argument('--count', type=int, default=3, help='Количество результатов поиска')
    args = parser.parse_args()
    
    # Создание экземпляра системы
    hr_system = HRSystem(data_path=args.data_path)
    
    # Выполнение выбранного действия
    if args.action == 'process':
        # Обработка PDF-файлов
        hr_system.process_pdf_files()
    elif args.action == 'search-resumes':
        # Поиск резюме под вакансию
        if not args.vacancy_id:
            print("Ошибка: не указан ID вакансии (--vacancy-id)")
            return
        
        results = hr_system.search_resumes_for_vacancy(args.vacancy_id, k=args.count)
        
        print(f"
Результаты поиска резюме для вакансии {args.vacancy_id}:")
        for result in results:
            print(f"{result['position']}. ID: {result['resume_id']}, "
                  f"Позиция: {result['position_title']}, "
                  f"Оценка схожести: {result['score']:.4f}")
    elif args.action == 'search-vacancies':
        # Поиск вакансий под резюме
        if not args.resume_id:
            print("Ошибка: не указан ID резюме (--resume-id)")
            return
        
        results = hr_system.search_vacancies_for_resume(args.resume_id, k=args.count)
        
        print(f"
Результаты поиска вакансий для резюме {args.resume_id}:")
        for result in results:
            print(f"{result['position']}. ID: {result['vacancy_id']}, "
                  f"Позиция: {result['position_title']}, "
                  f"Компания: {result.get('company', 'Не указана')}, "
                  f"Оценка схожести: {result['score']:.4f}")
    elif args.action == 'interview':
        # Проведение собеседования
        if not args.resume_id or not args.vacancy_id:
            print("Ошибка: не указаны ID резюме (--resume-id) и ID вакансии (--vacancy-id)")
            return
        
        hr_system.conduct_interview(args.resume_id, args.vacancy_id)
    
if __name__ == "__main__":
    main()
