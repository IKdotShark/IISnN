import numpy as np
import pickle
import json
from datetime import datetime


class NeuralNetwork:
    """
    Многослойный персептрон с одним скрытым слоем
    для распознавания геометрических фигур
    """

    def __init__(self, input_size=225, hidden_size=25, output_size=8):
        """
        Инициализация нейронной сети

        Параметры:
        ----------
        input_size : int
            Количество входных нейронов (GRID_SIZE * GRID_SIZE)
        hidden_size : int
            Количество нейронов в скрытом слое
        output_size : int
            Количество выходных нейронов (количество фигур)
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Инициализация весов методом Xavier/Glorot
        limit_input = np.sqrt(2.0 / (input_size + hidden_size))
        limit_hidden = np.sqrt(2.0 / (hidden_size + output_size))

        # Веса между входным и скрытым слоем
        self.W1 = np.random.randn(input_size, hidden_size) * limit_input
        self.b1 = np.zeros((1, hidden_size))

        # Веса между скрытым и выходным слоем
        self.W2 = np.random.randn(hidden_size, output_size) * limit_hidden
        self.b2 = np.zeros((1, output_size))

        # История ошибок для анализа
        self.training_history = {
            'errors': [],
            'accuracies': [],
            'timestamps': []
        }

    def sigmoid(self, x):
        """
        Сигмоидная функция активации

        Параметры:
        ----------
        x : numpy.ndarray
            Входной массив

        Возвращает:
        -----------
        numpy.ndarray
            Значения сигмоиды
        """
        # Ограничение для избежания переполнения
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        """
        Производная сигмоидной функции

        Параметры:
        ----------
        x : numpy.ndarray
            Входной массив

        Возвращает:
        -----------
        numpy.ndarray
            Значения производной
        """
        return x * (1 - x)

    def relu(self, x):
        """
        Функция активации ReLU (Rectified Linear Unit)

        Параметры:
        ----------
        x : numpy.ndarray
            Входной массив

        Возвращает:
        -----------
        numpy.ndarray
            Значения ReLU
        """
        return np.maximum(0, x)

    def relu_derivative(self, x):
        """
        Производная функции ReLU

        Параметры:
        ----------
        x : numpy.ndarray
            Входной массив

        Возвращает:
        -----------
        numpy.ndarray
            Значения производной ReLU
        """
        return (x > 0).astype(float)

    def softmax(self, x):
        """
        Функция активации Softmax для выходного слоя

        Параметры:
        ----------
        x : numpy.ndarray
            Входной массив

        Возвращает:
        -----------
        numpy.ndarray
            Вероятности классов
        """
        # Стабилизация численных значений
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def forward(self, X):
        """
        Прямое распространение сигнала

        Параметры:
        ----------
        X : numpy.ndarray
            Входные данные формы (n_samples, input_size)

        Возвращает:
        -----------
        numpy.ndarray
            Выход сети
        """
        # Сохраняем промежуточные значения для обратного распространения
        self.X = X

        # Входной слой → скрытый слой
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.relu(self.z1)  # Используем ReLU для скрытого слоя

        # Скрытый слой → выходной слой
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.softmax(self.z2)  # Используем Softmax для выходного слоя

        return self.a2

    def backward(self, X, y, output, learning_rate):
        """
        Обратное распространение ошибки

        Параметры:
        ----------
        X : numpy.ndarray
            Входные данные
        y : numpy.ndarray
            Ожидаемые выходные данные (one-hot encoded)
        output : numpy.ndarray
            Фактические выходы сети
        learning_rate : float
            Скорость обучения
        """
        m = X.shape[0]  # Количество образцов

        # Ошибка на выходном слое
        error_output = output - y

        # Градиенты для выходного слоя
        # Для softmax + кросс-энтропии градиент упрощается до error_output
        dW2 = np.dot(self.a1.T, error_output) / m
        db2 = np.sum(error_output, axis=0, keepdims=True) / m

        # Ошибка на скрытом слое
        error_hidden = np.dot(error_output, self.W2.T)

        # Градиенты для скрытого слоя (с производной ReLU)
        d_hidden = error_hidden * self.relu_derivative(self.a1)
        dW1 = np.dot(X.T, d_hidden) / m
        db1 = np.sum(d_hidden, axis=0, keepdims=True) / m

        # Обновление весов
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

        # Возвращаем среднюю ошибку для мониторинга
        return np.mean(np.abs(error_output))

    def compute_loss(self, y_true, y_pred):
        """
        Вычисление функции потерь (кросс-энтропия)

        Параметры:
        ----------
        y_true : numpy.ndarray
            Истинные метки (one-hot encoded)
        y_pred : numpy.ndarray
            Предсказанные вероятности

        Возвращает:
        -----------
        float
            Значение функции потерь
        """
        # Добавляем небольшое значение для избежания log(0)
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)

        # Кросс-энтропия
        loss = -np.sum(y_true * np.log(y_pred)) / y_true.shape[0]
        return loss

    def compute_accuracy(self, y_true, y_pred):
        """
        Вычисление точности классификации

        Параметры:
        ----------
        y_true : numpy.ndarray
            Истинные метки (one-hot encoded)
        y_pred : numpy.ndarray
            Предсказанные вероятности

        Возвращает:
        -----------
        float
            Точность классификации
        """
        predictions = np.argmax(y_pred, axis=1)
        true_labels = np.argmax(y_true, axis=1)
        accuracy = np.mean(predictions == true_labels)
        return accuracy

    def train(self, X, y, epochs=1000, learning_rate=0.1,
              validation_split=0.2, verbose=True):
        """
        Обучение нейронной сети

        Параметры:
        ----------
        X : numpy.ndarray
            Входные данные обучения
        y : numpy.ndarray
            Выходные данные обучения (one-hot encoded)
        epochs : int
            Количество эпох обучения
        learning_rate : float
            Скорость обучения
        validation_split : float
            Доля данных для валидации
        verbose : bool
            Выводить ли информацию о процессе обучения
        """
        # Разделение на обучающую и валидационную выборки
        n_samples = X.shape[0]
        indices = np.random.permutation(n_samples)
        split_idx = int(n_samples * (1 - validation_split))

        train_idx = indices[:split_idx]
        val_idx = indices[split_idx:]

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # История обучения
        train_loss_history = []
        val_loss_history = []
        train_acc_history = []
        val_acc_history = []

        # Градиентный спуск
        for epoch in range(epochs):
            # Прямое распространение
            output_train = self.forward(X_train)

            # Обратное распространение
            train_loss = self.backward(X_train, y_train, output_train, learning_rate)

            # Вычисление метрик
            train_accuracy = self.compute_accuracy(y_train, output_train)

            # Валидация
            output_val = self.forward(X_val)
            val_loss = self.compute_loss(y_val, output_val)
            val_accuracy = self.compute_accuracy(y_val, output_val)

            # Сохранение истории
            train_loss_history.append(train_loss)
            val_loss_history.append(val_loss)
            train_acc_history.append(train_accuracy)
            val_acc_history.append(val_accuracy)

            # Вывод прогресса
            if verbose and (epoch % 100 == 0 or epoch == epochs - 1):
                print(f"Эпоха {epoch + 1}/{epochs}: "
                      f"Ошибка обучения: {train_loss:.4f}, "
                      f"Точность обучения: {train_accuracy:.4f}, "
                      f"Ошибка валидации: {val_loss:.4f}, "
                      f"Точность валидации: {val_accuracy:.4f}")

        # Сохранение истории обучения
        self.training_history['errors'] = {
            'train': train_loss_history,
            'val': val_loss_history
        }
        self.training_history['accuracies'] = {
            'train': train_acc_history,
            'val': val_acc_history
        }
        self.training_history['timestamps'].append(datetime.now().isoformat())

        return self.training_history

    def predict(self, X):
        """
        Предсказание классов для входных данных

        Параметры:
        ----------
        X : numpy.ndarray
            Входные данные

        Возвращает:
        -----------
        numpy.ndarray
            Предсказанные классы
        """
        output = self.forward(X)
        return np.argmax(output, axis=1)

    def predict_proba(self, X):
        """
        Предсказание вероятностей классов

        Параметры:
        ----------
        X : numpy.ndarray
            Входные данные

        Возвращает:
        -----------
        numpy.ndarray
            Вероятности классов
        """
        return self.forward(X)

    def save_weights(self, filepath='network_weights.pkl'):
        """
        Сохранение весов сети в файл

        Параметры:
        ----------
        filepath : str
            Путь к файлу для сохранения
        """
        weights = {
            'W1': self.W1,
            'b1': self.b1,
            'W2': self.W2,
            'b2': self.b2,
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'output_size': self.output_size,
            'training_history': self.training_history
        }

        with open(filepath, 'wb') as f:
            pickle.dump(weights, f)

    def load_weights(self, filepath='network_weights.pkl'):
        """
        Загрузка весов сети из файла

        Параметры:
        ----------
        filepath : str
            Путь к файлу с весами
        """
        try:
            with open(filepath, 'rb') as f:
                weights = pickle.load(f)

            self.W1 = weights['W1']
            self.b1 = weights['b1']
            self.W2 = weights['W2']
            self.b2 = weights['b2']

            # Проверка совместимости размеров
            if (self.input_size != weights['input_size'] or
                    self.hidden_size != weights['hidden_size'] or
                    self.output_size != weights['output_size']):
                print("Внимание: Размеры сети не совпадают с загруженными весами!")
                print(f"Текущая: {self.input_size}-{self.hidden_size}-{self.output_size}")
                print(f"Загруженная: {weights['input_size']}-{weights['hidden_size']}-{weights['output_size']}")

            if 'training_history' in weights:
                self.training_history = weights['training_history']

        except FileNotFoundError:
            print(f"Файл весов {filepath} не найден. Используются случайные веса.")
        except Exception as e:
            print(f"Ошибка при загрузке весов: {e}. Используются случайные веса.")

    def get_architecture_info(self):
        """
        Получение информации об архитектуре сети

        Возвращает:
        -----------
        dict
            Словарь с информацией об архитектуре
        """
        return {
            'Архитектура': f"{self.input_size}-{self.hidden_size}-{self.output_size}",
            'Всего параметров': (
                    self.input_size * self.hidden_size +  # W1
                    self.hidden_size +  # b1
                    self.hidden_size * self.output_size +  # W2
                    self.output_size  # b2
            ),
            'Функция активации (скрытый слой)': 'ReLU',
            'Функция активации (выходной слой)': 'Softmax',
            'Функция потерь': 'Кросс-энтропия',
            'Алгоритм обучения': 'Обратное распространение ошибки',
            'Оптимизатор': 'Градиентный спуск',
            'Размеры весов': {
                'W1': f"{self.W1.shape[0]}x{self.W1.shape[1]}",
                'b1': f"1x{self.b1.shape[1]}",
                'W2': f"{self.W2.shape[0]}x{self.W2.shape[1]}",
                'b2': f"1x{self.b2.shape[1]}"
            }
        }

    def print_summary(self):
        """
        Вывод информации о сети
        """
        info = self.get_architecture_info()
        print("=" * 50)
        print("ИНФОРМАЦИЯ О НЕЙРОННОЙ СЕТИ")
        print("=" * 50)
        for key, value in info.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
        print("=" * 50)


# Пример использования
if __name__ == "__main__":
    # Создание и тестирование сети
    nn = NeuralNetwork(input_size=225, hidden_size=25, output_size=8)
    nn.print_summary()

    # Генерация тестовых данных
    X_test = np.random.randn(10, 225)
    y_test = np.random.randint(0, 8, size=10)

    # Преобразование в one-hot encoding
    Y_test = np.zeros((y_test.size, 8))
    Y_test[np.arange(y_test.size), y_test] = 1

    # Тестирование предсказаний
    predictions = nn.predict(X_test)
    print(f"\nТестовые предсказания: {predictions}")
    print(f"Истинные метки: {y_test}")