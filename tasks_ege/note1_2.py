import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import re
import math
import configparser

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тренажер ЕГЭ по математике")
        self.root.geometry("700x600")
        self.root.resizable(True, True)  # разрешаем менять размер
        self.root.minsize(600, 500)  # минимальный размер (по желанию)
        self.load_window_size()  # загружаем сохранённый размер
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # сохраняем при закрытии
        self.colors = {
            'bg': '#f0f8ff', 'primary': '#4a6fa5', 'secondary': '#6b9ac4',
            'success': '#90ee90', 'warning': '#ffcccb', 'text': '#2c3e50', 'light': '#e8f4f8'
        }
        self.current_task_type = None
        self.df = None
        self.load_data()
        self.create_main_frame()

    def delete_task(self):
        """Удаление задачи: сначала выбор типа, затем задачи из этого типа"""
        if len(self.df) == 0:
            messagebox.showinfo("Нет задач", "База задач пуста, нечего удалять.")
            return

        win = tk.Toplevel(self.root)
        win.title("Удаление задачи")
        win.geometry("600x400")
        win.configure(bg=self.colors['bg'])
        win.resizable(False, False)

        tk.Label(win, text="1. Выберите тип задачи:", font=("Arial", 11),
                 bg=self.colors['bg']).pack(pady=(15, 5))
        types = sorted(self.df['тип_задачи'].unique())
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(win, textvariable=type_var, values=types,
                                  state='readonly', width=40, font=("Arial", 10))
        type_combo.pack(pady=5)

        tk.Label(win, text="2. Выберите задачу:", font=("Arial", 11),
                 bg=self.colors['bg']).pack(pady=(15, 5))
        task_var = tk.StringVar()
        task_combo = ttk.Combobox(win, textvariable=task_var, state='readonly',
                                  width=70, font=("Arial", 10))
        task_combo.pack(pady=5, padx=20)

        def update_task_list(*args):
            selected_type = type_var.get()
            if not selected_type:
                task_combo['values'] = []
                return
            tasks = self.df[self.df['тип_задачи'] == selected_type]
            # Формируем понятные строки: номер + начало текста
            task_combo['values'] = [
                f"№{row['номер']} – {row['текст_задачи'][:70]}..."
                for idx, row in tasks.iterrows()
            ]
            if task_combo['values']:
                task_combo.current(0)

        type_combo.bind('<<ComboboxSelected>>', update_task_list)
        if types:
            type_combo.current(0)
            update_task_list()

        def confirm_delete():
            selected_type = type_var.get()
            task_str = task_var.get()
            if not selected_type or not task_str:
                messagebox.showwarning("Не выбрано", "Выберите тип и задачу")
                return
            # Извлекаем номер задачи из строки (первое число после №)
            import re
            match = re.search(r'№(\d+)', task_str)
            if not match:
                messagebox.showerror("Ошибка", "Не удалось определить номер задачи")
                return
            task_num = int(match.group(1))
            if messagebox.askyesno("Подтверждение",
                                   f"Удалить задачу №{task_num} (тип: {selected_type})?\nЭто действие нельзя отменить."):
                self.df = self.df[self.df['номер'] != task_num]
                # Перенумеровываем задачи по порядку
                self.df = self.df.reset_index(drop=True)
                self.df['номер'] = self.df.index + 1
                self.save_to_csv()
                messagebox.showinfo("Удалено", f"Задача №{task_num} удалена")
                win.destroy()
                self.create_main_frame()  # обновляем главное окно

        btn_frame = tk.Frame(win, bg=self.colors['bg'])
        btn_frame.pack(pady=25)
        tk.Button(btn_frame, text="Удалить выбранную задачу", command=confirm_delete,
                  bg='lightcoral', font=("Arial", 10), width=20).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Отмена", command=win.destroy,
                  font=("Arial", 10), width=10).pack(side='left', padx=10)
    def load_window_size(self):
        """Загружает сохранённый размер окна из config.ini"""
        if os.path.exists('config.ini'):
            config = configparser.ConfigParser()
            config.read('config.ini')
            if 'Window' in config:
                try:
                    width = config.getint('Window', 'width')
                    height = config.getint('Window', 'height')
                    if width >= 600 and height >= 500:  # проверка на минимальный размер
                        self.root.geometry(f'{width}x{height}')
                except:
                    pass

    def save_window_size(self):
        """Сохраняет текущий размер окна в config.ini"""
        config = configparser.ConfigParser()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        config['Window'] = {'width': str(width), 'height': str(height)}
        with open('config.ini', 'w') as f:
            config.write(f)

    def on_closing(self):
        """Вызывается при закрытии окна: сохраняет размер и завершает программу"""
        self.save_window_size()
        self.root.destroy()

    def load_data(self):
        csv_file = 'tasks_ege.csv'
        if not os.path.exists(csv_file):
            messagebox.showerror("Ошибка", f"Файл {csv_file} не найден. Добавьте задачи через кнопку 'Добавить задачу'.")
            self.df = pd.DataFrame(columns=['номер', 'тип_задачи', 'текст_задачи', 'изображение', 'выполнено', 'правильный_ответ'])
            return
        try:
            self.df = pd.read_csv(csv_file, sep=',', encoding='utf-8', quotechar='"')
            self.df['выполнено'] = self.df['выполнено'].astype(bool)
            self.df['изображение'] = self.df['изображение'].fillna('')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать CSV:\n{e}")
            self.df = pd.DataFrame(columns=['номер', 'тип_задачи', 'текст_задачи', 'изображение', 'выполнено', 'правильный_ответ'])

    def save_to_csv(self):
        try:
            self.df = self.df.sort_values('номер')
            self.df.to_csv('tasks_ege.csv', sep=',', index=False, encoding='utf-8', quoting=1)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def normalize_ege_answer(self, answer_str):
        if pd.isna(answer_str):
            return ""
        answer_str = str(answer_str).strip()
        if not answer_str:
            return ""
        if ';' in answer_str:
            parts = answer_str.split(';')
            normalized_parts = []
            for part in parts:
                norm_part = self.normalize_single_answer(part.strip())
                if norm_part:
                    normalized_parts.append(norm_part)
            try:
                normalized_parts.sort(key=lambda x: float(x) if self.is_number(x) else x)
            except:
                normalized_parts.sort()
            return ';'.join(normalized_parts)
        return self.normalize_single_answer(answer_str)

    def normalize_single_answer(self, answer_str):
        answer_str = str(answer_str).strip()
        answer_str = re.sub(r'\s+', ' ', answer_str)
        if re.match(r'^\d+/\d+$', answer_str):
            try:
                num, denom = map(int, answer_str.split('/'))
                value = num / denom
                if value.is_integer():
                    return str(int(value))
                return str(round(value, 6)).rstrip('0').rstrip('.')
            except:
                pass
        if '√' in answer_str:
            try:
                if answer_str == '√2':
                    return str(round(math.sqrt(2), 6)).rstrip('0').rstrip('.')
                elif answer_str == '√3':
                    return str(round(math.sqrt(3), 6)).rstrip('0').rstrip('.')
                elif answer_str == '√2/2':
                    return str(round(math.sqrt(2)/2, 6)).rstrip('0').rstrip('.')
                elif answer_str == '√3/2':
                    return str(round(math.sqrt(3)/2, 6)).rstrip('0').rstrip('.')
                elif re.match(r'^√\(?(\d+)\)?$', answer_str):
                    num = int(re.search(r'(\d+)', answer_str).group(1))
                    return str(round(math.sqrt(num), 6)).rstrip('0').rstrip('.')
            except:
                pass
        if 'π' in answer_str:
            try:
                expr = answer_str.replace('π', '*3.141592653589793')
                expr = re.sub(r'(\d)(\*)', r'\1', expr)
                value = eval(expr)
                return str(round(value, 6)).rstrip('0').rstrip('.')
            except:
                pass
        if self.is_number(answer_str):
            try:
                num_str = answer_str.replace(',', '.')
                value = float(num_str)
                if value.is_integer():
                    return str(int(value))
                return str(round(value, 6)).rstrip('0').rstrip('.')
            except:
                pass
        return answer_str.lower()

    def is_number(self, s):
        try:
            s = s.replace(',', '.')
            float(s)
            return True
        except:
            return False

    def create_main_frame(self):
        if hasattr(self, 'task_frame') and self.task_frame is not None:
            self.task_frame.destroy()
        if hasattr(self, 'main_frame') and self.main_frame is not None:
            self.main_frame.destroy()
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill='both', expand=True)

        tk.Label(self.main_frame, text="Тренажер ЕГЭ по математике", font=("Arial", 20, "bold"),
                 bg=self.colors['bg'], fg=self.colors['primary']).pack(pady=20)
        tk.Label(self.main_frame, text="Часть 1 - Профильный уровень", font=("Arial", 12),
                 bg=self.colors['bg'], fg=self.colors['secondary']).pack()

        total = len(self.df)
        completed = len(self.df[self.df['выполнено'] == True])
        percent = (completed/total*100) if total>0 else 0
        tk.Label(self.main_frame, text=f"Прогресс: {completed}/{total} ({percent:.1f}%)",
                 font=("Arial", 14), bg=self.colors['bg'], fg=self.colors['text']).pack(pady=10)
        progress = ttk.Progressbar(self.main_frame, length=500, maximum=100, mode='determinate')
        progress.pack(pady=10)
        progress['value'] = percent

        if total == 0:
            tk.Label(self.main_frame, text="Нет задач. Нажмите 'Добавить задачу'", font=("Arial", 14),
                     bg=self.colors['bg']).pack(pady=50)
        else:
            task_types = sorted(self.df['тип_задачи'].unique())
            btn_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
            btn_frame.pack(pady=20, padx=20, fill='both', expand=True)
            rows, cols = 4, 3
            for i in range(rows):
                btn_frame.grid_rowconfigure(i, weight=1)
            for j in range(cols):
                btn_frame.grid_columnconfigure(j, weight=1)
            for i, t in enumerate(task_types):
                type_tasks = self.df[self.df['тип_задачи'] == t]
                c = len(type_tasks[type_tasks['выполнено'] == True])
                total_c = len(type_tasks)
                p = (c/total_c*100) if total_c>0 else 0
                if p == 100: bg = self.colors['success']
                elif p >= 50: bg = '#FFFACD'
                elif p > 0: bg = '#ADD8E6'
                else: bg = self.colors['light']
                btn = tk.Button(btn_frame, text=f"{t}\n{c}/{total_c}", font=("Arial", 11),
                                bg=bg, height=3, width=15, command=lambda tt=t: self.start_task_type(tt))
                btn.grid(row=i//cols, column=i%cols, padx=5, pady=5, sticky='nsew')

        bottom = tk.Frame(self.main_frame, bg=self.colors['bg'])
        bottom.pack(pady=20)
        tk.Button(bottom, text="Статистика", font=("Arial", 10), bg=self.colors['secondary'], fg='white',
                  command=self.show_statistics).pack(side='left', padx=5)
        tk.Button(bottom, text="Сбросить все", font=("Arial", 10), bg=self.colors['warning'],
                  command=self.reset_all_tasks).pack(side='left', padx=5)
        tk.Button(bottom, text="Добавить задачу", font=("Arial", 10), bg='#98FB98',
                  command=self.add_new_task).pack(side='left', padx=5)
        tk.Button(bottom, text="Удалить задачу", font=("Arial", 10), bg='lightcoral',
                  command=self.delete_task).pack(side='left', padx=5)
        tk.Button(bottom, text="Выход", font=("Arial", 10), command=self.on_closing).pack(side='left', padx=5)

    def start_task_type(self, task_type):
        self.current_task_type = task_type
        self.main_frame.pack_forget()
        self.show_next_task()

    def show_next_task(self):
        tasks = self.df[(self.df['тип_задачи'] == self.current_task_type) & (self.df['выполнено'] == False)]
        if tasks.empty:
            messagebox.showinfo("Все задачи выполнены", f"Все задачи типа '{self.current_task_type}' решены. Возврат в меню.")
            self.back_to_menu()
            return
        self.current_task = tasks.iloc[0]
        self.create_task_frame()

    def create_task_frame(self):
        if hasattr(self, 'task_frame') and self.task_frame is not None:
            self.task_frame.destroy()
        self.task_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.task_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(self.task_frame, bg=self.colors['bg'])
        scrollbar = ttk.Scrollbar(self.task_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(scrollable, text=f"{self.current_task['тип_задачи']} - Задача №{self.current_task['номер']}",
                 font=("Arial", 16, "bold"), bg=self.colors['bg'], fg=self.colors['primary']).pack(pady=10)
        total_type = len(self.df[self.df['тип_задачи'] == self.current_task_type])
        completed_type = len(self.df[(self.df['тип_задачи'] == self.current_task_type) & (self.df['выполнено'] == True)])
        tk.Label(scrollable, text=f"Прогресс: {completed_type}/{total_type}", font=("Arial", 10),
                 bg=self.colors['bg'], fg=self.colors['secondary']).pack()

        text_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        text_frame.pack(fill='x', padx=20, pady=10)
        tk.Label(text_frame, text=self.current_task['текст_задачи'], font=("Arial", 12),
                 wraplength=650, justify='left', bg='white', padx=20, pady=20).pack()

        ans_frame = tk.Frame(scrollable, bg=self.colors['bg'])
        ans_frame.pack(pady=10)
        self.answer_entries = []

        def add_field(value=""):
            f = tk.Frame(ans_frame, bg=self.colors['bg'])
            f.pack(pady=2)
            tk.Label(f, text=f"Ответ {len(self.answer_entries)+1}:", width=8, anchor='e', bg=self.colors['bg']).pack(side='left')
            e = tk.Entry(f, width=40, font=("Arial", 11))
            e.pack(side='left', padx=5)
            if value:
                e.insert(0, value)
            btn_del = tk.Button(f, text="X", font=("Arial", 8), command=lambda: remove_field(f, e))
            btn_del.pack(side='left', padx=2)
            self.answer_entries.append(e)
            if len(self.answer_entries) == 1:
                btn_del.pack_forget()
            return e

        def remove_field(frame, entry):
            if len(self.answer_entries) > 1:
                frame.destroy()
                self.answer_entries.remove(entry)
                for i, en in enumerate(self.answer_entries):
                    en.master.winfo_children()[0].config(text=f"Ответ {i+1}:")
            else:
                messagebox.showwarning("Нельзя удалить", "Должен быть хотя бы один ответ")

        add_field()
        tk.Button(scrollable, text="+ Добавить ещё ответ", font=("Arial", 10),
                  command=lambda: add_field()).pack(pady=5)

        sym_frame = tk.Frame(scrollable, bg=self.colors['bg'])
        sym_frame.pack(pady=5)
        for sym in ['π', '√', '/', ';', 'x²', 'x³', '←', 'Очистить']:
            btn = tk.Button(sym_frame, text=sym, font=("Arial", 10), width=6,
                            command=lambda s=sym: self.insert_to_active(s))
            btn.pack(side='left', padx=2)

        tk.Label(scrollable, text="Введите каждый корень в отдельное поле", font=("Arial", 9),
                 bg=self.colors['bg'], fg='gray').pack(pady=5)

        btn_frame = tk.Frame(scrollable, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Отправить ответ", font=("Arial", 12), bg='lightgreen',
                  command=self.collect_and_check).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Пропустить", font=("Arial", 12), bg=self.colors['light'],
                  command=self.skip_task).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Назад в меню", font=("Arial", 12), bg=self.colors['light'],
                  command=self.back_to_menu).pack(side='left', padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def insert_to_active(self, symbol):
        if not self.answer_entries:
            return
        active = None
        for e in self.answer_entries:
            if e.focus_get() == e:
                active = e
                break
        if active is None:
            active = self.answer_entries[0]
        if symbol == '←':
            cur = active.get()
            active.delete(len(cur)-1, tk.END)
        elif symbol == 'Очистить':
            active.delete(0, tk.END)
        elif symbol == 'x²':
            active.insert(tk.INSERT, '^2')
        elif symbol == 'x³':
            active.insert(tk.INSERT, '^3')
        else:
            active.insert(tk.INSERT, symbol)

    def collect_and_check(self):
        answers = [e.get().strip() for e in self.answer_entries if e.get().strip()]
        if not answers:
            messagebox.showwarning("Пустой ответ", "Введите хотя бы один ответ")
            return
        combined = ';'.join(answers)
        self.check_answer(combined)

    def check_answer(self, user_answer):
        correct = self.current_task['правильный_ответ']
        user_norm = self.normalize_ege_answer(user_answer)
        correct_norm = self.normalize_ege_answer(correct)
        if user_norm == correct_norm:
            self.df.loc[self.df['номер'] == self.current_task['номер'], 'выполнено'] = True
            self.save_to_csv()
            # Вместо диалога – краткое уведомление в заголовке окна (исчезнет через 1 сек)
            original_title = self.root.title()
            self.root.title("✓ Верно! Загружается следующая задача...")
            self.root.after(1000, lambda: self.root.title(original_title))
            # Сразу переходим к следующей задаче
            self.show_next_task()
        else:
            response = messagebox.askretrycancel("Неправильно",
                                                 f"Неверно.\nПравильный ответ: {correct}\n\nПопробовать ещё?")
            if not response:
                self.back_to_menu()

    def skip_task(self):
        """Переходит к следующей нерешённой задаче того же типа, не засчитывая текущую"""
        if not hasattr(self, 'current_task_type'):
            self.back_to_menu()
            return

        # Все нерешённые задачи текущего типа
        unsolved = self.df[(self.df['тип_задачи'] == self.current_task_type) & (self.df['выполнено'] == False)]
        if len(unsolved) == 0:
            messagebox.showinfo("Нет задач", "Нет нерешённых задач. Возврат в меню.")
            self.back_to_menu()
            return

        current_id = self.current_task['номер']
        # Найти индекс текущей задачи в списке unsolved
        try:
            current_index = unsolved[unsolved['номер'] == current_id].index[0]
            indices = unsolved.index.tolist()
            pos = indices.index(current_index)
        except:
            # Если текущей задачи нет в списке (ошибка), берём первую
            next_task = unsolved.iloc[0]
        else:
            # Следующая задача после текущей, если это последняя — берём первую (зацикливание)
            next_task = unsolved.iloc[(pos + 1) % len(unsolved)]

        # Уничтожаем текущее окно задачи
        if hasattr(self, 'task_frame') and self.task_frame is not None:
            self.task_frame.destroy()
            self.task_frame = None

        self.current_task = next_task
        self.create_task_frame()

    def back_to_menu(self):
        if hasattr(self, 'task_frame') and self.task_frame is not None:
            self.task_frame.destroy()
            self.task_frame = None
        self.main_frame.pack(fill='both', expand=True)

    def show_statistics(self):
        total = len(self.df)
        completed = len(self.df[self.df['выполнено'] == True])
        percent = (completed/total*100) if total>0 else 0
        text = f"Всего: {total}\nВыполнено: {completed}\nПроцент: {percent:.1f}%\n\n"
        types = sorted(self.df['тип_задачи'].unique())
        for t in types:
            tt = self.df[self.df['тип_задачи'] == t]
            tc = len(tt[tt['выполнено'] == True])
            tt_c = len(tt)
            tp = (tc/tt_c*100) if tt_c>0 else 0
            bar = '█' * int(15*tp/100) + '░' * (15 - int(15*tp/100))
            text += f"{t:15} {tc:3}/{tt_c:3} {bar} {tp:5.1f}%\n"
        messagebox.showinfo("Статистика", text)

    def reset_all_tasks(self):
        if messagebox.askyesno("Сброс", "Сбросить все задачи?"):
            self.df['выполнено'] = False
            self.save_to_csv()
            if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
                self.main_frame.destroy()
            if hasattr(self, 'task_frame') and self.task_frame is not None:
                self.task_frame.destroy()
            self.create_main_frame()
            messagebox.showinfo("Сброс", "Все задачи сброшены")

    def add_new_task(self):
        win = tk.Toplevel(self.root)
        win.title("Добавить задачу")
        win.geometry("500x450")
        win.configure(bg=self.colors['bg'])
        next_id = self.df['номер'].max() + 1 if len(self.df) > 0 else 1
        entries = {}
        labels = ['тип_задачи', 'текст_задачи', 'правильный_ответ']
        for i, lbl in enumerate(labels):
            tk.Label(win, text=lbl+':', bg=self.colors['bg']).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            e = tk.Entry(win, width=50)
            e.grid(row=i, column=1, padx=5, pady=5)
            entries[lbl] = e
        tk.Label(win, text='изображение (опционально):', bg=self.colors['bg']).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        img_e = tk.Entry(win, width=50)
        img_e.grid(row=3, column=1, padx=5, pady=5)
        def save():
            new = {
                'номер': next_id,
                'тип_задачи': entries['тип_задачи'].get().strip(),
                'текст_задачи': entries['текст_задачи'].get().strip(),
                'правильный_ответ': entries['правильный_ответ'].get().strip(),
                'изображение': img_e.get().strip(),
                'выполнено': False
            }
            if not new['тип_задачи'] or not new['текст_задачи'] or not new['правильный_ответ']:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return
            self.df = pd.concat([self.df, pd.DataFrame([new])], ignore_index=True)
            self.save_to_csv()
            messagebox.showinfo("Успех", f"Задача №{next_id} добавлена")
            win.destroy()
            self.back_to_menu()
            self.create_main_frame()
        tk.Button(win, text="Сохранить", command=save, bg='lightgreen').grid(row=4, column=0, columnspan=2, pady=20)

def main():
    root = tk.Tk()
    app = TaskApp(root)
    root.update_idletasks()
    if not os.path.exists('config.ini'):
        w = root.winfo_width()
        h = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (w // 2)
        y = (root.winfo_screenheight() // 2) - (h // 2)
        root.geometry(f'{w}x{h}+{x}+{y}')
    root.mainloop()

if __name__ == "__main__":
    main()