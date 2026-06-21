import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import subprocess
import sys
import calendar

# Импорт модулей и настройка констант
DATA_FILE = "money_watcher_data.json"
BACKUP_DIR = "backups"
MAX_AMOUNT = 4_200_000_000_000

# Определение цветовых схем для светлой темы
LIGHT_BG_WHITE = "#ffffff"
LIGHT_TEXT_BLACK = "#000000"
LIGHT_ACCENT_GRAY = "#b1b1b1"
LIGHT_BG_DARK = "#000000"
LIGHT_BG_LIGHT_GRAY = "#f9f9f9"
LIGHT_HOVER_GRAY = "#e0e0e0"
LIGHT_ACTIVE_BG = "#000000"
LIGHT_ACTIVE_FG = "#ffffff"
LIGHT_INACTIVE_BG = "#ffffff"
LIGHT_INACTIVE_FG = "#000000"
LIGHT_ENTRY_BG = "#f0f0f0"
LIGHT_BUTTON_BG = "#000000"
LIGHT_BUTTON_FG = "#ffffff"
LIGHT_PROGRESS_FILL = "#000000"
LIGHT_TITLE_BG = "#f0f0f0"
LIGHT_TITLE_FG = "#000000"

# Определение цветовых схем для тёмной темы
DARK_BG_WHITE = "#1e1e1e"
DARK_TEXT_BLACK = "#ffffff"
DARK_ACCENT_GRAY = "#888888"
DARK_BG_DARK = "#333333"
DARK_BG_LIGHT_GRAY = "#2d2d2d"
DARK_HOVER_GRAY = "#444444"
DARK_ACTIVE_BG = "#555555"
DARK_ACTIVE_FG = "#ffffff"
DARK_INACTIVE_BG = "#1e1e1e"
DARK_INACTIVE_FG = "#ffffff"
DARK_ENTRY_BG = "#3a3a3a"
DARK_BUTTON_BG = "#000000"
DARK_BUTTON_FG = "#ffffff"
DARK_PROGRESS_FILL = "#ffffff"
DARK_TITLE_BG = "#2d2d2d"
DARK_TITLE_FG = "#ffffff"

# Список доступных валют
CURRENCIES = {
    "₽ (Рубль)": "₽",
    "$ (Доллар)": "$",
    "€ (Евро)": "€",
    "£ (Фунт)": "£",
    "¥ (Йена)": "¥"
}

# Словарь с названиями месяцев на русском языке
MONTHS_RU = {
    "January": "Январь", "February": "Февраль", "March": "Март",
    "April": "Апрель", "May": "Май", "June": "Июнь",
    "July": "Июль", "August": "Август", "September": "Сентябрь",
    "October": "Октябрь", "November": "Ноябрь", "December": "Декабрь"
}


# Класс для управления данными приложения
class DataManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.data = {
            "transactions": [],
            "goals": [],
            "settings": {
                "theme": "light",
                "currency": "₽"
            }
        }
        self.load_data()

    # Загрузка данных из файла
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
                    if "settings" not in self.data:
                        self.data["settings"] = {"theme": "light", "currency": "₽"}
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                self.data = {"transactions": [], "goals": [], "settings": {"theme": "light", "currency": "₽"}}
        else:
            self.save_data()

    # Сохранение данных в файл
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    # Создание резервной копии данных
    def create_backup(self):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(BACKUP_DIR, f"резерв_{timestamp}.json")

        try:
            shutil.copy2(self.data_file, backup_file)
            return backup_file
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {e}")
            return None

    # Смена файла данных
    def change_data_file(self, new_file):
        try:
            self.data_file = new_file
            self.load_data()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
            return False

    # Получение текущей валюты
    def get_currency(self):
        return self.data["settings"].get("currency", "₽")

    # Получение текущей темы
    def get_theme(self):
        return self.data["settings"].get("theme", "light")

    # Обновление настроек приложения
    def update_settings(self, theme=None, currency=None):
        if theme is not None:
            self.data["settings"]["theme"] = theme
        if currency is not None:
            self.data["settings"]["currency"] = currency
        self.save_data()

    # Расчёт текущего баланса
    def get_balance(self):
        income = sum(t['amount'] for t in self.data['transactions'] if t['type'] == 'income')
        expense = sum(t['amount'] for t in self.data['transactions'] if t['type'] == 'expense')
        return income - expense

    # Получение месячного дохода
    def get_monthly_income(self, target_date=None):
        if target_date is None:
            target_date = datetime.now()
        return sum(t['amount'] for t in self.data['transactions']
                   if t['type'] == 'income' and datetime.strptime(t['date'], '%Y-%m-%d').month == target_date.month
                   and datetime.strptime(t['date'], '%Y-%m-%d').year == target_date.year)

    # Получение месячного расхода
    def get_monthly_expense(self, target_date=None):
        if target_date is None:
            target_date = datetime.now()
        return sum(t['amount'] for t in self.data['transactions']
                   if t['type'] == 'expense' and datetime.strptime(t['date'], '%Y-%m-%d').month == target_date.month
                   and datetime.strptime(t['date'], '%Y-%m-%d').year == target_date.year)

    # Валидация суммы операции
    def validate_amount(self, amount):
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Сумма должна быть больше нуля")
            if amount_float > 4_200_000_000_000:
                raise ValueError(f"Сумма не может превышать 4 200 000 000 000 ₽")
            return amount_float
        except ValueError as e:
            if "не может превышать" in str(e) or "больше нуля" in str(e):
                raise
            raise ValueError("Введите корректную сумму (число)")

    # Добавление новой транзакции
    def add_transaction(self, name, amount, trans_type, date=None):
        if not name or len(name.strip()) == 0:
            raise ValueError("Название операции не может быть пустым")

        amount_float = self.validate_amount(amount)

        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        transaction = {
            "id": len(self.data['transactions']) + 1,
            "name": name.strip(),
            "amount": amount_float,
            "type": trans_type,
            "date": date
        }
        self.data['transactions'].append(transaction)
        self.save_data()
        return transaction

    # Обновление существующей транзакции
    def update_transaction(self, trans_id, name, amount, trans_type, date):
        for trans in self.data['transactions']:
            if trans['id'] == trans_id:
                trans['name'] = name.strip()
                trans['amount'] = self.validate_amount(amount)
                trans['type'] = trans_type
                trans['date'] = date
                self.save_data()
                return True
        return False

    # Удаление транзакции с возвратом средств в цель
    def delete_transaction(self, trans_id):
        transaction = next((t for t in self.data['transactions'] if t['id'] == trans_id), None)
        if transaction and transaction['type'] == 'expense':
            goal_name_prefix = "Пополнение цели: "
            if transaction['name'].startswith(goal_name_prefix):
                goal_name = transaction['name'][len(goal_name_prefix):]
                for goal in self.data['goals']:
                    if goal['name'] == goal_name:
                        goal['current_amount'] = max(0, goal['current_amount'] - transaction['amount'])
                        if goal['completed'] and goal['current_amount'] < goal['target_amount']:
                            goal['completed'] = False
                        break
        self.data['transactions'] = [t for t in self.data['transactions'] if t['id'] != trans_id]
        self.save_data()

    # Массовое удаление транзакций
    def delete_transactions_bulk(self, trans_ids):
        for trans_id in trans_ids:
            transaction = next((t for t in self.data['transactions'] if t['id'] == trans_id), None)
            if transaction and transaction['type'] == 'expense':
                goal_name_prefix = "Пополнение цели: "
                if transaction['name'].startswith(goal_name_prefix):
                    goal_name = transaction['name'][len(goal_name_prefix):]
                    for goal in self.data['goals']:
                        if goal['name'] == goal_name:
                            goal['current_amount'] = max(0, goal['current_amount'] - transaction['amount'])
                            if goal['completed'] and goal['current_amount'] < goal['target_amount']:
                                goal['completed'] = False
                            break
        self.data['transactions'] = [t for t in self.data['transactions'] if t['id'] not in trans_ids]
        self.save_data()

    # Получение последних транзакций
    def get_recent_transactions(self, limit=5):
        return sorted(self.data['transactions'], key=lambda x: x['date'], reverse=True)[:limit]

    # Получение всех транзакций
    def get_all_transactions(self):
        return sorted(self.data['transactions'], key=lambda x: x['date'], reverse=True)

    # Добавление новой цели
    def add_goal(self, name, target_amount, current_amount=0, deadline_date=None, completed=False):
        if not name or len(name.strip()) == 0:
            raise ValueError("Название цели не может быть пустым")

        target_float = self.validate_amount(target_amount)

        current_float = 0
        if current_amount and str(current_amount).strip():
            try:
                current_float = float(current_amount)
                if current_float < 0:
                    raise ValueError("Текущая сумма не может быть отрицательной")
            except ValueError:
                raise ValueError("Введите корректную текущую сумму")

        if current_float > target_float:
            raise ValueError("Текущая сумма не может превышать целевую")

        if deadline_date is None or deadline_date.strip() == "":
            deadline_date = ""

        if current_float > 0:
            self.add_transaction(
                f"Начальный капитал для цели: {name}",
                current_float,
                "income"
            )

        goal = {
            "id": len(self.data['goals']) + 1,
            "name": name.strip(),
            "target_amount": target_float,
            "current_amount": current_float,
            "deadline": deadline_date,
            "completed": completed
        }
        self.data['goals'].append(goal)
        self.save_data()
        return goal

    # Обновление существующей цели
    def update_goal(self, goal_id, name, target_amount, current_amount, deadline_date, completed=False):
        for goal in self.data['goals']:
            if goal['id'] == goal_id:
                goal['name'] = name.strip()
                goal['target_amount'] = self.validate_amount(target_amount)
                if current_amount and str(current_amount).strip():
                    goal['current_amount'] = float(current_amount)
                else:
                    goal['current_amount'] = 0
                goal['deadline'] = deadline_date if deadline_date else ""
                goal['completed'] = completed
                self.save_data()
                return True
        return False

    # Пополнение цели
    def update_goal_progress(self, goal_id, add_amount):
        add_amount_float = self.validate_amount(str(add_amount))

        for goal in self.data['goals']:
            if goal['id'] == goal_id:
                remaining = goal['target_amount'] - goal['current_amount']
                if add_amount_float > remaining:
                    add_amount_float = remaining

                self.add_transaction(
                    f"Пополнение цели: {goal['name']}",
                    add_amount_float,
                    "expense"
                )

                goal['current_amount'] += add_amount_float
                if goal['current_amount'] >= goal['target_amount']:
                    goal['completed'] = True
                self.save_data()
                return add_amount_float
        return 0

    # Удаление цели
    def delete_goal(self, goal_id, refund_to_balance=False):
        goal = next((g for g in self.data['goals'] if g['id'] == goal_id), None)
        if goal:
            if refund_to_balance and goal['current_amount'] > 0:
                self.add_transaction(
                    f"Возврат средств от удаления цели: {goal['name']}",
                    goal['current_amount'],
                    "income"
                )
            self.data['goals'] = [g for g in self.data['goals'] if g['id'] != goal_id]
            self.save_data()
            return True
        return False

    # Массовое удаление целей
    def delete_goals_bulk(self, goal_ids, refund_to_balance=False):
        for goal_id in goal_ids:
            goal = next((g for g in self.data['goals'] if g['id'] == goal_id), None)
            if goal and refund_to_balance and goal['current_amount'] > 0:
                self.add_transaction(
                    f"Возврат средств от удаления цели: {goal['name']}",
                    goal['current_amount'],
                    "income"
                )
        self.data['goals'] = [g for g in self.data['goals'] if g['id'] not in goal_ids]
        self.save_data()

    # Получение активных целей
    def get_active_goals(self):
        return [g for g in self.data['goals'] if not g.get('completed', False)]

    # Получение завершённых целей
    def get_completed_goals(self):
        return [g for g in self.data['goals'] if g.get('completed', False)]


