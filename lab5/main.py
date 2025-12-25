import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
import numpy as np
import pickle
import os
import json
from datetime import datetime
from neural_network import NeuralNetwork

# Определение геометрических фигур
GEOMETRIC_SHAPES = [
    'Круг', 'Квадрат', 'Треугольник',
    'Прямоугольник', 'Ромб', 'Звезда',
    'Сердце', 'Крест'
]
GRID_SIZE = 15  # Увеличим размер сетки для лучшего распознавания
PIXEL_SIZE = 20
TRAINING_DATA_FILE = 'training_data.pkl'
NETWORK_WEIGHTS_FILE = 'network_weights.pkl'
CONFIG_FILE = 'config.json'


class ShapeRecognizerApp:
    """Основной класс приложения для распознавания фигур"""

    def __init__(self, root):
        """Инициализация приложения"""
        self.root = root
        self.root.title("Распознавание геометрических фигур")
        self.root.geometry("900x500")

        # Инициализация сетки для рисования
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.drawing = False
        self.last_point = None
        self.brush_size = 2  # Размер кисти для рисования

        # Загрузка конфигурации
        self.config = self.load_config()

        # Инициализация нейронной сети
        input_size = GRID_SIZE * GRID_SIZE
        hidden_size = self.config.get('hidden_neurons', 25)
        output_size = len(GEOMETRIC_SHAPES)

        self.nn = NeuralNetwork(input_size, hidden_size, output_size)

        # Загрузка весов, если они есть
        if os.path.exists(NETWORK_WEIGHTS_FILE):
            self.nn.load_weights(NETWORK_WEIGHTS_FILE)

        # Загрузка обучающей выборки
        self.training_data = self.load_training_data()

        # Статистика
        self.stats = {
            'training_sessions': 0,
            'last_trained': None,
            'accuracy': 0.0
        }

        # Создание интерфейса
        self.create_widgets()
        self.draw_grid()

        # Отображение архитектуры
        self.show_network_architecture()

    def create_widgets(self):
        """Создание элементов интерфейса"""

        # Основной фрейм
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - холст для рисования
        left_frame = tk.Frame(main_frame, bg='#f0f0f0')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Нарисуйте фигуру:",
                 font=("Arial", 12, "bold"), bg='#f0f0f0').pack(pady=5)

        # Холст для рисования
        canvas_frame = tk.Frame(left_frame, relief=tk.SUNKEN, borderwidth=2)
        canvas_frame.pack(pady=10)

        canvas_width = GRID_SIZE * PIXEL_SIZE
        canvas_height = GRID_SIZE * PIXEL_SIZE
        self.canvas = tk.Canvas(canvas_frame, width=canvas_width,
                                height=canvas_height, bg='white',
                                cursor="crosshair")
        self.canvas.pack()

        # Привязка событий мыши
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<Button-3>", self.erase_pixel)  # Правый клик - стирание

        # Панель инструментов рисования
        tools_frame = tk.Frame(left_frame, bg='#f0f0f0')
        tools_frame.pack(pady=5)

        tk.Button(tools_frame, text="Очистить", command=self.clear_canvas,
                  width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Толще", command=self.increase_brush,
                  width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text="Тоньше", command=self.decrease_brush,
                  width=8).pack(side=tk.LEFT, padx=2)

        # Правая панель - управление
        right_frame = tk.Frame(main_frame, bg='#f0f0f0', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))

        # Информационная панель
        info_frame = tk.LabelFrame(right_frame, text="Информация",
                                   font=("Arial", 10, "bold"),
                                   bg='#f0f0f0', padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_label = tk.Label(info_frame,
                                    text=f"Примеров в выборке: {len(self.training_data)}\n"
                                         f"Точность: {self.stats['accuracy']:.1%}",
                                    font=("Arial", 10), bg='#f0f0f0',
                                    justify=tk.LEFT)
        self.stats_label.pack()

        # Панель результатов
        result_frame = tk.LabelFrame(right_frame, text="Результат распознавания",
                                     font=("Arial", 10, "bold"),
                                     bg='#f0f0f0', padx=10, pady=10)
        result_frame.pack(fill=tk.X, pady=(0, 10))

        self.result_text = tk.StringVar(value="Нарисуйте фигуру")
        self.result_label = tk.Label(result_frame, textvariable=self.result_text,
                                     font=("Arial", 14, "bold"), bg='white',
                                     relief=tk.SUNKEN, width=20, height=2)
        self.result_label.pack()

        self.confidence_text = tk.StringVar()
        self.confidence_label = tk.Label(result_frame,
                                         textvariable=self.confidence_text,
                                         font=("Arial", 9), bg='#f0f0f0')
        self.confidence_label.pack(pady=5)

        # Панель управления
        control_frame = tk.LabelFrame(right_frame, text="Управление",
                                      font=("Arial", 10, "bold"),
                                      bg='#f0f0f0', padx=10, pady=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Кнопки управления
        buttons = [
            ("Распознать", self.recognize_shape, "#4CAF50"),
            ("Добавить в обучение", self.add_to_training, "#2196F3"),
            ("Обучить сеть", self.train_network, "#FF9800"),
            ("Тестировать сеть", self.test_network, "#9C27B0"),
            ("Управление выборкой", self.manage_dataset, "#607D8B"),
            ("Показать архитектуру", self.show_network_architecture, "#795548"),
            ("Сохранить всё", self.save_all, "#009688"),
        ]

        for text, command, color in buttons:
            btn = tk.Button(control_frame, text=text, command=command,
                            bg=color, fg='white', font=("Arial", 10),
                            width=20, height=1)
            btn.pack(pady=4)

    def start_draw(self, event):
        """Начало рисования"""
        self.drawing = True
        self.last_point = (event.x, event.y)
        self.update_pixel(event.x, event.y)

    def draw(self, event):
        """Рисование с перемещением мыши"""
        if self.drawing and self.last_point:
            x1, y1 = self.last_point
            x2, y2 = event.x, event.y

            # Рисуем линию между точками для плавности
            self.draw_line(x1, y1, x2, y2)
            self.last_point = (x2, y2)

    def draw_line(self, x1, y1, x2, y2):
        """Рисование линии между двумя точками"""
        # Простой алгоритм Брезенхэма для рисования линии
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.update_pixel(x1, y1)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def update_pixel(self, x, y):
        """Обновление пикселей в сетке с учетом размера кисти"""
        center_col = x // PIXEL_SIZE
        center_row = y // PIXEL_SIZE

        # Закрашиваем область вокруг центральной точки
        for dr in range(-self.brush_size + 1, self.brush_size):
            for dc in range(-self.brush_size + 1, self.brush_size):
                row = center_row + dr
                col = center_col + dc
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    self.grid[row][col] = 1
                    self.draw_pixel(row, col, "black")

    def erase_pixel(self, event):
        """Стирание пикселя"""
        col = event.x // PIXEL_SIZE
        row = event.y // PIXEL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.grid[row][col] = 0
            self.draw_pixel(row, col, "white")

    def stop_draw(self, _):
        """Окончание рисования"""
        self.drawing = False
        self.last_point = None

    def draw_pixel(self, row, col, color):
        """Отрисовка одного пикселя на холсте"""
        x1 = col * PIXEL_SIZE
        y1 = row * PIXEL_SIZE
        x2 = x1 + PIXEL_SIZE
        y2 = y1 + PIXEL_SIZE

        # Создаем или обновляем прямоугольник
        if not hasattr(self, 'pixel_rects'):
            self.pixel_rects = {}

        key = (row, col)
        if key in self.pixel_rects:
            self.canvas.itemconfig(self.pixel_rects[key], fill=color)
        else:
            rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                fill=color, outline="lightgray")
            self.pixel_rects[key] = rect

    def draw_grid(self):
        """Отрисовка всей сетки"""
        self.canvas.delete("all")
        self.pixel_rects = {}

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                color = "black" if self.grid[i][j] else "white"
                self.draw_pixel(i, j, color)

    def clear_canvas(self):
        """Очистка холста"""
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.draw_grid()
        self.result_text.set("Нарисуйте фигуру")
        self.confidence_text.set("")

    def increase_brush(self):
        """Увеличение размера кисти"""
        if self.brush_size < 4:
            self.brush_size += 1

    def decrease_brush(self):
        """Уменьшение размера кисти"""
        if self.brush_size > 1:
            self.brush_size -= 1

    def get_flattened_input(self):
        """Преобразование сетки в одномерный массив"""
        return np.array(self.grid, dtype=float).flatten().reshape(1, -1)

    def recognize_shape(self):
        """Распознавание нарисованной фигуры"""
        X = self.get_flattened_input()
        if X.sum() == 0:
            messagebox.showwarning("Предупреждение", "Сначала нарисуйте фигуру!")
            return

        # Получаем предсказание нейросети
        predictions = self.nn.predict_proba(X)[0]
        predicted_class = np.argmax(predictions)
        confidence = predictions[predicted_class]

        # Обновляем интерфейс
        self.result_text.set(GEOMETRIC_SHAPES[predicted_class])

        # Цветовая индикация уверенности
        if confidence > 0.7:
            color = "#4CAF50"  # Зеленый
        elif confidence > 0.4:
            color = "#FF9800"  # Оранжевый
        else:
            color = "#F44336"  # Красный

        self.result_label.config(bg=color)
        self.confidence_text.set(f"Уверенность: {confidence:.1%}")

    def add_to_training(self):
        """Добавление текущего рисунка в обучающую выборку"""
        X = self.get_flattened_input()
        if X.sum() == 0:
            messagebox.showwarning("Ошибка", "Сначала нарисуйте фигуру!")
            return

        # Диалог выбора метки
        dialog = Toplevel(self.root)
        dialog.title("Выбор фигуры")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Выберите фигуру:",
                 font=("Arial", 12, "bold")).pack(pady=10)

        selected_shape = tk.StringVar(value=GEOMETRIC_SHAPES[0])

        for shape in GEOMETRIC_SHAPES:
            rb = tk.Radiobutton(dialog, text=shape,
                                variable=selected_shape,
                                value=shape,
                                font=("Arial", 10))
            rb.pack(anchor=tk.W, padx=20)

        def save_selection():
            shape = selected_shape.get()
            y = GEOMETRIC_SHAPES.index(shape)
            self.training_data.append((X.flatten(), y))
            self.save_training_data()
            self.update_stats()
            dialog.destroy()
            messagebox.showinfo("Успех", f"Фигура '{shape}' добавлена в обучение!")

        tk.Button(dialog, text="Добавить", command=save_selection,
                  bg="#4CAF50", fg="white", width=15).pack(pady=20)

    def manage_dataset(self):
        """Управление обучающей выборкой"""
        if not self.training_data:
            messagebox.showinfo("Выборка", "Обучающая выборка пуста.")
            return

        # Создание окна управления
        manage_window = Toplevel(self.root)
        manage_window.title("Управление обучающей выборкой")
        manage_window.geometry("500x400")

        # Список примеров
        listbox = tk.Listbox(manage_window, font=("Arial", 10),
                             selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(manage_window, orient=tk.VERTICAL)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        for i, (_, y) in enumerate(self.training_data):
            listbox.insert(tk.END, f"{i + 1}. {GEOMETRIC_SHAPES[y]}")

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Панель кнопок
        button_frame = tk.Frame(manage_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def delete_selected():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                del self.training_data[idx]
                listbox.delete(idx)
                self.save_training_data()
                self.update_stats()

        def clear_all():
            if messagebox.askyesno("Подтверждение",
                                   "Удалить всю обучающую выборку?"):
                self.training_data.clear()
                listbox.delete(0, tk.END)
                self.save_training_data()
                self.update_stats()

        def view_selected():
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                X, y = self.training_data[idx]
                self.view_sample(X, y)

        tk.Button(button_frame, text="Просмотреть", command=view_selected,
                  width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Удалить", command=delete_selected,
                  width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Очистить всё", command=clear_all,
                  width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Закрыть",
                  command=manage_window.destroy,
                  width=15).pack(side=tk.RIGHT, padx=5)

    def view_sample(self, X, y):
        """Просмотр выбранного образца"""
        view_window = Toplevel(self.root)
        view_window.title(f"Просмотр: {GEOMETRIC_SHAPES[y]}")
        view_window.geometry("300x350")

        # Восстановление сетки
        grid_data = X.reshape(GRID_SIZE, GRID_SIZE)

        # Создание мини-холста
        canvas = tk.Canvas(view_window, width=GRID_SIZE * 15,
                           height=GRID_SIZE * 15, bg='white')
        canvas.pack(pady=10)

        # Отрисовка образца
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                color = "black" if grid_data[i][j] else "white"
                x1 = j * 15
                y1 = i * 15
                x2 = x1 + 15
                y2 = y1 + 15
                canvas.create_rectangle(x1, y1, x2, y2,
                                        fill=color, outline="lightgray")

        tk.Label(view_window, text=GEOMETRIC_SHAPES[y],
                 font=("Arial", 14, "bold")).pack(pady=10)

    def train_network(self):
        """Обучение нейронной сети"""
        if len(self.training_data) < 5:
            messagebox.showwarning("Ошибка",
                                   f"Недостаточно данных для обучения (минимум 5 примеров, сейчас {len(self.training_data)}).")
            return

        # Подготовка данных
        X = np.array([item[0] for item in self.training_data])
        y = np.array([item[1] for item in self.training_data])

        # Преобразование меток в one-hot encoding
        Y = np.zeros((y.size, len(GEOMETRIC_SHAPES)))
        Y[np.arange(y.size), y] = 1

        # Диалог параметров обучения
        param_dialog = Toplevel(self.root)
        param_dialog.title("Параметры обучения")
        param_dialog.geometry("300x250")

        tk.Label(param_dialog, text="Эпох обучения:").pack(pady=5)
        epochs_var = tk.StringVar(value="1000")
        tk.Entry(param_dialog, textvariable=epochs_var, width=10).pack()

        tk.Label(param_dialog, text="Скорость обучения:").pack(pady=5)
        lr_var = tk.StringVar(value="0.1")
        tk.Entry(param_dialog, textvariable=lr_var, width=10).pack()

        progress_var = tk.StringVar(value="Готов к обучению")
        progress_label = tk.Label(param_dialog, textvariable=progress_var)
        progress_label.pack(pady=20)

        def start_training():
            try:
                epochs = int(epochs_var.get())
                lr = float(lr_var.get())

                if epochs <= 0 or lr <= 0:
                    raise ValueError

                param_dialog.destroy()

                # Обучение сети
                self.nn.train(X, Y, epochs=epochs, learning_rate=lr)
                self.nn.save_weights(NETWORK_WEIGHTS_FILE)

                # Обновление статистики
                self.stats['training_sessions'] += 1
                self.stats['last_trained'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_config()

                # Тестирование точности
                accuracy = self.calculate_accuracy()
                self.stats['accuracy'] = accuracy
                self.update_stats()

                messagebox.showinfo("Обучение завершено",
                                    f"Сеть обучена!\nТочность на обучающей выборке: {accuracy:.1%}")

            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числовые значения")

        tk.Button(param_dialog, text="Начать обучение",
                  command=start_training, width=15).pack(pady=10)

    def test_network(self):
        """Тестирование точности сети"""
        if not self.training_data:
            messagebox.showwarning("Ошибка", "Нет данных для тестирования")
            return

        X = np.array([item[0] for item in self.training_data])
        y = np.array([item[1] for item in self.training_data])

        accuracy = self.calculate_accuracy()

        # Показать результаты
        results_window = Toplevel(self.root)
        results_window.title("Результаты тестирования")
        results_window.geometry("400x300")

        tk.Label(results_window, text="Результаты тестирования нейронной сети",
                 font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(results_window,
                 text=f"Точность: {accuracy:.1%}\n"
                      f"Тестовых примеров: {len(self.training_data)}\n"
                      f"Классов: {len(GEOMETRIC_SHAPES)}",
                 font=("Arial", 11), justify=tk.LEFT).pack(pady=10)

        # Матрица ошибок (упрощенная)
        predictions = self.nn.predict(X)
        correct = (predictions == y).sum()

        tk.Label(results_window,
                 text=f"Правильно распознано: {correct} из {len(y)}\n"
                      f"Ошибок: {len(y) - correct}",
                 font=("Arial", 10)).pack(pady=10)

    def calculate_accuracy(self):
        """Вычисление точности сети"""
        if not self.training_data:
            return 0.0

        X = np.array([item[0] for item in self.training_data])
        y = np.array([item[1] for item in self.training_data])

        predictions = self.nn.predict(X)
        accuracy = (predictions == y).mean()
        return accuracy

    def show_network_architecture(self):
        """Отображение архитектуры нейронной сети"""
        arch_window = Toplevel(self.root)
        arch_window.title("Архитектура нейронной сети")
        arch_window.geometry("500x300")

        # Получаем информацию о сети
        info = self.nn.get_architecture_info()

        # Создаем текстовое поле с информацией
        text_widget = tk.Text(arch_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Добавляем информацию
        text_widget.insert(tk.END, "=" * 50 + "\n")
        text_widget.insert(tk.END, "АРХИТЕКТУРА НЕЙРОННОЙ СЕТИ\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")

        for key, value in info.items():
            text_widget.insert(tk.END, f"{key}:\n")
            text_widget.insert(tk.END, f"  {value}\n\n")

        text_widget.config(state=tk.DISABLED)

        # Кнопка для визуализации
        tk.Button(arch_window, text="Визуализировать архитектуру",
                  command=self.visualize_architecture).pack(pady=10)

    def visualize_architecture(self):
        """Визуализация архитектуры сети"""
        vis_window = Toplevel(self.root)
        vis_window.title("Визуализация архитектуры")
        vis_window.geometry("600x400")

        canvas = tk.Canvas(vis_window, bg='white')
        canvas.pack(fill=tk.BOTH, expand=True)

        # Параметры визуализации
        layer_spacing = 150
        neuron_radius = 15
        start_x = 100

        # Входной слой
        input_neurons = self.nn.input_size
        input_y = 200 - (input_neurons * neuron_radius)

        for i in range(input_neurons):
            y = input_y + i * neuron_radius * 3
            canvas.create_oval(start_x - neuron_radius, y - neuron_radius,
                               start_x + neuron_radius, y + neuron_radius,
                               fill='lightblue', outline='black')
            canvas.create_text(start_x, y, text=f"I{i + 1}", font=("Arial", 8))

        # Скрытый слой
        hidden_neurons = self.nn.hidden_size
        hidden_x = start_x + layer_spacing
        hidden_y = 200 - (hidden_neurons * neuron_radius)

        for i in range(hidden_neurons):
            y = hidden_y + i * neuron_radius * 3
            canvas.create_oval(hidden_x - neuron_radius, y - neuron_radius,
                               hidden_x + neuron_radius, y + neuron_radius,
                               fill='lightgreen', outline='black')
            canvas.create_text(hidden_x, y, text=f"H{i + 1}", font=("Arial", 8))

            # Соединения с входным слоем
            for j in range(min(3, input_neurons)):  # Показываем только несколько связей
                canvas.create_line(start_x + neuron_radius,
                                   input_y + j * neuron_radius * 3,
                                   hidden_x - neuron_radius, y,
                                   fill='gray', width=1, dash=(2, 2))

        # Выходной слой
        output_neurons = self.nn.output_size
        output_x = hidden_x + layer_spacing
        output_y = 200 - (output_neurons * neuron_radius)

        for i in range(output_neurons):
            y = output_y + i * neuron_radius * 3
            canvas.create_oval(output_x - neuron_radius, y - neuron_radius,
                               output_x + neuron_radius, y + neuron_radius,
                               fill='lightcoral', outline='black')
            canvas.create_text(output_x, y, text=GEOMETRIC_SHAPES[i][0],
                               font=("Arial", 8))

            # Соединения со скрытым слоем
            for j in range(min(3, hidden_neurons)):
                canvas.create_line(hidden_x + neuron_radius,
                                   hidden_y + j * neuron_radius * 3,
                                   output_x - neuron_radius, y,
                                   fill='gray', width=1, dash=(2, 2))

        # Подписи слоев
        canvas.create_text(start_x, 350, text="Входной слой\n(пиксели)",
                           font=("Arial", 10, "bold"))
        canvas.create_text(hidden_x, 350, text="Скрытый слой",
                           font=("Arial", 10, "bold"))
        canvas.create_text(output_x, 350, text="Выходной слой\n(фигуры)",
                           font=("Arial", 10, "bold"))

    def save_all(self):
        """Сохранение всех данных"""
        self.save_training_data()
        self.nn.save_weights(NETWORK_WEIGHTS_FILE)
        self.save_config()
        messagebox.showinfo("Сохранение", "Все данные успешно сохранены!")

    def update_stats(self):
        """Обновление статистики"""
        self.stats_label.config(
            text=f"Примеров в выборке: {len(self.training_data)}\n"
                 f"Точность: {self.stats['accuracy']:.1%}\n"
                 f"Сессий обучения: {self.stats['training_sessions']}"
        )

    def load_training_data(self):
        """Загрузка обучающей выборки"""
        if os.path.exists(TRAINING_DATA_FILE):
            try:
                with open(TRAINING_DATA_FILE, 'rb') as f:
                    return pickle.load(f)
            except:
                return []
        return []

    def save_training_data(self):
        """Сохранение обучающей выборки"""
        with open(TRAINING_DATA_FILE, 'wb') as f:
            pickle.dump(self.training_data, f)

    def load_config(self):
        """Загрузка конфигурации"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {'hidden_neurons': 25}
        return {'hidden_neurons': 25}

    def save_config(self):
        """Сохранение конфигурации"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump({**self.config, **self.stats}, f, indent=2)


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = ShapeRecognizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()