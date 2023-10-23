from tkinter import *
from tkinter import ttk
import sqlite3
import shutil
import os
from datetime import datetime, timedelta
import random

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ГЛАВНОЕ ОКНО;

m_window = Tk() ## главное окно;
m_window.title("Английский язык") ## заголовок окна;
m_window.geometry("1280x720+400+200") ## разрешение окна и смещение при запуске;
m_window.wm_minsize(854, 480)  ## минимальная ширина и высота окна;
m_window.wm_maxsize(1920, 1080)  ## максимальная ширина и высота окна;
m_window.bind("<Delete>", lambda event: delete_selected())  ## удаление выделенного в таблице;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ОБЪЯВЛЕНИЕ ВКЛАДОК;

tab_control = ttk.Notebook(m_window)
tab1 = ttk.Frame(tab_control) ## для заполнения бд;
tab2 = ttk.Frame(tab_control) ## для обучения;
tab3 = ttk.Frame(tab_control) ## для отображения прогресса;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## НАЗВАНИЯ ВКЛАДОК ВВЕРХУ СЛЕВА;

tab_control.add(tab1, text=" ")
tab_control.add(tab2, text=" ")
tab_control.add(tab3, text=" ")
tab_control.pack(expand=1, fill='both')

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ПЕРЕХОД НА ВКЛАДКИ;
## с вызовом обновления названий кнопок и блокировкой/разблокировкой выполнения space на клавиатуре;

def switch_to_tab1():
    tab_control.select(tab1)
    update_button_labels(switch_to_tab1_button)
    m_window.unbind("<space>")
    m_window.bind("<Delete>", lambda event: delete_selected())
## ##
def switch_to_tab2():
    tab_control.select(tab2)
    update_button_labels(switch_to_tab2_button)
    m_window.bind("<space>", toggle_translation) ## показать/скрыть перевод;
    m_window.unbind("<Delete>")
## ##
def switch_to_tab3():
    tab_control.select(tab3)
    update_button_labels(switch_to_tab3_button)
    m_window.unbind("<space>")
    m_window.unbind("<Delete>")

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## КНОПКИ ПЕРЕКЛЮЧЕНИЯ МЕЖДУ ВКЛАДКАМИ;

switch_to_tab1_button = Button(m_window, text="Словарь", width=15, command=switch_to_tab1)
switch_to_tab2_button = Button(m_window, text="Обучение", width=15, command=switch_to_tab2)
switch_to_tab3_button = Button(m_window, text="Прогресс", width=15, command=switch_to_tab3)

switch_to_tab1_button.place(x=500, y=10)
switch_to_tab2_button.place(x=700, y=10)
switch_to_tab3_button.place(x=900, y=10)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ОБНОВЛЕНИЕ НАЗВАНИЙ ВКЛАДОК ПО НАЖАТИЮ;
## (<кнопка> и изменяется цвет);

## изначальные названия кнопок для вкладок;
original_button_labels = {
    switch_to_tab1_button: ("Словарь", "SystemButtonFace"),
    switch_to_tab2_button: ("Обучение", "SystemButtonFace"),
    switch_to_tab3_button: ("Прогресс", "SystemButtonFace")
}

def update_button_labels(active_button):
    for button, (label, color) in original_button_labels.items():
        if button == active_button:
            button.config(text=f"<{label}>", bg="#00FFFF")
        else:
            button.config(text=label, bg=color)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ПОДКЛЮЧЕНИЕ БАЗЫ ДАННЫХ;

adb = sqlite3.connect("V:/Py_Pro/Tk_Bars1nter/vocabulary.db")
cur = adb.cursor()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ПРОВЕРКА НА ИЗУЧЕННОСТЬ СЛОВА
## если значение в бд больше 10, то слово считается изученным и к текущей дате прибавляется 1 неделя и заносится в бд;
## затем счётчик обнуляется, а к счётчику таких откладываний слова прибавляется 1;

def upd_learned():
    cur.execute("SELECT * FROM words WHERE learned > 10")
    for i in cur.fetchall():
        current_date = datetime.now() + timedelta(weeks=1)
        enough_date = current_date.strftime("%d.%m.%Y_%H:%M")
        cur.execute("UPDATE words SET enough_date = ?, learned = 0, learned_count = learned_count + 1 WHERE id = ?", (enough_date, i[0]))
    adb.commit()

