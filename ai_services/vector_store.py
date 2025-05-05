# -*- coding: utf-8 -*-
import os
import logging
from typing import List, Tuple, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

logger = logging.getLogger('hr_system')

def create_vector_db(documents: List[Document], save_path: str = None, index_name: str = 'index') -> FAISS:
    """
    Создает векторную базу данных из документов.
    
    Args:
        documents: Список документов
        save_path: Путь для сохранения базы (если None, база не сохраняется)
        index_name: Имя индекса
        
    Returns:
        Векторная база данных FAISS
    """
    try:
        # Создание векторной базы данных
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(documents, embeddings)
        
        # Сохранение базы, если указан путь
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            db.save_local(folder_path=save_path, index_name=index_name)
            logger.info(f"Векторная база данных сохранена: {save_path}/{index_name}")
            
        logger.info(f"Создана векторная база данных из {len(documents)} документов")
        return db
    except Exception as e:
        error_msg = f"Ошибка при создании векторной базы данных: {str(e)}"
        logger.error(error_msg)
        raise

def load_vector_db(load_path: str, index_name: str = 'index') -> Optional[FAISS]:
    """
    Загружает векторную базу данных.
    
    Args:
        load_path: Путь для загрузки базы
        index_name: Имя индекса
        
    Returns:
        Векторная база данных FAISS или None в случае ошибки
    """
    try:
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local(
            folder_path=load_path,
            allow_dangerous_deserialization=True,
            embeddings=embeddings,
            index_name=index_name
        )
        logger.info(f"Загружена векторная база данных: {load_path}/{index_name}")
        return db
    except Exception as e:
        error_msg = f"Ошибка при загрузке векторной базы данных: {str(e)}"
        logger.error(error_msg)
        return None

def similarity_search(query: str, db: FAISS, k: int = 3) -> Tuple[List[float], List[str]]:
    """
    Поиск наиболее похожих документов в векторной базе данных.
    
    Args:
        query: Текст запроса
        db: Векторная база данных
        k: Количество результатов
        
    Returns:
        Кортеж (список оценок, список метаданных)
    """
    try:
        # Поиск наиболее похожих документов
        docs_and_scores = db.similarity_search_with_score(query, k=k)
        
        # Извлечение оценок и метаданных
        scores = [doc[1] for doc in docs_and_scores]
        meta_data = [doc[0].metadata['meta'] for doc in docs_and_scores]
        
        logger.info(f"Найдено {len(docs_and_scores)} документов по запросу")
        return scores, meta_data
    except Exception as e:
        error_msg = f"Ошибка при поиске в векторной базе данных: {str(e)}"
        logger.error(error_msg)
        return [], []

def db_from_markdown_file(markdown_file: str, save_path: str = None, index_name: str = 'index') -> Optional[FAISS]:
    """
    Создает векторную базу данных из Markdown файла.
    
    Args:
        markdown_file: Путь к Markdown файлу
        save_path: Путь для сохранения базы (если None, база не сохраняется)
        index_name: Имя индекса
        
    Returns:
        Векторная база данных FAISS или None в случае ошибки
    """
    try:
        # Чтение Markdown файла
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_info = f.read()

        # Дублирование строк с заголовками
        markdown_info = duplicate_lines(markdown_info)

        # Определение заголовков для разбиения
        headers_to_split_on = [("#", "Header 1")]

        # Создание сплиттера и разбиение текста
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        chunks = splitter.split_text(markdown_info)

        # Создание векторной базы данных
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(chunks, embeddings)
        
        # Сохранение базы, если указан путь
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            db.save_local(folder_path=save_path, index_name=index_name)
            logger.info(f"Векторная база данных сохранена: {save_path}/{index_name}")

        logger.info(f"Создана векторная база из {len(chunks)} чанков из Markdown файла")
        return db
    except Exception as e:
        error_msg = f"Ошибка при создании векторной базы из Markdown: {str(e)}"
        logger.error(error_msg)
        return None

def duplicate_lines(text: str) -> str:
    """
    Дублирует строки, начинающиеся с символа '#', удаляя этот символ в дубликате.
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст с дублированными строками
    """
    lines = text.split('\n')
    result = []
    for line in lines:
        if line.startswith('#'):
            result.append(line)
        result.append(line.lstrip('# '))
    return '\n'.join(result)
