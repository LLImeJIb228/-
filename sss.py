import tkinter as tk
import pandas as pd
import numpy as np

nume = ''
#--------------------Pandas----------------------#

def cucumber():
    print()



#--------------------Tkinter---------------------#
predmet = ''

def menu1():
    global menu
    global predmet
    menu = tk.Tk()
    menu.title("Подготовка к профилю")
    menu.geometry("480x340")

    label = tk.Label(menu,text="Выберите задачу для изучения")
    label.pack()

    button = tk.Button(menu,
                       text="Уравнения",
                       command=lambda: pred('Уравнения',''))
    button.pack()
    button = tk.Button(menu,
                       text="Проценты",
                       command=lambda: pred('Проценты',''))
    button.pack()
    button = tk.Button(menu,
                       text="Вероятность",
                       command=lambda: pred('Вероятность',''))
    button.pack()
    button = tk.Button(menu,
                       text="Стереометрия",
                       command=lambda: data_load('Стериометрия') /pred('Стереометрия','',nume))
    button.pack()
    button = tk.Button(menu,
                       text="Планометрия",
                       command=lambda: pred('Планометрия',''))
    button.pack()
    button = tk.Button(menu,
                       text="Ставки",
                       command=lambda: pred('Ставки',''))
    button.pack()
    button = tk.Button(menu,
                       text="Счет",
                       command=lambda: pred('Счет',''))
    button.pack()

    menu.mainloop()

def pred(predmet,text_zadachi):

    """Создает следующее окно"""
    menu.destroy()
    Zadanie = tk.Tk()
    Zadanie.title("Задание")
    Zadanie.geometry("480x340")
    label = tk.Label(Zadanie, text="Вид задания: "+predmet)
    label.pack()
    if predmet in ['Стереометрия','Планометрия']:
        print()

    label = tk.Label(Zadanie, text=text_zadachi)
    label.pack()

    Otvet = tk.Entry(Zadanie)
    Otvet.pack(pady=10)
    print(Otvet)

    Zadanie.mainloop()

#------------------------------------------------#

menu1()
