import re
import sys
from datetime import datetime, timedelta

import mysql.connector
from mysql.connector import Error

from PyQt6 import QtCore
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QHeaderView, QTableWidgetItem, QListWidget, QVBoxLayout,
    QDialog, QComboBox, QTextEdit
)
class ProductDeleteWindow(QWidget):
    def __init__(self, product_prosmotr_window):
        super().__init__()
        self.product_prosmotr_window = product_prosmotr_window  # Сохраняем ссылку на окно просмотра продукции
        self.setGeometry(800, 430, 400, 150)
        self.setFixedSize(400, 150)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Удаление продукта")
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.title_label = QLabel("Удаление продукта", self)
        self.title_label.setGeometry(20, 5, 200, 35)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        self.confirm_button = QPushButton("Закрыть", self)
        self.confirm_button.setGeometry(270, 20, 120, 40)
        self.confirm_button.clicked.connect(self.close_ap)  # Закрываем окно при нажатии
        self.confirm_button.setStyleSheet(button_style)

        self.cancel_button = QPushButton("Удалить", self)
        self.cancel_button.setGeometry(270, 70, 120, 40)
        self.cancel_button.clicked.connect(self.confirm_delete)  # Подключаем к методу подтверждения удаления
        self.cancel_button.setStyleSheet(button_style)

        self.naim_product = QLabel("Наименование продукта", self)
        self.naim_product.setGeometry(40, 40, 200, 30)
        self.naim_product.setStyleSheet("font-size: 14px; color: #333;")
        self.naim_input = QLineEdit(self)
        self.naim_input.setGeometry(20, 70, 200, 25)
        self.naim_input.setMaxLength(25)
        self.naim_input.setStyleSheet("font-size: 12px; background-color: white;")
        regex = QRegularExpression(r'^[А-Яа-яЁё\s]+$')  # Разрешаем кириллические и латинские буквы и пробелы
        validator = QRegularExpressionValidator(regex, self.naim_input)
        self.naim_input.setValidator(validator)

        self.show()

    def close_ap(self):
        self.product_prosmotr_window.set_buttons_enabled(True)  # Разблокируем кнопки
        self.close()

    def confirm_delete(self):
        product_name = self.naim_input.text().strip()  # Получаем имя продукта из поля ввода и убираем лишние пробелы
        if not product_name:  # Проверяем, пустое ли поле
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите наименование продукта для удаления.")
            return  # Выходим из метода, если поле пустое

        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )
            cursor = connection.cursor()
            cursor.execute("DELETE FROM product WHERE naimenovanie = %s", (product_name,))
            connection.commit()
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Удаление", f"Продукт '{product_name}' был успешно удален!")
                self.product_prosmotr_window.clear_fields()  # Очищаем поля ввода после удаления
            else:
                QMessageBox.warning(self, "Удаление", f"Продукт '{product_name}' не найден.")
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении продукта: {error}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
            self.product_prosmotr_window.set_buttons_enabled(True)  # Разблокируем кнопки
            self.close()  # Закрываем окно подтверждения