# Кастомный выпадающий список для выбора валюты
class CurrencyButton(tk.Button):
    def __init__(self, master, text, command=None, colors=None, **kwargs):
        super().__init__(master, text=text, command=command, **kwargs)
        self.colors = colors
        self.menu_open = False
        self.menu_window = None
        self.bind("<Button-1>", self.toggle_menu)

    # Переключение состояния выпадающего меню
    def toggle_menu(self, event):
        if self.menu_open:
            self.close_menu()
        else:
            self.open_menu()

    # Открытие выпадающего меню с валютами
    def open_menu(self):
        if self.menu_window:
            self.close_menu()

        self.menu_window = tk.Toplevel(self)
        self.menu_window.overrideredirect(True)
        self.menu_window.configure(bg=self.colors["bg_white"])
        self.menu_window.focus_set()

        def on_focus_out(event):
            if self.menu_window and self.menu_window.focus_get() is None:
                self.after(100, self.check_focus)

        self.menu_window.bind("<FocusOut>", on_focus_out)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.menu_window.geometry(f"{self.winfo_width()}x200+{x}+{y}")

        listbox = tk.Listbox(self.menu_window, font=("Arial", 12),
                             bg=self.colors["bg_white"], fg=self.colors["text_black"],
                             selectbackground=self.colors["active_bg"],
                             selectforeground=self.colors["active_fg"],
                             bd=1, relief="solid")
        listbox.pack(fill=tk.BOTH, expand=True)

        for currency in CURRENCIES.keys():
            listbox.insert(tk.END, currency)

        current_text = self.cget("text")
        for i in range(listbox.size()):
            if listbox.get(i) == current_text:
                listbox.selection_set(i)
                listbox.see(i)
                break

        def select_currency(event):
            selection = listbox.curselection()
            if selection:
                selected = listbox.get(selection[0])
                self.config(text=selected)
                if selected in CURRENCIES:
                    self.master.master.master.data_manager.update_settings(currency=CURRENCIES[selected])
                    self.master.master.master.refresh_all_displays()
                self.close_menu()

        listbox.bind("<<ListboxSelect>>", select_currency)

        self.listbox = listbox
        self.menu_open = True

    # Проверка фокуса для закрытия меню
    def check_focus(self):
        if self.menu_window and not self.menu_window.focus_get():
            self.close_menu()

    # Закрытие выпадающего меню
    def close_menu(self):
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None
        self.menu_open = False


