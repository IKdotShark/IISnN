;; ИНСТРУКЦИЯ ПО ЗАПУСКУ:
;; ----------------------
;; 1. Запустить CLIPS
;; 2. Выполнить команды в следующей последовательности:
;;    CLIPS> (clear)
;;    CLIPS> (load "recipe.clp")
;;    CLIPS> (reset)     ; Команда reset подставляет факты из deffacts
;;    CLIPS> (run)

;; ============================================================================
;; РАЗДЕЛ 1: ОПРЕДЕЛЕНИЕ ШАБЛОНОВ (DEFTEMPLATES)
;; ============================================================================

;; Шаблон для хранения всех входных данных пользователя
(deftemplate user-input
  "Структура для хранения всех ответов пользователя"
  (slot budget            (type INTEGER)  (default 0))
  (slot dietary-restrictions (type SYMBOL) (default nil) (allowed-symbols да нет nil))
  (slot want-meat         (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot want-soups        (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot want-side-dishes  (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot want-salads       (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot have-spices       (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot quick-cooking     (type SYMBOL)   (default nil) (allowed-symbols да нет nil)))

;; ============================================================================
;; РАЗДЕЛ 2: НАЧАЛЬНЫЕ ФАКТЫ (DEFFACTS)
;; ============================================================================

(deffacts startup
  "Начальные факты для запуска системы после команды (reset)"
  (stage awaiting-input)
  (system-ready))

;; ============================================================================
;; РАЗДЕЛ 3: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (DEFFUNCTIONS)
;; ============================================================================

;; Функция для запроса целого числа с валидацией
(deffunction ask-int (?question)
  "Запрашивает у пользователя целое число и проверяет корректность ввода"
  (printout t ?question " ")
  (bind ?input (read))
  (while (not (integerp ?input))
    (printout t "Ошибка! Введите целое число." crlf)
    (printout t ?question " ")
    (bind ?input (read)))
  (return ?input))

;; Функция для запроса ответа да/нет с валидацией
(deffunction ask-yes-no (?question)
  "Запрашивает у пользователя ответ да или нет и проверяет корректность"
  (printout t ?question " (да/нет): ")
  (bind ?input (read))
  (while (and (neq ?input да) (neq ?input нет))
    (printout t "Ошибка! Введите 'да' или 'нет'." crlf)
    (printout t ?question " (да/нет): ")
    (bind ?input (read)))
  (return ?input))

;; ============================================================================
;; РАЗДЕЛ 4: ПРАВИЛА ИНИЦИАЛИЗАЦИИ И ОПРОСА
;; ============================================================================

;; Правило запуска интерактивного опроса
(defrule init-questions
  "Запускает процесс опроса пользователя при старте системы"
  (declare (salience 100))
  ?stage-fact <- (stage awaiting-input)
  (system-ready)
  =>
  (printout t crlf)
  (printout t "========================================" crlf)
  (printout t "СИСТЕМА ВЫБОРА РЕЦЕПТА" crlf)
  (printout t "========================================" crlf)
  (printout t crlf)
  
  ;; Опрос пользователя через функции
  (bind ?budget (ask-int "Введите ваш бюджет (в рублях):"))
  (bind ?dietary (ask-yes-no "Есть ли у вас диетические ограничения?"))
  (bind ?meat (ask-yes-no "Хотите ли вы мясные блюда?"))
  (bind ?soups (ask-yes-no "Хотите ли вы супы?"))
  (bind ?side-dishes (ask-yes-no "Хотите ли вы гарниры?"))
  (bind ?salads (ask-yes-no "Хотите ли вы салаты?"))
  (bind ?spices (ask-yes-no "Есть ли у вас специи?"))
  (bind ?quick (ask-yes-no "Предпочитаете быстрое приготовление?"))
  
  ;; Ассерт факта с пользовательскими данными
  (assert (user-input
    (budget ?budget)
    (dietary-restrictions ?dietary)
    (want-meat ?meat)
    (want-soups ?soups)
    (want-side-dishes ?side-dishes)
    (want-salads ?salads)
    (have-spices ?spices)
    (quick-cooking ?quick)))
  
  ;; Проверка на отсутствие всех предпочтений
  (if (and (eq ?meat нет)
           (eq ?soups нет)
           (eq ?side-dishes нет)
           (eq ?salads нет))
  then
    (assert (all-questions-no да))
    (printout t "[Отметка] Все основные предпочтения = нет" crlf))
  
  ;; Переход к фазе вывода
  (retract ?stage-fact)
  (assert (stage inference))
  (printout t crlf "Анализируем ваши предпочтения..." crlf crlf))

;; ============================================================================
;; РАЗДЕЛ 5: ПРАВИЛА КАТЕГОРИЗАЦИИ БЮДЖЕТА (ПРАВИЛА 1-3)
;; ============================================================================

;; Правило 1: Бюджет < 1000 руб => низкий
(defrule rule-01-categorize-budget-low
  "Категоризация бюджета как низкого при значении < 1000"
  (stage inference)
  (user-input (budget ?n))
  (test (< ?n 1000))
  (not (budget-category ?))
  =>
  (assert (budget-category низкий))
  (printout t "[Правило 1] Бюджет < 1000 руб => категория: низкий" crlf))

;; Правило 2: 1000 <= Бюджет <= 3000 => средний
(defrule rule-02-categorize-budget-medium
  "Категоризация бюджета как среднего при значении 1000-3000"
  (stage inference)
  (user-input (budget ?n))
  (test (>= ?n 1000))
  (test (<= ?n 3000))
  (not (budget-category ?))
  =>
  (assert (budget-category средний))
  (printout t "[Правило 2] 1000 <= Бюджет <= 3000 => категория: средний" crlf))

;; Правило 3: Бюджет > 3000 => высокий
(defrule rule-03-categorize-budget-high
  "Категоризация бюджета как высокого при значении > 3000"
  (stage inference)
  (user-input (budget ?n))
  (test (> ?n 3000))
  (not (budget-category ?))
  =>
  (assert (budget-category высокий))
  (printout t "[Правило 3] Бюджет > 3000 => категория: высокий" crlf))

;; ============================================================================
;; РАЗДЕЛ 6: ПРАВИЛА ОПРЕДЕЛЕНИЯ ТИПА КУХНИ (ПРАВИЛА 4-5)
;; ============================================================================

;; Правило 4: низкий бюджет => простая кухня
(defrule rule-04-simple-cuisine
  "Низкий бюджет => простая кухня"
  (stage inference)
  (budget-category низкий)
  (not (cuisine-simple да))
  =>
  (assert (cuisine-simple да))
  (printout t "[Правило 4] Бюджет низкий => Простая кухня = да" crlf))

;; Правило 5: средний бюджет + нет ограничений => ресторанная кухня
(defrule rule-05-restaurant-cuisine-medium
  "Средний бюджет без ограничений => ресторанная кухня"
  (stage inference)
  (budget-category средний)
  (user-input (dietary-restrictions нет))
  (not (cuisine-restaurant да))
  =>
  (assert (cuisine-restaurant да))
  (printout t "[Правило 5] Бюджет средний + нет ограничений => Ресторанная кухня = да" crlf))

;; Правило 5b: высокий бюджет + нет ограничений => ресторанная кухня
(defrule rule-05b-restaurant-cuisine-high
  "Высокий бюджет без ограничений => ресторанная кухня"
  (stage inference)
  (budget-category высокий)
  (user-input (dietary-restrictions нет))
  (not (cuisine-restaurant да))
  =>
  (assert (cuisine-restaurant да))
  (printout t "[Правило 5b] Бюджет высокий + нет ограничений => Ресторанная кухня = да" crlf))

;; ============================================================================
;; РАЗДЕЛ 7: ПРАВИЛА ДОСТУПНОСТИ ТИПОВ БЛЮД
;; ============================================================================

;; Правило 6: хочу мясо => доступны мясные блюда
(defrule rule-06-meat-dishes-available
  "Желание мясных блюд => мясные блюда доступны"
  (stage inference)
  (user-input (want-meat да))
  (not (meat-dishes-available да))
  =>
  (assert (meat-dishes-available да))
  (printout t "[Правило 6] Хочу мясо => Мясные блюда доступны = да" crlf))

;; Правило 7: хочу супы => доступны супы
(defrule rule-07-soups-available
  "Желание супов => супы доступны"
  (stage inference)
  (user-input (want-soups да))
  (not (soups-available да))
  =>
  (assert (soups-available да))
  (printout t "[Правило 7] Хочу супы => Супы доступны = да" crlf))

;; Правило 8: хочу гарниры => доступны гарниры
(defrule rule-08-side-dishes-available
  "Желание гарниров => гарниры доступны"
  (stage inference)
  (user-input (want-side-dishes да))
  (not (side-dishes-available да))
  =>
  (assert (side-dishes-available да))
  (printout t "[Правило 8] Хочу гарниры => Гарниры доступны = да" crlf))

;; Правило 9: хочу салаты + есть специи => доступны салаты
(defrule rule-09-salads-available
  "Желание салатов и наличие специй => салаты доступны"
  (stage inference)
  (user-input (want-salads да) (have-spices да))
  (not (salads-available да))
  =>
  (assert (salads-available да))
  (printout t "[Правило 9] Хочу салаты + есть специи => Салаты доступны = да" crlf))

;; ============================================================================
;; РАЗДЕЛ 8: ПРАВИЛА СОЧЕТАНИЯ КУХНИ И ТИПОВ БЛЮД
;; ============================================================================

;; Правило 10: простая кухня + мясные блюда => простые мясные блюда
(defrule rule-10-simple-meat-dishes
  "Простая кухня и доступные мясные блюда => простые мясные блюда"
  (stage inference)
  (cuisine-simple да)
  (meat-dishes-available да)
  (not (simple-meat-dishes да))
  =>
  (assert (simple-meat-dishes да))
  (printout t "[Правило 10] Простая кухня + мясные блюда => Простые мясные блюда = да" crlf))

;; Правило 11: ресторанная кухня + мясные блюда => ресторанные мясные блюда
(defrule rule-11-restaurant-meat-dishes
  "Ресторанная кухня и доступные мясные блюда => ресторанные мясные блюда"
  (stage inference)
  (cuisine-restaurant да)
  (meat-dishes-available да)
  (not (restaurant-meat-dishes да))
  =>
  (assert (restaurant-meat-dishes да))
  (printout t "[Правило 11] Ресторанная кухня + мясные блюда => Ресторанные мясные блюда = да" crlf))

;; Правило 12: простая кухня + супы => простые супы
(defrule rule-12-simple-soups
  "Простая кухня и доступные супы => простые супы"
  (stage inference)
  (cuisine-simple да)
  (soups-available да)
  (not (simple-soups да))
  =>
  (assert (simple-soups да))
  (printout t "[Правило 12] Простая кухня + супы => Простые супы = да" crlf))

;; Правило 13: ресторанная кухня + супы => ресторанные супы
(defrule rule-13-restaurant-soups
  "Ресторанная кухня и доступные супы => ресторанные супы"
  (stage inference)
  (cuisine-restaurant да)
  (soups-available да)
  (not (restaurant-soups да))
  =>
  (assert (restaurant-soups да))
  (printout t "[Правило 13] Ресторанная кухня + супы => Ресторанные супы = да" crlf))

;; Правило 14: простая кухня + гарниры => простые гарниры
(defrule rule-14-simple-side-dishes
  "Простая кухня и доступные гарниры => простые гарниры"
  (stage inference)
  (cuisine-simple да)
  (side-dishes-available да)
  (not (simple-side-dishes да))
  =>
  (assert (simple-side-dishes да))
  (printout t "[Правило 14] Простая кухня + гарниры => Простые гарниры = да" crlf))

;; Правило 15: простая кухня + салаты => простые салаты
(defrule rule-15-simple-salads
  "Простая кухня и доступные салаты => простые салаты"
  (stage inference)
  (cuisine-simple да)
  (salads-available да)
  (not (simple-salads да))
  =>
  (assert (simple-salads да))
  (printout t "[Правило 15] Простая кухня + салаты => Простые салаты = да" crlf))

;; Правило 16: ресторанная кухня + салаты => ресторанные салаты
(defrule rule-16-restaurant-salads
  "Ресторанная кухня и доступные салаты => ресторанные салаты"
  (stage inference)
  (cuisine-restaurant да)
  (salads-available да)
  (not (restaurant-salads да))
  =>
  (assert (restaurant-salads да))
  (printout t "[Правило 16] Ресторанная кухня + салаты => Ресторанные салаты = да" crlf))

;; ============================================================================
;; РАЗДЕЛ 9: ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ РЕЦЕПТОВ
;; ============================================================================

;; Правило 17: Простые мясные блюда + быстрое приготовление => Котлеты
(defrule rule-17-recommend-cutlets
  "Простые мясные блюда + быстрое приготовление => Котлеты"
  (declare (salience 10))
  (stage inference)
  (simple-meat-dishes да)
  (user-input (quick-cooking да))
  (not (final-result ?))
  =>
  (assert (final-result Котлеты))
  (printout t "[Правило 17] Простые мясные блюда + быстрое приготовление => Результат = Котлеты" crlf))

;; Правило 18: Простые мясные блюда + долгое приготовление => Гуляш
(defrule rule-18-recommend-goulash
  "Простые мясные блюда + долгое приготовление => Гуляш"
  (declare (salience 10))
  (stage inference)
  (simple-meat-dishes да)
  (user-input (quick-cooking нет))
  (not (final-result ?))
  =>
  (assert (final-result Гуляш))
  (printout t "[Правило 18] Простые мясные блюда + долгое приготовление => Результат = Гуляш" crlf))

;; Правило 19: Ресторанные мясные блюда + быстрое приготовление => Стейк
(defrule rule-19-recommend-steak
  "Ресторанные мясные блюда + быстрое приготовление => Стейк"
  (declare (salience 10))
  (stage inference)
  (restaurant-meat-dishes да)
  (user-input (quick-cooking да))
  (not (final-result ?))
  =>
  (assert (final-result Стейк))
  (printout t "[Правило 19] Ресторанные мясные блюда + быстрое приготовление => Результат = Стейк" crlf))

;; Правило 20: Ресторанные мясные блюда + долгое приготовление => Утка по-пекински
(defrule rule-20-recommend-peking-duck
  "Ресторанные мясные блюда + долгое приготовление => Утка по-пекински"
  (declare (salience 10))
  (stage inference)
  (restaurant-meat-dishes да)
  (user-input (quick-cooking нет))
  (not (final-result ?))
  =>
  (assert (final-result "Утка по-пекински"))
  (printout t "[Правило 20] Ресторанные мясные блюда + долгое приготовление => Результат = Утка по-пекински" crlf))

;; Правило 21: Простые супы + быстрое приготовление => Куриный суп
(defrule rule-21-recommend-chicken-soup
  "Простые супы + быстрое приготовление => Куриный суп"
  (declare (salience 10))
  (stage inference)
  (simple-soups да)
  (user-input (quick-cooking да))
  (not (final-result ?))
  =>
  (assert (final-result "Куриный суп"))
  (printout t "[Правило 21] Простые супы + быстрое приготовление => Результат = Куриный суп" crlf))

;; Правило 22: Простые супы + долгое приготовление => Борщ
(defrule rule-22-recommend-borscht
  "Простые супы + долгое приготовление => Борщ"
  (declare (salience 10))
  (stage inference)
  (simple-soups да)
  (user-input (quick-cooking нет))
  (not (final-result ?))
  =>
  (assert (final-result Борщ))
  (printout t "[Правило 22] Простые супы + долгое приготовление => Результат = Борщ" crlf))

;; Правило 23: Ресторанные супы + быстрое/долгое приготовление => Том-ям
(defrule rule-23-recommend-tom-yam
  "Ресторанные супы => Том-ям"
  (declare (salience 10))
  (stage inference)
  (restaurant-soups да)
  (not (final-result ?))
  =>
  (assert (final-result "Том-ям"))
  (printout t "[Правило 23] Ресторанные супы => Результат = Том-ям" crlf))

;; Правило 24: Простые гарниры + быстрое приготовление => Гречка
(defrule rule-24-recommend-buckwheat
  "Простые гарниры + быстрое приготовление => Гречка"
  (declare (salience 10))
  (stage inference)
  (simple-side-dishes да)
  (user-input (quick-cooking да))
  (not (final-result ?))
  =>
  (assert (final-result Гречка))
  (printout t "[Правило 24] Простые гарниры + быстрое приготовление => Результат = Гречка" crlf))

;; Правило 25: Простые гарниры + долгое приготовление => Рис с овощами
(defrule rule-25-recommend-rice-vegetables
  "Простые гарниры + долгое приготовление => Рис с овощами"
  (declare (salience 10))
  (stage inference)
  (simple-side-dishes да)
  (user-input (quick-cooking нет))
  (not (final-result ?))
  =>
  (assert (final-result "Рис с овощами"))
  (printout t "[Правило 25] Простые гарниры + долгое приготовление => Результат = Рис с овощами" crlf))

;; Правило 26: Простые салаты + быстрое приготовление => Овощной салат
(defrule rule-26-recommend-vegetable-salad
  "Простые салаты + быстрое приготовление => Овощной салат"
  (declare (salience 10))
  (stage inference)
  (simple-salads да)
  (user-input (quick-cooking да))
  (not (final-result ?))
  =>
  (assert (final-result "Овощной салат"))
  (printout t "[Правило 26] Простые салаты + быстрое приготовление => Результат = Овощной салат" crlf))

;; Правило 27: Простые салаты + долгое приготовление => Цезарь
(defrule rule-27-recommend-caesar
  "Простые салаты + долгое приготовление => Цезарь"
  (declare (salience 10))
  (stage inference)
  (simple-salads да)
  (user-input (quick-cooking нет))
  (not (final-result ?))
  =>
  (assert (final-result Цезарь))
  (printout t "[Правило 27] Простые салаты + долгое приготовление => Результат = Цезарь" crlf))

;; Правило 28: Ресторанные салаты + быстрое/долгое приготовление => Греческий салат
(defrule rule-28-recommend-greek-salad
  "Ресторанные салаты => Греческий салат"
  (declare (salience 10))
  (stage inference)
  (restaurant-salads да)
  (not (final-result ?))
  =>
  (assert (final-result "Греческий салат"))
  (printout t "[Правило 28] Ресторанные салаты => Результат = Греческий салат" crlf))

;; Правило 29: Все вопросы на первом уровне = нет => Не можем подобрать
(defrule rule-29-no-recommendation
  "Все основные предпочтения = нет => Не можем подобрать рецепт"
  (declare (salience 10))
  (stage inference)
  (all-questions-no да)
  (not (final-result ?))
  =>
  (assert (final-result "Мы не можем подобрать рецепт исходя из ваших ответов"))
  (printout t "[Правило 29] Все основные предпочтения = нет => Результат = Не можем подобрать" crlf))

;; ============================================================================
;; РАЗДЕЛ 10: ПРАВИЛА ВЫВОДА ИТОГОВОГО РЕЗУЛЬТАТА
;; ============================================================================

;; Правило вывода финальной рекомендации
(defrule display-final-recommendation
  "Выводит итоговую рекомендацию пользователю"
  (declare (salience 5))
  (stage inference)
  (final-result ?recipe)
  (not (result-displayed))
  =>
  (assert (result-displayed))
  (printout t crlf)
  (printout t "========================================" crlf)
  (printout t "  ИТОГОВАЯ РЕКОМЕНДАЦИЯ" crlf)
  (printout t "========================================" crlf)
  (printout t "  Рекомендуем приготовить: " ?recipe crlf)
  (printout t "========================================" crlf)
  (printout t crlf))

;; Правило завершения работы системы
(defrule finalize-system
  "Завершает работу экспертной системы"
  (declare (salience 1))
  (stage inference)
  (result-displayed)
  =>
  (printout t "Работа экспертной системы завершена." crlf)
  (printout t "Для просмотра всех фактов введите: (facts)" crlf)
  (printout t crlf))

;; ============================================================================
;; КОНЕЦ СКРИПТА
;; ============================================================================