class ProductAddWindow(QWidget):
    def __init__(self, product_window):
        super().__init__()
        self.product_window = product_window  # Сохраняем ссылку на окно продукции
        self.setGeometry(700, 300, 600, 420)
        self.setFixedSize(600, 420)
        self.setWindowTitle("Добавление продукта")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        # Заголовок
        self.title_label = QLabel("Добавьте новый продукт", self)
        self.title_label.setGeometry(10, 10, 260, 35)
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        # Поля ввода
        self.naimenovanie_label = QLabel("Наименование", self)
        self.naimenovanie_label.setGeometry(10, 50, 200, 30)
        self.naimenovanie_label.setStyleSheet("font-size: 14px;")
        self.naimenovanie_input = QLineEdit(self)
        self.naimenovanie_input.setGeometry(10, 80, 300, 25)
        self.naimenovanie_input.setStyleSheet("font-size: 12px; background-color: white;")

        self.sostav_label = QLabel("Состав", self)
        self.sostav_label.setGeometry(10, 110, 200, 20)
        self.sostav_label.setStyleSheet("font-size: 14px;")
        self.sostav_input = QLineEdit(self)
        self.sostav_input.setGeometry(10, 130, 300, 25)
        self.sostav_input.setStyleSheet("font-size: 12px; background-color: white;")

        self.nutritionalvalue_label = QLabel("Пищевая ценность", self)
        self.nutritionalvalue_label.setGeometry(10, 160, 200, 20)
        self.nutritionalvalue_label.setStyleSheet("font-size: 14px;")
        self.nutritionalvalue_input = QLineEdit(self)
        self.nutritionalvalue_input.setGeometry(10, 180, 300, 25)
        self.nutritionalvalue_input.setStyleSheet("font-size: 12px; background-color: white;")

        self.datepostavki_label = QLabel("Дата поставки", self)
        self.datepostavki_label.setGeometry(10, 210, 200, 20)
        self.datepostavki_label.setStyleSheet("font-size: 14px;")
        self.datepostavki_input = QLineEdit(self)
        self.datepostavki_input.setGeometry(10, 230, 300, 25)
        self.datepostavki_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.datepostavki_input.setInputMask("0000-00-00;_")
        self.datepostavki_input.editingFinished.connect(self.validate_date)
        today = datetime.today().strftime('%Y-%m-%d')
        self.datepostavki_input.setText(today)

        self.srokxran_label = QLabel("Срок хранения до", self)
        self.srokxran_label.setGeometry(10, 260, 200, 20)
        self.srokxran_label.setStyleSheet("font-size: 14px;")

        self.srokxran_input = QLineEdit(self)
        self.srokxran_input.setGeometry(10, 280, 300, 25)
        self.srokxran_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.srokxran_input.setInputMask("0000-00-00;_")
        self.srokxran_input.editingFinished.connect(self.validate_storage_date)
        today = datetime.today()
        min_storage_date = today + timedelta(days=1)
        self.srokxran_input.setText(min_storage_date.strftime('%Y-%m-%d'))

        self.id_sclada_label = QLabel("Выберите склад", self)
        self.id_sclada_label.setGeometry(10, 310, 200, 20)
        self.id_sclada_label.setStyleSheet("font-size: 14px;")

        self.id_sclada_combo = QComboBox(self)
        self.id_sclada_combo.setGeometry(10, 330, 300, 25)
        self.id_sclada_combo.setStyleSheet("font-size: 14px; background-color: white;")
        self.load_warehouses()
        self.id_sclada_combo.currentIndexChanged.connect(self.on_warehouse_selected)

        self.kolvo_label = QLabel("Кол-во на складе", self)
        self.kolvo_label.setGeometry(10, 360, 300, 20)
        self.kolvo_label.setStyleSheet("font-size: 14px;")
        self.kolvo_input = QLineEdit(self)
        self.kolvo_input.setGeometry(10, 380, 300, 25)
        self.kolvo_input.setStyleSheet("font-size: 12px; background-color: white;")

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(470, 110, 120, 40)
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_product)

        self.sbros_button = QPushButton("Сбросить", self)
        self.sbros_button.setGeometry(470, 60, 120, 40)
        self.sbros_button.setStyleSheet(button_style)
        self.sbros_button.clicked.connect(self.reset_fields)

        self.Exit = QPushButton("Закрыть", self)
        self.Exit.setGeometry(470, 10, 120, 40)
        self.Exit.setStyleSheet(button_style)
        self.Exit.clicked.connect(self.close_application)

        self.show()

    def validate_date(self):
        date_text = self.datepostavki_input.text().strip()

        # Проверяем, соответствует ли введенная дата формату YYYY-MM-DD
        if len(date_text) == 10:  # Дата должна быть в формате YYYY-MM-DD
            year = int(date_text[0:4])
            month = int(date_text[5:7])
            day = int(date_text[8:10])

            # Проверяем, не превышает ли дата 31 декабря 2025 года
            if year > 2025 or (year == 2025 and (month > 12 or (month == 12 and day > 31))) or month > 12 or (month == 12 and day > 31) or day > 31:
                QMessageBox.warning(self, "Ошибка", "Введите корректную дату.")

    def validate_storage_date(self):
        storage_date_text = self.srokxran_input.text().strip()
        datepostavki_text = self.datepostavki_input.text().strip()

        # Проверяем, соответствует ли введенная дата формату YYYY-MM-DD
        if len(storage_date_text) == 10 and len(datepostavki_text) == 10:  # Дата должна быть в формате YYYY-MM-DD
            year_srok = int(storage_date_text[0:4])
            month_srok = int(storage_date_text[5:7])
            day_srok = int(storage_date_text[8:10])

            year_postavki = int(datepostavki_text[0:4])
            month_postavki = int(datepostavki_text[5:7])
            day_postavki = int(datepostavki_text[8:10])

            # Создаем объект даты для введенной даты срока хранения
            entered_storage_date = datetime(year_srok, month_srok, day_srok)
            # Создаем объект даты для введенной даты поставки
            entered_datepostavki = datetime(year_postavki, month_postavki, day_postavki)

            # Проверяем, что срок хранения не меньше даты поставки
            if entered_storage_date < entered_datepostavki:
                QMessageBox.warning(self, "Ошибка", "Срок хранения не может быть меньше даты поставки.")
                return  # Прерываем выполнение метода, если есть ошибка

            # Получаем сегодняшнюю дату и добавляем 1 день
            today = datetime.today()
            min_storage_date = today + timedelta(days=1)

            # Проверяем, не меньше ли дата минимальной даты хранения (включительно) и не больше 31 декабря 2065 года
            if (entered_storage_date < today) or (entered_storage_date > datetime(2065, 12, 31)):
                QMessageBox.warning(self, "Ошибка",
                                    "Введите корректный срок хранения, который должен быть больше или равен завтрашнему дню и не превышать 31 декабря 2065 года.")

    def load_warehouses(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )
            cursor = connection.cursor()
            cursor.execute("SELECT id_sclada, adres FROM warehouse")  # Получаем ID и адрес склада
            warehouses = cursor.fetchall()

            # Очищаем ComboBox перед загрузкой новых данных
            self.id_sclada_combo.clear()

            for warehouse in warehouses:
                self.id_sclada_combo.addItem(f"{warehouse[1]} (ID: {warehouse[0]})",
                                             warehouse[0])  # Добавляем в ComboBox

            # Устанавливаем индекс на -1, чтобы ничего не было выбрано
            self.id_sclada_combo.setCurrentIndex(-1)

        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке складов: {error}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def on_warehouse_selected(self):
        id_sclada = self.id_sclada_combo.currentData()  # Получаем ID выбранного склада
        if id_sclada is not None:
            quantity = self.get_quantity_from_warehouse(id_sclada)  # Получаем количество товара на складе
            self.kolvo_input.setText(str(quantity))  # Заполняем поле "кол-во"

    def get_quantity_from_warehouse(self, id_sclada):
        """Получает количество товара на складе по его ID."""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT kolvo FROM warehouse WHERE id_sclada = %s", (id_sclada,))
                result = cursor.fetchone()
                if result:
                    return result[0]  # Возвращаем количество товара
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении количества товара: {error}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return 0  # Возвращаем 0, если не удалось получить количество

    def reset_fields(self):
        self.naimenovanie_input.clear()
        self.sostav_input.clear()
        self.nutritionalvalue_input.clear()
        self.datepostavki_input.clear()
        self.srokxran_input.clear()
        self.id_sclada_combo.setCurrentIndex(-1)  # Сбрасываем выбор склада
        self.kolvo_input.clear()

    def close_application(self):
        self.product_window.show()  # Показываем окно продукции
        self.close()

    def save_product(self):
        # Вызов валидации
        self.validate_date()
        self.validate_storage_date()

        naimenovanie = self.naimenovanie_input.text()
        sostav = self.sostav_input.text()
        nutritionalvalue = self.nutritionalvalue_input.text()
        datepostavki = self.datepostavki_input.text()
        srokxran = self.srokxran_input.text()
        id_sclada = self.id_sclada_combo.currentData()  # Получаем ID выбранного склада
        kolvo = self.kolvo_input.text()

        # Проверка на заполненность всех полей
        if not naimenovanie or not sostav or not nutritionalvalue or not datepostavki or not srokxran or id_sclada is None or not kolvo:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")
            return  # Прерываем выполнение метода, если есть незаполненные поля

        # Проверка количества на складе
        available_quantity = self.get_quantity_from_warehouse(id_sclada)
        if int(kolvo) > available_quantity:
            QMessageBox.warning(self, "Ошибка", "Количество превышает доступное на складе!")
            return

        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )
            cursor = connection.cursor()
            sql_insert_query = """INSERT INTO product (naimenovanie, sostav, nutritionalvalue, datepostavki, srokxran, id_sclada, kolvo) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql_insert_query,
                           (naimenovanie, sostav, nutritionalvalue, datepostavki, srokxran, id_sclada, kolvo))
            connection.commit()
            QMessageBox.information(self, "Успех", "Продукт успешно добавлен!")
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении продукта: {error}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

class ProductWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setGeometry(700, 300, 600, 420)
        self.setFixedSize(600, 420)
        self.setWindowTitle("Продукция")
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
            QPushButton {
                background-color: #D2B48C;  /* Цвет бежевой картона */
                color: #3B2A1D;              /* Темно-коричневый цвет текста */
                border: none;                /* Без рамки */
                border-radius: 5px;         /* Закругленные углы */
                font-size: 16px;             /* Размер шрифта */
                font-weight: bold;           /* Полужирный шрифт */
                padding: 10px;               /* Отступы внутри кнопки */
                text-align: center;          /* Выравнивание текста по центру */
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
            }
            QPushButton:hover {
                background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
            }
            QPushButton:pressed {
                background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
            }
        """

        # Создание кнопок с применением общего стиля
        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(430, 10, 160, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.title_label = QLabel("Продукция", self)
        self.title_label.setGeometry(225, 20, 120, 40)
        self.title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #333; 
            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
            padding: 6px;  /* Отступы для улучшения внешнего вида */
            border-radius: 5px;  /* Закругленные углы */
            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
        """)

        self.Prosmotr = QPushButton("Просмотр продукции", self)
        self.Prosmotr.setGeometry(190, 170, 200, 40)
        self.Prosmotr.clicked.connect(self.open_product_prosmotr_window)  # Подключаем сигнал нажатия
        self.Prosmotr.setStyleSheet(button_style)

        self.Dobavit = QPushButton("Добавить продукт", self)
        self.Dobavit.setGeometry(190, 230, 200, 40)
        self.Dobavit.clicked.connect(self.open_product_add_window)  # Подключаем сигнал нажатия
        self.Dobavit.setStyleSheet(button_style)

        self.label = QLabel(self)
        pixmap = QtGui.QPixmap("factoryicon.png")  # Укажите путь к вашему изображению
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.resize(50, 50)
        self.label.move(0, 0)

        self.show()

    def open_product_add_window(self):
        self.product_add_window = ProductAddWindow(self)  # Открываем окно добавления продукта
        self.hide()  # Скрываем текущее окно

    def open_product_prosmotr_window(self):
        self.product_prosmotr_window = Product_ProsmotrWindow(self)  # Открываем окно просмотра продукции
        self.hide()  # Скрываем текущее окно

    def close_application(self):
        self.main_window.show()  # Показываем главное окно
        self.close()  # Закрываем текущее окно

class Product_ProsmotrWindow(QWidget):
    def __init__(self, product_window):
        super().__init__()
        self.product_window = product_window  # Сохраняем ссылку на окно продукции
        self.setGeometry(700, 300, 600, 620)
        self.setFixedSize(600, 520)
        self.setWindowTitle("Просмотр продукции")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        # Создание элементов интерфейса
        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(430, 10, 160, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.Naim = QLabel("Наименование", self)
        self.Naim.setGeometry(10, 60, 200, 15)
        self.Naim.setStyleSheet("font-size: 14px")
        self.Naim_input = QLineEdit(self)
        self.Naim_input.setGeometry(10, 80, 300, 25)
        self.Naim_input.setStyleSheet("font-size: 12px; background-color: white;")
        self.Naim_input.setReadOnly(True)  # Блокируем редактирование

        self.Sostav = QLabel("Состав", self)
        self.Sostav.setGeometry(10, 110, 200, 15)
        self.Sostav.setStyleSheet("font-size: 14px")
        self.Sostav_input = QTextEdit(self)  # Заменяем QLineEdit на QTextEdit
        self.Sostav_input.setGeometry(10, 130, 300, 80)  # Увеличиваем высоту
        self.Sostav_input.setStyleSheet("font-size: 12px; background-color: white;")
        self.Sostav_input.setReadOnly(True)  # Блокируем редактирование

        self.Picha = QLabel("Пищевая ценность", self)
        self.Picha.setGeometry(10, 220, 200, 15)
        self.Picha.setStyleSheet("font-size: 14px")
        self.Picha_input = QTextEdit(self)  # Заменяем QLineEdit на QTextEdit
        self.Picha_input.setGeometry(10, 240, 300, 60)  # Увеличиваем высоту
        self.Picha_input.setStyleSheet(" font-size: 12px; background-color: white;")
        self.Picha_input.setReadOnly(True)  # Блокируем редактирование

        self.Datapost = QLabel("Дата поставки", self)
        self.Datapost.setGeometry(10, 310, 200, 15)
        self.Datapost.setStyleSheet("font-size: 14px")
        self.Datapost_input = QLineEdit(self)
        self.Datapost_input.setGeometry(10, 330, 300, 25)
        self.Datapost_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.Datapost_input.setReadOnly(True)  # Блокируем редактирование

        self.Srok = QLabel("Срок хранения", self)
        self.Srok.setGeometry(10, 360, 200, 15)
        self.Srok.setStyleSheet("font-size: 14px")
        self.Srok_input = QLineEdit(self)
        self.Srok_input.setGeometry(10, 380, 300, 25)
        self.Srok_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.Srok_input.setReadOnly(True)  # Блокируем редактирование

        self.Kol_vo = QLabel("Количество на складе", self)
        self.Kol_vo.setGeometry(10, 410, 200, 15)
        self.Kol_vo.setStyleSheet("font-size: 14px")
        self.Kol_vo_input = QLineEdit(self)
        self.Kol_vo_input.setGeometry(10, 430, 300, 25)
        self.Kol_vo_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.Kol_vo_input.setReadOnly(True)  # Блокируем редактирование

        self.Sclad = QLabel("Склад", self)
        self.Sclad.setGeometry(10, 460, 200, 15)
        self.Sclad.setStyleSheet("font-size: 14px")
        self.Sclad_input = QLineEdit(self)
        self.Sclad_input.setGeometry(10, 480, 300, 25)
        self.Sclad_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.Sclad_input.setReadOnly(True)

        self.Vibor = QPushButton("Выберите продукт", self)
        self.Vibor.setGeometry(415, 470, 180, 40)
        self.Vibor.clicked.connect(self.open_selection_window)  # Подключаем кнопку к методу
        self.Vibor.setStyleSheet(button_style)

        self.title_label = QLabel("Продукт", self)
        self.title_label.setGeometry(240, 10, 100, 40)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #333; 
                    background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                    padding: 6px;  /* Отступы для улучшения внешнего вида */
                    border-radius: 5px;  /* Закругленные углы */
                    border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                """)

        self.Dobavit = QPushButton("Удалить продукт", self)
        self.Dobavit.setGeometry(415, 420, 180, 40)
        self.Dobavit.clicked.connect(self.open_delete_window)  # Подключаем сигнал нажатия
        self.Dobavit.setStyleSheet(button_style)

        self.show()

    def clear_fields(self):
        self.Naim_input.clear()
        self.Sostav_input.clear()
        self.Picha_input.clear()
        self.Datapost_input.clear()
        self.Srok_input.clear()
        self.Kol_vo_input.clear()
        self.Sclad_input.clear()

    def open_selection_window(self):
        self.selection_window = ProductSelectionWindow(self)  # Открываем окно выбора продукта
        self.selection_window.exec()  # Запускаем диалоговое окно

    def load_product_data(self, product_id):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM product WHERE id_product = %s", (product_id,))
            product = cursor.fetchone()

            if product:
                self.Naim_input.setText(product[1])  # Наименование
                self.Sostav_input.setText(product[2])  # Состав
                self.Picha_input.setText(product[3])  # Пищевая ценность
                self.Datapost_input.setText(str(product[4]))  # Дата поставки
                self.Srok_input.setText(str(product[7]))  # Срок хранения
                self.Kol_vo_input.setText(str(product[6]))  # Количество на складе

                # Получаем id_sclada из продукта
                id_sclada = product[5]  # Теперь id_sclada находится в product[5]

                # Получаем адрес склада
                cursor.execute("SELECT adres FROM warehouse WHERE id_sclada = %s", (id_sclada,))
                sklad = cursor.fetchone()

                if sklad:
                    self.Sclad_input.setText(sklad[0])  # Устанавливаем адрес склада
                else:
                    self.Sclad_input.setText("Склад не найден")  # Если склад не найден

                # Обновляем количество на складе
                self.update_stock_quantity(id_sclada)

            else:
                QMessageBox.information(self, "Информация", "Продукт не найден.")

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_stock_quantity(self, id_sclada):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )

            cursor = connection.cursor()
            cursor.execute("SELECT SUM(kolvo) FROM warehouse WHERE id_sclada = %s", (id_sclada,))
            stock_quantity = cursor.fetchone()[0]

            if stock_quantity is not None:
                self.Kol_vo_input.setText(str(stock_quantity))  # Обновляем поле количества на складе
            else:
                self.Kol_vo_input.setText("0")  # Если нет данных о количестве

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def open_delete_window(self):
        self.set_buttons_enabled(False)  # Блокируем кнопки перед открытием окна удаления
        self.delete_window = ProductDeleteWindow(self)  # Открываем окно удаления продукта
        self.delete_window.naim_input.setText(self.Naim_input.text())

    def set_buttons_enabled(self, enabled):
        self.Exit.setEnabled(enabled)
        self.Dobavit.setEnabled(enabled)
        self.Vibor.setEnabled(enabled)

    def close_application(self):
        self.product_window.show()  # Показываем окно продукции
        self.close()  # Закрываем текущее окно

