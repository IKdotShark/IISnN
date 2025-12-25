"""
Система коллективного принятия решений
Предметная область: Выбор совместного места отдыха
Автор: [Ваше имя]
Дата: [Дата]
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.font as tkfont
import json
import os
from datetime import datetime
import models

class VacationPlannerApp:
    """Основное приложение для планирования совместного отдыха"""

    def __init__(self, root):
        self.root = root
        self.root.title("Планировщик совместного отдыха")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f8ff')

        # Загрузка данных о курортах
        self.load_resorts_data()

        # Инициализация данных
        self.travelers = []
        self.resorts = []
        self.profile = []

        # Цветовая схема
        self.colors = {
            'primary': '#4a90e2',
            'secondary': '#5cb85c',
            'accent': '#f0ad4e',
            'background': '#f0f8ff',
            'card_bg': '#ffffff',
            'text': '#333333'
        }

        # Настройка стилей
        self.setup_styles()

        # Создание интерфейса
        self.create_widgets()

        # Привязка событий
        self.bind_events()

        # Центрирование окна
        self.center_window()

    def load_resorts_data(self):
        """Загрузка справочника курортов"""
        resorts_file = "resorts_data.json"

        # Если файл существует, загружаем его
        if os.path.exists(resorts_file):
            try:
                with open(resorts_file, 'r', encoding='utf-8') as f:
                    self.resorts_catalog = json.load(f)
            except:
                self.create_default_resorts_catalog()
        else:
            self.create_default_resorts_catalog()

    def create_default_resorts_catalog(self):
        """Создание стандартного каталога курортов"""
        self.resorts_catalog = {
            "categories": ["Пляжный", "Горнолыжный", "Экскурсионный", "СПА", "Экологический"],
            "countries": ["Турция", "Египет", "Тайланд", "Испания", "Италия", "Франция"],
            "resorts": [
                {"name": "Анталья", "category": "Пляжный", "country": "Турция", "price": "средний"},
                {"name": "Шарм-эль-Шейх", "category": "Пляжный", "country": "Египет", "price": "бюджетный"},
                {"name": "Пхукет", "category": "Пляжный", "country": "Тайланд", "price": "средний"},
                {"name": "Куршевель", "category": "Горнолыжный", "country": "Франция", "price": "высокий"},
                {"name": "Барселона", "category": "Экскурсионный", "country": "Испания", "price": "средний"},
                {"name": "Рим", "category": "Экскурсионный", "country": "Италия", "price": "средний"},
                {"name": "Карловы Вары", "category": "СПА", "country": "Чехия", "price": "высокий"},
                {"name": "Байкал", "category": "Экологический", "country": "Россия", "price": "бюджетный"}
            ]
        }

        # Сохраняем каталог в файл
        with open("resorts_data.json", 'w', encoding='utf-8') as f:
            json.dump(self.resorts_catalog, f, ensure_ascii=False, indent=2)

    def setup_styles(self):
        """Настройка стилей элементов интерфейса"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Настройка цветов для виджетов
        self.style.configure('Primary.TButton',
                             background=self.colors['primary'],
                             foreground='white',
                             padding=10,
                             font=('Segoe UI', 10, 'bold'))

        self.style.configure('Secondary.TButton',
                             background=self.colors['secondary'],
                             foreground='white',
                             padding=10,
                             font=('Segoe UI', 10))

        self.style.configure('Title.TLabel',
                             font=('Segoe UI', 16, 'bold'),
                             foreground=self.colors['primary'])

        self.style.configure('Card.TFrame',
                             background=self.colors['card_bg'],
                             relief='raised',
                             borderwidth=2)

    def create_widgets(self):
        """Создание всех элементов интерфейса"""

        # Заголовок
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame,
                               text="Планировщик Совместного Отдыха",
                               font=('Segoe UI', 24, 'bold'),
                               fg='white',
                               bg=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        # Основной контейнер с вкладками
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка 1: Участники
        participants_frame = self.create_participants_tab()
        notebook.add(participants_frame, text="Участники")

        # Вкладка 2: Варианты отдыха
        resorts_frame = self.create_resorts_tab()
        notebook.add(resorts_frame, text="Варианты отдыха")

        # Вкладка 3: Голосование
        voting_frame = self.create_voting_tab()
        notebook.add(voting_frame, text="Голосование")

        # Вкладка 4: Результаты
        results_frame = self.create_results_tab()
        notebook.add(results_frame, text="Результаты")

        # Статус бар
        self.status_bar = tk.Label(self.root,
                                   text="Готов к работе. Добавьте участников и варианты отдыха.",
                                   bd=1,
                                   relief=tk.SUNKEN,
                                   anchor=tk.W,
                                   bg='white')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_participants_tab(self):
        """Создание вкладки для управления участниками"""
        frame = tk.Frame(self.root, bg=self.colors['background'])

        # Заголовок
        title = tk.Label(frame,
                         text="Участники поездки",
                         font=('Segoe UI', 18, 'bold'),
                         fg=self.colors['primary'],
                         bg=self.colors['background'])
        title.pack(pady=(20, 10))

        # Карточка добавления участника
        add_card = tk.Frame(frame,
                            bg=self.colors['card_bg'],
                            relief='ridge',
                            borderwidth=1)
        add_card.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(add_card,
                 text="Добавить нового участника:",
                 font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card_bg']).pack(pady=10)

        # Поля для ввода
        input_frame = tk.Frame(add_card, bg=self.colors['card_bg'])
        input_frame.pack(pady=10)

        tk.Label(input_frame,
                 text="Имя:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).grid(row=0, column=0, padx=5, pady=5)

        self.name_entry = tk.Entry(input_frame,
                                   font=('Segoe UI', 10),
                                   width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame,
                 text="Предпочтения:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).grid(row=1, column=0, padx=5, pady=5)

        self.preferences_entry = tk.Entry(input_frame,
                                          font=('Segoe UI', 10),
                                          width=30)
        self.preferences_entry.grid(row=1, column=1, padx=5, pady=5)

        # Кнопка добавления
        add_button = ttk.Button(add_card,
                                text="Добавить участника",
                                style='Primary.TButton',
                                command=self.add_traveler)
        add_button.pack(pady=10)

        # Список участников
        list_frame = tk.Frame(frame, bg=self.colors['background'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(list_frame,
                 text="Список участников:",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['background']).pack(anchor=tk.W)

        # Treeview для отображения участников
        columns = ('name', 'preferences')
        self.travelers_tree = ttk.Treeview(list_frame,
                                           columns=columns,
                                           show='headings',
                                           height=8)

        self.travelers_tree.heading('name', text='Имя')
        self.travelers_tree.heading('preferences', text='Предпочтения')

        self.travelers_tree.column('name', width=150)
        self.travelers_tree.column('preferences', width=300)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(list_frame,
                                  orient=tk.VERTICAL,
                                  command=self.travelers_tree.yview)
        self.travelers_tree.configure(yscrollcommand=scrollbar.set)

        self.travelers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка удаления
        delete_button = ttk.Button(list_frame,
                                   text="Удалить выбранного",
                                   style='Secondary.TButton',
                                   command=self.delete_traveler)
        delete_button.pack(pady=5)

        return frame

    def create_resorts_tab(self):
        """Создание вкладки для управления вариантами отдыха"""
        frame = tk.Frame(self.root, bg=self.colors['background'])

        # Заголовок
        title = tk.Label(frame,
                         text="Варианты мест для отдыха",
                         font=('Segoe UI', 18, 'bold'),
                         fg=self.colors['primary'],
                         bg=self.colors['background'])
        title.pack(pady=(20, 10))

        # Карточка добавления курорта
        add_card = tk.Frame(frame,
                            bg=self.colors['card_bg'],
                            relief='ridge',
                            borderwidth=1)
        add_card.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(add_card,
                 text="Добавить вариант отдыха:",
                 font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card_bg']).pack(pady=10)

        # Поля для ввода с выпадающими списками
        input_frame = tk.Frame(add_card, bg=self.colors['card_bg'])
        input_frame.pack(pady=10)

        # Название курорта
        tk.Label(input_frame,
                 text="Название:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).grid(row=0, column=0, padx=5, pady=5)

        self.resort_name_entry = tk.Entry(input_frame,
                                          font=('Segoe UI', 10),
                                          width=30)
        self.resort_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Страна (выпадающий список)
        tk.Label(input_frame,
                 text="Страна:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).grid(row=1, column=0, padx=5, pady=5)

        self.country_var = tk.StringVar()
        country_combo = ttk.Combobox(input_frame,
                                     textvariable=self.country_var,
                                     values=self.resorts_catalog['countries'],
                                     width=28,
                                     state='readonly')
        country_combo.grid(row=1, column=1, padx=5, pady=5)
        country_combo.set("Выберите страну")

        # Тип отдыха (выпадающий список)
        tk.Label(input_frame,
                 text="Тип отдыха:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).grid(row=2, column=0, padx=5, pady=5)

        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(input_frame,
                                      textvariable=self.category_var,
                                      values=self.resorts_catalog['categories'],
                                      width=28,
                                      state='readonly')
        category_combo.grid(row=2, column=1, padx=5, pady=5)
        category_combo.set("Выберите тип")

        # Ценовой диапазон
        tk.Label(input_frame,
                 text="Ценовой диапазон:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).grid(row=3, column=0, padx=5, pady=5)

        self.price_var = tk.StringVar()
        price_combo = ttk.Combobox(input_frame,
                                   textvariable=self.price_var,
                                   values=["бюджетный", "средний", "высокий"],
                                   width=28,
                                   state='readonly')
        price_combo.grid(row=3, column=1, padx=5, pady=5)
        price_combo.set("Выберите цену")

        # Кнопка добавления из каталога
        catalog_frame = tk.Frame(add_card, bg=self.colors['card_bg'])
        catalog_frame.pack(pady=10)

        tk.Label(catalog_frame,
                 text="Или выберите из каталога:",
                 font=('Segoe UI', 10),
                 bg=self.colors['card_bg']).pack(side=tk.LEFT, padx=5)

        self.catalog_var = tk.StringVar()
        catalog_combo = ttk.Combobox(catalog_frame,
                                     textvariable=self.catalog_var,
                                     values=[r["name"] for r in self.resorts_catalog["resorts"]],
                                     width=25,
                                     state='readonly')
        catalog_combo.pack(side=tk.LEFT, padx=5)
        catalog_combo.set("Выберите из списка")

        catalog_button = ttk.Button(catalog_frame,
                                    text="Добавить",
                                    command=self.add_from_catalog)
        catalog_button.pack(side=tk.LEFT, padx=5)

        # Кнопки добавления
        button_frame = tk.Frame(add_card, bg=self.colors['card_bg'])
        button_frame.pack(pady=10)

        add_manual_button = ttk.Button(button_frame,
                                       text="Добавить вручную",
                                       style='Primary.TButton',
                                       command=self.add_resort_manual)
        add_manual_button.pack(side=tk.LEFT, padx=5)

        # Список курортов
        list_frame = tk.Frame(frame, bg=self.colors['background'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(list_frame,
                 text="Доступные варианты:",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['background']).pack(anchor=tk.W)

        # Treeview для отображения курортов
        columns = ('name', 'country', 'category', 'price')
        self.resorts_tree = ttk.Treeview(list_frame,
                                         columns=columns,
                                         show='headings',
                                         height=8)

        self.resorts_tree.heading('name', text='Название')
        self.resorts_tree.heading('country', text='Страна')
        self.resorts_tree.heading('category', text='Тип отдыха')
        self.resorts_tree.heading('price', text='Цена')

        self.resorts_tree.column('name', width=150)
        self.resorts_tree.column('country', width=100)
        self.resorts_tree.column('category', width=120)
        self.resorts_tree.column('price', width=80)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(list_frame,
                                  orient=tk.VERTICAL,
                                  command=self.resorts_tree.yview)
        self.resorts_tree.configure(yscrollcommand=scrollbar.set)

        self.resorts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка удаления
        delete_button = ttk.Button(list_frame,
                                   text="Удалить выбранное",
                                   style='Secondary.TButton',
                                   command=self.delete_resort)
        delete_button.pack(pady=5)

        return frame

    def create_voting_tab(self):
        """Создание вкладки для голосования"""
        frame = tk.Frame(self.root, bg=self.colors['background'])

        # Заголовок
        title = tk.Label(frame,
                         text="Ранжирование вариантов отдыха",
                         font=('Segoe UI', 18, 'bold'),
                         fg=self.colors['primary'],
                         bg=self.colors['background'])
        title.pack(pady=(20, 10))

        # Выбор участника для голосования
        voter_frame = tk.Frame(frame, bg=self.colors['background'])
        voter_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(voter_frame,
                 text="Выберите участника для голосования:",
                 font=('Segoe UI', 11),
                 bg=self.colors['background']).pack(side=tk.LEFT, padx=5)

        self.voter_var = tk.StringVar()
        self.voter_combo = ttk.Combobox(voter_frame,
                                        textvariable=self.voter_var,
                                        width=25,
                                        state='readonly')
        self.voter_combo.pack(side=tk.LEFT, padx=5)

        # Область для ранжирования
        ranking_frame = tk.Frame(frame, bg=self.colors['card_bg'], relief='ridge', borderwidth=1)
        ranking_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(ranking_frame,
                 text="Перетащите варианты для установки приоритета (сверху - самый желаемый):",
                 font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card_bg']).pack(pady=10)

        # Список для ранжирования
        self.ranking_listbox = tk.Listbox(ranking_frame,
                                          font=('Segoe UI', 10),
                                          height=12,
                                          selectmode=tk.SINGLE)
        self.ranking_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Кнопки управления ранжированием
        button_frame = tk.Frame(ranking_frame, bg=self.colors['card_bg'])
        button_frame.pack(pady=10)

        ttk.Button(button_frame,
                   text="Выше",
                   command=self.move_up).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Ниже",
                   command=self.move_down).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Сохранить голос",
                   style='Primary.TButton',
                   command=self.save_vote).pack(side=tk.LEFT, padx=20)

        # Информация о прогрессе
        self.progress_label = tk.Label(frame,
                                       text="Голосов сохранено: 0 из 0",
                                       font=('Segoe UI', 10),
                                       bg=self.colors['background'])
        self.progress_label.pack(pady=5)

        # Кнопка начала голосования заново
        ttk.Button(frame,
                   text="Начать голосование заново",
                   style='Secondary.TButton',
                   command=self.reset_voting).pack(pady=10)

        return frame

    def create_results_tab(self):
        """Создание вкладки для отображения результатов"""
        frame = tk.Frame(self.root, bg=self.colors['background'])

        # Заголовок
        title = tk.Label(frame,
                         text="Результаты голосования",
                         font=('Segoe UI', 18, 'bold'),
                         fg=self.colors['primary'],
                         bg=self.colors['background'])
        title.pack(pady=(20, 10))

        # Кнопка расчета результатов
        calculate_button = ttk.Button(frame,
                                      text="Рассчитать результаты",
                                      style='Primary.TButton',
                                      command=self.calculate_results)
        calculate_button.pack(pady=10)

        # Область для отображения результатов
        results_frame = tk.Frame(frame, bg=self.colors['card_bg'], relief='ridge', borderwidth=1)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Notebook для разных методов
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Метод относительного большинства
        majority_frame = tk.Frame(results_notebook, bg='white')
        results_notebook.add(majority_frame, text="Относительное большинство")
        self.majority_text = scrolledtext.ScrolledText(majority_frame,
                                                       wrap=tk.WORD,
                                                       font=('Segoe UI', 10))
        self.majority_text.pack(fill=tk.BOTH, expand=True)

        # Метод Кондорсе
        condorcet_frame = tk.Frame(results_notebook, bg='white')
        results_notebook.add(condorcet_frame, text="Метод Кондорсе")
        self.condorcet_text = scrolledtext.ScrolledText(condorcet_frame,
                                                        wrap=tk.WORD,
                                                        font=('Segoe UI', 10))
        self.condorcet_text.pack(fill=tk.BOTH, expand=True)

        # Метод Борда
        borda_frame = tk.Frame(results_notebook, bg='white')
        results_notebook.add(borda_frame, text="Метод Борда")
        self.borda_text = scrolledtext.ScrolledText(borda_frame,
                                                    wrap=tk.WORD,
                                                    font=('Segoe UI', 10))
        self.borda_text.pack(fill=tk.BOTH, expand=True)

        # Сводный отчет
        summary_frame = tk.Frame(results_notebook, bg='white')
        results_notebook.add(summary_frame, text="Сводный отчет")
        self.summary_text = scrolledtext.ScrolledText(summary_frame,
                                                      wrap=tk.WORD,
                                                      font=('Segoe UI', 10))
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Область для визуализации
        viz_frame = tk.Frame(frame, bg=self.colors['card_bg'], relief='ridge', borderwidth=1)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(viz_frame,
                 text="Визуализация результатов:",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['card_bg']).pack(pady=10)

        self.visualization_text = scrolledtext.ScrolledText(viz_frame,
                                                            wrap=tk.WORD,
                                                            font=('Courier', 10),
                                                            height=10)
        self.visualization_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        return frame

    def bind_events(self):
        """Привязка обработчиков событий"""
        self.voter_combo.bind('<<ComboboxSelected>>', self.on_voter_selected)

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def update_status(self, message):
        """Обновление статусной строки"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")

    def add_traveler(self):
        """Добавление нового участника"""
        name = self.name_entry.get().strip()
        preferences = self.preferences_entry.get().strip()

        if not name:
            messagebox.showwarning("Внимание", "Введите имя участника!")
            return

        if name in self.travelers:
            messagebox.showwarning("Внимание", "Участник с таким именем уже существует!")
            return

        self.travelers.append(name)

        # Добавление в Treeview
        self.travelers_tree.insert('', 'end', values=(name, preferences))

        # Обновление выпадающего списка для голосования
        self.voter_combo['values'] = self.travelers

        # Очистка полей ввода
        self.name_entry.delete(0, tk.END)
        self.preferences_entry.delete(0, tk.END)

        self.update_status(f"Добавлен участник: {name}")

    def delete_traveler(self):
        """Удаление выбранного участника"""
        selection = self.travelers_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите участника для удаления!")
            return

        for item in selection:
            values = self.travelers_tree.item(item, 'values')
            name = values[0]

            # Удаление из списка
            if name in self.travelers:
                self.travelers.remove(name)

            # Удаление из Treeview
            self.travelers_tree.delete(item)

        # Обновление выпадающего списка
        self.voter_combo['values'] = self.travelers

        self.update_status(f"Удален участник: {name}")

    def add_resort_manual(self):
        """Добавление курорта вручную"""
        name = self.resort_name_entry.get().strip()
        country = self.country_var.get()
        category = self.category_var.get()
        price = self.price_var.get()

        if not name:
            messagebox.showwarning("Внимание", "Введите название курорта!")
            return

        if country == "Выберите страну":
            messagebox.showwarning("Внимание", "Выберите страну!")
            return

        if category == "Выберите тип":
            messagebox.showwarning("Внимание", "Выберите тип отдыха!")
            return

        if price == "Выберите цену":
            messagebox.showwarning("Внимание", "Выберите ценовой диапазон!")
            return

        # Формирование полного названия
        full_name = f"{name} ({country}, {category}, {price})"

        if full_name in self.resorts:
            messagebox.showwarning("Внимание", "Такой курорт уже существует!")
            return

        self.resorts.append(full_name)

        # Добавление в Treeview
        self.resorts_tree.insert('', 'end', values=(name, country, category, price))

        # Очистка полей ввода
        self.resort_name_entry.delete(0, tk.END)
        self.country_var.set("Выберите страну")
        self.category_var.set("Выберите тип")
        self.price_var.set("Выберите цену")

        self.update_status(f"Добавлен курорт: {name}")

    def add_from_catalog(self):
        """Добавление курорта из каталога"""
        selection = self.catalog_var.get()

        if selection == "Выберите из списка":
            messagebox.showwarning("Внимание", "Выберите курорт из каталога!")
            return

        # Поиск выбранного курорта в каталоге
        for resort in self.resorts_catalog['resorts']:
            if resort['name'] == selection:
                full_name = f"{resort['name']} ({resort['country']}, {resort['category']}, {resort['price']})"

                if full_name in self.resorts:
                    messagebox.showwarning("Внимание", "Этот курорт уже добавлен!")
                    return

                self.resorts.append(full_name)

                # Добавление в Treeview
                self.resorts_tree.insert('', 'end',
                                         values=(resort['name'],
                                                 resort['country'],
                                                 resort['category'],
                                                 resort['price']))

                self.update_status(f"Добавлен курорт из каталога: {resort['name']}")
                break

        # Сброс выбора
        self.catalog_var.set("Выберите из списка")

    def delete_resort(self):
        """Удаление выбранного курорта"""
        selection = self.resorts_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите курорт для удаления!")
            return

        for item in selection:
            values = self.resorts_tree.item(item, 'values')
            full_name = f"{values[0]} ({values[1]}, {values[2]}, {values[3]})"

            # Удаление из списка
            if full_name in self.resorts:
                self.resorts.remove(full_name)

            # Удаление из Treeview
            self.resorts_tree.delete(item)

        self.update_status(f"Удален курорт: {values[0]}")

    def on_voter_selected(self, event):
        """Обработка выбора участника для голосования"""
        voter = self.voter_var.get()

        # Очистка списка для ранжирования
        self.ranking_listbox.delete(0, tk.END)

        # Добавление всех курортов в список для ранжирования
        for resort in self.resorts:
            self.ranking_listbox.insert(tk.END, resort)

        self.update_status(f"Выбран участник для голосования: {voter}")

    def move_up(self):
        """Перемещение выбранного элемента вверх"""
        selection = self.ranking_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index == 0:
            return

        # Получение текста
        text = self.ranking_listbox.get(index)

        # Удаление и вставка на новую позицию
        self.ranking_listbox.delete(index)
        self.ranking_listbox.insert(index - 1, text)
        self.ranking_listbox.selection_set(index - 1)

    def move_down(self):
        """Перемещение выбранного элемента вниз"""
        selection = self.ranking_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index == self.ranking_listbox.size() - 1:
            return

        # Получение текста
        text = self.ranking_listbox.get(index)

        # Удаление и вставка на новую позицию
        self.ranking_listbox.delete(index)
        self.ranking_listbox.insert(index + 1, text)
        self.ranking_listbox.selection_set(index + 1)

    def save_vote(self):
        """Сохранение голоса выбранного участника"""
        voter = self.voter_var.get()

        if not voter:
            messagebox.showwarning("Внимание", "Выберите участника для голосования!")
            return

        if self.ranking_listbox.size() == 0:
            messagebox.showwarning("Внимание", "Нет вариантов для голосования!")
            return

        # Получение ранжирования
        ranking = []
        for i in range(self.ranking_listbox.size()):
            ranking.append(self.ranking_listbox.get(i))

        # Проверка, что все варианты учтены
        if set(ranking) != set(self.resorts):
            messagebox.showwarning("Внимание", "Не все варианты были проранжированы!")
            return

        # Сохранение в профиль
        self.profile.append(ranking)

        # Обновление прогресса
        self.update_progress()

        # Сброс выбора участника
        self.voter_var.set('')
        self.ranking_listbox.delete(0, tk.END)

        self.update_status(f"Сохранен голос участника: {voter}")

    def update_progress(self):
        """Обновление информации о прогрессе голосования"""
        saved = len(self.profile)
        total = len(self.travelers)
        self.progress_label.config(text=f"Голосов сохранено: {saved} из {total}")

    def reset_voting(self):
        """Сброс всех голосов"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить все голоса?"):
            self.profile = []
            self.progress_label.config(text="Голосов сохранено: 0 из 0")
            self.voter_var.set('')
            self.ranking_listbox.delete(0, tk.END)
            self.update_status("Голосование сброшено")

    def calculate_results(self):
        """Расчет и отображение результатов всеми методами"""
        if len(self.profile) == 0:
            messagebox.showwarning("Внимание", "Нет данных для анализа!")
            return

        if len(self.profile) != len(self.travelers):
            messagebox.showwarning("Внимание", "Не все участники проголосовали!")
            return

        # Получаем простые названия курортов для моделей
        simple_resorts = []
        for resort in self.resorts:
            # Извлекаем только название до первой скобки
            simple_name = resort.split('(')[0].strip()
            simple_resorts.append(simple_name)

        # 1. Относительное большинство
        majority_winner, majority_counts = models.relative_majority(self.profile, self.resorts)
        self.display_majority_results(majority_winner, majority_counts)

        # 2. Метод Кондорсе
        condorcet_results = self.display_condorcet_results(self.profile, self.resorts)

        # 3. Метод Борда
        borda_scores = models.borda_count(self.profile, self.resorts)
        borda_winner = max(borda_scores, key=borda_scores.get)
        self.display_borda_results(borda_scores, borda_winner)

        # 4. Сводный отчет
        self.display_summary_report(majority_winner, condorcet_results, borda_winner)

        # 5. Визуализация
        self.display_visualization(self.profile, self.resorts)

        self.update_status("Результаты рассчитаны")

    def display_majority_results(self, winner, counts):
        """Отображение результатов относительного большинства"""
        text = "РЕЗУЛЬТАТЫ: ОТНОСИТЕЛЬНОЕ БОЛЬШИНСТВО\n"
        text += "=" * 60 + "\n\n"
        text += "Принцип метода: Побеждает вариант, который чаще всего стоит на 1-м месте\n\n"

        text += "Результаты по первым местам:\n"
        for resort, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            # Извлекаем простое название
            simple_name = resort.split('(')[0].strip()
            text += f"   * {simple_name}: {count} голосов\n"

        text += f"\nПОБЕДИТЕЛЬ: {winner.split('(')[0].strip()}\n\n"

        text += "Объяснение:\n"
        text += f"Вариант '{winner.split('(')[0].strip()}' получил наибольшее количество "
        text += f"первых мест ({counts[winner]}), что делает его победителем по методу относительного большинства.\n"

        self.majority_text.delete(1.0, tk.END)
        self.majority_text.insert(1.0, text)
        self.majority_text.configure(state='disabled')

    def display_condorcet_results(self, profile, resorts):
        """Отображение результатов метода Кондорсе"""
        text = "РЕЗУЛЬТАТЫ: МЕТОД КОНДОРСЕ\n"
        text += "=" * 60 + "\n\n"

        text += "Принцип метода: Побеждает вариант, который побеждает всех остальных в попарных сравнениях\n\n"

        # Явный победитель Кондорсе
        condorcet_winner = models.condorcet_winner(profile, resorts)

        text += "1. ЯВНЫЙ ПОБЕДИТЕЛЬ КОНДОРСЕ:\n"
        if condorcet_winner:
            text += f"   Найден победитель: {condorcet_winner.split('(')[0].strip()}\n"
            text += f"   Этот вариант побеждает все остальные в прямых сравнениях\n"
        else:
            text += "   Явный победитель не найден (парадокс Кондорсе)\n"
            text += "   Это означает, что существует цикл предпочтений\n"

        text += "\n2. ПРАВИЛО КОПЛЕНДА:\n"
        copeland_scores = models.copeland_score(profile, resorts)

        # Сортировка по убыванию очков
        sorted_copeland = sorted(copeland_scores.items(), key=lambda x: x[1], reverse=True)

        for resort, score in sorted_copeland:
            simple_name = resort.split('(')[0].strip()
            text += f"   * {simple_name}: {score} очков\n"

        copeland_winner = max(copeland_scores, key=copeland_scores.get)
        text += f"\n   Победитель по Копленду: {copeland_winner.split('(')[0].strip()}\n"

        text += "\n3. ПРАВИЛО СИМПСОНА:\n"
        simpson_scores = models.simpson_score(profile, resorts)

        # Сортировка по убыванию минимальной поддержки
        sorted_simpson = sorted(simpson_scores.items(), key=lambda x: x[1], reverse=True)

        for resort, score in sorted_simpson:
            simple_name = resort.split('(')[0].strip()
            text += f"   * {simple_name}: минимальная поддержка = {score}\n"

        simpson_winner = max(simpson_scores, key=simpson_scores.get)
        text += f"\n   Победитель по Симпсону: {simpson_winner.split('(')[0].strip()}\n"

        text += "\nИТОГИ МЕТОДА КОНДОРСЕ:\n"
        if condorcet_winner:
            text += f"* Единогласный выбор: {condorcet_winner.split('(')[0].strip()}\n"
        else:
            text += "* Единогласного выбора нет\n"
            text += f"* Рекомендация Копленда: {copeland_winner.split('(')[0].strip()}\n"
            text += f"* Рекомендация Симпсона: {simpson_winner.split('(')[0].strip()}\n"

        self.condorcet_text.delete(1.0, tk.END)
        self.condorcet_text.insert(1.0, text)
        self.condorcet_text.configure(state='disabled')

        return {
            'condorcet_winner': condorcet_winner,
            'copeland_winner': copeland_winner,
            'simpson_winner': simpson_winner
        }

    def display_borda_results(self, scores, winner):
        """Отображение результатов метода Борда"""
        text = "РЕЗУЛЬТАТЫ: МЕТОД БОРДА\n"
        text += "=" * 60 + "\n\n"

        text += "Принцип метода: Каждый вариант получает очки в зависимости от позиции в рейтинге\n"
        text += "   * 1-е место: N-1 очков\n"
        text += "   * 2-е место: N-2 очков\n"
        text += "   * ...\n"
        text += "   * Последнее место: 0 очков\n\n"

        text += "БАЛЛЫ ПО БОРДА:\n"

        # Сортировка по убыванию очков
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        max_score = max(scores.values())
        for resort, score in sorted_scores:
            simple_name = resort.split('(')[0].strip()
            percentage = (score / max_score * 100) if max_score > 0 else 0

            # Создание строки прогресса
            bar_length = 30
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)

            text += f"   * {simple_name:<30} {score:>4} очков [{bar}] {percentage:.1f}%\n"

        text += f"\nПОБЕДИТЕЛЬ: {winner.split('(')[0].strip()}\n\n"

        text += "Объяснение:\n"
        text += f"Вариант '{winner.split('(')[0].strip()}' набрал максимальное количество очков "
        text += f"({scores[winner]}), что означает его наилучшую среднюю позицию во всех рейтингах.\n"

        self.borda_text.delete(1.0, tk.END)
        self.borda_text.insert(1.0, text)
        self.borda_text.configure(state='disabled')

    def display_summary_report(self, majority_winner, condorcet_results, borda_winner):
        """Отображение сводного отчета"""
        text = "СВОДНЫЙ ОТЧЕТ ПО ВСЕМ МЕТОДАМ\n"
        text += "=" * 60 + "\n\n"

        text += "РЕЗУЛЬТАТЫ ГОЛОСОВАНИЯ:\n\n"

        text += "1. ОТНОСИТЕЛЬНОЕ БОЛЬШИНСТВО:\n"
        text += f"   Победитель: {majority_winner.split('(')[0].strip()}\n"
        text += "   Примечание: Метод простой, но может не учитывать полные предпочтения\n\n"

        text += "2. МЕТОД КОНДОРСЕ:\n"
        if condorcet_results['condorcet_winner']:
            text += f"   Явный победитель: {condorcet_results['condorcet_winner'].split('(')[0].strip()}\n"
            text += "   Этот вариант побеждает все остальные в прямых сравнениях\n"
        else:
            text += "   Явного победителя нет\n"
            text += f"   Победитель по Копленду: {condorcet_results['copeland_winner'].split('(')[0].strip()}\n"
            text += f"   Победитель по Симпсону: {condorcet_results['simpson_winner'].split('(')[0].strip()}\n"
        text += "   Примечание: Учитывает попарные сравнения, но может давать циклы\n\n"

        text += "3. МЕТОД БОРДА:\n"
        text += f"   Победитель: {borda_winner.split('(')[0].strip()}\n"
        text += "   Примечание: Учитывает все позиции в рейтингах, дает компромиссный вариант\n\n"

        text += "РЕКОМЕНДАЦИЯ СИСТЕМЫ:\n"
        text += "=" * 40 + "\n"

        # Анализ согласованности результатов
        winners = [
            majority_winner.split('(')[0].strip(),
            condorcet_results['condorcet_winner'].split('(')[0].strip() if condorcet_results['condorcet_winner'] else
            condorcet_results['copeland_winner'].split('(')[0].strip(),
            borda_winner.split('(')[0].strip()
        ]

        # Проверяем, есть ли общий победитель
        if len(set(winners)) == 1:
            text += f"ВСЕ МЕТОДЫ СОГЛАСНЫ: {winners[0]}\n"
            text += "Это самый предпочтительный вариант для всей группы!\n"
        else:
            text += "Методы дали разные результаты. Рекомендуем:\n"
            for i, method in enumerate(["Относительное большинство", "Кондорсе", "Борда"]):
                text += f"   * По методу {method}: {winners[i]}\n"
            text += "\nПредлагаем обсудить эти варианты в группе или провести повторное голосование\n"

        text += "\nСледующие шаги:\n"
        text += "1. Обсудить результаты в группе\n"
        text += "2. Учесть бюджетные ограничения\n"
        text += "3. Проверить доступность выбранного варианта\n"
        text += "4. Начать планирование поездки!\n"

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, text)
        self.summary_text.configure(state='disabled')

    def display_visualization(self, profile, resorts):
        """Визуализация результатов в текстовом виде"""
        text = "ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ\n"
        text += "=" * 60 + "\n\n"

        # Матрица попарных сравнений
        text += "МАТРИЦА ПОПАРНЫХ СРАВНЕНИЙ:\n"
        text += "(число показывает, сколько участников предпочитают строку столбцу)\n\n"

        # Заголовок таблицы
        simple_names = [r.split('(')[0].strip() for r in resorts]
        max_len = max(len(name) for name in simple_names)

        # Заголовок
        text += " " * (max_len + 2)
        for name in simple_names:
            text += f"{name[:8]:>8} "
        text += "\n" + "-" * (max_len + 2 + 9 * len(simple_names)) + "\n"

        # Данные матрицы
        for i, resort_a in enumerate(resorts):
            simple_a = simple_names[i]
            text += f"{simple_a:<{max_len}} |"

            for j, resort_b in enumerate(resorts):
                if i == j:
                    text += "   --   "
                else:
                    wins = models.pairwise_comparison(profile, resort_a, resort_b)
                    if wins > 0:
                        text += f"   +{wins:<2}  "
                    elif wins < 0:
                        text += f"   {wins:<3}  "
                    else:
                        text += "   0    "

            text += "\n"

        text += "\n" + "=" * 60 + "\n\n"

        # График голосов за первые места
        text += "РАСПРЕДЕЛЕНИЕ ПЕРВЫХ МЕСТ:\n\n"

        _, majority_counts = models.relative_majority(profile, resorts)
        total_votes = len(profile)

        for resort, count in sorted(majority_counts.items(), key=lambda x: x[1], reverse=True):
            simple_name = resort.split('(')[0].strip()
            percentage = (count / total_votes) * 100
            bar_length = int(percentage / 4)  # Масштабируем для отображения
            bar = '█' * bar_length + '░' * (25 - bar_length)

            text += f"{simple_name:<30} {bar} {count:>2}/{total_votes} ({percentage:.1f}%)\n"

        self.visualization_text.delete(1.0, tk.END)
        self.visualization_text.insert(1.0, text)
        self.visualization_text.configure(state='disabled')


def main():
    """Точка входа в программу"""
    try:
        root = tk.Tk()
        app = VacationPlannerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    main()