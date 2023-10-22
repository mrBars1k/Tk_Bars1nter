from tkinter import *
from tkinter import ttk
import sqlite3
import shutil
import os
from datetime import datetime
import random

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ГЛАВНОЕ ОКНО

m_window = Tk()
m_window.title("Английский язык") ## заголовок окна;
m_window.geometry("1280x720+400+200") ## разрешение окна и смещение при запуске;
m_window.wm_minsize(854, 480)  # Минимальная ширина и высота окна
m_window.wm_maxsize(1920, 1080)  # Максимальная ширина и высота окна
m_window.bind("<Delete>", lambda event: delete_selected())

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ВКЛАДКИ;

tab_control = ttk.Notebook(m_window)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)

## ## названия вкладок;

tab_control.add(tab1, text=" ")
tab_control.add(tab2, text=" ")
tab_control.add(tab3, text=" ")
tab_control.pack(expand=1, fill='both')

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def switch_to_tab1():
    tab_control.select(tab1)
    update_button_labels(switch_to_tab1_button)
    m_window.unbind("<space>")

def switch_to_tab2():
    tab_control.select(tab2)
    update_button_labels(switch_to_tab2_button)
    m_window.bind("<space>", toggle_translation)

def switch_to_tab3():
    tab_control.select(tab3)
    update_button_labels(switch_to_tab3_button)
    m_window.unbind("<space>")


## ## ## ##

switch_to_tab1_button = Button(m_window, text="Словарь", width=15, command=switch_to_tab1)
switch_to_tab2_button = Button(m_window, text="Обучение", width=15, command=switch_to_tab2)
switch_to_tab3_button = Button(m_window, text="Прогресс", width=15, command=switch_to_tab3)

switch_to_tab1_button.place(x=500, y=10)
switch_to_tab2_button.place(x=700, y=10)
switch_to_tab3_button.place(x=900, y=10)

## ## ## ##
## изначальные названия;
original_button_labels = {
    switch_to_tab1_button: ("Словарь", "SystemButtonFace"),
    switch_to_tab2_button: ("Обучение", "SystemButtonFace"),
    switch_to_tab3_button: ("Прогресс", "SystemButtonFace")
}

## ## ## ##
## обновление названий;
def update_button_labels(active_button):
    for button, (label, color) in original_button_labels.items():
        if button == active_button:
            button.config(text=f"<{label}>", bg="#00FFFF")
        else:
            button.config(text=label, bg=color)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ##

adb = sqlite3.connect("V:/Py_Pro/Tk_Bars1nter/vocabulary.db")
cur = adb.cursor()

## ## ## ##

cur.execute("""CREATE TABLE IF NOT EXISTS words (
    id            INTEGER PRIMARY KEY,
    english       TEXT    UNIQUE,
    russian       TEXT    UNIQUE,
    transcription TEXT    UNIQUE,
    learned       INTEGER DEFAULT 0,
    added_date    TEXT,
    enough_date   TEXT,
    learned_count INTEGER
);""")
adb.commit()

## ## ## ##

cur.execute("""CREATE TABLE IF NOT EXISTS recycle_bin (
    id            INTEGER PRIMARY KEY,
    english       TEXT    UNIQUE,
    russian       TEXT    UNIQUE,
    transcription TEXT    UNIQUE,
    deleted_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);""")
adb.commit()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## копия базы данных;

def create_backup():
    current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") ## дата в формате;
    backup_filename = f"vocabulary_backup_{current_datetime}.db" ## новое имя файла;
    current_database = "V:/Py_Pro/Bars_Tkinter/vocabulary.db" ## путь к бд;
    shutil.copy(current_database, backup_filename) ## копирование;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def delete_selected():
    # Получить выбранные элементы в таблице
    selected_items = tree.selection()

    for selected_item in selected_items:
        data = tree.item(selected_item)
        values = data['values']

        if values:
            record_id = values[0]

            if record_id:
                # Сначала скопируйте запись в корзину
                cur.execute(
                    "INSERT INTO recycle_bin (english, russian, transcription) SELECT english, russian, transcription FROM words WHERE ID = ?",
                    (record_id,))

                cur.execute("DELETE FROM words WHERE ID = ?", (record_id,))
    adb.commit()
    update_table()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def focus_next(event):
    event.widget.tk_focusNext().focus()

## ## ## ##

def focus_previous(event):
    event.widget.tk_focusPrev().focus()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def update_table(): ## вывод всех данных из бд;
    cur.execute("SELECT * FROM words")
    data = cur.fetchall()
    for row in tree.get_children():
        tree.delete(row)
    for row in data:
        tree.insert("", "end", values=row)

## ## ## ##

lbl_notall = None
def clicked():
    eng_text = eng_entry.get()
    ru_text = ru_entry.get()
    trans_text = trans_entry.get()

    global lbl_notall  # Объявляем переменную lbl_notall как глобальную

    if lbl_notall:
        lbl_notall.destroy()  # Убирает надпись, если она есть

    if eng_text and ru_text and trans_text:
        cur.execute("INSERT INTO words (english, russian, transcription) VALUES (?, ?, ?)",
                       (eng_text, ru_text, trans_text))
        adb.commit()

        ## очищает поля ввода, после отправки;
        eng_entry.delete(0, END)
        ru_entry.delete(0, END)
        trans_entry.delete(0, END)

        eng_entry.focus_set() ## фокус на поле английского;
        update_table()

    else:
        custom_font = ("Helvetica", 16)
        lbl_notall = Label(tab1, text="Заполните все поля!", font=custom_font)
        lbl_notall.place(x=30, y=340)

