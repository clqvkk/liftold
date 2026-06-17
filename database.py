import sqlite3
from sqlite3 import Error
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершена"
    CANCELLED = "Отменена"

class ElevatorType(Enum):
    PASSENGER = "Пассажирский"
    CARGO = "Грузовой"
    HOSPITAL = "Больничный"
    PANTOGRAPH = "Пандусный"

class Database:
    def __init__(self, db_file: str = "elevator_company.db"):
        self.db_file = db_file
        self._initialize_database()

    def _initialize_database(self):
        """Инициализирует БД с правильной структурой"""
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                
                # Создаем таблицу заказов
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    address TEXT NOT NULL,
                    elevator_type TEXT NOT NULL,
                    floors INTEGER NOT NULL,
                    capacity INTEGER NOT NULL,
                    installation_date TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    comments TEXT,
                    priority INTEGER DEFAULT 1,
                    manager TEXT,
                    price REAL
                );
                """)
                
                # Создаем индексы для ускорения поиска
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_name);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_priority ON orders(priority);
                """)
                
                conn.commit()
        except Error as e:
            print(f"Ошибка инициализации БД: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return None

    def create_order(self, order_data: Dict[str, any]) -> Optional[int]:
        """Создает новую заявку"""
        sql = """
        INSERT INTO orders(
            customer_name, phone, email, address, elevator_type, floors, 
            capacity, installation_date, status, created_at, updated_at,
            comments, priority, manager, price
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    order_data['customer_name'],
                    order_data['phone'],
                    order_data.get('email'),
                    order_data['address'],
                    order_data['elevator_type'],
                    order_data['floors'],
                    order_data['capacity'],
                    order_data.get('installation_date'),
                    order_data.get('status', OrderStatus.NEW.value),
                    now,
                    now,
                    order_data.get('comments'),
                    order_data.get('priority', 1),
                    order_data.get('manager'),
                    order_data.get('price')
                ))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Ошибка создания заявки: {e}")
        finally:
            if conn:
                conn.close()
        return None

    def search_orders(self, search_query: str = None, status_filter: str = None, 
                     elevator_type: str = None, priority: int = None,
                     date_from: str = None, date_to: str = None) -> List[Dict[str, any]]:
        """
        Поиск заявок с фильтрацией по:
        - ФИО, телефону или адресу (поиск)
        - Статусу
        - Типу лифта
        - Приоритету
        - Диапазону дат
        """
        sql = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        # Поиск по тексту
        if search_query:
            sql += " AND (customer_name LIKE ? OR phone LIKE ? OR address LIKE ?)"
            params.extend([f"%{search_query}%"] * 3)
        
        # Фильтр по статусу
        if status_filter:
            sql += " AND status = ?"
            params.append(status_filter)
            
        # Фильтр по типу лифта
        if elevator_type:
            sql += " AND elevator_type = ?"
            params.append(elevator_type)
            
        # Фильтр по приоритету
        if priority:
            sql += " AND priority = ?"
            params.append(priority)
            
        # Фильтр по дате
        if date_from:
            sql += " AND date(created_at) >= ?"
            params.append(date_from)
            
        if date_to:
            sql += " AND date(created_at) <= ?"
            params.append(date_to)
            
        sql += " ORDER BY priority DESC, created_at DESC"
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Error as e:
            print(f"Ошибка поиска заявок: {e}")
        finally:
            if conn:
                conn.close()
        return []

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, any]]:
        """Получает заявку по ID"""
        sql = "SELECT * FROM orders WHERE id = ?"
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql, (order_id,))
                row = cursor.fetchone()
                if row:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
        except Error as e:
            print(f"Ошибка получения заявки: {e}")
        finally:
            if conn:
                conn.close()
        return None

    def update_order(self, order_id: int, update_data: Dict[str, any]) -> bool:
        """Обновляет данные заявки"""
        sql = """
        UPDATE orders SET
            customer_name = ?,
            phone = ?,
            email = ?,
            address = ?,
            elevator_type = ?,
            floors = ?,
            capacity = ?,
            installation_date = ?,
            status = ?,
            updated_at = ?,
            comments = ?,
            priority = ?,
            manager = ?,
            price = ?
        WHERE id = ?
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    update_data.get('customer_name'),
                    update_data.get('phone'),
                    update_data.get('email'),
                    update_data.get('address'),
                    update_data.get('elevator_type'),
                    update_data.get('floors'),
                    update_data.get('capacity'),
                    update_data.get('installation_date'),
                    update_data.get('status'),
                    now,
                    update_data.get('comments'),
                    update_data.get('priority'),
                    update_data.get('manager'),
                    update_data.get('price'),
                    order_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Ошибка обновления заявки: {e}")
        finally:
            if conn:
                conn.close()
        return False

    def delete_order(self, order_id: int) -> bool:
        """Удаляет заявку"""
        sql = "DELETE FROM orders WHERE id = ?"
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql, (order_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Ошибка удаления заявки: {e}")
        finally:
            if conn:
                conn.close()
        return False

    def get_status_stats(self) -> Dict[str, int]:
        """Статистика по статусам заявок"""
        sql = "SELECT status, COUNT(*) FROM orders GROUP BY status"
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql)
                return {row[0]: row[1] for row in cursor.fetchall()}
        except Error as e:
            print(f"Ошибка получения статистики: {e}")
        finally:
            if conn:
                conn.close()
        return {}

    def get_priority_stats(self) -> Dict[int, int]:
        """Статистика по приоритетам"""
        sql = "SELECT priority, COUNT(*) FROM orders GROUP BY priority ORDER BY priority"
        
        conn = None
        try:
            conn = self._create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(sql)
                return {row[0]: row[1] for row in cursor.fetchall()}
        except Error as e:
            print(f"Ошибка получения статистики: {e}")
        finally:
            if conn:
                conn.close()
        return {}