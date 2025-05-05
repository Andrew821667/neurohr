# НейроHR

Система для проведения собеседований с использованием нейросетей.

## Описание

НейроHR - это инструмент для автоматизации процесса подбора персонала, который использует искусственный интеллект и нейросети для анализа резюме, поиска подходящих кандидатов, проведения собеседований и оценки результатов.

## Возможности

- Парсинг PDF-файлов резюме и вакансий
- Векторизация документов и создание базы данных для быстрого поиска
- Поиск релевантных резюме под конкретную вакансию
- Поиск релевантных вакансий под конкретное резюме
- Проведение автоматизированных собеседований с использованием нейросетей
- Генерация дополнительных вопросов на основе ответов кандидата
- Презентация компании и вакансии кандидату
- Ответы на вопросы кандидата с использованием векторной базы знаний
- Формирование итоговой оценки кандидата с рекомендацией по найму

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/hr_assistant.git
cd hr_assistant

# Установка зависимостей
pip install -r requirements.txt

# Установка пакета в режиме разработки
pip install -e .
```

## Настройка

1. Создайте файл `.env` в корневой директории проекта со следующим содержимым:

```
OPENAI_API_KEY=ваш_ключ_api_openai
```

2. Создайте структуру каталогов для хранения данных:

```
data/
  ├── vacancies_pdf/      # PDF-файлы вакансий
  ├── vacancies_json/     # Обработанные данные вакансий в JSON
  ├── resumes_pdf/        # PDF-файлы резюме
  ├── resumes_json/       # Обработанные данные резюме в JSON
  ├── db_faiss/           # Векторные базы данных
  └── add_data/           # Дополнительные данные
```

## Использование

### Обработка PDF-файлов

```bash
python -m neurohr --action process --data-path ./data
```

### Поиск резюме под конкретную вакансию

```bash
python -m neurohr --action search-resumes --vacancy-id vacancy_123 --count 5
```

### Поиск вакансий под конкретное резюме

```bash
python -m neurohr --action search-vacancies --resume-id resume_456 --count 5
```

### Проведение собеседования

```bash
python -m neurohr --action interview --resume-id resume_456 --vacancy-id vacancy_123
```

## Использование в Jupyter Notebook/Colab

Пример использования в Jupyter Notebook или Google Colab:

```python
from hr_assistant.main import HRSystem

# Инициализация системы
hr_system = HRSystem(data_path='./data')

# Обработка PDF-файлов
hr_system.process_pdf_files()

# Поиск подходящих резюме для вакансии
resumes = hr_system.search_resumes_for_vacancy('Python_Dev_1', k=3)
for resume in resumes:
    print(f"Резюме: {resume['resume_id']}, Позиция: {resume['position_title']}")

# Проведение собеседования
hr_system.conduct_interview('Resume_Python_Dev', 'Python_Dev_1')
```

## Структура проекта

```
hr_assistant/
  ├── hr_utils/              # Утилиты
  │   ├── file_utils.py      # Работа с файлами
  │   ├── api_utils.py       # Работа с API OpenAI
  │   └── audio_utils.py     # Работа с аудио
  ├── hr_models/             # Модели данных
  │   ├── schema.py          # Схемы данных для парсинга
  │   └── document_store.py  # Хранилище документов
  ├── ai_services/           # AI сервисы
  │   ├── parser.py          # Парсинг текста
  │   └── vector_store.py    # Работа с векторными базами
  ├── interview/             # Модули собеседования
  │   ├── question_generator.py  # Генерация вопросов
  │   ├── interviewer.py         # Проведение собеседования
  │   └── assessment.py          # Оценка кандидата
  └── main.py                # Основной модуль приложения
```

## Требования

- Python 3.8+
- OpenAI API ключ
- Зависимости из requirements.txt

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле LICENSE.