## ## ## ##

def clear_fields(): ## отчистка полей ввода;
    eng_entry.delete(0, END)
    ru_entry.delete(0, END)
    trans_entry.delete(0, END)

## ## ## ##

def click_and():
    clicked()
    update_table()

## ## ## ##

def reorder_and_update():
    cur.execute("SELECT ID, russian, english, transcription FROM words ORDER BY ID")
    data = cur.fetchall()
    cur.execute("DELETE FROM words")
    for index, row in enumerate(data):
        cur.execute("INSERT INTO words (ID, russian, english, transcription) VALUES (?, ?, ?, ?)", (index + 1, row[1], row[2], row[3]))
    adb.commit()
    update_table()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

eng_lbl = Label(tab1, text="Английский")
eng_entry = Entry(tab1, width=30, borderwidth=2)
##
ru_lbl = Label(tab1, text="Русский")
ru_entry = Entry(tab1, width=30, borderwidth=2)
##
trans_lbl = Label(tab1, text="Транскрипция")
trans_entry = Entry(tab1, width=30, borderwidth=2)

## ## ## ## РАЗМЕЩЕНИЕ ВИДЖЕТОВ;

eng_lbl.place(x=40, y=20)
eng_entry.place(x=40, y=40)
##
ru_lbl.place(x=40, y=70)
ru_entry.place(x=40, y=90)
##
trans_lbl.place(x=40, y=120)
trans_entry.place(x=40, y=140)
##

## ## ## ##

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
## ##
delete_btn = Button(tab1, text="Удалить", width=30, height=1, command=delete_selected)
delete_btn.place(x=20, y=230)
## ##
reorder_btn = Button(tab1, text="Упорядочить и обновить", width=30, height=1, command=reorder_and_update)
reorder_btn.place(x=20, y=270)
## ##
delete_btn = Button(tab1, text="Создать копию базы данных", width=30, height=1, command=create_backup)
delete_btn.place(x=20, y=300)
## ##
clear_button = Button(tab1, text="Очистить\nполя", width=8, height=8, command=clear_fields)
clear_button.place(x=235, y=36)

## ## ## ##

eng_entry.bind("<Return>", lambda event=None: ru_entry.focus_set())
ru_entry.bind("<Return>", lambda event=None: trans_entry.focus_set())
trans_entry.bind("<Return>", lambda event=None: clicked())

eng_entry.bind("<Down>", focus_next)  # Перемещение вниз при нажатии на стрелку вниз
eng_entry.bind("<Up>", focus_previous)  # Перемещение вверх при нажатии на стрелку вверх

ru_entry.bind("<Down>", focus_next)
ru_entry.bind("<Up>", focus_previous)
ru_entry.bind("<Left>", focus_previous)  # Опционально: перемещение к предыдущему полю при нажатии стрелки влево

trans_entry.bind("<Down>", focus_next)
trans_entry.bind("<Up>", focus_previous)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ##

cw = 'Открыто'
def toggle_translation(event=None):
    global cw
    if cw == 'Открыто':
        cw = 'Скрыто'
        new_text = "Показать перевод"
        russian_translation_label.configure(text=f"{word1[1]}")
        toggle_translation_button.configure(text=new_text)

    elif cw == 'Скрыто':
        new_text = "Скрыть перевод"
        cw = 'Открыто'
        toggle_translation_button.configure(text=new_text)
        russian_translation_label.configure(text=' ')

## ## ## ##

def learn_word():
    cur.execute("""SELECT english, russian, transcription, learned FROM words""")
    word1 = cur.fetchall()
    word2 = []
    for i in word1:
        if i[3] <= 10:
            word2 += {i}
    random_word = random.choice(word2)
    return random_word

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

word1 = learn_word()

empty_word_label  = Label(tab2, text=" ")
english_word_label  = Label(tab2, text=f"{word1[0]}", font=("Helvetica", 34), anchor="center")
russian_translation_label  = Label(tab2, text=f" ", font=("Helvetica", 16), anchor="center", wraplength=400)
transcription_label  = Label(tab2, text=f"{word1[2]}", font=("Helvetica", 12), anchor="center")

empty_word_label.pack(pady=70)
english_word_label.pack()
transcription_label.pack()

toggle_translation_button = Button(tab2, text="Показать перевод", font=("Helvetica", 18), width=30, height=1, command=toggle_translation, bg='pink')
toggle_translation_button.pack(pady=20)

russian_translation_label.pack(pady=40)

# next_button = Button(tab2, text="Далее", font=("Helvetica", 16), width=16, height=1, bg='blue', command=next_word)
# next_button.place(x=535, y=450)

next_button1 = Button(tab2, text="Плохо", font=("Helvetica", 16), width=16, height=1, bg='red')
next_button1.place(x=245, y=550)

next_button2 = Button(tab2, text="Хорошо", font=("Helvetica", 16), width=16, height=1, bg='green')
next_button2.place(x=535, y=550)

next_button3 = Button(tab2, text="Отлично", font=("Helvetica", 16), width=16, height=1, bg='yellow')
next_button3.place(x=825, y=550)

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

m_window.mainloop() ## запуск программы;
adb.close() ## закрыть подключение;

