# -*- coding: utf-8 -*-
import os
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_community.docstore.document import Document

logger = logging.getLogger('hr_system')

class DocumentStore:
    """Класс для управления хранилищем документов (резюме и вакансий)."""
    
    def __init__(self, base_path='./data'):
        """
        Инициализация хранилища документов.
        
        Args:
            base_path: Базовый путь для хранения данных
        """
        self.base_path = base_path
        self.vacancies_pdf_path = os.path.join(base_path, 'vacancies_pdf')
        self.vacancies_json_path = os.path.join(base_path, 'vacancies_json')
        self.resumes_pdf_path = os.path.join(base_path, 'resumes_pdf')
        self.resumes_json_path = os.path.join(base_path, 'resumes_json')
        self.db_path = os.path.join(base_path, 'db_faiss')
        self.add_data_path = os.path.join(base_path, 'add_data')
        
        # Создаем все необходимые директории
        self._create_directories()
        
    def _create_directories(self):
        """Создает необходимые директории для хранения данных."""
        paths = [
            self.base_path,
            self.vacancies_pdf_path,
            self.vacancies_json_path,
            self.resumes_pdf_path,
            self.resumes_json_path,
            self.db_path,
            self.add_data_path
        ]
        
        for path in paths:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Создана директория: {path}")
            
    def save_document_json(self, data: Dict[str, Any], doc_id: str, doc_type: str):
        """
        Сохраняет данные документа в JSON формате.
        
        Args:
            data: Данные для сохранения
            doc_id: Идентификатор документа
            doc_type: Тип документа ('vacancy' или 'resume')
        """
        if doc_type == 'vacancy':
            save_path = os.path.join(self.vacancies_json_path, f"{doc_id}.json")
        elif doc_type == 'resume':
            save_path = os.path.join(self.resumes_json_path, f"{doc_id}.json")
        else:
            logger.error(f"Неизвестный тип документа: {doc_type}")
            return False
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранен {doc_type} с ID {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении {doc_type} {doc_id}: {str(e)}")
            return False
            
    def load_document_json(self, doc_id: str, doc_type: str) -> Optional[Dict[str, Any]]:
        """
        Загружает данные документа из JSON формата.
        
        Args:
            doc_id: Идентификатор документа
            doc_type: Тип документа ('vacancy' или 'resume')
            
        Returns:
            Словарь с данными документа или None в случае ошибки
        """
        if doc_type == 'vacancy':
            load_path = os.path.join(self.vacancies_json_path, f"{doc_id}.json")
        elif doc_type == 'resume':
            load_path = os.path.join(self.resumes_json_path, f"{doc_id}.json")
        else:
            logger.error(f"Неизвестный тип документа: {doc_type}")
            return None
        
        try:
            if not os.path.exists(load_path):
                logger.warning(f"Файл {load_path} не существует")
                return None
                
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Загружен {doc_type} с ID {doc_id}")
            return data
        except Exception as e:
            logger.error(f"Ошибка при загрузке {doc_type} {doc_id}: {str(e)}")
            return None
            
    def list_documents(self, doc_type: str) -> List[str]:
        """
        Возвращает список идентификаторов документов указанного типа.
        
        Args:
            doc_type: Тип документа ('vacancy' или 'resume')
            
        Returns:
            Список идентификаторов документов
        """
        if doc_type == 'vacancy':
            path = self.vacancies_json_path
        elif doc_type == 'resume':
            path = self.resumes_json_path
        else:
            logger.error(f"Неизвестный тип документа: {doc_type}")
            return []
        
        try:
            files = [f.split('.')[0] for f in os.listdir(path) if f.endswith('.json')]
            return files
        except Exception as e:
            logger.error(f"Ошибка при получении списка документов {doc_type}: {str(e)}")
            return []
            
    def document_to_chunk(self, doc_id: str, doc_type: str) -> Optional[Document]:
        """
        Преобразует документ в чанк для векторной базы данных.
        
        Args:
            doc_id: Идентификатор документа
            doc_type: Тип документа ('vacancy' или 'resume')
            
        Returns:
            Объект Document для векторной базы данных или None в случае ошибки
        """
        data = self.load_document_json(doc_id, doc_type)
        if not data:
            return None
            
        try:
            if doc_type == 'vacancy':
                chunk = (f"1.Позиция: {data.get('position', '')}. "
                         f"2.Навыки: {data.get('skills', '')}. "
                         f"3.Требования: {data.get('requirements', '')}. "
                         f"4.Обязанности: {data.get('responsibilities', '')}")
            elif doc_type == 'resume':
                chunk = (f"1.Позиция: {data.get('position', '')}. "
                         f"2.Навыки: {data.get('skills', '')}. "
                         f"3.Опыт: {data.get('experience', '')}")
            else:
                logger.error(f"Неизвестный тип документа: {doc_type}")
                return None
                
            return Document(
                page_content=chunk,
                metadata={"meta": doc_id, "type": doc_type}
            )
        except Exception as e:
            logger.error(f"Ошибка при создании чанка для {doc_type} {doc_id}: {str(e)}")
            return None