# Основной класс приложения Money Watcher
class MoneyWatcherApp:
    def __init__(self, root):
        self.root = root
        self.data_manager = DataManager()
        self.current_view = "Главная"
        self.current_date = datetime.now()
        self.hide_completed_goals = False
        self.current_sort_column = None
        self.current_sort_reverse = False
        self.current_sort_type_order = None

        self.selected_transactions = set()
        self.selected_goals = set()
        self.multi_delete_mode = False

        self.setup_window()
        self.apply_theme()
        self.create_sidebar()
        self.create_main_area()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.refresh_all_displays()

    # Настройка параметров главного окна
    def setup_window(self):
        self.root.title("Money Watcher")
        self.root.geometry("1350x820")
        self.root.minsize(1350, 820)
        self.root.maxsize(1350, 820)
        self.root.resizable(False, False)

        try:
            self.root.tk.call('tk', 'scaling', 1.25)
        except:
            pass

    # Обработчик закрытия приложения
    def on_closing(self):
        self.data_manager.save_data()
        self.root.destroy()

    # Применение цветовой темы
    def apply_theme(self):
        theme = self.data_manager.get_theme()
        if theme == "dark":
            self.colors = {
                "bg_white": DARK_BG_WHITE,
                "text_black": DARK_TEXT_BLACK,
                "accent_gray": DARK_ACCENT_GRAY,
                "bg_dark": DARK_BG_DARK,
                "bg_light_gray": DARK_BG_LIGHT_GRAY,
                "hover_gray": DARK_HOVER_GRAY,
                "active_bg": DARK_ACTIVE_BG,
                "active_fg": DARK_ACTIVE_FG,
                "inactive_bg": DARK_INACTIVE_BG,
                "inactive_fg": DARK_INACTIVE_FG,
                "entry_bg": DARK_ENTRY_BG,
                "button_bg": DARK_BUTTON_BG,
                "button_fg": DARK_BUTTON_FG,
                "progress_fill": DARK_PROGRESS_FILL,
                "title_bg": DARK_TITLE_BG,
                "title_fg": DARK_TITLE_FG
            }
        else:
            self.colors = {
                "bg_white": LIGHT_BG_WHITE,
                "text_black": LIGHT_TEXT_BLACK,
                "accent_gray": LIGHT_ACCENT_GRAY,
                "bg_dark": LIGHT_BG_DARK,
                "bg_light_gray": LIGHT_BG_LIGHT_GRAY,
                "hover_gray": LIGHT_HOVER_GRAY,
                "active_bg": LIGHT_ACTIVE_BG,
                "active_fg": LIGHT_ACTIVE_FG,
                "inactive_bg": LIGHT_INACTIVE_BG,
                "inactive_fg": LIGHT_INACTIVE_FG,
                "entry_bg": LIGHT_ENTRY_BG,
                "button_bg": LIGHT_BUTTON_BG,
                "button_fg": LIGHT_BUTTON_FG,
                "progress_fill": LIGHT_PROGRESS_FILL,
                "title_bg": LIGHT_TITLE_BG,
                "title_fg": LIGHT_TITLE_FG
            }

        self.root.configure(bg=self.colors["bg_white"])

        try:
            import ctypes
            HWND = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if self.data_manager.get_theme() == "dark":
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 20, ctypes.byref(ctypes.c_int(1)), 4)
            else:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 20, ctypes.byref(ctypes.c_int(0)), 4)
        except:
            pass

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background=self.colors["bg_white"],
                        foreground=self.colors["text_black"],
                        fieldbackground=self.colors["bg_white"],
                        rowheight=35,
                        borderwidth=1,
                        relief="solid",
                        font=("Arial", 11))
        style.configure("Treeview.Heading",
                        background=self.colors["bg_light_gray"],
                        foreground=self.colors["text_black"],
                        font=("Arial", 12, "bold"))
        style.map('Treeview', background=[('selected', self.colors["active_bg"])])

    # Перестроение интерфейса
    def rebuild_ui(self):
        current_view = self.current_view

        if hasattr(self, 'sidebar'):
            self.sidebar.destroy()
        if hasattr(self, 'main_container'):
            self.main_container.destroy()

        self.create_sidebar()
        self.create_main_area()
        self.current_view = current_view
        self.refresh_all_displays()

    # Создание боковой панели навигации
    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=280, bg=self.colors["bg_white"],
                                highlightbackground=self.colors["accent_gray"], highlightthickness=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.sidebar.pack_propagate(False)

        # Отрисовка логотипа в боковой панели
        logo_frame = tk.Frame(self.sidebar, bg=self.colors["bg_white"])
        logo_frame.pack(fill=tk.X, padx=20, pady=28)

        wallet_icon = tk.Label(logo_frame, text="💰", font=("Arial", 28),
                               bg=self.colors["bg_white"], fg=self.colors["text_black"])
        wallet_icon.pack(side=tk.LEFT, padx=(0, 10))

        logo_label = tk.Label(logo_frame, text="MONEY WATCHER", font=("Arial", 14, "bold"),
                              bg=self.colors["bg_white"], fg=self.colors["text_black"])
        logo_label.pack(side=tk.LEFT)

        # Отрисовка разделителя после логотипа
        separator = tk.Frame(self.sidebar, height=1, bg=self.colors["accent_gray"])
        separator.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Отрисовка навигационных кнопок в боковой панели
        self.nav_buttons = {}
        nav_items = [("🏠", "Главная"), ("📊", "Операции"), ("🎯", "Цели"), ("⚙️", "Настройки")]

        for icon, text in nav_items:
            btn_frame = tk.Frame(self.sidebar, bg=self.colors["bg_white"])
            btn_frame.pack(fill=tk.X, padx=16, pady=6)

            btn = tk.Button(btn_frame, text=f"{icon}  {text}", font=("Arial", 14),
                            bg=self.colors["inactive_bg"], fg=self.colors["inactive_fg"],
                            bd=0, anchor="w", padx=16, pady=12,
                            activebackground=self.colors["hover_gray"],
                            activeforeground=self.colors["inactive_fg"],
                            command=lambda t=text: self.switch_view(t))
            btn.pack(fill=tk.X)

            btn.bind("<Enter>", lambda e, b=btn, t=text: self.on_button_hover(b, t))
            btn.bind("<Leave>", lambda e, b=btn, t=text: self.on_button_leave(b, t))

            self.nav_buttons[text] = btn

        self.update_active_button()

    # Функционал подсветки кнопки при наведении
    def on_button_hover(self, button, text):
        if self.current_view != text:
            button.configure(bg=self.colors["hover_gray"], fg=self.colors["inactive_fg"])

    # Функционал возврата цвета кнопки после ухода курсора
    def on_button_leave(self, button, text):
        if self.current_view != text:
            button.configure(bg=self.colors["inactive_bg"], fg=self.colors["inactive_fg"])

    # Функционал обновления активной кнопки навигации
    def update_active_button(self):
        for text, btn in self.nav_buttons.items():
            if text == self.current_view:
                btn.configure(bg=self.colors["active_bg"], fg=self.colors["active_fg"])
            else:
                btn.configure(bg=self.colors["inactive_bg"], fg=self.colors["inactive_fg"])

    # Функционал переключения между страницами
    def switch_view(self, view_name):
        self.current_view = view_name
        self.multi_delete_mode = False
        self.selected_transactions.clear()
        self.selected_goals.clear()
        self.close_all_dropdowns()
        self.update_active_button()
        self.refresh_all_displays()

    # Функционал закрытия всех выпадающих меню
    def close_all_dropdowns(self):
        if hasattr(self, 'date_menu') and self.date_menu and self.date_menu.winfo_exists():
            self.close_date_menu()

    # Создание основной области с контентом
    def create_main_area(self):
        self.main_container = tk.Frame(self.root, bg=self.colors["bg_white"])
        self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.content_frame = tk.Frame(self.main_container, bg=self.colors["bg_white"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=28)

        self.scrollable_container = tk.Frame(self.main_container, bg=self.colors["bg_white"])
        self.scrollable_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=28)
        self.scrollable_container.pack_forget()

        self.canvas = tk.Canvas(self.scrollable_container, bg=self.colors["bg_white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.scrollable_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg_white"])

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Настройка прокрутки для основного Canvas главной страницы
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<Enter>", lambda e: self._bind_scroll_to_canvas())
        self.canvas.bind("<Leave>", lambda e: self._unbind_scroll_from_canvas())

        self.scrollable_frame.bind("<Enter>", lambda e: self._bind_scroll_to_canvas())
        self.scrollable_frame.bind("<Leave>", lambda e: self._unbind_scroll_from_canvas())

    # Привязка прокрутки к основному Canvas
    def _bind_scroll_to_canvas(self):
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self._scroll_bound = True

    # Отвязка прокрутки от основного Canvas
    def _unbind_scroll_from_canvas(self):
        self.canvas.unbind_all("<MouseWheel>")
        self._scroll_bound = False

    # Привязка прокрутки к виджету
    def _bind_scroll_to_widget(self, widget, scroll_func):
        def on_enter(event):
            widget.bind_all("<MouseWheel>", scroll_func)

        def on_leave(event):
            widget.unbind_all("<MouseWheel>")

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # Обновление всех отображаемых данных
    def refresh_all_displays(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if self.current_view == "Главная":
            self.content_frame.pack_forget()
            self.scrollable_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=28)
            self.build_dashboard()
        else:
            self.scrollable_container.pack_forget()
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=28)
            if self.current_view == "Операции":
                self.build_transactions_view()
            elif self.current_view == "Цели":
                self.build_goals_view()
            elif self.current_view == "Настройки":
                self.build_settings_view()

    # Форматирование валюты для отображения
    def format_currency(self, amount):
        currency = self.data_manager.get_currency()
        return f"{int(amount):,} {currency}".replace(",", " ")

    # Получение названия месяца на русском
    def get_month_name_ru(self, date_obj):
        eng_name = date_obj.strftime("%B")
        return MONTHS_RU.get(eng_name, eng_name)

    # Получение списка доступных месяцев
    def get_available_months_ru(self):
        months = []
        current = datetime.now()
        for i in range(-12, 13):
            date = current.replace(day=1) + timedelta(days=30 * i)
            months.append(f"{self.get_month_name_ru(date)} {date.year}")
        return months

    # Обработчик изменения месяца
    def on_month_change(self, selected_date_str):
        if not selected_date_str:
            return
        parts = selected_date_str.split()
        if len(parts) == 2:
            month_ru, year = parts[0], int(parts[1])
            for eng, ru in MONTHS_RU.items():
                if ru == month_ru:
                    self.current_date = datetime.strptime(f"{eng} {year}", "%B %Y")
                    break
        self.refresh_all_displays()

    # Переключение режима множественного удаления
    def toggle_multi_delete_mode(self):
        self.multi_delete_mode = not self.multi_delete_mode
        if not self.multi_delete_mode:
            self.selected_transactions.clear()
            self.selected_goals.clear()
        self.refresh_all_displays()

    # Удаление выбранных транзакций
    def delete_selected_transactions(self):
        if self.selected_transactions:
            if messagebox.askyesno("Подтверждение", f"Удалить {len(self.selected_transactions)} операций?"):
                self.data_manager.delete_transactions_bulk(list(self.selected_transactions))
                self.selected_transactions.clear()
                self.multi_delete_mode = False
                self.refresh_all_displays()

    # Удаление выбранных целей
    def delete_selected_goals(self):
        if self.selected_goals:
            dialog = tk.Toplevel(self.root)
            dialog.title("Удаление целей")
            dialog.geometry("450x240")
            dialog.configure(bg=self.colors["bg_white"])
            dialog.grab_set()

            tk.Label(dialog, text=f"Удалить {len(self.selected_goals)} целей?", font=("Arial", 14, "bold"),
                     bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)
            tk.Label(dialog, text="Выберите действие с накопленными средствами:",
                     bg=self.colors["bg_white"], fg=self.colors["text_black"], font=("Arial", 12)).pack()

            def delete_with_refund():
                self.data_manager.delete_goals_bulk(list(self.selected_goals), refund_to_balance=True)
                self.selected_goals.clear()
                self.multi_delete_mode = False
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех", "Цели удалены. Средства возвращены в баланс.")

            def delete_without_refund():
                self.data_manager.delete_goals_bulk(list(self.selected_goals), refund_to_balance=False)
                self.selected_goals.clear()
                self.multi_delete_mode = False
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех", "Цели удалены. Средства потеряны.")

            btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
            btn_frame.pack(pady=28)
            tk.Button(btn_frame, text="Вернуть в баланс", command=delete_with_refund,
                      bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=8,
                      font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Потерять средства", command=delete_without_refund,
                      bg=self.colors["bg_white"], fg=self.colors["text_black"], bd=1, padx=20, pady=8,
                      font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                      bg=self.colors["bg_white"], fg=self.colors["text_black"], bd=1, padx=20, pady=8,
                      font=("Arial", 11)).pack(side=tk.LEFT, padx=10)

    # Переключение выбора цели
    def toggle_goal_selection(self, goal_id):
        if goal_id in self.selected_goals:
            self.selected_goals.discard(goal_id)
        else:
            self.selected_goals.add(goal_id)

    # Переключение выбора транзакции
    def toggle_transaction_selection(self, trans_id):
        if trans_id in self.selected_transactions:
            self.selected_transactions.discard(trans_id)
        else:
            self.selected_transactions.add(trans_id)

    # Сортировка транзакций
    def sort_transactions(self, column):
        if column == "action":
            return

        if self.current_sort_column == column:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_column = column
            self.current_sort_reverse = False
            self.current_sort_type_order = None

        transactions = self.data_manager.get_all_transactions()

        if column == "id":
            transactions.sort(key=lambda x: x['id'], reverse=not self.current_sort_reverse)
        elif column == "date":
            transactions.sort(key=lambda x: x['date'], reverse=not self.current_sort_reverse)
        elif column == "name":
            transactions.sort(key=lambda x: x['name'].lower(), reverse=self.current_sort_reverse)
        elif column == "type":
            transactions.sort(key=lambda x: 0 if x['type'] == 'income' else 1, reverse=self.current_sort_reverse)
        elif column == "amount":
            if self.current_sort_reverse:
                income_trans = sorted([t for t in transactions if t['type'] == 'income'],
                                      key=lambda x: x['amount'], reverse=True)
                expense_trans = sorted([t for t in transactions if t['type'] == 'expense'],
                                       key=lambda x: x['amount'], reverse=True)
                transactions = income_trans + expense_trans
            else:
                income_trans = sorted([t for t in transactions if t['type'] == 'income'],
                                      key=lambda x: x['amount'])
                expense_trans = sorted([t for t in transactions if t['type'] == 'expense'],
                                       key=lambda x: x['amount'])
                transactions = income_trans + expense_trans

        self.current_transactions = transactions
        self.refresh_transactions_table()

    # Построение главной страницы
    def build_dashboard(self):
        # Отрисовка заголовка главной страницы
        header_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_white"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_frame = tk.Frame(header_frame, bg=self.colors["bg_white"])
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="ГЛАВНЫЙ ЭКРАН", font=("Arial", 28, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(anchor="w")
        tk.Label(title_frame, text="Анализ финансов и постановка целей", font=("Arial", 16),
                 fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(anchor="w")

        # Отрисовка панели действий на главной странице
        actions_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_white"])
        actions_frame.pack(fill=tk.X, pady=(20, 28))

        # Отрисовка кнопок действий в зависимости от режима
        if self.multi_delete_mode:
            delete_btn = tk.Button(actions_frame, text="🗑️ Удалить выбранные", font=("Arial", 13, "bold"),
                                   bg="#ff4444", fg="white", padx=20, pady=10, bd=0,
                                   command=self.delete_selected_transactions)
            delete_btn.pack(side=tk.LEFT, padx=(0, 16))

            cancel_btn = tk.Button(actions_frame, text="Отмена", font=("Arial", 13, "bold"),
                                   bg=self.colors["bg_dark"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                                   command=self.toggle_multi_delete_mode)
            cancel_btn.pack(side=tk.LEFT, padx=(0, 16))
        else:
            multi_btn = tk.Button(actions_frame, text="✓ Множественное удаление", font=("Arial", 13, "bold"),
                                  bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=10, bd=2,
                                  highlightbackground=self.colors["text_black"],
                                  command=self.toggle_multi_delete_mode)
            multi_btn.pack(side=tk.LEFT, padx=(0, 16))

        add_trans_btn = tk.Button(actions_frame, text="+ Добавить операцию", font=("Arial", 13, "bold"),
                                  bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                                  command=self.open_add_transaction_dialog)
        add_trans_btn.pack(side=tk.LEFT, padx=(0, 16))

        add_goal_btn = tk.Button(actions_frame, text="+ Добавить цель", font=("Arial", 13, "bold"),
                                 bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                                 command=self.open_add_goal_dialog)
        add_goal_btn.pack(side=tk.LEFT)

        # Отрисовка выбора даты на главной странице
        date_frame = tk.Frame(actions_frame, bg=self.colors["bg_white"])
        date_frame.pack(side=tk.RIGHT)

        self.month_var = tk.StringVar(value=f"{self.get_month_name_ru(self.current_date)} {self.current_date.year}")
        self.date_button = tk.Button(date_frame, textvariable=self.month_var, font=("Arial", 13),
                                     bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                     bd=1, relief="solid", padx=16, pady=6,
                                     command=self.toggle_date_menu)
        self.date_button.pack(side=tk.LEFT)

        # Отрисовка карточек с финансовой сводкой
        cards_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_white"])
        cards_frame.pack(fill=tk.X, pady=(0, 20))

        balance_card = tk.Frame(cards_frame, bg=self.colors["bg_white"],
                                highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        balance_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.create_summary_card(balance_card, "💰", "БАЛАНС",
                                 self.format_currency(self.data_manager.get_balance()))

        income_card = tk.Frame(cards_frame, bg=self.colors["bg_white"],
                               highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        income_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        self.create_summary_card(income_card, "📈", "ДОХОДЫ",
                                 self.format_currency(self.data_manager.get_monthly_income(self.current_date)),
                                 text_color=self.colors["text_black"])

        expense_card = tk.Frame(cards_frame, bg=self.colors["bg_white"],
                                highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        expense_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        self.create_summary_card(expense_card, "📉", "РАСХОДЫ",
                                 self.format_currency(self.data_manager.get_monthly_expense(self.current_date)),
                                 text_color=self.colors["text_black"])

        # Отрисовка основного контента с графиком и целями
        main_grid = tk.Frame(self.scrollable_frame, bg=self.colors["bg_white"])
        main_grid.pack(fill=tk.BOTH, expand=True)

        # Отрисовка левой колонки с графиком
        left_col = tk.Frame(main_grid, bg=self.colors["bg_white"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        chart_block = tk.Frame(left_col, bg=self.colors["bg_white"],
                               highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        chart_block.pack(fill=tk.BOTH, expand=True)

        # Отрисовка легенды графика
        legend_frame = tk.Frame(chart_block, bg=self.colors["bg_white"])
        legend_frame.pack(fill=tk.X, padx=16, pady=(10, 0))

        income_legend = tk.Frame(legend_frame, bg=self.colors["bg_white"])
        income_legend.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(income_legend, text="●", font=("Arial", 14), fg=self.colors["bg_dark"],
                 bg=self.colors["bg_white"]).pack(side=tk.LEFT)
        tk.Label(income_legend, text=f"Доходы", font=("Arial", 13),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, padx=(6, 0))

        expense_legend = tk.Frame(legend_frame, bg=self.colors["bg_white"])
        expense_legend.pack(side=tk.LEFT)
        tk.Label(expense_legend, text="●", font=("Arial", 14), fg=self.colors["accent_gray"],
                 bg=self.colors["bg_white"]).pack(side=tk.LEFT)
        tk.Label(expense_legend, text=f"Расходы", font=("Arial", 13),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, padx=(6, 0))

        sep = tk.Frame(chart_block, height=1, bg=self.colors["accent_gray"])
        sep.pack(fill=tk.X, padx=16, pady=8)

        self.chart_frame = tk.Frame(chart_block, bg=self.colors["bg_white"])
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        self.update_chart()

        # Отрисовка правой колонки с целями
        right_col = tk.Frame(main_grid, bg=self.colors["bg_white"])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(16, 0))

        goals_block = tk.Frame(right_col, bg=self.colors["bg_white"],
                               highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        goals_block.pack(fill=tk.BOTH, expand=True)

        # Отрисовка заголовка блока целей
        goals_header = tk.Frame(goals_block, bg=self.colors["bg_white"])
        goals_header.pack(fill=tk.X, padx=16, pady=10)
        tk.Label(goals_header, text="АКТУАЛЬНЫЕ ЦЕЛИ", font=("Arial", 15, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT)

        open_all_goals_btn = tk.Button(goals_header, text="Открыть все", font=("Arial", 12),
                                       bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                       bd=1, command=lambda: self.switch_view("Цели"))
        open_all_goals_btn.pack(side=tk.RIGHT)

        sep = tk.Frame(goals_block, height=1, bg=self.colors["accent_gray"])
        sep.pack(fill=tk.X)

        self.goals_list_frame = tk.Frame(goals_block, bg=self.colors["bg_white"])
        self.goals_list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        self.update_goals_list_dashboard()

        # Отрисовка нижнего блока с последними операциями
        bottom_frame = tk.Frame(self.scrollable_frame, bg=self.colors["bg_white"])
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        operations_block = tk.Frame(bottom_frame, bg=self.colors["bg_white"],
                                    highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        operations_block.pack(fill=tk.BOTH, expand=True)

        # Отрисовка заголовка блока операций
        ops_header = tk.Frame(operations_block, bg=self.colors["bg_white"])
        ops_header.pack(fill=tk.X, padx=16, pady=10)
        tk.Label(ops_header, text="ПОСЛЕДНИЕ ОПЕРАЦИИ", font=("Arial", 15, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT)

        open_all_ops_btn = tk.Button(ops_header, text="Открыть все", font=("Arial", 12),
                                     bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                     bd=1, command=lambda: self.switch_view("Операции"))
        open_all_ops_btn.pack(side=tk.RIGHT)

        sep = tk.Frame(operations_block, height=1, bg=self.colors["accent_gray"])
        sep.pack(fill=tk.X)

        self.operations_table_frame = tk.Frame(operations_block, bg=self.colors["bg_white"])
        self.operations_table_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        self.update_operations_table_dashboard()

        # Настройка прокрутки для всех элементов главной страницы
        self._setup_dashboard_scroll()

    # Настройка прокрутки для всех элементов главной страницы
    def _setup_dashboard_scroll(self):
        def scroll_canvas(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_scroll_recursive(widget):
            widget.bind("<MouseWheel>", scroll_canvas)
            for child in widget.winfo_children():
                bind_scroll_recursive(child)

        bind_scroll_recursive(self.scrollable_frame)

    # Открытие меню выбора даты
    def toggle_date_menu(self):
        if hasattr(self, 'date_menu') and self.date_menu and self.date_menu.winfo_exists():
            self.close_date_menu()
            return

        self.date_menu = tk.Toplevel(self.root)
        self.date_menu.overrideredirect(True)
        self.date_menu.configure(bg=self.colors["bg_white"])
        self.date_menu.focus_set()

        def on_focus_out(event):
            if self.date_menu and self.date_menu.focus_get() is None:
                self.after(100, self.check_date_menu_focus)

        self.date_menu.bind("<FocusOut>", on_focus_out)

        x = self.date_button.winfo_rootx()
        y = self.date_button.winfo_rooty() + self.date_button.winfo_height()
        self.date_menu.geometry(f"260x400+{x}+{y}")

        frame = tk.Frame(self.date_menu, bg=self.colors["bg_white"],
                         highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        frame.pack(fill=tk.BOTH, expand=True)

        # Отрисовка поля ручного ввода даты
        manual_frame = tk.Frame(frame, bg=self.colors["bg_white"])
        manual_frame.pack(fill=tk.X, padx=12, pady=12)

        tk.Label(manual_frame, text="Введите дату:", font=("Arial", 11),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(anchor="w")

        manual_entry = tk.Entry(manual_frame, font=("Arial", 12),
                                bg=self.colors["entry_bg"], fg=self.colors["text_black"])
        manual_entry.pack(fill=tk.X, pady=(6, 0))

        def apply_manual_date():
            date_str = manual_entry.get().strip()
            if date_str:
                try:
                    parts = date_str.split()
                    if len(parts) == 2:
                        month_ru, year = parts[0], int(parts[1])
                        for eng, ru in MONTHS_RU.items():
                            if ru == month_ru:
                                self.current_date = datetime.strptime(f"{eng} {year}", "%B %Y")
                                self.month_var.set(f"{month_ru} {year}")
                                self.close_date_menu()
                                self.refresh_all_displays()
                                return
                    date_obj = datetime.strptime(date_str, "%Y-%m")
                    self.current_date = date_obj
                    self.month_var.set(f"{self.get_month_name_ru(date_obj)} {date_obj.year}")
                    self.close_date_menu()
                    self.refresh_all_displays()
                except:
                    messagebox.showerror("Ошибка", "Неверный формат. Используйте: Месяц ГГГГ или ГГГГ-ММ")

        manual_btn = tk.Button(manual_frame, text="Применить", command=apply_manual_date,
                               bg=self.colors["button_bg"], fg=self.colors["button_fg"],
                               font=("Arial", 11), padx=12, pady=4)
        manual_btn.pack(anchor="e", pady=(6, 0))

        sep = tk.Frame(frame, height=1, bg=self.colors["accent_gray"])
        sep.pack(fill=tk.X, padx=12)

        # Отрисовка списка выбора даты
        list_frame = tk.Frame(frame, bg=self.colors["bg_white"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        listbox = tk.Listbox(list_frame, font=("Arial", 12),
                             bg=self.colors["bg_white"], fg=self.colors["text_black"],
                             selectbackground=self.colors["active_bg"],
                             selectforeground=self.colors["active_fg"],
                             bd=0, highlightthickness=0)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        months_set = set()
        current = datetime.now()
        for i in range(-24, 25):
            date = current.replace(day=1) + timedelta(days=30 * i)
            month_str = f"{self.get_month_name_ru(date)} {date.year}"
            if month_str not in months_set:
                months_set.add(month_str)
                listbox.insert(tk.END, month_str)

        current_str = self.month_var.get()
        for i in range(listbox.size()):
            if listbox.get(i) == current_str:
                listbox.selection_set(i)
                listbox.see(i)
                break

        def select_date(event):
            selection = listbox.curselection()
            if selection:
                selected = listbox.get(selection[0])
                parts = selected.split()
                if len(parts) == 2:
                    month_ru, year = parts[0], int(parts[1])
                    for eng, ru in MONTHS_RU.items():
                        if ru == month_ru:
                            self.current_date = datetime.strptime(f"{eng} {year}", "%B %Y")
                            self.month_var.set(selected)
                            self.close_date_menu()
                            self.refresh_all_displays()
                            break

        listbox.bind("<<ListboxSelect>>", select_date)

        self.date_listbox = listbox

    # Проверка фокуса меню даты
    def check_date_menu_focus(self):
        if self.date_menu and not self.date_menu.focus_get():
            self.close_date_menu()

    # Закрытие меню выбора даты
    def close_date_menu(self):
        if hasattr(self, 'date_menu') and self.date_menu and self.date_menu.winfo_exists():
            self.date_menu.destroy()
        self.date_menu = None

    # Создание карточки с финансовой сводкой
    def create_summary_card(self, parent, icon, title, value, text_color=None):
        if text_color is None:
            text_color = self.colors["text_black"]

        icon_label = tk.Label(parent, text=icon, font=("Arial", 28), bg=parent.cget("bg"), fg=text_color)
        icon_label.pack(pady=(14, 6))
        tk.Label(parent, text=title, font=("Arial", 13, "bold"), fg=self.colors["accent_gray"],
                 bg=parent.cget("bg")).pack()
        tk.Label(parent, text=value, font=("Arial", 20, "bold"), fg=text_color, bg=parent.cget("bg")).pack(pady=(6, 14))

    # Обновление графика доходов и расходов
    def update_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        income = self.data_manager.get_monthly_income(self.current_date)
        expense = self.data_manager.get_monthly_expense(self.current_date)

        fig = Figure(figsize=(5.5, 4.2), dpi=100, facecolor=self.colors["bg_white"])
        ax = fig.add_subplot(111)

        if income == 0 and expense == 0:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center',
                    fontsize=14, color=self.colors["accent_gray"])
            ax.axis('off')
        else:
            sizes = [income, expense]
            colors = [self.colors["bg_dark"], self.colors["accent_gray"]]
            labels = ["Доходы", "Расходы"]

            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                              startangle=90, textprops={'fontsize': 12})
            for text in texts:
                text.set_color(self.colors["text_black"])
                text.set_fontsize(12)
            for autotext in autotexts:
                autotext.set_color(self.colors["bg_white"])
                autotext.set_fontsize(12)
                autotext.set_weight('bold')
            ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Обновление списка целей на главной странице
    def update_goals_list_dashboard(self):
        for widget in self.goals_list_frame.winfo_children():
            widget.destroy()

        goals = self.data_manager.get_active_goals()
        if not goals:
            tk.Label(self.goals_list_frame, text="Нет активных целей.\nНажмите «+ Добавить цель»",
                     font=("Arial", 14), fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(pady=30)
            return

        for goal in goals:
            goal_frame = tk.Frame(self.goals_list_frame, bg=self.colors["bg_white"])
            goal_frame.pack(fill=tk.X, pady=12)

            # Отрисовка заголовка цели
            header = tk.Frame(goal_frame, bg=self.colors["bg_white"])
            header.pack(fill=tk.X)

            if self.multi_delete_mode:
                var = tk.BooleanVar(value=(goal['id'] in self.selected_goals))
                cb = tk.Checkbutton(header, bg=self.colors["bg_white"],
                                    variable=var,
                                    selectcolor=self.colors["bg_white"],
                                    activebackground=self.colors["bg_white"],
                                    fg=self.colors["text_black"],
                                    command=lambda gid=goal['id'], v=var: self._toggle_goal_check(gid, v))
                cb.pack(side=tk.LEFT, padx=(0, 10))

            tk.Label(header, text=goal['name'], font=("Arial", 14, "bold"),
                     fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, expand=True)

            if not self.multi_delete_mode:
                delete_btn = tk.Button(header, text="🗑️", font=("Arial", 12),
                                       bg=self.colors["bg_white"], fg=self.colors["text_black"], bd=0,
                                       command=lambda gid=goal['id']: self.delete_goal_with_options(gid))
                delete_btn.pack(side=tk.RIGHT)

            # Отрисовка сумм цели
            sums_frame = tk.Frame(goal_frame, bg=self.colors["bg_white"])
            sums_frame.pack(fill=tk.X, pady=(6, 4))
            current_str = self.format_currency(goal['current_amount'])
            target_str = self.format_currency(goal['target_amount'])
            tk.Label(sums_frame, text=current_str, font=("Arial", 13),
                     fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT)
            tk.Label(sums_frame, text=f"/ {target_str}", font=("Arial", 13),
                     fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, padx=(6, 0))

            # Отрисовка прогресс-бара цели
            progress = min(goal['current_amount'] / goal['target_amount'], 1.0) if goal['target_amount'] > 0 else 0
            progress_bar_bg = tk.Frame(goal_frame, height=10, bg=self.colors["hover_gray"],
                                       highlightbackground=self.colors["accent_gray"], highlightthickness=1)
            progress_bar_bg.pack(fill=tk.X, pady=(6, 4))

            progress_bar_fill = tk.Frame(progress_bar_bg, height=10, bg=self.colors["progress_fill"])
            progress_bar_fill.pack(side=tk.LEFT)

            def update_width(pb, p):
                self.root.update_idletasks()
                width = int(p * pb.master.winfo_width()) if pb.master.winfo_width() > 0 else 50
                pb.config(width=width)

            self.root.after(100, lambda: update_width(progress_bar_fill, progress))

            percent = int(progress * 100)
            deadline = goal.get('deadline', '')
            if deadline:
                deadline_text = f"до {deadline} ({percent}%)"
            else:
                deadline_text = f"({percent}%)"
            tk.Label(goal_frame, text=deadline_text, font=("Arial", 12),
                     fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(anchor="w")

            add_btn = tk.Button(goal_frame, text="+ Пополнить", font=("Arial", 12),
                                bg=self.colors["button_bg"], fg=self.colors["button_fg"], bd=0, padx=16, pady=6,
                                command=lambda gid=goal['id']: self.open_add_progress_dialog(gid))
            add_btn.pack(anchor="e", pady=(8, 0))

    # Обработчик переключения чекбокса цели
    def _toggle_goal_check(self, goal_id, var):
        if var.get():
            self.selected_goals.add(goal_id)
        else:
            self.selected_goals.discard(goal_id)

    # Обновление таблицы операций на главной странице
    def update_operations_table_dashboard(self):
        for widget in self.operations_table_frame.winfo_children():
            widget.destroy()

        columns = ("select", "date", "name", "type", "amount", "action")
        tree = ttk.Treeview(self.operations_table_frame, columns=columns, show="headings", height=5)

        tree.heading("select", text="✓")
        tree.heading("date", text="ДАТА", command=lambda: self.sort_dashboard_transactions("date"))
        tree.heading("name", text="НАЗВАНИЕ", command=lambda: self.sort_dashboard_transactions("name"))
        tree.heading("type", text="ТИП", command=lambda: self.sort_dashboard_transactions("type"))
        tree.heading("amount", text="СУММА", command=lambda: self.sort_dashboard_transactions("amount"))
        tree.heading("action", text="ДЕЙСТВИЕ")

        tree.column("select", width=50, anchor="center")
        tree.column("date", width=120, anchor="center")
        tree.column("name", width=300, anchor="w")
        tree.column("type", width=100, anchor="center")
        tree.column("amount", width=150, anchor="e")
        tree.column("action", width=100, anchor="center")

        style = ttk.Style()
        style.map('Treeview.Heading', background=[], foreground=[])

        transactions = self.data_manager.get_recent_transactions(5)

        for trans in transactions:
            trans_type = "Доход" if trans['type'] == 'income' else "Расход"
            sign = "+" if trans['type'] == 'income' else "-"
            amount_text = f"{sign}{self.format_currency(trans['amount'])}"

            if self.multi_delete_mode:
                tree.insert("", tk.END, values=("☐", trans['date'], trans['name'], trans_type, amount_text, ""))
            else:
                tree.insert("", tk.END, values=("", trans['date'], trans['name'], trans_type, amount_text, "🗑️"))

        def on_click(event):
            region = tree.identify_region(event.x, event.y)
            if region == "heading":
                return
            if region != "cell":
                return

            column = tree.identify_column(event.x)
            item = tree.identify_row(event.y)
            if not item:
                return

            values = tree.item(item, "values")
            if not values:
                return

            if self.multi_delete_mode and column == "#1":
                for trans in transactions:
                    if trans['date'] == values[1] and trans['name'] == values[2]:
                        self.toggle_transaction_selection(trans['id'])
                        if trans['id'] in self.selected_transactions:
                            tree.set(item, "select", "☑")
                        else:
                            tree.set(item, "select", "☐")
                        break
            elif not self.multi_delete_mode and column == "#6":
                for trans in transactions:
                    if trans['date'] == values[1] and trans['name'] == values[2]:
                        self.delete_transaction(trans['id'])
                        break

        tree.bind("<ButtonRelease-1>", on_click)

        tree.pack(fill=tk.BOTH, expand=True)

        self.dashboard_tree = tree
        self.dashboard_transactions = transactions

    # Сортировка транзакций на главной странице
    def sort_dashboard_transactions(self, column):
        if column == "action":
            return

        if not hasattr(self, 'dashboard_sort_column') or self.dashboard_sort_column != column:
            self.dashboard_sort_column = column
            self.dashboard_sort_reverse = False
        else:
            self.dashboard_sort_reverse = not self.dashboard_sort_reverse

        transactions = self.dashboard_transactions.copy()

        if column == "date":
            transactions.sort(key=lambda x: x['date'], reverse=not self.dashboard_sort_reverse)
        elif column == "name":
            transactions.sort(key=lambda x: x['name'].lower(), reverse=self.dashboard_sort_reverse)
        elif column == "type":
            transactions.sort(key=lambda x: 0 if x['type'] == 'income' else 1, reverse=self.dashboard_sort_reverse)
        elif column == "amount":
            if self.dashboard_sort_reverse:
                income_trans = sorted([t for t in transactions if t['type'] == 'income'],
                                      key=lambda x: x['amount'], reverse=True)
                expense_trans = sorted([t for t in transactions if t['type'] == 'expense'],
                                       key=lambda x: x['amount'], reverse=True)
                transactions = income_trans + expense_trans
            else:
                income_trans = sorted([t for t in transactions if t['type'] == 'income'],
                                      key=lambda x: x['amount'])
                expense_trans = sorted([t for t in transactions if t['type'] == 'expense'],
                                       key=lambda x: x['amount'])
                transactions = income_trans + expense_trans

        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)

        for trans in transactions:
            trans_type = "Доход" if trans['type'] == 'income' else "Расход"
            sign = "+" if trans['type'] == 'income' else "-"
            amount_text = f"{sign}{self.format_currency(trans['amount'])}"

            if self.multi_delete_mode:
                self.dashboard_tree.insert("", tk.END,
                                           values=("☐", trans['date'], trans['name'], trans_type, amount_text, ""))
            else:
                self.dashboard_tree.insert("", tk.END,
                                           values=("", trans['date'], trans['name'], trans_type, amount_text, "🗑️"))

        self.dashboard_transactions = transactions

    # Построение страницы управления операциями
    def build_transactions_view(self):
        # Отрисовка заголовка страницы операций
        header_frame = tk.Frame(self.content_frame, bg=self.colors["bg_white"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="УПРАВЛЕНИЕ ОПЕРАЦИЯМИ", font=("Arial", 28, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(anchor="w")

        # Отрисовка панели действий для операций
        actions_frame = tk.Frame(self.content_frame, bg=self.colors["bg_white"])
        actions_frame.pack(fill=tk.X, pady=(20, 28))

        if self.multi_delete_mode:
            delete_btn = tk.Button(actions_frame, text="🗑️ Удалить выбранные", font=("Arial", 13, "bold"),
                                   bg="#ff4444", fg="white", padx=20, pady=10, bd=0,
                                   command=self.delete_selected_transactions)
            delete_btn.pack(side=tk.LEFT, padx=(0, 16))

            cancel_btn = tk.Button(actions_frame, text="Отмена", font=("Arial", 13, "bold"),
                                   bg=self.colors["bg_dark"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                                   command=self.toggle_multi_delete_mode)
            cancel_btn.pack(side=tk.LEFT, padx=(0, 16))
        else:
            multi_btn = tk.Button(actions_frame, text="✓ Множественное удаление", font=("Arial", 13, "bold"),
                                  bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=10, bd=2,
                                  highlightbackground=self.colors["text_black"],
                                  command=self.toggle_multi_delete_mode)
            multi_btn.pack(side=tk.LEFT, padx=(0, 16))

        add_btn = tk.Button(actions_frame, text="+ Добавить операцию", font=("Arial", 13, "bold"),
                            bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                            command=self.open_add_transaction_dialog)
        add_btn.pack(side=tk.LEFT, padx=(0, 16))

        edit_btn = tk.Button(actions_frame, text="✏️ Редактировать операцию", font=("Arial", 13, "bold"),
                             bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=10, bd=2,
                             highlightbackground=self.colors["text_black"],
                             command=self.open_edit_transaction_dialog)
        edit_btn.pack(side=tk.LEFT)

        # Отрисовка таблицы операций
        table_container = tk.Frame(self.content_frame, bg=self.colors["bg_white"])
        table_container.pack(fill=tk.BOTH, expand=True)

        tree_frame = tk.Frame(table_container, bg=self.colors["bg_white"],
                              highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        if self.multi_delete_mode:
            columns = ("select", "id", "date", "name", "type", "amount")
            self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=14)
            self.tree.heading("select", text="✓")
            self.tree.heading("id", text="ID", command=lambda: self.sort_transactions("id"))
            self.tree.heading("date", text="ДАТА", command=lambda: self.sort_transactions("date"))
            self.tree.heading("name", text="НАЗВАНИЕ", command=lambda: self.sort_transactions("name"))
            self.tree.heading("type", text="ТИП", command=lambda: self.sort_transactions("type"))
            self.tree.heading("amount", text="СУММА", command=lambda: self.sort_transactions("amount"))
            self.tree.column("select", width=50, anchor="center")
        else:
            columns = ("id", "date", "name", "type", "amount", "action")
            self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=14)
            self.tree.heading("id", text="ID", command=lambda: self.sort_transactions("id"))
            self.tree.heading("date", text="ДАТА", command=lambda: self.sort_transactions("date"))
            self.tree.heading("name", text="НАЗВАНИЕ", command=lambda: self.sort_transactions("name"))
            self.tree.heading("type", text="ТИП", command=lambda: self.sort_transactions("type"))
            self.tree.heading("amount", text="СУММА", command=lambda: self.sort_transactions("amount"))
            self.tree.heading("action", text="ДЕЙСТВИЕ")
            self.tree.column("action", width=100, anchor="center")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("name", width=320, anchor="w")
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("amount", width=150, anchor="e")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.current_transactions = self.data_manager.get_all_transactions()
        self.refresh_transactions_table()

        def on_click(event):
            if self.multi_delete_mode:
                region = self.tree.identify_region(event.x, event.y)
                if region == "cell":
                    column = self.tree.identify_column(event.x)
                    if column == "#1":
                        item = self.tree.identify_row(event.y)
                        if item:
                            values = self.tree.item(item, "values")
                            if values and len(values) >= 6:
                                trans_id = int(values[1])
                                self.toggle_transaction_selection(trans_id)
                                if trans_id in self.selected_transactions:
                                    self.tree.set(item, "select", "☑")
                                else:
                                    self.tree.set(item, "select", "☐")
            else:
                region = self.tree.identify_region(event.x, event.y)
                if region == "cell":
                    column = self.tree.identify_column(event.x)
                    if column == "#6":
                        item = self.tree.identify_row(event.y)
                        if item:
                            values = self.tree.item(item, "values")
                            if values and len(values) >= 6:
                                trans_id = int(values[0])
                                self.delete_transaction(trans_id)

        self.tree.bind("<ButtonRelease-1>", on_click)

        # Настройка прокрутки для таблицы операций
        def on_tree_mousewheel(event):
            self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_tree_enter(event):
            self.tree.bind_all("<MouseWheel>", on_tree_mousewheel)

        def on_tree_leave(event):
            self.tree.unbind_all("<MouseWheel>")

        self.tree.bind("<Enter>", on_tree_enter)
        self.tree.bind("<Leave>", on_tree_leave)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)

    # Обновление данных в таблице операций
    def refresh_transactions_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for trans in self.current_transactions:
            trans_type = "Доход" if trans['type'] == 'income' else "Расход"
            sign = "+" if trans['type'] == 'income' else "-"
            amount_text = f"{sign}{self.format_currency(trans['amount'])}"

            if self.multi_delete_mode:
                self.tree.insert("", tk.END,
                                 values=("☐", trans['id'], trans['date'], trans['name'], trans_type, amount_text))
            else:
                self.tree.insert("", tk.END,
                                 values=(trans['id'], trans['date'], trans['name'], trans_type, amount_text, "🗑️"))

    # Диалог редактирования операции
    def open_edit_transaction_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите операцию для редактирования")
            return

        values = self.tree.item(selected[0], "values")
        if not values:
            return

        trans_id = int(values[0] if not self.multi_delete_mode else values[1])
        trans = next((t for t in self.data_manager.data['transactions'] if t['id'] == trans_id), None)
        if not trans:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать операцию")
        dialog.geometry("500x520")
        dialog.configure(bg=self.colors["bg_white"])
        dialog.grab_set()

        tk.Label(dialog, text=f"Редактирование операции #{trans['id']}", font=("Arial", 18, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)

        frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        frame.pack(pady=10, padx=28, fill=tk.BOTH)

        # Отрисовка полей формы редактирования
        tk.Label(frame, text="Название:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        name_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        name_entry.insert(0, trans['name'])
        name_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Сумма:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        amount_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                fg=self.colors["text_black"])
        amount_entry.insert(0, str(trans['amount']))
        amount_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        date_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        date_entry.insert(0, trans['date'])
        date_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Тип:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        type_var = tk.StringVar(value=trans['type'])

        type_frame = tk.Frame(frame, bg=self.colors["bg_white"])
        type_frame.pack(fill=tk.X, pady=(0, 16))

        expense_radio = tk.Radiobutton(type_frame, text="Расход", variable=type_var, value="expense",
                                       bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                       selectcolor=self.colors["bg_white"], font=("Arial", 12))
        expense_radio.pack(side=tk.LEFT, padx=(0, 20))

        income_radio = tk.Radiobutton(type_frame, text="Доход", variable=type_var, value="income",
                                      bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                      selectcolor=self.colors["bg_white"], font=("Arial", 12))
        income_radio.pack(side=tk.LEFT)

        # Функционал сохранения изменений операции
        def save():
            try:
                self.data_manager.update_transaction(
                    trans['id'],
                    name_entry.get(),
                    amount_entry.get(),
                    type_var.get(),
                    date_entry.get()
                )
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех", "Операция обновлена!")
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))

        btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        btn_frame.pack(pady=28)
        tk.Button(btn_frame, text="Сохранить", command=save, bg=self.colors["button_bg"],
                  fg=self.colors["button_fg"], padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg=self.colors["bg_white"],
                  fg=self.colors["text_black"], bd=1, padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

    # Построение страницы управления целями
    def build_goals_view(self):
        # Отрисовка заголовка страницы целей
        header_frame = tk.Frame(self.content_frame, bg=self.colors["bg_white"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="УПРАВЛЕНИЕ ЦЕЛЯМИ", font=("Arial", 28, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(anchor="w")

        # Отрисовка панели действий для целей
        actions_frame = tk.Frame(self.content_frame, bg=self.colors["bg_white"])
        actions_frame.pack(fill=tk.X, pady=(20, 28))

        if self.multi_delete_mode:
            delete_btn = tk.Button(actions_frame, text="🗑️ Удалить выбранные", font=("Arial", 13, "bold"),
                                   bg="#ff4444", fg="white", padx=20, pady=10, bd=0,
                                   command=self.delete_selected_goals)
            delete_btn.pack(side=tk.LEFT, padx=(0, 16))

            cancel_btn = tk.Button(actions_frame, text="Отмена", font=("Arial", 13, "bold"),
                                   bg=self.colors["bg_dark"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                                   command=self.toggle_multi_delete_mode)
            cancel_btn.pack(side=tk.LEFT, padx=(0, 16))
        else:
            multi_btn = tk.Button(actions_frame, text="✓ Множественное удаление", font=("Arial", 13, "bold"),
                                  bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=10, bd=2,
                                  highlightbackground=self.colors["text_black"],
                                  command=self.toggle_multi_delete_mode)
            multi_btn.pack(side=tk.LEFT, padx=(0, 16))

        add_btn = tk.Button(actions_frame, text="+ Добавить цель", font=("Arial", 13, "bold"),
                            bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=10, bd=0,
                            command=self.open_add_goal_dialog)
        add_btn.pack(side=tk.LEFT, padx=(0, 16))

        edit_btn = tk.Button(actions_frame, text="✏️ Редактировать цель", font=("Arial", 13, "bold"),
                             bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=10, bd=2,
                             highlightbackground=self.colors["text_black"],
                             command=self.open_edit_goal_dialog)
        edit_btn.pack(side=tk.LEFT, padx=(0, 16))

        hide_text = "🔒 Скрыть завершённые" if not self.hide_completed_goals else "🔓 Показать завершённые"
        hide_btn = tk.Button(actions_frame, text=hide_text, font=("Arial", 13, "bold"),
                             bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=10, bd=2,
                             highlightbackground=self.colors["text_black"],
                             command=self.toggle_hide_completed)
        hide_btn.pack(side=tk.LEFT)

        # Отрисовка контейнера с целями
        goals_container = tk.Frame(self.content_frame, bg=self.colors["bg_white"])
        goals_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(goals_container, bg=self.colors["bg_white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(goals_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_white"])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def set_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(0)

        scrollable_frame.bind("<Configure>", set_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Настройка прокрутки для целей
        def on_goals_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_goals_enter(event):
            canvas.bind_all("<MouseWheel>", on_goals_mousewheel)

        def on_goals_leave(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", on_goals_enter)
        canvas.bind("<Leave>", on_goals_leave)

        goals = self.data_manager.get_active_goals() if self.hide_completed_goals else self.data_manager.data['goals']
        row_frame = None
        for i, goal in enumerate(goals):
            if i % 3 == 0:
                row_frame = tk.Frame(scrollable_frame, bg=self.colors["bg_white"])
                row_frame.pack(fill=tk.X, pady=8)

            # Отрисовка карточки цели
            card = tk.Frame(row_frame, bg=self.colors["bg_white"],
                            highlightbackground=self.colors["accent_gray"], highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)

            # Отрисовка заголовка карточки цели
            header = tk.Frame(card, bg=self.colors["bg_white"])
            header.pack(fill=tk.X, padx=14, pady=8)

            if self.multi_delete_mode:
                var = tk.BooleanVar(value=(goal['id'] in self.selected_goals))
                cb = tk.Checkbutton(header, bg=self.colors["bg_white"],
                                    variable=var,
                                    selectcolor=self.colors["bg_white"],
                                    activebackground=self.colors["bg_white"],
                                    fg=self.colors["text_black"],
                                    command=lambda gid=goal['id'], v=var: self._toggle_goal_check(gid, v))
                cb.pack(side=tk.LEFT, padx=(0, 8))

            status_text = "✅ " if goal.get('completed', False) else ""
            tk.Label(header, text=f"{status_text}{goal['name']}", font=("Arial", 14, "bold"),
                     fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, expand=True)

            if not self.multi_delete_mode:
                delete_btn = tk.Button(header, text="🗑️", font=("Arial", 12),
                                       bg=self.colors["bg_white"], fg=self.colors["text_black"], bd=0,
                                       command=lambda gid=goal['id']: self.delete_goal_with_options(gid))
                delete_btn.pack(side=tk.RIGHT)

            # Отрисовка содержимого карточки цели
            content = tk.Frame(card, bg=self.colors["bg_white"])
            content.pack(fill=tk.X, padx=14, pady=(0, 10))

            target_str = self.format_currency(goal['target_amount'])
            current_str = self.format_currency(goal['current_amount'])
            tk.Label(content, text=f"{current_str} / {target_str}", font=("Arial", 13),
                     bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(anchor="w")

            progress = min(goal['current_amount'] / goal['target_amount'], 1.0) if goal['target_amount'] > 0 else 0
            percent = int(progress * 100)

            progress_bar_bg = tk.Frame(content, height=8, bg=self.colors["hover_gray"],
                                       highlightbackground=self.colors["accent_gray"], highlightthickness=1)
            progress_bar_bg.pack(fill=tk.X, pady=(6, 6))

            progress_bar_fill = tk.Frame(progress_bar_bg, height=8, bg=self.colors["progress_fill"])
            progress_bar_fill.pack(side=tk.LEFT)

            def update_width(pb, p):
                self.root.update_idletasks()
                width = int(p * pb.master.winfo_width()) if pb.master.winfo_width() > 0 else 50
                pb.config(width=width)

            self.root.after(100, lambda: update_width(progress_bar_fill, progress))

            deadline = goal.get('deadline', '')
            if deadline:
                deadline_text = f"до {deadline} ({percent}%)"
            else:
                deadline_text = f"({percent}%)"
            tk.Label(content, text=deadline_text, font=("Arial", 11),
                     fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(anchor="w")

            add_btn = tk.Button(content, text="+ Пополнить", font=("Arial", 12),
                                bg=self.colors["button_bg"], fg=self.colors["button_fg"], bd=0, padx=14, pady=5,
                                command=lambda gid=goal['id']: self.open_add_progress_dialog(gid))
            add_btn.pack(anchor="e", pady=(7, 0))

        canvas.yview_moveto(0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Переключение отображения завершённых целей
    def toggle_hide_completed(self):
        self.hide_completed_goals = not self.hide_completed_goals
        self.refresh_all_displays()

    # Диалог выбора цели для редактирования
    def open_edit_goal_dialog(self):
        goals = self.data_manager.get_active_goals() if self.hide_completed_goals else self.data_manager.data['goals']
        if not goals:
            messagebox.showwarning("Внимание", "Нет целей для редактирования")
            return

        if len(goals) == 1:
            goal = goals[0]
            self._show_edit_goal_dialog(goal)
            return

        select_dialog = tk.Toplevel(self.root)
        select_dialog.title("Выбор цели")
        select_dialog.geometry("450x350")
        select_dialog.configure(bg=self.colors["bg_white"])
        select_dialog.grab_set()

        tk.Label(select_dialog, text="Выберите цель для редактирования:", font=("Arial", 15, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)

        listbox = tk.Listbox(select_dialog, font=("Arial", 13), bg=self.colors["bg_white"],
                             fg=self.colors["text_black"])
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for g in goals:
            listbox.insert(tk.END,
                           f"{g['id']}: {g['name']} ({self.format_currency(g['current_amount'])} / {self.format_currency(g['target_amount'])})")

        def select_goal():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                goal = goals[idx]
                select_dialog.destroy()
                self._show_edit_goal_dialog(goal)
            else:
                messagebox.showwarning("Внимание", "Выберите цель")

        tk.Button(select_dialog, text="Выбрать", command=select_goal,
                  bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=8,
                  font=("Arial", 12)).pack(pady=20)

    # Диалог редактирования цели
    def _show_edit_goal_dialog(self, goal):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать цель")
        dialog.geometry("500x560")
        dialog.configure(bg=self.colors["bg_white"])
        dialog.grab_set()

        tk.Label(dialog, text=f"Редактирование цели #{goal['id']}", font=("Arial", 18, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)

        frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        frame.pack(pady=10, padx=28, fill=tk.BOTH)

        # Отрисовка полей формы редактирования цели
        tk.Label(frame, text="Название цели:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        name_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        name_entry.insert(0, goal['name'])
        name_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Целевая сумма:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        target_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                fg=self.colors["text_black"])
        target_entry.insert(0, str(goal['target_amount']))
        target_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Текущая сумма (опционально):", bg=self.colors["bg_white"],
                 fg=self.colors["text_black"], anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        current_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                 fg=self.colors["text_black"])
        if goal['current_amount'] > 0:
            current_entry.insert(0, str(goal['current_amount']))
        else:
            current_entry.insert(0, "")
        current_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Дата окончания (опционально):", bg=self.colors["bg_white"],
                 fg=self.colors["text_black"], anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        date_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        date_entry.insert(0, goal.get('deadline', ''))
        date_entry.pack(fill=tk.X, pady=(0, 16))

        completed_var = tk.BooleanVar(value=goal.get('completed', False))
        tk.Checkbutton(frame, text="Цель выполнена", variable=completed_var,
                       bg=self.colors["bg_white"], fg=self.colors["text_black"],
                       selectcolor=self.colors["bg_white"], font=("Arial", 12)).pack(anchor="w", pady=(0, 16))

        # Функционал сохранения изменений цели
        def save():
            try:
                current_val = current_entry.get().strip()
                self.data_manager.update_goal(
                    goal['id'],
                    name_entry.get(),
                    target_entry.get(),
                    current_val if current_val else "0",
                    date_entry.get(),
                    completed_var.get()
                )
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех", "Цель обновлена!")
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))

        btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        btn_frame.pack(pady=28)
        tk.Button(btn_frame, text="Сохранить", command=save, bg=self.colors["button_bg"],
                  fg=self.colors["button_fg"], padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg=self.colors["bg_white"],
                  fg=self.colors["text_black"], bd=1, padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

    # Построение страницы настроек
    def build_settings_view(self):
        settings_card = tk.Frame(self.content_frame, bg=self.colors["bg_white"],
                                 highlightbackground=self.colors["accent_gray"], highlightthickness=1)
        settings_card.pack(fill=tk.BOTH, expand=False, pady=20)

        # Отрисовка секции внешнего вида
        tk.Label(settings_card, text="Внешний вид", font=("Arial", 18, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(anchor="w", padx=28, pady=(28, 10))

        theme_frame = tk.Frame(settings_card, bg=self.colors["bg_white"])
        theme_frame.pack(anchor="w", padx=28, pady=(0, 20))

        tk.Label(theme_frame, text="Тема:", font=("Arial", 15),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, padx=(0, 20))

        theme_var = tk.StringVar(value=self.data_manager.get_theme())

        # Функционал смены темы
        def change_theme():
            new_theme = theme_var.get()
            self.data_manager.update_settings(theme=new_theme)
            self.apply_theme()
            self.rebuild_ui()

        light_radio = tk.Radiobutton(theme_frame, text="Светлая", variable=theme_var, value="light",
                                     bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                     selectcolor=self.colors["bg_white"], command=change_theme, font=("Arial", 13))
        light_radio.pack(side=tk.LEFT, padx=(0, 20))

        dark_radio = tk.Radiobutton(theme_frame, text="Тёмная", variable=theme_var, value="dark",
                                    bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                    selectcolor=self.colors["bg_white"], command=change_theme, font=("Arial", 13))
        dark_radio.pack(side=tk.LEFT)

        # Отрисовка секции выбора валюты
        currency_frame = tk.Frame(settings_card, bg=self.colors["bg_white"])
        currency_frame.pack(anchor="w", padx=28, pady=(0, 20))

        tk.Label(currency_frame, text="Валюта:", font=("Arial", 15),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(side=tk.LEFT, padx=(0, 20))

        current_currency = self.data_manager.get_currency()
        currency_text = "₽ (Рубль)"
        for name, symbol in CURRENCIES.items():
            if symbol == current_currency:
                currency_text = name
                break

        currency_btn = CurrencyButton(currency_frame, text=currency_text,
                                      colors=self.colors,
                                      bg=self.colors["bg_white"],
                                      fg=self.colors["text_black"],
                                      bd=1, relief="solid", padx=16, pady=6,
                                      font=("Arial", 13))
        currency_btn.pack(side=tk.LEFT)

        separator = tk.Frame(settings_card, height=1, bg=self.colors["accent_gray"])
        separator.pack(fill=tk.X, padx=28, pady=20)

        # Отрисовка секции управления данными
        tk.Label(settings_card, text="Управление данными", font=("Arial", 18, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(anchor="w", padx=28, pady=(0, 10))

        data_frame = tk.Frame(settings_card, bg=self.colors["bg_white"])
        data_frame.pack(anchor="w", padx=28, pady=(0, 20))

        save_btn = tk.Button(data_frame, text="Сохранить данные", font=("Arial", 13),
                             bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=8,
                             command=self.manual_save)
        save_btn.pack(side=tk.LEFT, padx=(0, 16))

        backup_btn = tk.Button(data_frame, text="Создать резервную копию", font=("Arial", 13),
                               bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=8, bd=2,
                               highlightbackground=self.colors["text_black"],
                               command=self.create_backup)
        backup_btn.pack(side=tk.LEFT, padx=(0, 16))

        change_file_btn = tk.Button(data_frame, text="Изменить файл данных", font=("Arial", 13),
                                    bg=self.colors["bg_white"], fg=self.colors["text_black"], padx=20, pady=8, bd=2,
                                    highlightbackground=self.colors["text_black"],
                                    command=self.change_data_file)
        change_file_btn.pack(side=tk.LEFT)

        separator = tk.Frame(settings_card, height=1, bg=self.colors["accent_gray"])
        separator.pack(fill=tk.X, padx=28, pady=20)

        # Отрисовка секции "О приложении"
        tk.Label(settings_card, text="О приложении", font=("Arial", 18, "bold"),
                 fg=self.colors["text_black"], bg=self.colors["bg_white"]).pack(anchor="w", padx=28, pady=(0, 10))
        tk.Label(settings_card, text="Money Watcher - приложение для учета личных финансов",
                 font=("Arial", 14), fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(anchor="w",
                                                                                                     padx=28,
                                                                                                     pady=(0, 6))
        tk.Label(settings_card, text=f"Текущий файл данных: {os.path.basename(self.data_manager.data_file)}",
                 font=("Arial", 13), fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(anchor="w",
                                                                                                     padx=28,
                                                                                                     pady=(0, 6))
        tk.Label(settings_card, text=f"Максимальная сумма операции: 4 200 000 000 000 ₽",
                 font=("Arial", 13), fg=self.colors["accent_gray"], bg=self.colors["bg_white"]).pack(anchor="w",
                                                                                                     padx=28,
                                                                                                     pady=(0, 28))

        # Отрисовка кнопки сброса данных
        reset_btn = tk.Button(settings_card, text="Сбросить все данные", font=("Arial", 13),
                              bg=self.colors["bg_white"], fg="red", bd=2, highlightbackground="red",
                              command=self.reset_all_data)
        reset_btn.pack(anchor="w", padx=28, pady=(0, 28))

    # Сохранение данных вручную
    def manual_save(self):
        self.data_manager.save_data()
        messagebox.showinfo("Успех", "Данные сохранены!")

    # Создание резервной копии
    def create_backup(self):
        backup_file = self.data_manager.create_backup()
        if backup_file:
            messagebox.showinfo("Успех", f"Резервная копия создана:\n{backup_file}")

    # Смена файла данных
    def change_data_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл данных",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
            defaultextension=".json"
        )
        if file_path:
            if self.data_manager.change_data_file(file_path):
                messagebox.showinfo("Успех", f"Файл данных изменён на:\n{file_path}")
                self.rebuild_ui()

    # Диалог добавления операции
    def open_add_transaction_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить операцию")
        dialog.geometry("500x520")
        dialog.configure(bg=self.colors["bg_white"])
        dialog.grab_set()

        tk.Label(dialog, text="Новая операция", font=("Arial", 18, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)

        frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        frame.pack(pady=10, padx=28, fill=tk.BOTH)

        # Отрисовка полей формы добавления операции
        tk.Label(frame, text="Название:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        name_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        name_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Сумма:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        amount_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                fg=self.colors["text_black"])
        amount_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        date_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Тип:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        type_var = tk.StringVar(value="expense")

        type_frame = tk.Frame(frame, bg=self.colors["bg_white"])
        type_frame.pack(fill=tk.X, pady=(0, 16))

        expense_radio = tk.Radiobutton(type_frame, text="Расход", variable=type_var, value="expense",
                                       bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                       selectcolor=self.colors["bg_white"], font=("Arial", 12))
        expense_radio.pack(side=tk.LEFT, padx=(0, 20))

        income_radio = tk.Radiobutton(type_frame, text="Доход", variable=type_var, value="income",
                                      bg=self.colors["bg_white"], fg=self.colors["text_black"],
                                      selectcolor=self.colors["bg_white"], font=("Arial", 12))
        income_radio.pack(side=tk.LEFT)

        # Функционал сохранения новой операции
        def save():
            try:
                self.data_manager.add_transaction(
                    name_entry.get(),
                    amount_entry.get(),
                    type_var.get(),
                    date_entry.get()
                )
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех", "Операция добавлена!")
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))

        btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        btn_frame.pack(pady=28)
        tk.Button(btn_frame, text="Сохранить", command=save, bg=self.colors["button_bg"],
                  fg=self.colors["button_fg"], padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg=self.colors["bg_white"],
                  fg=self.colors["text_black"], bd=1, padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

    # Диалог добавления цели
    def open_add_goal_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить цель")
        dialog.geometry("500x520")
        dialog.configure(bg=self.colors["bg_white"])
        dialog.grab_set()

        tk.Label(dialog, text="Новая цель", font=("Arial", 18, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)

        frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        frame.pack(pady=10, padx=28, fill=tk.BOTH)

        # Отрисовка полей формы добавления цели
        tk.Label(frame, text="Название цели:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        name_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        name_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Целевая сумма:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        target_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                fg=self.colors["text_black"])
        target_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Текущая сумма (опционально):", bg=self.colors["bg_white"],
                 fg=self.colors["text_black"], anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        current_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                 fg=self.colors["text_black"])
        current_entry.pack(fill=tk.X, pady=(0, 16))

        tk.Label(frame, text="Дата окончания (опционально):", bg=self.colors["bg_white"],
                 fg=self.colors["text_black"], anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        date_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                              fg=self.colors["text_black"])
        date_entry.pack(fill=tk.X, pady=(0, 16))

        # Функционал сохранения новой цели
        def save():
            try:
                current_val = current_entry.get().strip()
                date_val = date_entry.get().strip()
                self.data_manager.add_goal(
                    name_entry.get(),
                    target_entry.get(),
                    current_val if current_val else "0",
                    date_val if date_val else ""
                )
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех", "Цель добавлена!")
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))

        btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        btn_frame.pack(pady=28)
        tk.Button(btn_frame, text="Сохранить", command=save, bg=self.colors["button_bg"],
                  fg=self.colors["button_fg"], padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg=self.colors["bg_white"],
                  fg=self.colors["text_black"], bd=1, padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

    # Диалог пополнения цели
    def open_add_progress_dialog(self, goal_id):
        goal = next((g for g in self.data_manager.data['goals'] if g['id'] == goal_id), None)
        if not goal:
            return

        remaining = goal['target_amount'] - goal['current_amount']

        dialog = tk.Toplevel(self.root)
        dialog.title("Пополнить цель")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors["bg_white"])
        dialog.grab_set()

        tk.Label(dialog, text=f"Цель: {goal['name']}", font=("Arial", 16, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)
        tk.Label(dialog, text=f"Осталось накопить: {self.format_currency(remaining)}",
                 font=("Arial", 15), bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=(0, 20))

        frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        frame.pack(pady=10, padx=28, fill=tk.BOTH)

        tk.Label(frame, text="Сумма пополнения:", bg=self.colors["bg_white"], fg=self.colors["text_black"],
                 anchor="w", font=("Arial", 12)).pack(fill=tk.X, pady=(0, 6))
        amount_entry = tk.Entry(frame, font=("Arial", 13), bg=self.colors["entry_bg"],
                                fg=self.colors["text_black"])
        amount_entry.pack(fill=tk.X, pady=(0, 16))

        # Функционал пополнения цели
        def save():
            try:
                add_amount = self.data_manager.update_goal_progress(goal_id, amount_entry.get())
                dialog.destroy()
                self.refresh_all_displays()
                messagebox.showinfo("Успех",
                                    f"Цель пополнена на {self.format_currency(add_amount)}!\nСумма списана как расход.")
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))

        btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        btn_frame.pack(pady=28)
        tk.Button(btn_frame, text="Пополнить", command=save, bg=self.colors["button_bg"],
                  fg=self.colors["button_fg"], padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, bg=self.colors["bg_white"],
                  fg=self.colors["text_black"], bd=1, padx=28, pady=8, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

    # Удаление цели с выбором опций
    def delete_goal_with_options(self, goal_id):
        goal = next((g for g in self.data_manager.data['goals'] if g['id'] == goal_id), None)
        if not goal:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Удаление цели")
        dialog.geometry("500x280")
        dialog.configure(bg=self.colors["bg_white"])
        dialog.grab_set()

        tk.Label(dialog, text=f"Цель: {goal['name']}", font=("Arial", 16, "bold"),
                 bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=20)
        tk.Label(dialog, text=f"Накоплено: {self.format_currency(goal['current_amount'])}",
                 font=("Arial", 15), bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack(pady=(0, 20))
        tk.Label(dialog, text="Выберите действие с накопленными средствами:",
                 font=("Arial", 14), bg=self.colors["bg_white"], fg=self.colors["text_black"]).pack()

        # Функционал удаления с возвратом средств
        def delete_with_refund():
            self.data_manager.delete_goal(goal_id, refund_to_balance=True)
            dialog.destroy()
            self.refresh_all_displays()
            messagebox.showinfo("Успех", "Цель удалена. Средства возвращены в баланс.")

        # Функционал удаления без возврата средств
        def delete_without_refund():
            self.data_manager.delete_goal(goal_id, refund_to_balance=False)
            dialog.destroy()
            self.refresh_all_displays()
            messagebox.showinfo("Успех", "Цель удалена. Средства потеряны.")

        btn_frame = tk.Frame(dialog, bg=self.colors["bg_white"])
        btn_frame.pack(pady=28)
        tk.Button(btn_frame, text="Вернуть в баланс", command=delete_with_refund,
                  bg=self.colors["button_bg"], fg=self.colors["button_fg"], padx=20, pady=8,
                  font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Потерять средства", command=delete_without_refund,
                  bg=self.colors["bg_white"], fg=self.colors["text_black"], bd=1, padx=20, pady=8,
                  font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy,
                  bg=self.colors["bg_white"], fg=self.colors["text_black"], bd=1, padx=20, pady=8,
                  font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

    # Удаление транзакции с подтверждением
    def delete_transaction(self, trans_id):
        if messagebox.askyesno("Подтверждение", "Удалить эту операцию?"):
            self.data_manager.delete_transaction(trans_id)
            self.refresh_all_displays()

    # Сброс всех данных приложения
    def reset_all_data(self):
        if messagebox.askyesno("Сброс данных", "ВНИМАНИЕ! Все данные будут безвозвратно удалены.\nПродолжить?"):
            self.data_manager.data = {"transactions": [], "goals": [], "settings": self.data_manager.data["settings"]}
            self.data_manager.save_data()
            self.refresh_all_displays()
            messagebox.showinfo("Готово", "Все данные сброшены")


# Точка входа в приложение
if __name__ == "__main__":
    root = tk.Tk()
    app = MoneyWatcherApp(root)
    root.mainloop()
