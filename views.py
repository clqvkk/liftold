from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QDateEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QTabWidget, QFormLayout, QHeaderView,
    QGroupBox, QFrame
)
from PyQt5.QtCore import QDate, Qt, QDateTime
from PyQt5.QtGui import QColor, QFont
from database import Database, OrderStatus, ElevatorType
from datetime import datetime, timedelta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Управление заявками на лифты")
        self.setGeometry(100, 100, 1200, 800)
        self._setup_ui()
        self._update_orders_table()

    def _setup_ui(self):
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Создаем вкладки
        self._create_order_tab()
        self._create_orders_list_tab()
        self._create_stats_tab()

    def _create_order_tab(self):
        """Вкладка создания новой заявки"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Группа "Информация о клиенте"
        customer_group = QGroupBox("Информация о клиенте")
        customer_layout = QFormLayout()
        
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("ФИО клиента")
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+7XXXXXXXXXX")
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@example.com")
        self.address = QLineEdit()
        self.address.setPlaceholderText("Адрес установки")
        
        customer_layout.addRow("ФИО*:", self.customer_name)
        customer_layout.addRow("Телефон*:", self.phone)
        customer_layout.addRow("Email:", self.email)
        customer_layout.addRow("Адрес*:", self.address)
        customer_group.setLayout(customer_layout)
        
        # Группа "Характеристики лифта"
        elevator_group = QGroupBox("Характеристики лифта")
        elevator_layout = QFormLayout()
        
        self.elevator_type = QComboBox()
        self.elevator_type.addItems([e.value for e in ElevatorType])
        
        self.floors = QSpinBox()
        self.floors.setRange(1, 100)
        self.floors.setValue(5)
        
        self.capacity = QSpinBox()
        self.capacity.setRange(1, 20)
        self.capacity.setValue(4)
        
        self.installation_date = QDateEdit()
        self.installation_date.setDate(QDate.currentDate().addDays(30))
        self.installation_date.setCalendarPopup(True)
        
        elevator_layout.addRow("Тип лифта*:", self.elevator_type)
        elevator_layout.addRow("Этажи*:", self.floors)
        elevator_layout.addRow("Вместимость*:", self.capacity)
        elevator_layout.addRow("Дата установки:", self.installation_date)
        elevator_group.setLayout(elevator_layout)
        
        # Группа "Дополнительно"
        extra_group = QGroupBox("Дополнительная информация")
        extra_layout = QFormLayout()
        
        self.status = QComboBox()
        self.status.addItems([s.value for s in OrderStatus])
        
        self.priority = QComboBox()
        self.priority.addItems([f"{i} ({'Низкий' if i == 1 else 'Высокий' if i == 5 else 'Средний'})" 
                              for i in range(1, 6)])
        self.priority.setCurrentIndex(2)  # Средний приоритет по умолчанию
        
        self.manager = QLineEdit()
        self.manager.setPlaceholderText("Ответственный менеджер")
        
        self.price = QLineEdit()
        self.price.setPlaceholderText("Стоимость в рублях")
        
        self.comments = QTextEdit()
        self.comments.setPlaceholderText("Дополнительные комментарии...")
        
        extra_layout.addRow("Статус:", self.status)
        extra_layout.addRow("Приоритет:", self.priority)
        extra_layout.addRow("Менеджер:", self.manager)
        extra_layout.addRow("Стоимость:", self.price)
        extra_layout.addRow("Комментарии:", self.comments)
        extra_group.setLayout(extra_layout)
        
        # Кнопка создания заявки
        create_btn = QPushButton("Создать заявку")
        create_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        create_btn.clicked.connect(self._create_order)
        
        # Добавляем все на вкладку
        layout.addWidget(customer_group)
        layout.addWidget(elevator_group)
        layout.addWidget(extra_group)
        layout.addWidget(create_btn)
        
        self.tabs.addTab(tab, "Новая заявка")

    def _create_orders_list_tab(self):
        """Вкладка списка заявок с поиском и фильтрами"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Панель поиска и фильтров
        filter_frame = QFrame()
        filter_layout = QVBoxLayout()
        filter_frame.setLayout(filter_layout)
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по клиенту, телефону или адресу...")
        self.search_input.textChanged.connect(self._update_orders_table)
        
        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self._update_orders_table)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        filter_layout.addLayout(search_layout)
        
        # Фильтры
        filters_layout = QHBoxLayout()
        
        # Фильтр по статусу
        self.status_filter = QComboBox()
        self.status_filter.addItem("Все статусы", None)
        for status in OrderStatus:
            self.status_filter.addItem(status.value, status.value)
        self.status_filter.currentIndexChanged.connect(self._update_orders_table)
        
        # Фильтр по типу лифта
        self.type_filter = QComboBox()
        self.type_filter.addItem("Все типы", None)
        for elevator_type in ElevatorType:
            self.type_filter.addItem(elevator_type.value, elevator_type.value)
        self.type_filter.currentIndexChanged.connect(self._update_orders_table)
        
        # Фильтр по приоритету
        self.priority_filter = QComboBox()
        self.priority_filter.addItem("Любой приоритет", None)
        for i in range(1, 6):
            self.priority_filter.addItem(f"{i}", i)
        self.priority_filter.currentIndexChanged.connect(self._update_orders_table)
        
        # Фильтр по дате
        date_filter_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        current_date = datetime.now().date()
        date_30_days_ago = current_date - timedelta(days=30)
        q_date_30_days_ago = QDate(date_30_days_ago.year, date_30_days_ago.month, date_30_days_ago.day)
        
        self.date_from.setDate(q_date_30_days_ago)
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.dateChanged.connect(self._update_orders_table)
        
        self.date_to = QDateEdit()
        q_current_date = QDate(current_date.year, current_date.month, current_date.day)
        self.date_to.setDate(q_current_date)
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.dateChanged.connect(self._update_orders_table)
        
        date_filter_layout.addWidget(QLabel("С:"))
        date_filter_layout.addWidget(self.date_from)
        date_filter_layout.addWidget(QLabel("По:"))
        date_filter_layout.addWidget(self.date_to)
        
        # Кнопка сброса
        reset_btn = QPushButton("Сбросить фильтры")
        reset_btn.clicked.connect(self._reset_filters)
        
        # Добавляем фильтры
        filters_layout.addWidget(QLabel("Статус:"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(QLabel("Тип:"))
        filters_layout.addWidget(self.type_filter)
        filters_layout.addWidget(QLabel("Приоритет:"))
        filters_layout.addWidget(self.priority_filter)
        filters_layout.addWidget(reset_btn)
        
        filter_layout.addLayout(filters_layout)
        filter_layout.addLayout(date_filter_layout)
        layout.addWidget(filter_frame)
        
        # Таблица заявок
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(12)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Клиент", "Телефон", "Адрес", "Тип", 
            "Этажи", "Вмест.", "Статус", "Приор.", "Дата", "Цена", "Менеджер"
        ])
        
        # Настройка таблицы
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Клиент
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Адрес
        self.orders_table.setSortingEnabled(True)
        self.orders_table.verticalHeader().setVisible(False)
        
        # Двойной клик для редактирования
        self.orders_table.doubleClicked.connect(self._edit_order)
        
        layout.addWidget(self.orders_table)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self._edit_selected_order)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self._delete_selected_order)
        self.delete_btn.setEnabled(False)
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self._update_orders_table)
        
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Выделение строки
        self.orders_table.itemSelectionChanged.connect(self._update_buttons_state)
        
        self.tabs.addTab(tab, "Все заявки")

    def _create_stats_tab(self):
        """Вкладка статистики"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Заголовок
        title = QLabel("Статистика заявок")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Статистика по статусам
        status_group = QGroupBox("Статистика по статусам")
        status_layout = QVBoxLayout()
        self.status_stats_label = QLabel()
        self.status_stats_label.setAlignment(Qt.AlignLeft)
        status_layout.addWidget(self.status_stats_label)
        status_group.setLayout(status_layout)
        
        # Статистика по приоритетам
        priority_group = QGroupBox("Статистика по приоритетам")
        priority_layout = QVBoxLayout()
        self.priority_stats_label = QLabel()
        self.priority_stats_label.setAlignment(Qt.AlignLeft)
        priority_layout.addWidget(self.priority_stats_label)
        priority_group.setLayout(priority_layout)
        
        # Добавляем группы на вкладку
        layout.addWidget(status_group)
        layout.addWidget(priority_group)
        layout.addStretch()
        
        # Кнопка обновления
        refresh_btn = QPushButton("Обновить статистику")
        refresh_btn.clicked.connect(self._update_stats)
        layout.addWidget(refresh_btn)
        
        self.tabs.addTab(tab, "Статистика")
        self._update_stats()

    def _update_orders_table(self):
        """Обновляет таблицу с учетом фильтров"""
        search_query = self.search_input.text().strip()
        status_filter = self.status_filter.currentData()
        elevator_type = self.type_filter.currentData()
        priority = self.priority_filter.currentData()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        orders = self.db.search_orders(
            search_query=search_query,
            status_filter=status_filter,
            elevator_type=elevator_type,
            priority=priority,
            date_from=date_from,
            date_to=date_to
        )
        
        self.orders_table.setRowCount(len(orders))
        
        for row_idx, order in enumerate(orders):
            self._add_order_to_table(row_idx, order)

    def _add_order_to_table(self, row_idx: int, order: dict[str, any]):
        """Добавляет заявку в таблицу"""
        self.orders_table.setItem(row_idx, 0, QTableWidgetItem(str(order['id'])))
        self.orders_table.setItem(row_idx, 1, QTableWidgetItem(order['customer_name']))
        self.orders_table.setItem(row_idx, 2, QTableWidgetItem(order['phone']))
        self.orders_table.setItem(row_idx, 3, QTableWidgetItem(order['address']))
        self.orders_table.setItem(row_idx, 4, QTableWidgetItem(order['elevator_type']))
        self.orders_table.setItem(row_idx, 5, QTableWidgetItem(str(order['floors'])))
        self.orders_table.setItem(row_idx, 6, QTableWidgetItem(str(order['capacity'])))
        
        status_item = QTableWidgetItem(order['status'])
        self._set_status_color(status_item, order['status'])
        self.orders_table.setItem(row_idx, 7, status_item)
        
        priority_item = QTableWidgetItem(str(order['priority']))
        self._set_priority_color(priority_item, order['priority'])
        self.orders_table.setItem(row_idx, 8, priority_item)
        
        self.orders_table.setItem(row_idx, 9, QTableWidgetItem(order['created_at']))
        self.orders_table.setItem(row_idx, 10, QTableWidgetItem(str(order.get('price', ''))))
        self.orders_table.setItem(row_idx, 11, QTableWidgetItem(order.get('manager', '')))

    def _set_status_color(self, item: QTableWidgetItem, status: str):
        """Устанавливает цвет в зависимости от статуса"""
        colors = {
            "Новая": QColor(200, 255, 200),     # Светло-зеленый
            "В работе": QColor(255, 255, 150),   # Светло-желтый
            "Завершена": QColor(200, 200, 255),  # Светло-синий
            "Отменена": QColor(255, 200, 200)    # Светло-красный
        }
        item.setBackground(colors.get(status, QColor(255, 255, 255)))

    def _set_priority_color(self, item: QTableWidgetItem, priority: int):
        """Устанавливает цвет в зависимости от приоритета"""
        if priority >= 4:
            item.setBackground(QColor(255, 150, 150))  # Красный
        elif priority == 3:
            item.setBackground(QColor(255, 255, 150))  # Желтый
        else:
            item.setBackground(QColor(150, 255, 150))  # Зеленый

    def _reset_filters(self):
        """Сбрасывает все фильтры"""
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.priority_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate() - timedelta(days=30))
        self.date_to.setDate(QDate.currentDate())
        self._update_orders_table()

    def _update_buttons_state(self):
        """Обновляет состояние кнопок в зависимости от выбора"""
        selected = len(self.orders_table.selectedItems()) > 0
        self.edit_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)

    def _create_order(self):
        """Создает новую заявку"""
        # Проверка обязательных полей
        if not all([
            self.customer_name.text().strip(),
            self.phone.text().strip(),
            self.address.text().strip()
        ]):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля (помечены *)")
            return
        
        try:
            order_data = {
                'customer_name': self.customer_name.text(),
                'phone': self.phone.text(),
                'email': self.email.text(),
                'address': self.address.text(),
                'elevator_type': self.elevator_type.currentText(),
                'floors': self.floors.value(),
                'capacity': self.capacity.value(),
                'installation_date': self.installation_date.date().toString("yyyy-MM-dd"),
                'status': self.status.currentText(),
                'priority': self.priority.currentIndex() + 1,
                'manager': self.manager.text(),
                'price': float(self.price.text()) if self.price.text() else None,
                'comments': self.comments.toPlainText()
            }
            
            order_id = self.db.create_order(order_data)
            if order_id:
                QMessageBox.information(self, "Успех", f"Заявка #{order_id} создана!")
                self._clear_form()
                self._update_orders_table()
                self.tabs.setCurrentIndex(1)  # Переключаемся на список заявок
                self._update_stats()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать заявку")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка данных", f"Проверьте правильность введенных данных: {str(e)}")

    def _clear_form(self):
        """Очищает форму создания заявки"""
        self.customer_name.clear()
        self.phone.clear()
        self.email.clear()
        self.address.clear()
        self.elevator_type.setCurrentIndex(0)
        self.floors.setValue(5)
        self.capacity.setValue(4)
        self.installation_date.setDate(QDate.currentDate().addDays(30))
        self.status.setCurrentIndex(0)
        self.priority.setCurrentIndex(2)
        self.manager.clear()
        self.price.clear()
        self.comments.clear()

    def _edit_selected_order(self):
        """Редактирует выбранную заявку"""
        selected = self.orders_table.selectedItems()
        if selected:
            order_id = int(self.orders_table.item(selected[0].row(), 0).text())
            self._edit_order_dialog(order_id)

    def _edit_order(self, index):
        """Редактирует заявку по двойному клику"""
        order_id = int(self.orders_table.item(index.row(), 0).text())
        self._edit_order_dialog(order_id)

    def _edit_order_dialog(self, order_id: int):
        """Диалог редактирования заявки"""
        order = self.db.get_order_by_id(order_id)
        if not order:
            QMessageBox.warning(self, "Ошибка", "Заявка не найдена")
            return
        
        # Создаем диалоговое окно редактирования
        dialog = QWidget()
        dialog.setWindowTitle(f"Редактирование заявки #{order_id}")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Форма редактирования
        form = QFormLayout()
        
        customer_name = QLineEdit(order['customer_name'])
        phone = QLineEdit(order['phone'])
        email = QLineEdit(order.get('email', ''))
        address = QLineEdit(order['address'])
        
        elevator_type = QComboBox()
        elevator_type.addItems([e.value for e in ElevatorType])
        elevator_type.setCurrentText(order['elevator_type'])
        
        floors = QSpinBox()
        floors.setRange(1, 100)
        floors.setValue(order['floors'])
        
        capacity = QSpinBox()
        capacity.setRange(1, 20)
        capacity.setValue(order['capacity'])
        
        installation_date = QDateEdit()
        installation_date.setDate(QDate.fromString(order.get('installation_date', ''), "yyyy-MM-dd"))
        installation_date.setCalendarPopup(True)
        
        status = QComboBox()
        status.addItems([s.value for s in OrderStatus])
        status.setCurrentText(order['status'])
        
        priority = QComboBox()
        priority.addItems([f"{i}" for i in range(1, 6)])
        priority.setCurrentText(str(order['priority']))
        
        manager = QLineEdit(order.get('manager', ''))
        price = QLineEdit(str(order.get('price', '')))
        comments = QTextEdit(order.get('comments', ''))
        
        # Добавляем поля в форму
        form.addRow("ФИО клиента*:", customer_name)
        form.addRow("Телефон*:", phone)
        form.addRow("Email:", email)
        form.addRow("Адрес*:", address)
        form.addRow("Тип лифта*:", elevator_type)
        form.addRow("Этажи*:", floors)
        form.addRow("Вместимость*:", capacity)
        form.addRow("Дата установки:", installation_date)
        form.addRow("Статус:", status)
        form.addRow("Приоритет:", priority)
        form.addRow("Менеджер:", manager)
        form.addRow("Стоимость:", price)
        form.addRow("Комментарии:", comments)
        
        layout.addLayout(form)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self._save_order_changes(
            order_id, {
                'customer_name': customer_name.text(),
                'phone': phone.text(),
                'email': email.text(),
                'address': address.text(),
                'elevator_type': elevator_type.currentText(),
                'floors': floors.value(),
                'capacity': capacity.value(),
                'installation_date': installation_date.date().toString("yyyy-MM-dd"),
                'status': status.currentText(),
                'priority': int(priority.currentText()),
                'manager': manager.text(),
                'price': float(price.text()) if price.text() else None,
                'comments': comments.toPlainText()
            },
            dialog
        ))
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.show()

    def _save_order_changes(self, order_id: int, update_data: dict[str, any], dialog: QWidget):
        """Сохраняет изменения в заявке"""
        if not all([
            update_data['customer_name'].strip(),
            update_data['phone'].strip(),
            update_data['address'].strip()
        ]):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля (помечены *)")
            return
        
        try:
            if self.db.update_order(order_id, update_data):
                QMessageBox.information(self, "Успех", "Изменения сохранены")
                dialog.close()
                self._update_orders_table()
                self._update_stats()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изменения")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка данных", f"Проверьте правильность введенных данных: {str(e)}")

    def _delete_selected_order(self):
        """Удаляет выбранную заявку"""
        selected = self.orders_table.selectedItems()
        if not selected:
            return
            
        order_id = int(self.orders_table.item(selected[0].row(), 0).text())
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Вы уверены, что хотите удалить заявку #{order_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_order(order_id):
                QMessageBox.information(self, "Успех", "Заявка удалена")
                self._update_orders_table()
                self._update_stats()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить заявку")

    def _update_stats(self):
        """Обновляет статистику"""
        status_stats = self.db.get_status_stats()
        priority_stats = self.db.get_priority_stats()
        
        # Форматируем статистику по статусам
        status_text = "\n".join([
            f"{status}: {count} заявок" 
            for status, count in status_stats.items()
        ])
        self.status_stats_label.setText(status_text)
        
        # Форматируем статистику по приоритетам
        priority_text = "\n".join([
            f"Приоритет {priority}: {count} заявок" 
            for priority, count in sorted(priority_stats.items())
        ])
        self.priority_stats_label.setText(priority_text)