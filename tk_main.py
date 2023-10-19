from tkinter import *
from tkinter import ttk
import sqlite3
import shutil
import os
from datetime import datetime

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

## ## Названия вкладок;

tab_control.add(tab1)
tab_control.add(tab2)
tab_control.add(tab3)

tab_control.pack(expand=1, fill='both')

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## копия базы данных;

def create_backup():
    current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") ## дата в формате;
    backup_filename = f"vocabulary_backup_{current_datetime}.db" ## новое имя файла;
    current_database = "V:/Py_Pro/Bars_Tkinter/vocabulary.db" ## путь к бд;
    shutil.copy(current_database, backup_filename) ## копирование;

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def switch_to_tab1():
    tab_control.select(tab1)

def switch_to_tab2():
    tab_control.select(tab2)

def switch_to_tab3():
    tab_control.select(tab3)

## ## ## ##

switch_to_tab1_button = Button(m_window, text="Словарь", width=15, command=switch_to_tab1)
switch_to_tab2_button = Button(m_window, text="Обучение", width=15, command=switch_to_tab2)
switch_to_tab3_button = Button(m_window, text="Прогресс", width=15, command=switch_to_tab3)

switch_to_tab1_button.place(x=500, y=10)
switch_to_tab2_button.place(x=700, y=10)
switch_to_tab3_button.place(x=900, y=10)

## ## ## ##

adb = sqlite3.connect("vocabulary.db")
cur = adb.cursor()

## ## ## ##

cur.execute("""CREATE TABLE IF NOT EXISTS words (
    id            INTEGER PRIMARY KEY,
    english       TEXT    UNIQUE,
    russian       TEXT    UNIQUE,
    transcription TEXT    UNIQUE,
    learned       INTEGER DEFAULT 0
);""")
adb.commit()

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
                cur.execute("DELETE FROM words WHERE ID = ?", (record_id,))
    adb.commit()
    update_table()

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def update_table(): ## вывод всех данных из бд;
    cur.execute("SELECT * FROM words")
    data = cur.fetchall()
    for row in tree.get_children():
        tree.delete(row)
    for row in data:
        tree.insert("", "end", values=row)

## ## ## ##

def clicked():
    eng_text = eng_entry.get()
    ru_text = ru_entry.get()
    trans_text = trans_entry.get()

    if eng_text and ru_text and trans_text:
        print("Английский:", eng_text)
        print("Русский:", ru_text)
        print("Транскрипция:", trans_text)

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
        print("Пожалуйста, заполните все поля перед отправкой.")

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

btn = Button(tab1, text="Отправить!", width=30, height=1, command=click_and)
##
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
btn.place(x=20, y=180)

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
tree.place(x=300, y=60, height=600, width=950)
update_table()

## ## ## ##

reorder_btn = Button(tab1, text="Упорядочить и обновить", width=30, height=1, command=reorder_and_update)
reorder_btn.place(x=20, y=240)
## ##
delete_btn = Button(tab1, text="Удалить", width=30, height=1, command=delete_selected)
delete_btn.place(x=20, y=210)
## ##
delete_btn = Button(tab1, text="Создать копию базы данных", width=30, height=1, command=create_backup)
delete_btn.place(x=20, y=270)

## ## ## ##

eng_entry.bind("<Return>", lambda event=None: ru_entry.focus_set())
ru_entry.bind("<Return>", lambda event=None: trans_entry.focus_set())
trans_entry.bind("<Return>", lambda event=None: clicked())

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

m_window.mainloop() ## запуск программы;
adb.close() ## закрыть подключение;