def upd_date_learn(): ## если дата в бд позже текущей даты, то состояние close, в других случаях open;
    current_date = datetime.now().strftime("%d.%m.%Y_%H:%M")
    cur.execute("UPDATE words SET op_cl = CASE WHEN enough_date <= ? THEN 'open' ELSE 'close' END", (current_date,))
    adb.commit()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## СОЗДАНИЕ ТАБЛИЦ (СЛОВАРЬ И КОРЗИНА) В БД;

cur.execute("""CREATE TABLE IF NOT EXISTS words (
    id            INTEGER PRIMARY KEY,
    english       TEXT    UNIQUE,
    russian       TEXT    UNIQUE,
    transcription TEXT    UNIQUE,
    learned       INTEGER DEFAULT 0,
    added_date    TEXT,
    enough_date   TEXT,
    learned_count INTEGER DEFAULT (0),
    op_cl         TEXT    DEFAULT open
);""")
adb.commit()

## ## ## ##

cur.execute("""CREATE TABLE IF NOT EXISTS recycle_bin (
    id            INTEGER PRIMARY KEY,
    english       TEXT    UNIQUE,
    russian       TEXT    UNIQUE,
    transcription TEXT    UNIQUE,
    learned       INTEGER DEFAULT 0,
    added_date    TEXT,
    enough_date   TEXT,
    learned_count INTEGER DEFAULT (0),
    op_cl         TEXT    DEFAULT open
);""")
adb.commit()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## КОПИЯ БАЗЫ ДАННЫХ;

def create_backup():
    current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") ## дата в формате;
    backup_filename = f"vocabulary_backup_{current_datetime}.db" ## новое имя файла;
    current_database = "V:/Py_Pro/Bars_Tkinter/vocabulary.db" ## путь к бд;
    shutil.copy(current_database, backup_filename) ## копирование;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## УДАЛЕНИЕ ВЫДЕЛЕННОГО В ТАБЛИЦЕ ПРИЛОЖЕНИЯ ИЗ БД И ПЕРЕНОС В КОРЗИНУ;

def delete_selected():
    selected_items = tree.selection()

    for selected_item in selected_items:
        data = tree.item(selected_item)
        values = data['values']

        if values:
            record_id = values[0]

            if record_id:
                cur.execute("""INSERT INTO recycle_bin (russian, english, transcription, learned, added_date, enough_date, learned_count, op_cl) 
                    SELECT russian, english, transcription, learned, added_date, enough_date, learned_count, op_cl FROM words WHERE ID = ?""",
                    (record_id,))

                cur.execute("DELETE FROM words WHERE ID = ?", (record_id,))
    adb.commit()
    update_table()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## СМЕНА ФОКУСА МЕЖДУ ПОЛЯМИ ВВОДА, ПОСЛЕ ENTER;

def focus_next(event):
    current_widget = event.widget
    if current_widget == eng_entry:
        ru_entry.focus_set()
    elif current_widget == ru_entry:
        trans_entry.focus_set()

## ## ## ##

def focus_previous(event):
    current_widget = event.widget
    if current_widget == trans_entry:
        ru_entry.focus_set()
    elif current_widget == ru_entry:
        eng_entry.focus_set()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ОБНОВЛЕНИЕ И ВЫВОД ДАННЫХ ИЗ БД В ТАБЛИЦУ ПРИЛОЖЕНИЯ;

def update_table():
    cur.execute("SELECT * FROM words")
    data = cur.fetchall()
    for row in tree.get_children():
        tree.delete(row)
    for row in data:
        tree.insert("", "end", values=row)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ВВОД И ОТПРАВКА ДАННЫХ ДЛЯ ЗАПОЛНЕНИЯ БД;

lbl_notall = None