class ProductSelectionWindow(QDialog):
    def __init__(self, product_prosmotr_window):
        super().__init__(product_prosmotr_window)
        self.product_prosmotr_window = product_prosmotr_window
        self.setGeometry(800, 500, 400, 200)
        self.setFixedSize(400, 200)
        self.setWindowTitle("Выбор продукта")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("Выберите продукт", self)
        self.layout.addWidget(self.title_label)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем QLabel в компоновщик
        self.layout.addWidget(self.title_label)

        # Устанавливаем выравнивание для компоновщика
        self.layout.setAlignment(self.title_label, Qt.AlignmentFlag.AlignCenter)

        self.product_combo = QComboBox(self)
        self.product_combo.setFixedHeight(30)
        self.layout.addWidget(self.product_combo)
        self.product_combo.setStyleSheet("""
            QComboBox {
                background-color: white;  /* Цвет фона */
                color: #3B2A1D;            /* Цвет текста */
                border: 1px solid #D2B48C; /* Цвет рамки */
                border-radius: 5px;        /* Закругленные углы */
                padding: 5px;              /* Отступы для выравнивания текста */
                font-size: 16px;           /* Размер шрифта */
            }
            QComboBox::drop-down {
                border: none;              /* Убираем рамку у выпадающего списка */
            }
            QComboBox::hover {
                background-color: #F0EDE5; /* Цвет фона при наведении */
            }
            QComboBox::focus {
                border: 1px solid #A0522D; /* Цвет рамки при фокусе */
            }
        """)

        self.confirm_button = QPushButton("Выбрать", self)
        self.confirm_button.clicked.connect(self.select_product)
        self.layout.addWidget(self.confirm_button)
        self.confirm_button.setStyleSheet(button_style)

        self.cancel_button = QPushButton("Закрыть", self)
        self.cancel_button.clicked.connect(self.close)
        self.layout.addWidget(self.cancel_button)
        self.cancel_button.setStyleSheet(button_style)

        self.load_products()

    def load_products(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )

            cursor = connection.cursor()
            cursor.execute("SELECT id_product, naimenovanie FROM product")
            products = cursor.fetchall()

            for product in products:
                self.product_combo.addItem(product[1], product[0])  # Добавляем наименование и id продукта

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def select_product(self):
        product_id = self.product_combo.currentData()  # Получаем id выбранного продукта
        if product_id is not None:
            self.product_prosmotr_window.load_product_data(product_id)
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите продукт.")

class EmployeeWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setGeometry(700, 300, 600, 420)
        self.setFixedSize(600, 420)
        self.setWindowTitle("Работники")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Установка стиля для окна
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        # Общий стиль для всех кнопок
        button_style = """
            QPushButton {
                background-color: #D2B48C;  /* Цвет бежевой картона */
                color: #3B2A1D;              /* Темно-коричневый цвет текста */
                border: none;                /* Без рамки */
                border-radius: 5px;         /* Закругленные углы */
                font-size: 16px;             /* Размер шрифта */
                font-weight: bold;           /* Полужирный шрифт */
                padding: 10px;               /* Отступы внутри кнопки */
                text-align: center;          /* Выравнивание текста по центру */
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
            }
            QPushButton:hover {
                background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
            }
            QPushButton:pressed {
                background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
            }
        """

        # Создание кнопки "Назад"
        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(450, 10, 140, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        # Заголовок окна
        self.title_label = QLabel("Работники", self)
        self.title_label.setGeometry(230, 20, 115, 30)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                    font-size: 18px; 
                    font-weight: bold; 
                    color: #333; 
                    background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                    padding: 6px;  /* Отступы для улучшения внешнего вида */
                    border-radius: 5px;  /* Закругленные углы */
                    border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                """)

        # Кнопка "Просмотр работников"
        self.Prosmotr = QPushButton("Просмотр работников", self)
        self.Prosmotr.setGeometry(190, 170, 200, 40)
        self.Prosmotr.clicked.connect(self.open_employee_prosmotr_window)  # Подключаем сигнал нажатия
        self.Prosmotr.setStyleSheet(button_style)

        # Кнопка "Добавить работника"
        self.Dobavit = QPushButton("Добавить работника", self)
        self.Dobavit.setGeometry(190, 230, 200, 40)
        self.Dobavit.clicked.connect(self.open_employee_add_window)  # Подключаем сигнал нажатия
        self.Dobavit.setStyleSheet(button_style)

        # Добавление изображения
        self.label = QLabel(self)
        pixmap = QtGui.QPixmap("factoryicon.png")  # Укажите путь к вашему изображению
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.resize(50, 50)
        self.label.move(0, 0)

        self.show()

    def open_employee_add_window(self):
        self.employee_add_window = EmployeeAddWindow(self)  # Открываем окно добавления работника
        self.hide()  # Скрываем текущее окно

    def open_employee_prosmotr_window(self):
        self.employee_prosmotr_window = EmployeeProsmotrWindow(self)  # Открываем окно просмотра работников
        self.hide()  # Скрываем текущее окно

    def close_application(self):
        self.main_window.show()  # Показываем главное окно
        self.close()  # Закрываем текущее окно

class EmployeeProsmotrWindow(QWidget):
    def __init__(self, employee_window):
        super().__init__()
        self.employee_window = employee_window  # Сохраняем ссылку на окно работников
        self.setGeometry(600, 300, 700, 420)
        self.setFixedSize(700, 420)
        self.setWindowTitle("Просмотр работников")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                            QPushButton {
                                background-color: #D2B48C;  /* Цвет бежевой картона */
                                color: #3B2A1D;              /* Темно-коричневый цвет текста */
                                border: none;                /* Без рамки */
                                border-radius: 5px;         /* Закругленные углы */
                                font-size: 16px;             /* Размер шрифта */
                                font-weight: bold;           /* Полужирный шрифт */
                                padding: 10px;               /* Отступы внутри кнопки */
                                text-align: center;          /* Выравнивание текста по центру */
                                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                            }
                            QPushButton:hover {
                                background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                            }
                            QPushButton:pressed {
                                background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                            }
                        """

        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(530, 10, 160, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)  # Убедитесь, что количество столбцов соответствует вашим данным
        self.table.setHorizontalHeaderLabels(["Ид. работника", "ФИО", "Должность", "Возраст", "Стаж", "Телефон", "E-mail"])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 115)
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(4, 30)
        self.table.setColumnWidth(5, 123)
        self.table.setColumnWidth(6, 150)
        self.table.setGeometry(10, 60, 680, 350)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.title_label = QLabel("Работники", self)
        self.title_label.setGeometry(310, 10, 120, 30)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                                    font-size: 18px; 
                                    font-weight: bold; 
                                    color: #333; 
                                    background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                                    padding: 6px;  /* Отступы для улучшения внешнего вида */
                                    border-radius: 5px;  /* Закругленные углы */
                                    border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                                """)

        self.Delete = QPushButton("Удалить работника", self)
        self.Delete.setGeometry(10, 10, 180, 40)
        self.Delete.clicked.connect(self.open_delete_window)  # Подключаем сигнал нажатия
        self.Delete.setStyleSheet(button_style)

        self.load_data()  # Загружаем данные из базы данных

        self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал изменения элемента

        self.show()

    def load_data(self):
        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',  # или ваш хост
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM employees")  # Измените на ваш SQL-запрос
                records = cursor.fetchall()

                self.table.setRowCount(len(records))  # Устанавливаем количество строк в таблице

                for row_index, row_data in enumerate(records):
                    for column_index, item in enumerate(row_data):
                        self.table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def on_item_changed(self, item):
        # Получаем индекс строки и столбца
        row = item.row()
        column = item.column()

        # Получаем ID работника из первого столбца
        id_worker = self.table.item(row, 0).text()

        # Получаем новое значение
        new_value = item.text()

        # Отключаем сигнал itemChanged, чтобы избежать повторного вызова
        self.table.itemChanged.disconnect(self.on_item_changed)

        # Получаем текущее значение из базы данных
        current_value = self.get_current_value(id_worker, column)

        # Проверяем, что ввод соответствует требованиям
        if column == 1:  # ФИО
            if not self.is_valid_fio (new_value):
                self.show_error_message("Ошибка", "ФИО может содержать только буквы и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 2:  # Должность
            if not self.is_valid_dolzhnost(new_value):
                self.show_error_message("Ошибка", "Должность может содержать только буквы и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 3:  # Возраст
            if not self.is_valid_age(new_value):
                self.show_error_message("Ошибка", "Возраст может содержать только цифры.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 4:  # Стаж
            if not self.is_valid_stazh(new_value):
                self.show_error_message("Ошибка", "Стаж может содержать только цифры.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 5:  # Телефон
            if not self.is_valid_telefon(new_value):
                self.show_error_message("Ошибка", "Телефон может содержать только цифры, пробелы, + и ().")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        # Сохраняем изменения в базе данных
        self.save_data(id_worker, column, new_value)

        # Подключаем сигнал обратно после всех проверок
        self.table.itemChanged.connect(self.on_item_changed)

    def get_current_value(self, id_worker, column):
        """Получает текущее значение из базы данных для указанного работника и столбца."""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                column_name = {
                    1: "fio",         # ФИО
                    2: "dolzhnost",   # Должность
                    3: "vozrast",     # Возраст
                    4: "stazh",       # Стаж
                    5: "telefon",      # Телефон
                    6: "email"        # E-mail
                }.get(column)

                if column_name:
                    cursor.execute(f"SELECT {column_name} FROM employees WHERE id = %s", (id_worker,))
                    result = cursor.fetchone()
                    if result:
                        return str(result[0])  # Возвращаем текущее значение как строку

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return ""

    def is_valid_age(self, age):
        return bool(re.match(r'^\d+$', age))  # Проверка на цифры

    def is_valid_stazh(self, stazh):
        return bool(re.match(r'^\d+$', stazh))  # Проверка на цифры

    def is_valid_telefon(self, telefon):
        return bool(re.match(r'^[\d\s\+\(\)\-]+$', telefon))  # Проверка на цифры, пробелы, + и ()

    def is_valid_fio(self, fio):
        return bool(re.match(r'^[А-Яа-яЁё\s]+$', fio))  # Проверка на буквы и пробелы

    def is_valid_dolzhnost(self, dolzhnost):
        return bool(re.match(r'^[А-Яа-яЁё\s]+$', dolzhnost))  # Проверка на буквы и пробелы

    def save_data(self, id_worker, column, new_value):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password ='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Определяем, какой столбец нужно обновить
                column_name = {
                    1: "fio",         # ФИО
                    2: "dolzhnost",   # Должность
                    3: "vozrast",     # Возраст
                    4: "stazh",       # Стаж
                    5: "telefon",      # Телефон
                    6: "email"        # E-mail
                }.get(column)

                if column_name:
                    # SQL-запрос для обновления данных
                    cursor.execute(f"""
                        UPDATE employees
                        SET {column_name} = %s
                        WHERE id = %s
                    """, (new_value, id_worker))

                    connection.commit()  # Сохраняем изменения
                    print(f"Данные успешно обновлены: {column_name} для работника с ID {id_worker}.")

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def open_delete_window(self):
        self.delete_window = EmployeeDeleteWindow(self)  # Открываем окно удаления работника

    def close_application(self):
        self.employee_window.show()  # Показываем окно работников
        self.close()  # Закрываем текущее окно

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

class EmployeeDeleteWindow(QWidget):
    def __init__(self, employee_prosmotr_window):
        super().__init__()
        self.employee_prosmotr_window = employee_prosmotr_window  # Сохраняем ссылку на окно просмотра работников
        self.setGeometry(800, 430, 400, 150)
        self.setFixedSize(400, 150)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Удаление работника")
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.title_label = QLabel("Удаление работника", self)
        self.title_label.setGeometry(20, 5, 200, 35)
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        self.confirm_button = QPushButton("Закрыть", self)
        self.confirm_button.setGeometry(270, 20, 120, 40)
        self.confirm_button.clicked.connect(self.close)  # Закрываем окно при нажатии
        self.confirm_button.setStyleSheet(button_style)

        self.cancel_button = QPushButton("Удалить", self)
        self.cancel_button.setGeometry(270, 70, 120, 40)
        self.cancel_button.clicked.connect(self.confirm_delete)  # Подключаем к методу подтверждения удаления
        self.cancel_button.setStyleSheet(button_style)

        self.naim_employee = QLabel("Идентификатор работника", self)
        self.naim_employee.setGeometry(40, 40, 200, 30)
        self.naim_employee.setStyleSheet("font-size: 14px; color: #333;")
        self.naim_input = QLineEdit(self)
        self.naim_input.setGeometry(20, 70, 200, 25)
        self.naim_input.setMaxLength(25)
        self.naim_input.setStyleSheet("font-size: 12px; background-color: white;")
        regex = QRegularExpression(r'^[0-9]+$')  # Разрешаем только цифры
        validator = QRegularExpressionValidator(regex, self.naim_input)
        self.naim_input.setValidator(validator)

        self.show()

    def confirm_delete(self):
        employee_id = self.naim_input.text()  # Получаем ID работника из поля ввода
        if not employee_id:
            print("Пожалуйста, введите ID работника для удаления.")
            return

        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',  # или ваш хост
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                # SQL-запрос для удаления работника по ID
                delete_query = "DELETE FROM employees WHERE id = %s"
                cursor.execute(delete_query, (employee_id,))
                connection.commit()  # Подтверждаем изменения

                if cursor.rowcount > 0:
                    print(f"Работник с ID {employee_id} успешно удален.")
                else:
                    print(f"Работник с ID {employee_id} не найден.")

        except Error as e:
            print("Ошибка при работе с MySQL", e)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        self.employee_prosmotr_window.load_data()  # Обновляем данные в окне просмотра
        self.close()  # Закрываем окно после удаления

class EmployeeAddWindow(QWidget):
    def __init__(self, employee_window):
        super().__init__()
        self.employee_window = employee_window
        self.setGeometry(700, 300, 600, 420)
        self.setFixedSize(600, 420)
        self.setWindowTitle("Добавление работника")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        # UI Elements
        self.title_label = QLabel("Добавление работника", self)
        self.title_label.setGeometry(10, 10, 240, 35)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        self.id_label = QLabel("Идентификатор работника", self)
        self.id_label.setGeometry(10, 50, 200, 30)
        self.id_label.setStyleSheet("font-size: 14px;")
        self.id_input = QLineEdit(self)
        self.id_input.setGeometry(10, 80, 300, 25)
        self.id_input.setStyleSheet("font-size: 12px; background-color: white;")
        id_validator = QIntValidator(0, 999999, self.id_input)
        self.id_input.setValidator(id_validator)

        self.fio_label = QLabel("ФИО", self)
        self.fio_label.setGeometry(10, 110, 200, 20)
        self.fio_label.setStyleSheet("font-size: 14px;")
        self.fio_input = QLineEdit(self)
        self.fio_input.setGeometry(10, 130, 300, 25)
        self.fio_input.setStyleSheet("font-size: 12px; background-color: white;")
        self.fio_input.setMaxLength(50)
        fio_validator = QRegularExpressionValidator(QRegularExpression(r'^[А-Яа-яЁё\s]+$'), self.fio_input)
        self.fio_input.setValidator(fio_validator)

        self.dolzhnost_label = QLabel("Должность", self)
        self.dolzhnost_label.setGeometry(10, 160, 200, 20)
        self.dolzhnost_label.setStyleSheet("font-size: 14px;")
        self.dolzhnost_input = QLineEdit(self)
        self.dolzhnost_input.setGeometry(10, 180, 300, 25)
        self.dolzhnost_input.setStyleSheet("font-size: 12px; background-color: white;")
        self.dolzhnost_input.setMaxLength(30)
        dolzhnost_validator = QRegularExpressionValidator(QRegularExpression(r'^[А-Яа-яЁё\s]+$'), self.dolzhnost_input)
        self.dolzhnost_input.setValidator(dolzhnost_validator)

        self.vozrast_label = QLabel("Возраст", self)
        self.vozrast_label.setGeometry(10, 210, 200, 20)
        self.vozrast_label.setStyleSheet("font-size: 14px;")
        self.vozrast_input = QLineEdit(self)
        self.vozrast_input.setGeometry(10, 230, 300, 25)
        self.vozrast_input.setStyleSheet("font-size : 12px; background-color: white;")
        self.vozrast_input.setMaxLength(3)
        vozrast_validator = QIntValidator(0, 999999, self.vozrast_input)
        self.vozrast_input.setValidator(vozrast_validator)

        self.stazh_label = QLabel("Стаж", self)
        self.stazh_label.setGeometry(10, 260, 200, 20)
        self.stazh_label.setStyleSheet("font-size: 14px;")
        self.stazh_input = QLineEdit(self)
        self.stazh_input.setGeometry(10, 280, 300, 25)
        self.stazh_input.setStyleSheet("font-size: 12px; background-color: white;")
        self.stazh_input.setMaxLength(2)
        stazh_validator = QIntValidator(0, 999999, self.stazh_input)
        self.stazh_input.setValidator(stazh_validator)

        self.telefon_label = QLabel("Телефон", self)
        self.telefon_label.setGeometry(10, 310, 200, 20)
        self.telefon_label.setStyleSheet("font-size: 14px;")
        self.telefon_input = QLineEdit(self)
        self.telefon_input.setGeometry(10, 330, 300, 25)
        self.telefon_input.setStyleSheet("font-size: 12px; background-color: white;")
        self.telefon_input.setInputMask("+7 (999) 999 99-99;_")

        self.email_label = QLabel("E-mail", self)
        self.email_label.setGeometry(10, 360, 200, 20)
        self.email_label.setStyleSheet("font-size: 14px;")
        self.email_input = QLineEdit(self)
        self.email_input.setGeometry(10, 380, 300, 25)
        self.email_input.setStyleSheet("font-size: 12px; background-color: white;")
        email_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'), self.email_input)
        self.email_input.setValidator(email_validator)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(470, 110, 120, 40)
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_employee)

        self.reset_button = QPushButton("Сбросить", self)
        self.reset_button.setGeometry(470, 60, 120, 40)
        self.reset_button.setStyleSheet(button_style)
        self.reset_button.clicked.connect(self.reset_fields)

        self.exit_button = QPushButton("Закрыть", self)
        self.exit_button.setGeometry(470, 10, 120, 40)
        self.exit_button.setStyleSheet(button_style)
        self.exit_button.clicked.connect(self.close_application)

        self.show()

    def save_employee(self):
        id_rab = self.id_input.text()
        fio = self.fio_input.text()
        dolzhnost = self.dolzhnost_input.text()
        vozrast = self.vozrast_input.text()
        stazh = self.stazh_input.text()
        telefon = self.telefon_input.text()
        email = self.email_input.text()

        # Проверка на заполненность всех полей
        if not all([id_rab, fio, dolzhnost, vozrast, stazh, telefon, email]):
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, заполните все поля!")
            return

        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )
            cursor = connection.cursor()
            sql = "INSERT INTO employees (id, fio, dolzhnost, vozrast, stazh, telefon, email) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (id_rab, fio, dolzhnost, vozrast, stazh, telefon, email)
            cursor.execute(sql, values)
            connection.commit()
            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def reset_fields(self):
        self.id_input.clear()
        self.fio_input.clear()
        self.dolzhnost_input.clear()
        self.vozrast_input.clear()
        self.stazh_input.clear()
        self.telefon_input.clear()
        self.email_input.clear()

    def close_application(self):
        self.employee_window.show()
        self.close()

class SupplierWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setGeometry(700, 300, 600, 420)
        self.setFixedSize(600, 420)
        self.setWindowTitle("Поставщики")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Установка стиля для окна
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        # Общий стиль для всех кнопок
        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.label = QLabel(self)
        pixmap = QtGui.QPixmap("factoryicon.png")  # Укажите путь к вашему изображению
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.resize(50, 50)
        self.label.move(0, 0)

        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(450, 10, 140, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.title_label = QLabel("Поставщики", self)
        self.title_label.setGeometry(230, 20, 130, 40)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        self.Prosmotr = QPushButton("Просмотр поставщиков", self)
        self.Prosmotr.setGeometry(190, 170, 210, 40)
        self.Prosmotr.clicked.connect(self.open_supplier_prosmotr_window)
        self.Prosmotr.setStyleSheet(button_style)

        self.Dobavit = QPushButton("Добавить поставщика", self)
        self.Dobavit.setGeometry(190, 230, 210, 40)
        self.Dobavit.clicked.connect(self.open_supplier_add_window)
        self.Dobavit.setStyleSheet(button_style)

        self.show()

    def open_supplier_add_window(self):
        self.supplier_add_window = SupplierAddWindow(self)  # Открываем окно добавления поставщика
        self.hide()  # Скрываем текущее окно

    def open_supplier_prosmotr_window(self):
        self.supplier_prosmotr_window = SupplierProsmotrWindow(self)  # Открываем окно просмотра поставщиков
        self.hide()  # Скрываем текущее окно

    def close_application(self):
        self.main_window.show()  # Показываем главное окно
        self.close()  # Закрываем текущее окно

class SupplierProsmotrWindow(QWidget):
    def __init__(self, supplier_window):
        super().__init__()
        self.supplier_window = supplier_window  # Сохраняем ссылку на окно поставщиков
        self.setGeometry(600, 300, 700, 420)
        self.setFixedSize(700, 420)
        self.setWindowTitle("Просмотр поставщиков")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                            QPushButton {
                                background-color: #D2B48C;  /* Цвет бежевой картона */
                                color: #3B2A1D;              /* Темно-коричневый цвет текста */
                                border: none;                /* Без рамки */
                                border-radius: 5px;         /* Закругленные углы */
                                font-size: 16px;             /* Размер шрифта */
                                font-weight: bold;           /* Полужирный шрифт */
                                padding: 10px;               /* Отступы внутри кнопки */
                                text-align: center;          /* Выравнивание текста по центру */
                                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                            }
                            QPushButton:hover {
                                background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                            }
                            QPushButton:pressed {
                                background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                            }
                        """

        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(530, 10, 160, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.Delete = QPushButton("Удалить поставщика", self)
        self.Delete.setGeometry(10, 10, 180, 40)
        self.Delete.clicked.connect(self.open_delete_window)  # Подключаем сигнал нажатия
        self.Delete.setStyleSheet(button_style)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)  # Убедитесь, что количество столбцов соответствует вашим данным
        self.table.setHorizontalHeaderLabels(
            ["Ид. поставщика", "Название компании", "Адрес", "Контактный телефон", "Наименование товара", "Количество"])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 140)
        self.table.setColumnWidth(5, 100)  # Ширина для столбца "Количество"
        self.table.setGeometry(10, 60, 680, 350)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.title_label = QLabel("Просмотр поставщиков", self)
        self.title_label.setGeometry(240, 10, 230, 40)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                                    font-size: 18px; 
                                    font-weight: bold; 
                                    color: #333; 
                                    background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                                    padding: 6px;  /* Отступы для улучшения внешнего вида */
                                    border-radius: 5px;  /* Закругленные углы */
                                    border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                                """)

        self.load_data()  # Загружа ем данные из базы данных

        self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал изменения элемента

        self.show()

    def load_data(self):
        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',  # или ваш хост
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM supplier")  # Измените на ваш SQL-запрос
                records = cursor.fetchall()

                self.table.setRowCount(len(records))  # Устанавливаем количество строк в таблице

                for row_index, row_data in enumerate(records):
                    for column_index, item in enumerate(row_data):
                        self.table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def on_item_changed(self, item):
        # Получаем индекс строки и столбца
        row = item.row()
        column = item.column()

        # Получаем ID поставщика из первого столбца
        id_supplier = self.table.item(row, 0).text()

        # Получаем новое значение
        new_value = item.text()

        # Отключаем сигнал itemChanged, чтобы избежать повторного вызова
        self.table.itemChanged.disconnect(self.on_item_changed)

        # Получаем текущее значение из базы данных
        current_value = self.get_current_value(id_supplier, column)

        # Проверяем, что ввод соответствует требованиям
        if column == 1:  # Название компании
            if not self.is_valid_company_name(new_value):
                self.show_error_message("Ошибка", "Название компании может содержать только буквы и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 2:  # Адрес
            if not self.is_valid_address(new_value):
                self.show_error_message("Ошибка", "Адрес может содержать только буквы, цифры и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 3:  # Контактный телефон
            if not self.is_valid_contact_number(new_value):
                self.show_error_message("Ошибка", "Контактный телефон может содержать только цифры, пробелы, + и ().")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 4:  # Наименование товара
            if not self.is_valid_product_name(new_value):
                self.show_error_message("Ошибка", "Наименование товара может содержать только буквы и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 5:  # Количество
            if not self.is_valid_quantity(new_value):
                self.show_error_message("Ошибка", "Количество должно быть числом.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        # Сохраняем изменения в базе данных
        self.save_data(id_supplier, column, new_value)

        # Подключаем сигнал обратно после всех проверок
        self.table.itemChanged.connect(self.on_item_changed)

    def get_current_value(self, id_supplier, column):
        """Получает текущее значение из базы данных для указанного поставщика и столбца."""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                column_name = {
                    1: "name_company",  # Название компании
                    2: "adres",  # Адрес
                    3: "contact_number",  # Контактный телефон
                    4: "naimtov",  # Наименование товара
                    5: "kolvo"  # Количество
                }.get(column)

                if column_name:
                    cursor.execute(f"SELECT {column_name} FROM supplier WHERE id_supplier = %s", (id_supplier,))
                    result = cursor.fetchone()
                    if result:
                        return str(result[0])  # Возвращаем текущее значение как строку

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return ""

    def is_valid_contact_number(self, contact_number):
        return bool(re.match(r'^[\d\s\+\(\)\-]+$', contact_number))  # Проверка на цифры, пробелы, + и ()

    def is_valid_company_name(self, name):
        return bool(re.match(r'^[А-Яа-яЁё\s]+$', name))  # Проверка на буквы и пробелы

    def is_valid_address(self, address):
        return bool(re.match(r'^[А-Яа-яЁё\d\s,.-]+$', address))  # Проверка на буквы, цифры и пробелы

    def is_valid_product_name(self, product_name):
        return bool(re.match(r'^[А-Яа-яЁё\s]+$', product_name))  # Проверка на буквы и пробелы

    def is_valid_quantity(self, quantity):
        return quantity.isdigit()  # Проверка, что количество является числом

    def save_data(self, id_supplier, column, new_value):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Определяем, какой столбец нужно обновить
                column_name = {
                    1: "name_company",  # Название компании
                    2: "adres",  # Адрес
                    3: "contact_number",  # Контактный телефон
                    4: "naimtov",  # Наименование товара
                    5: "kolvo"  # Количество
                }.get(column)

                if column_name:
                    # SQL-запрос для обновления данных
                    cursor.execute(f"""
                               UPDATE supplier
                               SET {column_name} = %s
                               WHERE id_supplier = %s
                           """, (new_value, id_supplier))

                    connection.commit()  # Сохраняем изменения
                    print(f"Данные успешно обновлены: {column_name} для поставщика с ID {id_supplier}.")

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def open_delete_window(self):
        self.delete_window = SupplierDeleteWindow(self)  # Открываем окно удаления поставщика

    def close_application(self):
        self.supplier_window.show()  # Показываем окно поставщиков
        self.close()  # Закрываем текущее окно

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

class SupplierDeleteWindow(QWidget):
    def __init__(self, supplier_prosmotr_window):
        super().__init__()
        self.supplier_prosmotr_window = supplier_prosmotr_window  # Сохраняем ссылку на окно просмотра поставщиков
        self.setGeometry(800, 430, 400, 150)
        self.setFixedSize(400, 150)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Удаление поставщика")
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.title_label = QLabel("Удаление поставщика", self)
        self.title_label.setGeometry(10, 5, 220, 35)
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        self.naim_supplier_label = QLabel("Идентификатор поставщика", self)
        self.naim_supplier_label.setGeometry(30, 40, 230, 30)
        self.naim_supplier_label.setStyleSheet("font-size: 14px; color: #333;")

        self.naim_input = QLineEdit(self)
        self.naim_input.setGeometry(20, 70, 200, 25)
        self.naim_input.setMaxLength(25)
        self.naim_input.setStyleSheet("font-size: 12px; background-color: white;")
        regex = QRegularExpression(r'^[0-9]+$')  # Разрешаем только цифры
        validator = QRegularExpressionValidator(regex, self.naim_input)
        self.naim_input.setValidator(validator)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.setGeometry(270, 70, 120, 40)
        self.delete_button.clicked.connect(self.confirm_delete)  # Подключаем к методу подтверждения удаления
        self.delete_button.setStyleSheet(button_style)

        self.cancel_button = QPushButton("Закрыть", self)
        self.cancel_button.setGeometry(270, 20, 120, 40)
        self.cancel_button.clicked.connect(self.close)  # Закрываем окно при нажатии
        self.cancel_button.setStyleSheet(button_style)

        self.show()

    def confirm_delete(self):
        supplier_id = self.naim_input.text()  # Получаем ID поставщика из поля ввода
        if not supplier_id:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите ID поставщика для удаления.")
            return

        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',  # или ваш хост
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                # SQL-запрос для удаления поставщика по ID
                delete_query = "DELETE FROM supplier WHERE id_supplier = %s"
                cursor.execute(delete_query, (supplier_id,))
                connection.commit()  # Подтверждаем изменения

                if cursor.rowcount > 0:
                    QMessageBox.information(self, "Успех", f"Поставщик с ID {supplier_id} успешно удален.")
                else:
                    QMessageBox.warning(self, "Ошибка", f"Поставщик с ID {supplier_id} не найден.")

        except Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при работе с MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        self.supplier_prosmotr_window.load_data()  # Обновляем данные в окне просмотра
        self.close()

class SupplierAddWindow(QWidget):
    def __init__(self, supplier_window):
        super().__init__()
        self.supplier_window = supplier_window  # Сохраняем ссылку на окно поставщиков
        self.setGeometry(700, 300, 600, 430)
        self.setFixedSize(600, 430)
        self.setWindowTitle("Добавление поставщика")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.title_label = QLabel("Добавление поставщика", self)
        self.title_label.setGeometry(10, 10, 240, 40)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                                    font-size: 18px; 
                                    font-weight: bold; 
                                    color: #333; 
                                    background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                                    padding: 6px;  /* Отступы для улучшения внешнего вида */
                                    border-radius: 5px;  /* Закругленные углы */
                                    border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                                """)

        # Поля для ввода информации о поставщике
        self.idpost_label = QLabel("Идентификатор поставщика", self)
        self.idpost_label.setGeometry(10, 50, 200, 30)
        self.idpost_label.setStyleSheet("font-size: 14px;")
        self.idpost_input = QLineEdit(self)
        self.idpost_input.setGeometry(10, 80, 300, 25)
        self.idpost_input.setStyleSheet("font-size: 14px; background-color: white;")
        id_validator = QIntValidator(0, 999999, self.idpost_input)  # Установите диапазон по вашему усмотрению
        self.idpost_input.setValidator(id_validator)

        self.namecompany_label = QLabel("Название компании", self)
        self.namecompany_label.setGeometry(10, 110, 200, 30)
        self.namecompany_label.setStyleSheet("font-size: 14px;")
        self.namecompany_input = QLineEdit(self)
        self.namecompany_input.setGeometry(10, 140, 300, 25)
        self.namecompany_input.setStyleSheet("font-size: 14px; background-color: white;")

        self.adres_label = QLabel("Адрес", self)
        self.adres_label.setGeometry(10, 230, 200, 30)
        self.adres_label.setStyleSheet("font-size: 14px;")
        self.adres_input = QLineEdit(self)  # Изменено на QLineEdit
        self.adres_input.setGeometry(10, 260, 300, 25)
        self.adres_input.setStyleSheet("font-size:  14px; background-color: white;")

        self.number_label = QLabel("Контактный телефон", self)
        self.number_label.setGeometry(10, 170, 200, 30)
        self.number_label.setStyleSheet("font-size: 14px;")
        self.number_input = QLineEdit(self)
        self.number_input.setGeometry(10, 200, 300, 25)
        self.number_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.number_input.setInputMask("+7 (999) 999 99-99;_")  # Установка маски для ввода телефона

        self.naimtov_label = QLabel("Наименование товара", self)
        self.naimtov_label.setGeometry(10, 290, 200, 30)
        self.naimtov_label.setStyleSheet("font-size: 14px;")
        self.naimtov_input = QLineEdit(self)
        self.naimtov_input.setGeometry(10, 320, 300, 25)
        self.naimtov_input.setStyleSheet("font-size: 14px; background-color: white;")

        self.kolvo_label = QLabel("Количество", self)
        self.kolvo_label.setGeometry(10, 350, 200, 30)
        self.kolvo_label.setStyleSheet("font-size: 14px;")
        self.kolvo_input = QLineEdit(self)
        self.kolvo_input.setGeometry(10, 380, 300, 25)
        self.kolvo_input.setStyleSheet("font-size: 14px; background-color: white;")
        kolvo_validator = QIntValidator(0, 999999, self.kolvo_input)  # Установите диапазон по вашему усмотрению
        self.kolvo_input.setValidator(kolvo_validator)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(470, 110, 120, 40)
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_supplier)  # Здесь добавляем логику сохранения поставщика

        self.Exit = QPushButton("Закрыть", self)
        self.Exit.setGeometry(470, 10, 120, 40)
        self.Exit.setStyleSheet(button_style)
        self.Exit.clicked.connect(self.close_application)

        self.sbros_button = QPushButton("Сбросить", self)
        self.sbros_button.setGeometry(470, 60, 120, 40)
        self.sbros_button.setStyleSheet(button_style)
        self.sbros_button.clicked.connect(self.reset_fields)  # Связываем кнопку сброса с методом

        self.show()

    def save_supplier(self):
        id_supplier = self.idpost_input.text()
        name_company = self.namecompany_input.text()
        adres = self.adres_input.text()  # Получаем адрес из текстового поля
        contact_number = self.number_input.text()
        naimtov = self.naimtov_input.text()
        kolvo = self.kolvo_input.text()  # Получаем количество

        # Проверка на заполненность всех полей
        if not all([id_supplier, name_company, adres, contact_number, naimtov, kolvo]):
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, заполните все поля!")
            return

        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )
            cursor = connection.cursor()
            sql = "INSERT INTO supplier (id_supplier, name_company, adres, contact_number, naimtov, kolvo) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (id_supplier, name_company, adres, contact_number, naimtov, kolvo)
            cursor.execute(sql, values)
            connection.commit()
            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def reset_fields(self):
        self.idpost_input.clear()
        self.namecompany_input.clear()
        self.adres_input.clear()  # Сбрасываем поле адреса
        self.number_input.clear()
        self.naimtov_input.clear()
        self.kolvo_input.clear()

    def close_application(self):
        self.supplier_window.show()
        self.close()

class WarehouseWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setGeometry(700, 300, 600, 420)
        self.setFixedSize(600, 420)
        self.setWindowTitle("Склады")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        # Общий стиль для всех кнопок
        button_style = """
                            QPushButton {
                                background-color: #D2B48C;  /* Цвет бежевой картона */
                                color: #3B2A1D;              /* Темно-коричневый цвет текста */
                                border: none;                /* Без рамки */
                                border-radius: 5px;         /* Закругленные углы */
                                font-size: 16px;             /* Размер шрифта */
                                font-weight: bold;           /* Полужирный шрифт */
                                padding: 10px;               /* Отступы внутри кнопки */
                                text-align: center;          /* Выравнивание текста по центру */
                                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                            }
                            QPushButton:hover {
                                background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                            }
                            QPushButton:pressed {
                                background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                            }
                        """

        self.label = QLabel(self)
        pixmap = QtGui.QPixmap("factoryicon.png")  # Укажите путь к вашему изображению
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.resize(50, 50)
        self.label.move(0, 0)

        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(450, 10, 140, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.title_label = QLabel("Склады", self)
        self.title_label.setGeometry(240, 10, 90, 40)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.title_label.setStyleSheet("""
                                    font-size: 18px; 
                                    font-weight: bold; 
                                    color: #333; 
                                    background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                                    padding: 6px;  /* Отступы для улучшения внешнего вида */
                                    border-radius: 5px;  /* Закругленные углы */
                                    border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                                """)

        self.Prosmotr = QPushButton("Просмотр складов", self)
        self.Prosmotr.setGeometry(190, 170, 200, 40)
        self.Prosmotr.clicked.connect(self.open_warehouse_prosmotr_window)
        self.Prosmotr.setStyleSheet(button_style)

        self.Dobavit = QPushButton("Добавить склад", self)
        self.Dobavit.setGeometry(190, 230, 200, 40)
        self.Dobavit.clicked.connect(self.open_warehouse_add_window)
        self.Dobavit.setStyleSheet(button_style)

        self.show()

    def open_warehouse_add_window(self):
        self.warehouse_add_window = WarehouseAddWindow(self)  # Открываем окно добавления склада
        self.hide()  # Скрываем текущее окно

    def open_warehouse_prosmotr_window(self):
        self.warehouse_prosmotr_window = WarehouseProsmotrWindow(self)  # Открываем окно просмотра складов
        self.hide()  # Скрываем текущее окно

    def close_application(self):
        self.main_window.show()  # Показываем главное окно
        self.close()  # Закрываем текущее окно

class WarehouseProsmotrWindow(QWidget):
    def __init__(self, warehouse_window):
        super().__init__()
        self.warehouse_window = warehouse_window  # Сохраняем ссылку на окно складов
        self.setGeometry(600, 300, 700, 420)
        self.setFixedSize(700, 420)
        self.setWindowTitle("Просмотр складов")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                        QPushButton {
                            background-color: #D2B48C;  /* Цвет бежевой картона */
                            color: #3B2A1D;              /* Темно-коричневый цвет текста */
                            border: none;                /* Без рамки */
                            border-radius: 5px;         /* Закругленные углы */
                            font-size: 16px;             /* Размер шрифта */
                            font-weight: bold;           /* Полужирный шрифт */
                            padding: 10px;               /* Отступы внутри кнопки */
                            text-align: center;          /* Выравнивание текста по центру */
                            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                        }
                        QPushButton:hover {
                            background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                        }
                        QPushButton:pressed {
                            background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                        }
                    """

        self.Exit = QPushButton("Назад", self)
        self.Exit.setGeometry(530, 10, 160, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.Delete = QPushButton("Удалить склад", self)
        self.Delete.setGeometry(10, 10, 180, 40)
        self.Delete.clicked.connect(self.open_delete_window)  # Подключаем сигнал нажатия
        self.Delete.setStyleSheet(button_style)

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)  # Убедитесь, что количество столбцов соответствует вашим данным
        self.table.setHorizontalHeaderLabels(
            ["Ид. склада", "Адрес", "Контактный телефон", "Площадь", "E-mail", "Товар", "Кол-во"])
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 88)
        self.table.setGeometry(10, 60, 680, 350)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.title_label = QLabel("Просмотр складов", self)
        self.title_label.setGeometry(260, 10, 190, 40)
        self.title_label.setStyleSheet("""
                                        font-size: 18px; 
                                        font-weight: bold; 
                                        color: #333; 
                                        background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                                        padding: 6px;  /* Отступы для улучшения внешнего вида */
                                        border-radius: 5px;  /* Закругленные углы */
                                        border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                                    """)

        self.load_data()  # Загружаем данные из базы данных

        self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал изменения элемента

        self.show()

    def load_data(self):
        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM warehouse")  # Измените на ваш SQL-запрос
                records = cursor.fetchall()

                self.table.setRowCount(len(records))  # Устанавливаем количество строк в таблице

                for row_index, row_data in enumerate(records):
                    for column_index, item in enumerate(row_data):
                        table_item = QTableWidgetItem(str(item))
                        if column_index == 0:  # Если это ID склада
                            table_item.setFlags(
                                Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Запретить редактирование
                        self.table.setItem(row_index, column_index, table_item)

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def on_item_changed(self, item):
        # Получаем индекс строки и столбца
        row = item.row()
        column = item.column()

        # Получаем ID склада из первого столбца
        id_warehouse = self.table.item(row, 0).text()

        # Получаем новое значение
        new_value = item.text()

        # Отключаем сигнал itemChanged, чтобы избежать повторного вызова
        self.table.itemChanged.disconnect(self.on_item_changed)

        # Получаем текущее значение из базы данных
        current_value = self.get_current_value(id_warehouse, column)

        # Проверяем, что ввод соответствует требованиям
        if column == 1:  # Адрес
            if not self.is_valid_address(new_value):
                self.show_error_message("Ошибка", "Адрес может содержать только буквы, цифры и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 2:  # Контактный телефон
            if not self.is_valid_contact_number(new_value):
                self.show_error_message("Ошибка", "Контактный телефон может содержать только цифры, пробелы, + и ().")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 3:  # Площадь
            if not self.is_valid_area(new_value):
                self.show_error_message("Ошибка", "Площадь должна быть числом.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 4:  # E-mail
            if not self.is_valid_email(new_value):
                self.show_error_message("Ошибка", "Некорректный адрес электронной почты.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 5:  # Товар
            if not self.is_valid_product_name(new_value):
                self.show_error_message("Ошибка", "Наименование товара может содержать только буквы и пробелы.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        if column == 6:  # Кол-во
            if not self.is_valid_quantity(new_value):
                self.show_error_message("Ошибка", "Количество должно быть числом.")
                self.table.item(row, column).setText(current_value)  # Возвращаем текущее значение из базы данных
                self.table.itemChanged.connect(self.on_item_changed)  # Подключаем сигнал обратно
                return

        # Сохраняем изменения в базе данных
        self.save_data(id_warehouse, column, new_value)

        # Подключаем сигнал обратно после всех проверок
        self.table.itemChanged.connect(self.on_item_changed)

    def get_current_value(self, id_warehouse, column):
        """Получает текущее значение из базы данных для указанного склада и столбца."""
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                column_name = {
                    1: "adres",  # Адрес
                    2: "number",  # Контактный телефон
                    3: "ploshad",  # Площадь
                    4: "eMail",  # E-mail
                    5: "tovar",  # Товар
                    6: "kolvo"  # Кол-во
                }.get(column)

                if column_name:
                    cursor.execute(f"SELECT {column_name} FROM warehouse WHERE id_sclada = %s", (id_warehouse,))
                    result = cursor.fetchone()
                    if result:
                        return str(result[0])  # Возвращаем текущее значение как строку

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return ""

    def is_valid_contact_number(self, contact_number):
        return bool(re.match(r'^[\d\s\+\(\)\-]+$', contact_number))  # Проверка на цифры, пробелы, + и ()

    def is_valid_address(self, address):
        return bool(re.match(r'^[А-Яа-яЁё\d\s,.-]+$', address))  # Проверка на буквы, цифры и пробелы

    def is_valid_area(self, area):
        return bool(re.match(r'^\d+(\.\d+)?$', area))  # Проверка на числовое значение

    def is_valid_product_name(self, product_name):
        return bool(re.match(r'^[А-Яа-яЁё\s]+$', product_name))  # Проверка на буквы и пробелы

    def is_valid_email(self, email):
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))  # Проверка на корректный формат email

    def is_valid_quantity(self, quantity):
        return bool(re.match(r'^\d+$', quantity))  # Проверка на целое число

    def save_data(self, id_warehouse, column, new_value):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()

                # Определяем, какой столбец нужно обновить
                column_name = {
                    1: "adres",  # Адрес
                    2: "number",  # Контактный телефон
                    3: "ploshad",  # Площадь
                    4: "eMail",  # E-mail
                    5: "tovar",  # Товар
                    6: "kolvo"  # Кол-во
                }.get(column)

                if column_name:
                    # SQL-запрос для обновления данных
                    cursor.execute(f"""
                               UPDATE warehouse
                               SET {column_name} = %s
                               WHERE id_sclada = %s
                           """, (new_value, id_warehouse))

                    connection.commit()  # Сохраняем изменения
                    print(f"Данные успешно обновлены: {column_name} для склада с ID {id_warehouse}.")

        except Error as e:
            self.show_error_message("Ошибка при работе с MySQL", str(e))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def open_delete_window(self):
        self.delete_window = WarehouseDeleteWindow(self)  # Открываем окно удаления склада

    def close_application(self):
        self.warehouse_window.show()  # Показываем окно складов
        self.close()  # Закрываем текущее окно

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

class WarehouseAddWindow(QWidget):
    def __init__(self, warehouse_window):
        super().__init__()
        self.warehouse_window = warehouse_window  # Сохраняем ссылку на окно складов
        self.setGeometry(700, 300, 600, 480)
        self.setFixedSize(600, 480)
        self.setWindowTitle("Добавление склада")
        self.setStyleSheet("background-color: #F0EDE5;")  # Светлый серый цвет фона

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Общий стиль для всех кнопок
        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.title_label = QLabel("Добавление склада", self)
        self.title_label.setGeometry(10, 10, 210, 40)
        self.title_label.setStyleSheet("""
                                        font-size: 18px; 
                                        font-weight: bold; 
                                        color: #333; 
                                        background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                                        padding: 6px;  /* Отступы для улучшения внешнего вида */
                                        border-radius: 5px;  /* Закругленные углы */
                                        border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                                    """)

        # Поля для ввода информации о складе
        self.idsclada_label = QLabel("Идентификатор склада", self)
        self.idsclada_label.setGeometry(10, 50, 200, 30)
        self.idsclada_label.setStyleSheet("font-size: 14px;")
        self.idsclada_input = QLineEdit(self)
        self.idsclada_input.setGeometry(10, 80, 300, 25)
        self.idsclada_input.setStyleSheet("font-size: 14px; background-color: white;")
        id_validator = QIntValidator(0, 999999, self.idsclada_input)  # Установите диапазон по вашему усмотрению
        self.idsclada_input.setValidator(id_validator)

        self.adres_label = QLabel("Адрес", self)
        self.adres_label.setGeometry(10, 110, 200, 30)
        self.adres_label.setStyleSheet("font-size: 14px;")
        self.adres_input = QLineEdit(self)
        self.adres_input.setGeometry(10, 140, 300, 25)
        self.adres_input.setStyleSheet("font-size: 14px; background-color: white;")
        regex = QRegularExpression(r'^[А-Яа-яЁё0-9\s.-]+$')
        validator = QRegularExpressionValidator(regex, self.adres_input)
        self.adres_input.setValidator(validator)
        self.adres_input.setMaxLength(100)

        self.number_label = QLabel("Контактный телефон", self)
        self.number_label.setGeometry(10, 170, 200, 30)
        self.number_label.setStyleSheet("font-size:  14px;")
        self.number_input = QLineEdit(self)
        self.number_input.setGeometry(10, 200, 300, 25)
        self.number_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.number_input.setInputMask("+7 (999) 999 99-99;_")

        self.ploshad_label = QLabel("Площадь", self)
        self.ploshad_label.setGeometry(10, 230, 200, 30)
        self.ploshad_label.setStyleSheet("font-size: 14px;")
        self.ploshad_input = QLineEdit(self)
        self.ploshad_input.setGeometry(10, 260, 300, 25)
        self.ploshad_input.setStyleSheet("font-size: 14px; background-color: white;")
        id_validator = QIntValidator(0, 9999, self.ploshad_input)  # Установите диапазон по вашему усмотрению
        self.ploshad_input.setValidator(id_validator)
        self.unit_label1 = QLabel("кв. м", self)
        self.unit_label1.setStyleSheet("font-size: 14px; background-color: white;")
        self.unit_label1.setGeometry(50, 265, 100, 15)

        self.eMail_label = QLabel("E-mail", self)
        self.eMail_label.setGeometry(10, 290, 200, 30)
        self.eMail_label.setStyleSheet("font-size: 14px;")
        self.eMail_input = QLineEdit(self)
        self.eMail_input.setGeometry(10, 320, 300, 25)
        self.eMail_input.setStyleSheet("font-size: 14px; background-color: white;")
        email_validator = QRegularExpressionValidator(
            QRegularExpression(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'), self.eMail_input)
        self.eMail_input.setValidator(email_validator)
        self.eMail_input.setMaxLength(100)

        self.tovar_label = QLabel("Товар", self)
        self.tovar_label.setGeometry(10, 350, 200, 30)
        self.tovar_label.setStyleSheet("font-size: 14px;")
        self.tovar_input = QComboBox(self)
        self.tovar_input.setGeometry(10, 380, 300, 25)
        self.tovar_input.setStyleSheet("font-size: 14px; background-color: white;")
        self.load_products()  # Загружаем товары из базы данных
        self.tovar_input.currentIndexChanged.connect(self.update_quantity)  # Подключаем обработчик изменения товара

        self.kolvo_label = QLabel("Количество", self)
        self.kolvo_label.setGeometry(10, 410, 200, 30)
        self.kolvo_label.setStyleSheet("font-size: 14px;")
        self.kolvo_input = QLineEdit(self)
        self.kolvo_input.setGeometry(10, 440, 300, 25)
        self.kolvo_input.setStyleSheet("font-size: 14px; background-color: white;")
        id_validator = QIntValidator(0, 999999, self.kolvo_input)  # Установите диапазон по вашему усмотрению
        self.kolvo_input.setValidator(id_validator)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setGeometry(470, 110, 120, 40)
        self.save_button.setStyleSheet(button_style)
        self.save_button.clicked.connect(self.save_warehouse)  # Здесь добавляем логику сохранения склада

        self.Exit = QPushButton("Закрыть", self)
        self.Exit.setGeometry(470, 10, 120, 40)
        self.Exit.setStyleSheet(button_style)
        self.Exit.clicked.connect(self.close_application)

        self.sbros_button = QPushButton("Сбросить", self)
        self.sbros_button.setGeometry(470, 60, 120, 40)
        self.sbros_button.setStyleSheet(button_style)
        self.sbros_button.clicked.connect(self.reset_fields)  # Связываем кнопку сброса с методом

        self.show()

    def load_products(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )
            cursor = connection.cursor()
            cursor.execute("SELECT naimtov FROM supplier")
            products = cursor.fetchall()

            # Очищаем ComboBox перед загрузкой новых данных
            self.tovar_input.clear()

            for product in products:
                self.tovar_input.addItem(product[0])  # Добавляем товар в выпадающий список

            # Устанавливаем индекс на -1, чтобы ничего не было выбрано
            self.tovar_input.setCurrentIndex(-1)  # Устанавливаем пустой элемент как выбранный
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке товаров: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_quantity(self):
        selected_product = self.tovar_input.currentText()  # Получаем выбранный товар
        if selected_product:
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='password',
                    database='мясокомбинат'
                )
                cursor = connection.cursor()
                cursor.execute("SELECT kolvo FROM supplier WHERE naimtov = %s", (selected_product,))
                result = cursor.fetchone()
                if result:
                    self.kolvo_input.setText(str(result[0]))  # Устанавливаем количество в поле
                else:
                    self.kolvo_input.clear()  # Если товар не найден, очищаем поле
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке количества: {err}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def save_warehouse(self):
        id_sclada = self.idsclada_input.text()
        adres = self.adres_input.text()
        number = self.number_input.text()
        ploshad = self.ploshad_input.text()
        eMail = self.eMail_input.text()
        tovar = self.tovar_input.currentText()  # Получаем выбранный товар из выпадающего списка
        kolvo = self.kolvo_input.text()

        # Проверка на заполненность всех полей
        if not all([id_sclada, adres, number, ploshad, eMail, tovar, kolvo]):
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, заполните все поля!")
            return

        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                database='мясокомбинат'
            )
            cursor = connection.cursor()
            sql = "INSERT INTO warehouse (id_sclada, adres, number, ploshad, eMail, tovar, kolvo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (id_sclada, adres, number, ploshad, eMail, tovar, kolvo)
            cursor.execute(sql, values)
            connection.commit()
            QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def reset_fields(self):
        self.idsclada_input.clear()
        self.adres_input.clear()
        self.number_input.clear()
        self.ploshad_input.clear()
        self.eMail_input.clear()
        self.tovar_input.setCurrentIndex(0)  # Сбрасываем выбор товара
        self.kolvo_input.clear()

    def close_application(self):
        self.warehouse_window.show()  # Показываем окно складов
        self.close()

class WarehouseDeleteWindow(QWidget):
    def __init__(self, warehouse_prosmotr_window):
        super().__init__()
        self.warehouse_prosmotr_window = warehouse_prosmotr_window  # Сохраняем ссылку на окно просмотра складов
        self.setGeometry(800, 430, 400, 150)
        self.setFixedSize(400, 150)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Удаление склада")
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        button_style = """
                    QPushButton {
                        background-color: #D2B48C;  /* Цвет бежевой картона */
                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                        border: none;                /* Без рамки */
                        border-radius: 5px;         /* Закругленные углы */
                        font-size: 16px;             /* Размер шрифта */
                        font-weight: bold;           /* Полужирный шрифт */
                        padding: 10px;               /* Отступы внутри кнопки */
                        text-align: center;          /* Выравнивание текста по центру */
                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                    }
                    QPushButton:hover {
                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                    }
                    QPushButton:pressed {
                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                    }
                """

        self.title_label = QLabel("Удаление склада", self)
        self.title_label.setGeometry(30, 5, 170, 35)
        self.title_label.setStyleSheet("""
                            font-size: 18px; 
                            font-weight: bold; 
                            color: #333; 
                            background-color: rgba(255, 255, 255, 0.3);  /* Полупрозрачный белый фон с меньшей прозрачностью */
                            padding: 6px;  /* Отступы для улучшения внешнего вида */
                            border-radius: 5px;  /* Закругленные углы */
                            border: 1px solid rgba(0, 0, 0, 0.1);  /* Легкая тень для выделения */
                        """)

        self.naim_label = QLabel("Идентификатор склада", self)
        self.naim_label.setGeometry(40, 40, 230, 30)
        self.naim_label.setStyleSheet("font-size: 14px; color: #333;")

        self.naim_input = QLineEdit(self)
        self.naim_input.setGeometry(20, 70, 200, 25)
        self.naim_input.setMaxLength(25)
        self.naim_input.setStyleSheet("font-size: 12px; background-color: white;")
        regex = QRegularExpression(r'^[0-9]+$')  # Разрешаем только цифры
        validator = QRegularExpressionValidator(regex, self.naim_input)
        self.naim_input.setValidator(validator)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.setGeometry(270, 70, 120, 40)
        self.delete_button.clicked.connect(self.confirm_delete)  # Подключаем к методу подтверждения удаления
        self.delete_button.setStyleSheet(button_style)

        self.cancel_button = QPushButton("Закрыть", self)
        self.cancel_button.setGeometry(270, 20, 120, 40)
        self.cancel_button.clicked.connect(self.close)  # Закрываем окно при нажатии
        self.cancel_button.setStyleSheet(button_style)

        self.show()

    def confirm_delete(self):
        warehouse_id = self.naim_input.text()  # Получаем ID склада из поля ввода
        if not warehouse_id:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите ID склада для удаления.")
            return

        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',  # или ваш хост
                database='мясокомбинат',
                user='root',
                password='password'
            )

            if connection.is_connected():
                cursor = connection.cursor()
                # SQL-запрос для удаления склада по ID
                delete_query = "DELETE FROM warehouse WHERE id_sclada = %s"
                cursor.execute(delete_query, (warehouse_id,))
                connection.commit()  # Подтверждаем изменения

                if cursor.rowcount > 0:
                    QMessageBox.information(self, "Успех", f"Склад с ID {warehouse_id} успешно удален.")
                else:
                    QMessageBox.warning(self, "Ошибка", f"Склад с ID {warehouse_id} не найден.")

        except Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при работе с MySQL: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        self.warehouse_prosmotr_window.load_data()  # Обновляем данные в окне просмотра
        self.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(540, 200, 800, 564)
        self.setFixedSize(800, 564)
        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")
        #self.setStyleSheet("""background-color: #F5F5DC;  /* Светлый бежевый цвет фона */""")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        button_style = """
                   QPushButton {
                       background-color: #D2B48C;  /* Цвет бежевой картона */
                       color: #4B3D2A;              /* Темно-коричневый цвет текста */
                       border: none;                /* Без рамки */
                       border-radius: 5px;         /* Закругленные углы */
                       font-size: 16px;             /* Размер шрифта */
                       font-weight: bold;           /* Полужирный шрифт */
                       padding: 10px;               /* Отступы внутри кнопки */
                       text-align: center;          /* Выравнивание текста по центру */
                       text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                   }
                   QPushButton:hover {
                       background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                   }
                   QPushButton:pressed {
                       background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                   }
               """

        # Создание кнопок с применением общего стиля
        self.Prod = QPushButton("Продукция", self)
        self.Prod.setGeometry(30, 240, 150, 40)
        self.Prod.clicked.connect(self.open_product_window)
        self.Prod.setStyleSheet(button_style)

        self.Rab = QPushButton("Работники", self)
        self.Rab.setGeometry(230, 240, 150, 40)
        self.Rab.clicked.connect(self.open_rab_window)
        self.Rab.setStyleSheet(button_style)

        self.Post = QPushButton("Поставщики", self)
        self.Post.setGeometry(430, 240, 150, 40)
        self.Post.clicked.connect(self.open_supplier_window)  # Подключаем сигнал нажатия
        self.Post.setStyleSheet(button_style)

        self.Scl = QPushButton("Склады", self)
        self.Scl.setGeometry(630, 240, 150, 40)
        self.Scl.clicked.connect(self.open_warehouse_window)  # Подключаем сигнал нажатия
        self.Scl.setStyleSheet(button_style)

        self.Otchet = QPushButton("Печать отчета по запасам", self)
        self.Otchet.setGeometry(430, 10, 230, 40)
        self.Otchet.clicked.connect(self.open_report_window)
        self.Otchet.setStyleSheet(button_style)

        self.Exit = QPushButton("Закрыть", self)
        self.Exit.setGeometry(680, 10, 100, 40)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.label = QLabel(self)
        pixmap = QtGui.QPixmap("factoryicon.png")  # Укажите путь к вашему изображению
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)
        self.label.resize(50, 50)
        self.label.move(0, 0)

        self.label1 = QLabel(self)
        pixmap = QtGui.QPixmap("cow.png")  # Укажите путь к вашему изображению
        self.label1.setPixmap(pixmap)
        self.label1.setScaledContents(True)
        self.label1.resize(45, 45)
        self.label1.move(85, 195)

        self.label2 = QLabel(self)
        pixmap = QtGui.QPixmap("man.png")  # Укажите путь к вашему изображению
        self.label2.setPixmap(pixmap)
        self.label2.setScaledContents(True)
        self.label2.resize(50, 50)
        self.label2.move(280, 190)

        self.label3 = QLabel(self)
        pixmap = QtGui.QPixmap("distribution.png")  # Укажите путь к вашему изображению
        self.label3.setPixmap(pixmap)
        self.label3.setScaledContents(True)
        self.label3.resize(45, 45)
        self.label3.move(485, 193)

        self.label4 = QLabel(self)
        pixmap = QtGui.QPixmap("stock.png")  # Укажите путь к вашему изображению
        self.label4.setPixmap(pixmap)
        self.label4.setScaledContents(True)
        self.label4.resize(40, 40)
        self.label4.move(685, 195)

        # Set window title
        self.setWindowTitle("Информационная система для мясокомбината")

        # Show window
        self.show()

    def open_product_window(self):
        self.hide()  # Скрываем главное окно
        self.product_window = ProductWindow(self)  # Передаем ссылку на главное окно

    def open_rab_window(self):
        self.hide()  # Скрываем главное окно
        self.employee_window = EmployeeWindow(self)  # Передаем ссылку на главное окно

    def open_supplier_window(self):
        self.hide()  # Скрываем главное окно
        self.supplier_window = SupplierWindow(self)  # Передаем ссылку на главное окно

    def open_warehouse_window(self):
        self.hide()  # Скрываем главное окно
        self.warehouse_window = WarehouseWindow(self)  # Передаем ссылку на главное окно

    def open_report_window(self):
        self.block_buttons()  # Блокируем кнопки перед открытием окна отчета
        self.report_window = ReportWindow(self)

    def block_buttons(self):
        self.Prod.setEnabled(False)
        self.Rab.setEnabled(False)
        self.Post.setEnabled(False)
        self.Scl.setEnabled(False)
        self.Otchet.setEnabled(False)
        self.Exit.setEnabled(False)

    def unblock_buttons(self):
        self.Prod.setEnabled(True)
        self.Rab.setEnabled(True)
        self.Post.setEnabled(True)
        self.Scl.setEnabled(True)
        self.Otchet.setEnabled(True)
        self.Exit.setEnabled(True)

    def close_application(self):
        reply = QMessageBox()
        reply.setWindowIcon(QtGui.QIcon('factoryicon.png'))
        reply.setWindowTitle('Подтверждение')
        reply.setText("Вы увер ены, что хотите покинуть систему?")
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.button(QMessageBox.StandardButton.Yes).setText('Да')
        reply.button(QMessageBox.StandardButton.No).setText('Нет')

        if reply.exec() == QMessageBox.StandardButton.Yes:
            # Закрываем все дочерние окна
            if hasattr(self, 'product_window'):
                self.product_window.deleteLater()
            if hasattr(self, 'employee_window'):
                self.employee_window.deleteLater()
            if hasattr(self, 'supplier_window'):
                self.supplier_window.deleteLater()
            if hasattr(self, 'warehouse_window'):
                self.warehouse_window.deleteLater()
            if hasattr(self, 'report_window'):
                self.report_window.deleteLater()

            self.close()  # Закрываем главное окно

class ReportWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Сохраняем ссылку на главное окно
        self.setGeometry(750, 350, 400, 200)
        self.setWindowTitle("Отчет по запасам")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("factoryicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)

        # Устанавливаем флаги окна: без рамки и всегда поверх других окон
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setStyleSheet("""background-color: #F0EDE5;  /* Светлый серый цвет фона */""")

        # Общий стиль для всех кнопок
        button_style = """
                                    QPushButton {
                                        background-color: #D2B48C;  /* Цвет бежевой картона */
                                        color: #3B2A1D;              /* Темно-коричневый цвет текста */
                                        border: none;                /* Без рамки */
                                        border-radius: 5px;         /* Закругленные углы */
                                        font-size: 16px;             /* Размер шрифта */
                                        font-weight: bold;           /* Полужирный шрифт */
                                        padding: 10px;               /* Отступы внутри кнопки */
                                        text-align: center;          /* Выравнивание текста по центру */
                                        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5); /* Тень текста */
                                    }
                                    QPushButton:hover {
                                        background-color: #C19A6B;   /* Более темный бежевый цвет при наведении */
                                    }
                                    QPushButton:pressed {
                                        background-color: #A0522D;   /* Темно-коричневый цвет при нажатии */
                                    }
                                """

        # Создаем метку с текстом отчета
        self.label = QLabel("Общее количество\nзапасов на складах", self)
        self.label.setGeometry(110, 10, 300, 60)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        self.input_line = QLineEdit(self)
        self.input_line.setGeometry(90, 100, 220, 25)
        self.input_line.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выровнять текст по центру
        self.input_line.setStyleSheet("""background-color: white; font-size: 18px;  /* Светлый серый цвет фона */""")

        self.Pechat = QPushButton("Вывести", self)
        self.Pechat.setGeometry(95, 150, 100, 35)
        self.Pechat.clicked.connect(self.print_report)  # Подключаем кнопку к функции
        self.Pechat.setStyleSheet(button_style)

        self.Exit = QPushButton("Закрыть", self)
        self.Exit.setGeometry(205, 150, 100, 35)
        self.Exit.clicked.connect(self.close_application)
        self.Exit.setStyleSheet(button_style)

        self.show()

    def close_application(self):
        self.main_window.unblock_buttons()
        self.close()  # Закрываем окно

    def print_report(self):
        try:
            # Подключение к базе данных
            connection = mysql.connector.connect(
                host='localhost',  # Замените на ваш хост
                user='root',  # Замените на ваше имя пользователя
                password='password',  # Замените на ваш пароль
                database='мясокомбинат'  # Замените на вашу базу данных
            )

            cursor = connection.cursor()
            query = "SELECT SUM(kolvo) FROM warehouse"
            cursor.execute(query)
            result = cursor.fetchone()

            if result[0] is not None:
                total_kolvo = result[0]
                self.input_line.setText(str(total_kolvo))  # Устанавливаем текст в QLineEdit
            else:
                self.input_line.setText("Нет данных")  # Устанавливаем текст в случае отсутствия данных

        except mysql.connector.Error as err:
            self.input_line.setText(f"Ошибка: {err}")  # Устанавливаем текст ошибки в QLineEdit
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def close_window(self):
        self.close()  # Закрываем окно
        self.main_window.show()  # Показываем главное окно

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())