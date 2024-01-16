import re
import os
import statistics
import time
import tkinter
from PIL import ImageTk, Image
import io
import nltk
from langcodes import Language #Нужно дополнительно устанавливать пакет language_data
from nltk.tokenize import word_tokenize
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud
from langdetect import detect
from langdetect import DetectorFactory
import pyphen
from nltk.corpus import stopwords
from collections import Counter
from docx import Document #python-docx lib
import csv

#Скачивание модуля для фильтрации слов  (если запускаете в первый раз, необходимо его скачать
nltk.download('stopwords')
nltk.download('punkt')
#Решение для обнаружения пакета линуксом
stopwords_path = nltk.data.find('corpora/stopwords.zip')
# print(f"stopwords path is {stopwords_path}")
#Флаг - не используется т.к нет окна для ввода
button_flag = 0
#Флаги для обозначения типа файла при загрузке, переменные для присвоения текста из файла
text_from_csv = ""
csv_flag = 0
text_from_txt = ""
txt_flag = 0
text_from_docx = ""
docx_flag = 0
#Создается пустой лэйбл, для функции смены названия выбранным для обработки файлам
file_label = None
wordcloud_label = None
wordcloud_photo = None
click_count = 0
#Флаг загруженного документа
load_file_label_flag = 0

class Text_analysis:
    #Функция запуска графического интерфейса

    def GUI_start(self):

        root = tk.Tk()

        app_width = 500
        app_height = 780
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = (screen_width / 2) - (app_width / 2)
        y = (screen_height / 2) - (app_height / 2)

        root.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

        root.resizable(width=False, height=False)
        root.title("Анализ текста")

        intro_label = tk.Label(root, text="Анализ текста", font=("Calibri", 20))
        intro_label.pack(padx=10, pady=10)
        description_label = tk.Label(root, text="Для обработки загрузите файл\n(word, csv, txt)", font=("Calibri", 16))
        description_label.pack(padx=10, pady=10)

        #Функция определения формата входящего файла и считывания
        def read_file_contents(file_path):
            global text_from_txt, text_from_docx, text_from_csv, csv_flag, txt_flag, docx_flag
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    rows = [','.join(row) for row in csv_reader if any(row)]
                    text_from_csv = '\n'.join(rows)
                    print(f"ТЕКСТ ИЗ CSV {text_from_csv}")
                    csv_flag = 1
                    print(f"csv_flag {csv_flag}")
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    text_from_txt = txt_file.read()
                    print(f"ТЕКСТ ИЗ TXT {text_from_txt}")
                    txt_flag = 1
                    print(f"txt_flag {txt_flag}")
            elif file_path.endswith('.docx'):
                doc = Document(file_path)
                text_from_docx = '\n'.join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
                print(f"ТЕКСТ ИЗ DOCX {text_from_docx}")
                docx_flag = 1
                print(f"docx_flag {docx_flag}")

        #Функция открытия окна с выбором необходимого для обработки файла
        def open_file_dialog():
            global button_flag, file_label, file_label_text, load_file_label_flag
            try:
                if file_label:
                    file_label.after(1, file_label.destroy())
            except Exception as e:
                print(0)
            #На линукс не работает формат supported files, поэтому добавил каждый тип по отдельности
            file_path = filedialog.askopenfilename(filetypes=[("Supported files", "*.csv;*.txt;*.docx"),("csv", "*.csv"),("txt", "*.txt"),("docx", "*.docx")])
            #Добавляем название формата в общее наименеование в лэйбле, который отражает выбранный файл
            if file_path:
                try:
                    if file_path.endswith('.csv'):
                        particle = 'csv'
                    elif file_path.endswith('.docx'):
                        particle = 'docx'
                    elif file_path.endswith('.txt'):
                        particle = 'txt'
                    else:
                        print(0)
                except Exception as e:
                    print("Error in claiming particle in file_path")
                # button_flag = 1
                # print("Выбранный файл:", file_path)

                # ограничение текста в лэйбла выбранного файла
                max_chars = 50
                name = os.path.basename(file_path)
                if len(name) > max_chars:
                    name = name[:max_chars]+"..."

                file_label = tk.Label(root, text=f"Выбран файл {particle}:\n{name}", font=("Calibri", 12), justify='center')
                file_label.config(bg="yellow", fg="blue")
                file_label.pack(padx=20, pady=10, after=description_label)
                read_file_contents(file_path)
                load_file_label_flag = 1
                print(f"load_file_label_flag in loading def {load_file_label_flag}")
                check_text()

        def delete_file():
            global load_file_label_flag
            global csv_flag, txt_flag, docx_flag, load_file_label_flag
            print(f"load_file_label_flag in delete file {load_file_label_flag}")
            try:
                file_label.destroy()
                if not file_label.winfo_exists():
                    print("not exists")
                if file_label.winfo_exists():
                    print('exists')

            except Exception as e:
                # print('01')
                pass
            #Очищаем метки, чтобы при обработке не было захвата текста из загрузок
            csv_flag = 0
            txt_flag = 0
            docx_flag = 0
            load_file_label_flag = 0
            check_text()

        #Функция открытия окна ошибки при пустом вводе
        def error_window():
            global graph_window
            try:
                result_window.destroy()
            except Exception as e:
                pass
            try:
                plt.close()
            except Exception as e:
                pass
            try:
                graph_window.destroy()
            except Exception as e:
                pass
            er_window = tk.Toplevel(root) #Помещает ошибку поверх главного окна, что делает невозможным работу до тех пор пока ошибка не будет закрыта
            app_width = 400
            app_height = 200
            screen_width = er_window.winfo_screenwidth()
            screen_height = er_window.winfo_screenheight()

            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)

            er_window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            er_window.grab_set()
            er_window.title('Error')
            # er_window.geometry("400x200")
            err_label = tk.Label(er_window, text="ОШИБКА",
                                 font=("Calibri", 14))
            err_label_1 = tk.Label(er_window, text=" Слишком мало текста или его нет\n Пожалуйста, повторите попытку",
                                 font=("Calibri", 12))
            err_label.pack(padx=10, pady=10)
            err_label_1.pack(padx=10, pady=10)
            def shutdown():
                er_window.destroy()
            ok_button = tk.Button(er_window, text='Ок', command=shutdown, width=20, font='Calibri, 14')
            ok_button.pack(padx=10,pady=10)

        # Функция открытия окна результата
        def opening_the_text():
            global result_window, button_flag, docx_flag, csv_flag, txt_flag
            #Закрытие окон если они были ранее открыты
            try:
                plt.close('all')
            except Exception as e:
                print(f"Failed to close wordcloud")
                pass
            try:
                result_window.destroy()
            except Exception as e:
                print(f"Failed to close result_window")
                pass
            try:
                graph_window.destroy()
            except Exception as e:
                print(f"Failed to close graph_window")
                pass
            #Предобработка текста
            try:
                #Флаг и загрузка текста из окна текста entry
                if button_flag == 0:
                    entered_text = entry.get("1.0",tk.END)
                    val_words = word_tokenize(entered_text)
                    if entered_text and len(val_words) > 3:
                        text = entered_text.lower()

                if csv_flag == 1:
                    entered_text = text_from_csv
                    val_words = word_tokenize(entered_text)
                    if entered_text and len(val_words) > 3:
                        text = entered_text.lower()
                if docx_flag == 1:
                    entered_text = text_from_docx
                    val_words = word_tokenize(entered_text)
                    if entered_text and len(val_words) > 3:
                        text = entered_text.lower()
                if txt_flag == 1:
                    entered_text = text_from_txt
                    val_words = word_tokenize(entered_text)
                    if entered_text and len(val_words) > 3:
                        text = entered_text.lower()
            except ValueError as v:
                error_window()

            #Функция определения языка для последующей фильтрации слабозначимых слов
            def detect_lang_for_stopwords_1(text):
                try:
                    language = detect(text)
                    #Добавить функцию которая бы определяла несколько языков сразу (разбивка по блокам, чем больше слов,
                    # тем на большее количество блоков разбивается текст, далее поблочный анализ)
                    # print(f"lang is {language}")
                    lang = Language.get(language)
                    en_full_language_name = lang.display_name('en')
                    full_language_name = en_full_language_name.lower()
                    print(f"Language: {full_language_name}")
                    return full_language_name
                except Exception as e:
                    print(f"Error: {e}")
                    return "Language detection for stopwords failed"
            try:
                words = re.findall(r'\w+', text)
            except Exception as error:
                error_window()
            try:
                stop_words = set(stopwords.words(f"{detect_lang_for_stopwords_1(text)}"))  # Наименование пакетов может различаться (в линукс наименование пакетов идет с маленькой буквы)
            except Exception as e:
                print(f"no stopwords")
                #lang
                stop_words = set(stopwords.words("english"))
            # stop_words = set(stopwords.words(f"{detect_lang_for_stopwords_1(text)}"))  # Наименование пакетов может различаться (в линукс наименование пакетов идет с маленькой буквы)
            filtered_words = [word for word in words if word.lower() not in stop_words]
            print(f"old filtered words with nums {filtered_words}")
            pattern = re.compile(r'\d')
            filtered_words = [word for word in filtered_words if not pattern.search(word)]
            print(f"new filtered words list {filtered_words}")

            #Создаем окно с результатами
            result_window = tk.Tk()
            result_window.title("Результат")

            app_width = 500
            app_height = 600
            screen_width = result_window.winfo_screenwidth()
            screen_height = result_window.winfo_screenheight()

            x = (screen_width / 2) - (app_width / 2) + 400
            y = (screen_height / 2) - (app_height / 2)

            result_window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

            intro_label = tk.Label(result_window, text="Результат", font=("Calibri", 20))
            intro_label.pack(padx=10, pady=10)
            word_box_descript = tk.Label(result_window, text="Обработанный список слов и количество повторений в файле")
            word_box_descript.pack(pady=1)
            word_combobox = tk.Listbox(result_window, selectmode=tk.EXTENDED, width=60, height=10)
            word_combobox.pack(pady=1)

            #Функция для получения частоты слов
            def get_word_frequency():
                global text_parts, word_freq, word_list
                # Разбиение текста на 10 частей
                words = word_tokenize(text)
                text_parts = []
                part_size = len(words) // 10
                remainder = len(words) % 10 #Остаток
                try:
                    for i in range(0, len(words) - remainder, part_size):
                        if re.search("\d",words[i]):
                            pass
                        else:
                            text_parts.append(' '.join(words[i:i + part_size]))
                    # print(words)
                    if remainder > 0:
                        text_parts[-1] += ' '.join(words[-remainder:])
                    word_freq = dict(Counter(filtered_words))
                    # Заполнение listbox словами и их частотами
                    sorted_word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1], reverse=True))
                    word_list = list(sorted_word_freq.keys())
                    word_combobox.delete(0, tk.END)
                    i = 0
                    for word in word_list:
                        i += 1
                        word_combobox.insert(tk.END, f"{i}) {word} ({word_freq[word]})")
                except ValueError as v:
                    error_window()
                    print("Value Error in get_word_frequency function")
            get_word_frequency()

            #Функция графика относительных частот

            def plot_word_usage():
                global click_count
                # Ограничения на открытие графиков, чтобы нельзя было ими спамить
                # click_count += 1
                # if click_count == 5:
                #     print('Исчерпан лимит')
                #     return
                global graph_window
                selected_items = word_combobox.curselection()
                fig, ax = plt.subplots(figsize=(8, 5))

                for idx in selected_items:
                    selected_item = word_list[int(idx)]
                    word_part_freq = []
                    for part in text_parts:
                        words = word_tokenize(part)
                        total_words = len(words)
                        word_count = words.count(selected_item)
                        relative_freq = word_count / total_words if total_words > 0 else 0
                        word_part_freq.append(relative_freq)

                    ax.plot(range(1, len(text_parts)+1), word_part_freq, marker='o', linestyle='-',
                            label=f'{selected_item}')
                    for i, freq in enumerate(word_part_freq, start=1):
                        ax.text(i, freq, f'{freq:.4f}', ha='center', va='bottom', fontsize=8)
                ax.set_xlabel('Части текста')
                ax.set_ylabel('Относительная частота слова')
                ax.set_title(f'Относительная частота слов в частях текста')
                ax.legend()
                graph_window = tk.Toplevel(result_window)
                graph_window.title("График")
                ax.set_xticks(range(1, len(text_parts)+1 ))
                ax.set_ylim(0)
                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            select_button_for_graph = tk.Button(result_window, text="Построить график", command=plot_word_usage, )
            select_button_for_graph.pack(padx=10, pady=10)

            #Начало работы функции по анализу текста
            def text_analysis():
                global filtered_words
                #Повторная функция определения языка и стопслов (необходимо убрать\совместить с предыдущей функцией определения языка)
                def detect_language(text):
                    try:
                        language = detect(text)
                        lang = Language.get(language)
                        full_language_name = lang.display_name(lang)
                        full_language_name = full_language_name.lower()
                        # print(f"language code is {lang}")
                        # print(f"language is - {language}")
                        # print(f"Full language name is - {full_language_name}")
                        return language
                    except Exception as e:
                        print(f"Error: {e}")
                        return "Language detection failed"

                #По умолчанию пока что стоит английский для стопслов
                def detect_lang_for_stopwords(text):
                    try:
                        language = detect(text)
                        lang = Language.get(language)
                        en_full_language_name = lang.display_name('en')
                        full_language_name = en_full_language_name.lower()
                        print(full_language_name)
                        return full_language_name
                    except Exception as e:
                        print(f"Error: {e}")
                        return "Language detection for stopwords failed"
                words = re.findall(r'\w+', text)
                # print(f"Все слова в тексте: {words}")
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
                # print(f"Предложения в тексте: {sentences}")
                dic_en = pyphen.Pyphen(lang=f'{detect_language(text)}')
                lang_for_stop = detect_lang_for_stopwords(text)
                # print(f"lang for stop var - {lang_for_stop}")
                try:
                    stop_words = set(stopwords.words(f"{lang_for_stop}"))  # Наименование пакетов может различаться (в линукс наименование пакетов идет с маленькой буквы)
                except Exception as e:
                    print(f"no stopwords")
                    stop_words = set(stopwords.words("english"))
                filtered_words = [word for word in words if word.lower() not in stop_words]
                pattern = re.compile(r'\d')
                filtered_words = [word for word in filtered_words if not pattern.search(word)]

                total_words = len(filtered_words)
                total_not_filtered_words = len(words)
                words_freq = Counter(filtered_words)
                number_of_top_common_words = 10
                most_common_words = words_freq.most_common(number_of_top_common_words)
                words_frequency = words_freq.most_common()
                average_words_per_sentence = total_not_filtered_words / len(sentences)

                # Индекс читаемости 1
                def FKrt_index():
                    word_count = len(words)
                    sentence_count = len(sentences)
                    total_syllables = sum(len(dic_en.inserted(word).split('-')) for word in words)
                    index = 0.39 * (word_count / sentence_count) + 11.8 * (total_syllables / word_count) - 15.59
                    print('индекс FKRT',index)
                    return index
                fkrt_index = FKrt_index()

                # Индекс читаемости 2
                def gunning_fog_index():
                    word_count = len(words)
                    sentence_count = len(sentences)
                    syllables_list = [dic_en.inserted(word).split('-') for word in words]
                    complex_word_count = 0
                    for word_syllables in syllables_list:
                        word = ''.join(word_syllables)
                        if len(word_syllables) > 3:
                            complex_word_count += 1
                    # print('Количество сложных слов (более 3 слогов):', complex_word_count)
                    fog_index = 0.4 * ((word_count / sentence_count) + 100 * (complex_word_count / word_count))
                    print('Gunning fog index', fog_index)
                    return fog_index
                gunning = gunning_fog_index()

                # Индекс читаемости 3
                def SMOG_index():
                    sentence_count = len(sentences)
                    syllables_list = [dic_en.inserted(word).split('-') for word in words]
                    complex_word_count = 0  # aka polysyllables
                    for word_syllables in syllables_list:
                        word = ''.join(word_syllables)
                        if len(word_syllables) > 3:
                            complex_word_count += 1
                    smog_ind = 1.0430 * (30 * (complex_word_count / sentence_count)) ** 0.5 + 3.1291
                    print('SMOG index',smog_ind)
                    return smog_ind

                # Индекс читаемости 4
                smog = SMOG_index()
                def Coleman_Liau_index():
                    character_count = sum(len(word) for word in words)
                    sentences = text.split('. ')
                    sentences_count = len(sentences)
                    # Среднее количество символов в 100 словах
                    l = (character_count / total_not_filtered_words) * 100
                    # Среднее количество предложений на 100 слов
                    s = (sentences_count / total_not_filtered_words) * 100
                    collind = 0.0588 * l - 0.296 * s - 15.8
                    print('Coleman_Liau_index: ', collind)
                    return collind

                coleman = Coleman_Liau_index()

                # Индекс читаемости 5
                def ARI_index():
                    character_count = sum(len(word) for word in words)
                    sentences = text.split('. ')
                    sentences_count = len(sentences)
                    # Среднее количество символов в 100 словах
                    avg_char_per_wrd = (character_count / total_not_filtered_words) * 100
                    # Среднее количество предложений на 100 слов
                    avg_wrd_per_sentence = (total_not_filtered_words / sentences_count) * 100
                    # print(average_words_per_sentence)
                    # print('avg_wrd_per_sentence', avg_wrd_per_sentence)
                    ari_index = 4.71 * (character_count / total_not_filtered_words) + 0.5 * (total_not_filtered_words / sentences_count) - 21.43
                    print('ARI IND', ari_index)
                    return ari_index

                ariindex = ARI_index()

                # Индекс лексической плотностии - считается как отношение количества уникальных слов к общему количеству слов
                def lexical_density_index():  # Индекс лексической плотности
                    word_count = len(words)
                    unique_words = set(words)
                    unique_words_count = len(unique_words)
                    ldi = unique_words_count / word_count
                    print(f"lexical_density_index: {ldi}")
                    return ldi

                lexical_density_index()
                avg_index = (fkrt_index + gunning + smog + coleman + ariindex) / 5
                print(f"Avg_index: {avg_index}")
                median_ind = (statistics.median([fkrt_index, gunning, smog, coleman, ariindex]))
                print(f"Median_index: {median_ind}")

                # Создание отчета в txt формате
                def create_report():
                    curr_directory = os.getcwd()
                    DetectorFactory.seed = 0
                    try:
                        report_folder = os.path.join(curr_directory, "reports")
                        if not os.path.exists(report_folder):
                            os.mkdir(report_folder)
                        existing_reports = os.listdir(report_folder)
                        rep_counter = 1
                        for file in existing_reports:
                            if file.startswith("report_"):
                                part_name = file.split("_")
                                file_num = int(part_name[1].split(".")[0])
                                rep_counter = max(rep_counter, file_num + 1)
                        report_file_name = os.path.join(report_folder, f"report_{rep_counter}.txt")
                        with open(report_file_name, 'w') as report:
                            report.write(" 1 ")
                            print(f'report_file_name {report_file_name}')
                            report.write('Показатели с NLTK\n')
                            report.write('===========================================\n')
                            report.write('Общее количество слов : ')
                            report.write(str(f"{total_words}\n\n"))
                            report.write('Частота: \n')
                            report_wrd_cnt = 0
                            num_cntr = 0
                            for word, count in words_frequency:
                                num_cntr += 1
                                report.write(f"{num_cntr}) {word} - {count}; ")
                                report_wrd_cnt += 1
                                if report_wrd_cnt == 3:
                                    report.write("\n")
                                    report_wrd_cnt = 0
                            report.write("\n\n")
                            report_wrd_cnt = 0
                            num_cntr = 0
                            # report.write(str(f"{words_freq}\n"))
                            report.write(f'Частоупотребляемые слова (топ {number_of_top_common_words}):\n')
                            for word, count in most_common_words:
                                num_cntr += 1
                                report.write(f"{num_cntr}) {word} - {count}; ")
                                report_wrd_cnt += 1
                                if report_wrd_cnt == 3:
                                    report.write("\n")
                                    report_wrd_cnt = 0
                            report.write("\n\n")
                            report.write('Индексы читаемости: \n')

                            try:
                                report.write(str(f"1) Flesch–Kincaid index: {round(fkrt_index, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"1) Flesch–Kincaid index: n/a \n"))
                                pass
                            try:
                                report.write(str(f"2) Gunning fog index: {round(gunning, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"2) Gunning fog index: n/a \n"))
                                pass
                            try:
                                report.write(str(f"3) SMOG index: {round(smog, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"3) SMOG index: n/a \n"))
                                pass
                            try:
                                report.write(str(f"4) Coleman_Liau_index: {round(coleman, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"4) Coleman_Liau_index: n/a \n"))
                                pass
                            try:
                                report.write(str(f"5) ARI_index: {round(ariindex, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"5) ARI_index: n/a \n"))
                                pass
                            report.write("\n")
                            try:
                                report.write(str(f"Среднее значение по всем индексам: {round(avg_index, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"Среднее значение по всем индексам: n/a \n"))
                                pass
                            try:
                                report.write(str(f"Медианное значение по всем индексам: {round(median_ind, 3)}\n"))
                            except Exception as e:
                                report.write(str(f"Медианное значение по всем индексам: n/a \n"))
                                pass
                            try:
                                report.write(f"Лексическая плотность: {round(lexical_density_index(), 3)}\n")
                            except Exception as e:
                                report.write(f"Лексическая плотность: n/a\n")
                            try:
                                report.write(
                                    f"Среднее количество слов за предложение: {round(average_words_per_sentence, 3)}\n")
                            except Exception as e:
                                report.write(f"Среднее количество слов за предложение: n/a \n")
                                pass
                            report.write('===========================================')
                            return

                    except Exception as e:
                        print('Error - cannot create a report file')
                        pass

                create_report()

                #Нужно вставить wordcloud в окно tkinter
                #Функция вордклауд
                def generate_wordcloud():
                    global result_window, wordcloud_label
                    word_freq = dict(Counter(filtered_words))

                    wordcloud = WordCloud(width=1200, height=600, background_color='white',
                                          include_numbers=True, prefer_horizontal=True, min_font_size=8,
                                          font_step=2).generate_from_frequencies(
                        word_freq)

                    plt.figure(figsize=(10, 5))
                    # plt.imshow(wordcloud, interpolation='bilinear')
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis('off')
                    plt.tight_layout(pad=0)
                    plt.show()

                wordcloud_photo = 0
                #Попытка вставить водклауд в окно (почему то стирает значение image,
                # хотя в общем метод рабочий)
                def generate_wordcloud_tk():
                    global result_window, wordcloud_label, wordcloud_photo
                    word_freq = dict(Counter(filtered_words))

                    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)

                    # Сохранение изображения облака слов в память
                    image_stream = io.BytesIO()
                    wordcloud.to_image().save(image_stream, format='PNG')
                    image_stream.seek(0)

                    root1 = tk.Tk()
                    root1.title('1')

                    # Преобразование изображения в формат, подходящий для Tkinter
                    image = Image.open(image_stream)
                    wordcloud_photo = ImageTk.PhotoImage(image)

                    # time.sleep(1)
                    # Отображение изображения в окне Tkinter
                    label_wc = tk.Label(root1, image=wordcloud_photo)
                    label_wc.pack()

                    return wordcloud_photo

                #Лэйблы показателей обработки текста
                name_label = tk.Label(result_window, text="Индексы читаемости:")
                label_1 = tk.Label(result_window, text=f"1) Flesch–Kincaid index: {round(fkrt_index, 3)}\n "
                                                       f"2) Gunning fog index: {round(gunning, 3)}\n "
                                                       f"3) SMOG index: {round(smog, 3)}\n "
                                                       f"4) Coleman_Liau_index: {round(coleman, 3)}\n "
                                                       f"5) ARI_index: {round(ariindex, 3)}\n ", justify='left')

                label_2 = tk.Label(result_window, text=f"Среднее значение по всем индексам: {round(avg_index, 3)}\n "
                                                       f"Медианное значение по всем индексам: {round(median_ind, 3)}\n "
                                                       f"Лексическая плотность: {round(lexical_density_index(), 3)}\n "
                                                       f"Среднее количество слов за предложение: {round(average_words_per_sentence, 3)}\n", justify='left')
                name_label.pack(padx=10,pady=1)
                label_1.pack(padx=10, pady=1)
                label_2.pack(padx=10, pady=1)

                exit_res_window = tk.Button(result_window, text="Закрыть окно результатов", command=exit_result, width=30, background='#C42B1C', fg='white')
                exit_res_window.pack(padx=20, pady=10)
                exit_button_rw = tk.Button(result_window, text="Завершение работы", command=exit_program_rw, width=30, background='#C42B1C', fg='white')
                exit_button_rw.pack(padx=20, pady=10)

                # generate_wordcloud_tk()
                generate_wordcloud()

            text_analysis()
            return

        er_window = None

        def clear_text():
            entry.delete("1.0", tk.END)
            check_text()

        def check_text():
            global load_file_label_flag
            text_content = entry.get('1.0', tk.END).strip()
            label_content = entry.get("1.0", tk.END).strip()

            print(label_content)
            print(f"load_file_label_flag in check text {load_file_label_flag}")

            if text_content:
                print(f"is text content ")
            if not text_content:
                print( f" not text content")


            try:
                if text_content and load_file_label_flag == 1:
                    select_button.config(state=tk.DISABLED)
                print("01 check text")
            except Exception as e:
                print("01 check text err")
                pass
            try:
                if not text_content and load_file_label_flag == 1:
                    select_button.config(state=tk.NORMAL)
                print("02 check text")
                pass
            except Exception as e:
                print("02 check text err")
            try:
                if text_content and load_file_label_flag == 0:
                    select_button.config(state=tk.NORMAL)
                print("03 check text")
                pass
            except Exception as e:
                print("03 check text err")
            try:
                if not text_content and load_file_label_flag == 0:
                    select_button.config(state=tk.DISABLED)
                print("04 check text")
                pass
            except Exception as e:
                print("04 check text err")

        def exit_result():
            global result_window, exit_confirm_window

            try:
                result_window.destroy()
            except Exception as e:
                print(f"Failed to close result_window (exit_confirm)")
                pass
            try:
                plt.close('all')
            except Exception as e:
                print(f"Failed to close graph (exit_confirm)")
                pass
            try:
                graph_window.destroy()
            except Exception as e:
                print(f"Failed to close graph_window (exit_confirm)")
                pass
            try:
                exit_confirm_window.destroy()
            except Exception as e:
                print(f"Failed to close exit_confirm window")

        #Окно с подтверждением выхода
        def exit_program_rw():
            global result_window

            exit_confirm_window = tk.Toplevel(result_window)
            frame1 = tk.Frame(exit_confirm_window)

            app_width = 480
            app_height = 240
            screen_width = exit_confirm_window.winfo_screenwidth()
            screen_height = exit_confirm_window.winfo_screenheight()

            x = (screen_width / 2) - (app_width / 2)
            y = (screen_height / 2) - (app_height / 2)

            exit_confirm_window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
            exit_confirm_window.title('Выход')

            inf_l = tk.Label(frame1, text="Подтверждение", font=("Calibri", 14))
            sure_to_cls = tk.Label(exit_confirm_window, text=" Вы уверены, что хотите завершить программу ?",
                                 font=("Calibri", 16))
            inf_l.pack(padx=10, pady=10)
            sure_to_cls.pack(padx=10, pady=10)
            frame1.pack(padx=10, pady=10)
            def destroy():
                try:
                    root.destroy()
                except Exception as e:
                    print(f"Failed to close root (exit_confirm)")
                    pass
                try:
                    result_window.destroy()
                except Exception as e:
                    print(f"Failed to close result_window (exit_confirm)")
                    pass
                try:
                    plt.close('all')
                except Exception as e:
                    print(f"Failed to close graph (exit_confirm)")
                    pass
                try:
                    graph_window.destroy()
                except Exception as e:
                    print(f"Failed to close graph_window (exit_confirm)")
                    pass
                try:
                    exit_confirm_window.destroy()
                except Exception as e:
                    print(f"Failed to close exit_confirm window")
            def win_destroy():
                close_exit_window = exit_confirm_window.destroy()
            y_button = tk.Button(exit_confirm_window, text='Да', command=destroy, width=20)
            y_button.pack(padx=20, pady=10)
            n_button = tk.Button(exit_confirm_window, text='Нет', command=win_destroy, width=20)
            n_button.pack(padx=20, pady=10)

        #Функция закрытия окон для главного окна
        def exit_program_root():

            try:
                root.destroy()
            except Exception as e:
                print(f"Failed to close root")
                pass
            try:
                result_window.destroy()
            except Exception as e:
                print(f"Failed to close result_window")
                pass
            try:
                er_window.destroy()
            except Exception as e:
                print(f"Failed to close error_window")
                pass
            try:
                plt.close()
            except Exception as e:
                print(f"Failed to close graph")
                pass
            try:
                graph_window.destroy()
            except Exception as e:
                print(f"Failed to close graph_window")
                pass

        # Окно для текста

        entry = tk.Text(root, width=50, height=10)
        entry.pack(pady=10)
        entry.bind("<KeyRelease>", lambda event: check_text())

        text_delete_button = tk.Button(root, text='Удалить содержимое', command=clear_text, width= 25, font=("Calibri", 14))
        text_delete_button.pack(padx=10, pady=10)
        select_button = tk.Button(root, text="Обработать текст", command=opening_the_text, width= 25, font=("Calibri", 14))
        # select_button.config(state=tk.DISABLED)
        select_button.pack(padx=10, pady=10)
        upload_button = tk.Button(root, text="Выбрать файл", command=open_file_dialog, width= 25, font=("Calibri", 14))
        upload_button.pack(padx=10, pady=10)
        delete_file_button = tk.Button(root, text="Удалить файл", command=delete_file, width = 25, font=("Calibri", 14))
        delete_file_button.pack(padx=10, pady=10)
        upload_button.pack(padx=10, pady=10)
        # Показываем кнопку "завершение работы"
        exit_button = tk.Button(root, text="Завершение работы", command=exit_program_root, width= 25, background='#C42B1C', font=("Calibri", 14), fg='white')
        exit_button.pack(padx=20, pady=40)
        root.mainloop()

obj_text_an = Text_analysis()
obj_text_an.GUI_start()