def clicked():
    eng_text = eng_entry.get()
    ru_text = ru_entry.get() ## получить написанное в полях ввода;
    trans_text = trans_entry.get()

    current_date = datetime.now().strftime("%d.%m.%Y_%H:%M") ## текущая дата;

    global lbl_notall

    if lbl_notall:
        lbl_notall.destroy()

    if eng_text and ru_text and trans_text: ## если все три поля заполнены, то отправить;
        cur.execute("INSERT INTO words (english, russian, transcription, learned, added_date, enough_date) VALUES (?, ?, ?, ?, ?, ?)",
                       (eng_text, ru_text, trans_text, 0, current_date, current_date))
        adb.commit()

        eng_entry.delete(0, END)
        ru_entry.delete(0, END) ## очищает поля ввода, после отправки;
        trans_entry.delete(0, END)

        eng_entry.focus_set() ## фокус на поле английского, после отправки;
        update_table() ## обновить и отобразить данные;

    else: ## если не все заполнены, то оповестить надписью;
        custom_font = ("Helvetica", 16)
        lbl_notall = Label(tab1, text="Заполните все поля!", font=custom_font)
        lbl_notall.place(x=30, y=340)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ОТЧИСТКА ПОЛЕЙ ВВОДА;

def clear_fields():
    eng_entry.delete(0, END)
    ru_entry.delete(0, END)
    trans_entry.delete(0, END)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## НЕ ПОМНЮ УЖЕ ЗАЧЕМ ТАК, НО РАБОТАЕТ И НЕ МЕШАЕТ;
def click_and():
    clicked()
    update_table()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## УПОРЯДОЧИТЬ НУМЕРАЦИЮ ID И ОБНОВИТЬ ВИДИМЫЕ ДАННЫЕ В ТАБЛИЦЕ;

def reorder_and_update():
    cur.execute("SELECT ID, russian, english, transcription, learned, added_date, enough_date, learned_count, op_cl FROM words ORDER BY ID")
    data = cur.fetchall()
    cur.execute("DELETE FROM words")
    for index, row in enumerate(data):
        cur.execute("INSERT INTO words (ID, russian, english, transcription, learned, added_date, enough_date, learned_count, op_cl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (index + 1, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],))
    adb.commit()
    update_table()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## РАЗМЕЩЕНИЕ ВИДЖЕТОВ;

eng_lbl = Label(tab1, text="Английский")
eng_entry = Entry(tab1, width=30, borderwidth=2)

ru_lbl = Label(tab1, text="Русский")
ru_entry = Entry(tab1, width=30, borderwidth=2)

trans_lbl = Label(tab1, text="Транскрипция")
trans_entry = Entry(tab1, width=30, borderwidth=2)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## НАДПИСИ НАД ПОЛЯМИ ВВОДА И САМИ ПОЛЯ ВВОДА ДЛЯ ЗАПОЛНЕНИЯ БД;

eng_lbl.place(x=40, y=20)
eng_entry.place(x=40, y=40)

ru_lbl.place(x=40, y=70)
ru_entry.place(x=40, y=90)

trans_lbl.place(x=40, y=120)
trans_entry.place(x=40, y=140)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ТАБЛИЦА ДЛЯ ВЫВОДА ВСЕХ СЛОВ ИЗ БД;

tree = ttk.Treeview(tab1, columns=("ID", "Английский", "Русский", "Транскрипция"))
tree.column("#0", width=0)
tree.column("#1", width=10, anchor="center")
tree.column("#2", width=100, anchor="center")
tree.column("#3", width=450, anchor="center")
tree.column("#4", width=100, anchor="center")

## ## ## ##

tree.heading("#1", text="ID")
tree.heading("#2", text="Английский")
tree.heading("#3", text="Русский")
tree.heading("#4", text="Транскрипция")
tree.place(x=310, y=60, height=600, width=950)
update_table()

## ## ## ##

btn = Button(tab1, text="Отправить!", width=30, height=1, command=click_and)
btn.place(x=20, y=200)

delete_btn = Button(tab1, text="Удалить", width=30, height=1, command=delete_selected)
delete_btn.place(x=20, y=230)

reorder_btn = Button(tab1, text="Упорядочить и обновить", width=30, height=1, command=reorder_and_update)
reorder_btn.place(x=20, y=270)

delete_btn = Button(tab1, text="Создать копию базы данных", width=30, height=1, command=create_backup)
delete_btn.place(x=20, y=300)

clear_button = Button(tab1, text="Очистить\nполя", width=8, height=8, command=clear_fields)
clear_button.place(x=235, y=36)

## ## ## ##

eng_entry.bind("<Return>", lambda event=None: ru_entry.focus_set())
ru_entry.bind("<Return>", lambda event=None: trans_entry.focus_set())
trans_entry.bind("<Return>", lambda event=None: clicked())

eng_entry.bind("<Down>", focus_next)  ## фокус вниз стрелкой на клаве;
eng_entry.bind("<Up>", focus_previous)  ## фокус вверх стрелкой на клаве;

ru_entry.bind("<Down>", focus_next)
ru_entry.bind("<Up>", focus_previous)

trans_entry.bind("<Down>", focus_next)
trans_entry.bind("<Up>", focus_previous)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ПЕРЕКЛЮЧЕНИЕ НА СЛЕДУЮЩЕЕ СЛОВО БЕЗ ЗАПОЛНЕНИЯ БД;

random_word = None
cw = 'Скрыто'
def next_word():
    upd_learned()
    upd_date_learn()
    global cw
    global random_word

    cur.execute("""SELECT english, russian, transcription, learned, id FROM words""")
    word1 = cur.fetchall()
    word2 = []

    for i in word1:
        if i[3] <= 10:
            word2 += {i}

    random_word = random.choice(word2)
    english_word_label.configure(text=f'{random_word[0]}')
    transcription_label.configure(text=f'{random_word[2]}')

    if cw == 'Открыто':
        russian_translation_label.configure(text=f' ')
        toggle_translation_button.configure(text=f'Показать перевод')
        cw = 'Скрыто'

    return random_word

## ## ## ##

def bad_known():
    print(random_word[4])
    cur.execute("UPDATE words SET learned = learned - 1 WHERE id = ?", (random_word[4], ))
    upd_learned()
    upd_date_learn()
    next_word()
    adb.commit()

def good_known():
    print(random_word[4])
    cur.execute("UPDATE words SET learned = learned + 1 WHERE id = ?", (random_word[4], ))
    upd_learned()
    upd_date_learn()
    next_word()
    adb.commit()

def perfect_known():
    print(random_word[4])
    cur.execute("UPDATE words SET learned = learned + 2 WHERE id = ?", (random_word[4], ))
    upd_learned()
    upd_date_learn()
    next_word()
    adb.commit()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ПОКАЗАТЬ/СКРЫТЬ ПЕРЕВОД СЛОВА;

def toggle_translation(event=None):
    global cw
    if cw == 'Скрыто':
        cw = 'Открыто'
        new_text = "Скрыть перевод"
        russian_translation_label.configure(text=f"{random_word[1]}")
        toggle_translation_button.configure(text=new_text)

    elif cw == 'Открыто':
        new_text = "Показать перевод"
        cw = 'Скрыто'
        toggle_translation_button.configure(text=new_text)
        russian_translation_label.configure(text=' ')

empty_word_label  = Label(tab2, text=" ")
english_word_label  = Label(tab2, text=f" ", font=("Helvetica", 34), anchor="center")
russian_translation_label  = Label(tab2, text=f" ", font=("Helvetica", 16), anchor="center", wraplength=400)
transcription_label  = Label(tab2, text=f" ", font=("Helvetica", 12), anchor="center")

empty_word_label.pack(pady=70)
english_word_label.pack()
transcription_label.pack()

toggle_translation_button = Button(tab2, text="Показать перевод", font=("Helvetica", 18), width=30, height=1, command=toggle_translation, bg='pink')
toggle_translation_button.pack(pady=20)

russian_translation_label.pack(pady=40)

next_button = Button(tab2, text="Далее", font=("Helvetica", 16), width=16, height=1, bg='blue', command=next_word)
next_button.place(x=535, y=450)

next_button1 = Button(tab2, text="Плохо", font=("Helvetica", 16), width=16, height=1, bg='red', command=bad_known)
next_button1.place(x=245, y=550)

next_button2 = Button(tab2, text="Хорошо", font=("Helvetica", 16), width=16, height=1, bg='green', command=good_known)
next_button2.place(x=535, y=550)

next_button3 = Button(tab2, text="Отлично", font=("Helvetica", 16), width=16, height=1, bg='yellow', command=perfect_known)
next_button3.place(x=825, y=550)

next_word()
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
m_window.mainloop() ## запуск программы;
adb.close() ## закрыть подключение;

