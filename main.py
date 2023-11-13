import re
import os
import uuid
import statistics
import nltk
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
from langdetect import detect
from langdetect import detect_langs
import langid #альтернатива langdetect
from langdetect import DetectorFactory
import pyphen
from nltk.corpus import stopwords
from collections import Counter
from textstat import flesch_reading_ease
# nltk.download('stopwords')
#
# stopwords_path = nltk.data.find('corpora/stopwords.zip')
# print(f"stopwords path is {stopwords_path}")


class Text_analysis:
    # нужно делать проверку каждого слова на принадлежность к языку с помощью комплексного сравнения (берем по 3-4 слова проводим анализ по каждому, потому по перебору, потом
    # берем среднюю и присваиваем итоговое значение языка слову
    # Установка списков языков
    def __init__(self):

        curr_directory = os.getcwd()
        DetectorFactory.seed = 0
        # detect.set_languages
        def opening_the_text():
            global text
            global text_file_name
            try:
                text_file_name = 'x en.txt'
                text_folder = os.path.join(curr_directory, 'Text_examples')
                text_file_directory_and_name = os.path.join(text_folder, text_file_name)
                #Открытие временного тхт (нужно заменить на 1) либо автоматический забор текста по юрл , либо окошком с возможностью загрузки текста
                with open(text_file_directory_and_name, 'r') as file:
                    text = file.read()
            except Exception as e:
                print('Cannot open the text')
        opening_the_text()

        # Создание отчета
        def create_report():
            try:
                global report_file_name
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
                    report.write(" ")
            except Exception as e:
                print('Error - cannot create a report file')
                pass
        create_report()
        report_file = 'report.txt'
        dic_ru = pyphen.Pyphen(lang='ru')
        dic_en = pyphen.Pyphen(lang='en')
        words = re.findall(r'\w+', text)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s',text)
        #Использование фильтрации частиц, артиклей, предлогов с помощью nltk
        stop_words = set(stopwords.words('english')) #Наименование пакетов может различаться (в линукс наименование пакетов идет с маленькой буквы)
        filtered_words = [word for word in words if word.lower() not in stop_words]
        #Реализация скрипта с фильтрацией через NLTK
        def NLTK_method():
            total_words = len(filtered_words)
            total_not_filtered_words = len(words)
            words_freq = Counter(filtered_words)
            # print('2',words_freq)
            number_of_top_common_words = 10
            most_common_words = words_freq.most_common(number_of_top_common_words)
            words_frequency = words_freq.most_common()
            # print('1', words_frequency)
            #Тесты Флеша–Кинкейда на читаемость
            readability_score = flesch_reading_ease(text)
            average_words_per_sentence = total_not_filtered_words / len(sentences)
            # print(readability_score,type(readability_score))
            def FKrt_index():
                word_count = len(words)
                # print("Количество слов", word_count)
                sentence_count = len(sentences)
                # print("Количество предложений", sentence_count)
                # print("Все слова, которые употребляются в источнике", words)
                total_syllables = sum(len(dic_en.inserted(word).split('-')) for word in words)
                # print('Общее количество слогов',total_syllables)
                index = 0.39 * (word_count / sentence_count) + 11.8 * (total_syllables / word_count) - 15.59
                # print('индекс',index)
                return index
            fkrt_index = FKrt_index()
            # def difficulty_determination(index):
            #     if index > 100:
            #         result = 'Уровень сложности текста - за рамками теста, слишком легкий'
            #     elif (90 < index) and (index < 100):
            #         result = 'Уровень сложности текста - 5 класс \n(Very easy to read. Easily understood by an average 11-year-old student)'
            #     elif (80 < index) and (index < 90):
            #         result = 'Уровень сложности текста - 6 класс \n(Easy to read. Conversational English for consumers)'
            #     elif (70 < index) and (index < 80):
            #         result = 'Уровень сложности текста - 7 класс \n(Fairly easy to read)'
            #     elif (60 < index) and (index < 70):
            #         result = 'Уровень сложности текста - 8-9 класс \n(Plain English. Easily understood by 13- to 15-year-old students)'
            #     elif (50 < index) and (index < 60):
            #         result = 'Уровень сложности текста - 10-11 класс \n(Fairly difficult to read)'
            #     elif (30 < index) and (index < 50):
            #         result = 'Уровень сложности текста - Колледж \n(Difficult to read)'
            #     elif (10 < index) and (index < 30):
            #         result = 'Уровень сложности текста - Выпускник колледжа \n(Very difficult to read. Best understood by university graduates)'
            #     elif index < 10:
            #         result = 'Уровень сложности текста - Профессиональный \n(Extremely difficult to read. Best understood by university graduates)'
            #     return result
            # difficulty = difficulty_determination(readability_score)
            def gunning_fog_index():
                # Do not include proper nouns, familiar jargon, or compound words. Do not include common suffixes (such as -es, -ed, or -ing) as a syllable (информация требует проверки);
                word_count = len(words)
                sentence_count = len(sentences)
                syllables_list = [dic_en.inserted(word).split('-') for word in words]
                #Счет слогов
                complex_word_count = 0
                for word_syllables in syllables_list:
                    word = ''.join(word_syllables)
                    if len(word_syllables) > 3:
                        complex_word_count += 1
                # print('Количество сложных слов (более 3 слогов):', complex_word_count)
                fog_index = 0.4 * ((word_count / sentence_count) + 100 * (complex_word_count / word_count))
                # print('Gunning fog index', fog_index)
                return fog_index
            gunning= gunning_fog_index()
            def SMOG_index():
                sentence_count = len(sentences)
                syllables_list = [dic_en.inserted(word).split('-') for word in words]
                complex_word_count = 0 #aka polysyllables
                for word_syllables in syllables_list:
                    word = ''.join(word_syllables)
                    if len(word_syllables) > 3:
                        complex_word_count += 1
                smog_ind = 1.0430 * (30 * (complex_word_count / sentence_count)) ** 0.5 + 3.1291
                # print('SMOG index',smog_ind)
                return smog_ind
            smog = SMOG_index()
            def Coleman_Liau_index():
                character_count = sum(len(word) for word in words)
                # print('char count', character_count)
                sentences = text.split('. ')
                # print('tot words', total_not_filtered_words)
                sentences_count = len(sentences)
                # print('sent count',sentences_count)
                #Среднее количество символов в 100 словах
                l = (character_count/ total_not_filtered_words) * 100
                # print('l', l)
                #Среднее количество предложений на 100 слов
                s = (sentences_count / total_not_filtered_words) * 100
                # print('s', s)
                collind = 0.0588 * l - 0.296 * s - 15.8
                # print('Coleman_Liau_index: ', collind)
                return collind
            coleman = Coleman_Liau_index()
            def ARI_index():
                character_count = sum(len(word) for word in words)
                # print('char count',character_count)
                sentences = text.split('. ')
                sentences_count = len(sentences)
                # print('sent count', sentences_count)
                # Среднее количество символов в 100 словах
                avg_char_per_wrd = (character_count / total_not_filtered_words) * 100
                # print('avg_char_per_wrd', avg_char_per_wrd)
                # Среднее количество предложений на 100 слов
                avg_wrd_per_sentence = (total_not_filtered_words / sentences_count) * 100
                # print(average_words_per_sentence)
                # print('avg_wrd_per_sentence', avg_wrd_per_sentence)
                ari_index = 4.71 * (character_count / total_not_filtered_words) + 0.5 * (total_not_filtered_words / sentences_count) - 21.43
                # print('ARI IND', ari_index)
                return ari_index
            ariindex = ARI_index()
            #Индекс лексической плотностии - считается как отношение количества уникальных слов к общему количеству слов
            def lexical_density_index(): #Индекс лексической плотности
                word_count = len(words)
                unique_words = set(words)
                unique_words_count = len(unique_words)
                # print(unique_words_count)
                # print(word_count)
                # print(f'unique words {unique_words}')
                ldi = unique_words_count / word_count
                # print(f"ldi {ldi}")

                return ldi
            lexical_density_index()
            

            #Среднее и медиана по всем индексам
            avg_index = (fkrt_index + gunning + smog + coleman + ariindex)/5
            median_ind = (statistics.median([fkrt_index, gunning, smog, coleman, ariindex]))
            with open(report_file_name, 'w') as report:
                def report_creation():
                    report.write('===========================================\n')
                    report.write(f"{text_file_name}\n")
                    report.write('Показатели с NLTK\n')
                    report.write('===========================================\n')
                    report.write('Общее количество слов : ')
                    report.write(str(f"{total_words}\n\n"))
                    report.write('Частота: \n')
                    report_wrd_cnt = 0
                    num_cntr = 0
                    for word, count in words_frequency:
                        num_cntr +=1
                        report.write(f"{num_cntr}) {word} - {count}; ")
                        report_wrd_cnt +=1
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
                    # Старый, библотечный метод Flesch-Kincaid
                    # try:
                    #     report.write(str(f"1) Flesch–Kincaid readability tests old: {round(readability_score, 3)}\n"))
                    # except Exception as e:
                    #     report.write(str(f"1) Flesch–Kincaid readability tests old: n/a \n"))
                    #     pass
                    # try:
                    #     report.write(f"Интерпретация сложности old: {difficulty}\n")
                    # except Exception as e:
                    #     report.write(f"Интерпретация сложности old: n/a \n")
                    #     pass
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
                    #Нужно скорректировать индекс 1 и 5 (1 пересчитать, библиотека верно его считает, но выводит не в нужной шкале)
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
                        report.write(f"Среднее количество слов за предложение: {round(average_words_per_sentence, 3)}\n")
                    except Exception as e:
                        report.write(f"Среднее количество слов за предложение: n/a \n")
                        pass
                    report.write('===========================================')
                    return
                report_creation()

            def root_window():
                global avg_index
                root = tk.Tk()
                root.title("Анализ текста")

                def send_text():
                    avg_index = (fkrt_index + gunning + smog + coleman + ariindex) / 5
                    median_ind = (statistics.median([fkrt_index, gunning, smog, coleman, ariindex]))

                    try:
                        root.destroy()
                    except Exception as e:
                        root.destroy()
                    result_window = tk.Tk()
                    result_window.title("Результат")
                    intro_label = tk.Label(result_window, text="Результат", font=("Arial", 20))
                    intro_label.pack(padx=150, pady=10)

                    resourses_path = os.path.join(curr_directory,'resourses')
                    ref_pic_1_path = os.path.join(resourses_path, 'Readability_index_rating_scale.bmp')
                    print(ref_pic_1_path)
                    # ref_pic_1 = PhotoImage(ref_pic_1_path)
                    # ref_pic_1 = PhotoImage('./resourses/Readability_index_rating_scale.png')
                    # label_pic_1 = tk.Label(image=ref_pic_1, compound='top')
                    # label_pic_1.pack()

                    label_1 = tk.Label(result_window, text=f"1) Flesch–Kincaid index: {round(fkrt_index, 3)}\n")
                    label_2 = tk.Label(result_window, text=f"2) Gunning fog index: {round(gunning, 3)}\n")
                    label_3 = tk.Label(result_window, text=f"3) SMOG index: {round(smog, 3)}\n")
                    label_4 = tk.Label(result_window, text=f"4) Coleman_Liau_index: {round(coleman, 3)}\n")
                    label_5 = tk.Label(result_window, text=f"5) ARI_index: {round(ariindex, 3)}\n")
                    label_6 = tk.Label(result_window, text=f"Среднее значение по всем индексам: {round(avg_index, 3)}\n")
                    label_7 = tk.Label(result_window, text=f"Медианное значение по всем индексам: {round(median_ind, 3)}\n")
                    label_8 = tk.Label(result_window, text=f"Лексическая плотность: {round(lexical_density_index(), 3)}\n")
                    label_9 = tk.Label(result_window, text=f"Среднее количество слов за предложение: {round(average_words_per_sentence, 3)}\n")
                    label_10 = tk.Label(result_window, text='Label 10')
                    label_11 = tk.Label(result_window, text='Label 11')
                    label_12 = tk.Label(result_window, text='Label 12')

                    label_1.pack(padx=10, pady=10)
                    label_2.pack(padx=10, pady=10)
                    label_3.pack(padx=10, pady=10)
                    label_4.pack(padx=10, pady=10)
                    label_5.pack(padx=10, pady=10)
                    label_6.pack(padx=10, pady=10)
                    label_7.pack(padx=10, pady=10)
                    label_8.pack(padx=10, pady=10)
                    label_9.pack(padx=10, pady=10)
                    label_10.pack(padx=10, pady=10)
                    label_11.pack(padx=10, pady=10)
                    label_12.pack(padx=10, pady=10)
                    entered_text = entry.get()
                    if entered_text:
                        print("Sent text:", entered_text)

                def exit_program():
                    cap = None
                    if cap is not None:
                        cap.release()
                    root.destroy()

                # Окно с надписью "Система мониторинга"
                intro_label = tk.Label(root, text="Анализ текста", font=("Arial", 20))
                intro_label.pack(padx=150, pady=10)

                # Окно для текста
                entry = tk.Entry(root, width=50)
                entry.pack(pady=10)
                select_button = tk.Button(root, text="Обработать текст", command=send_text, )
                select_button.pack(padx=10, pady=10)

                # Показываем кнопку "завершение работы"
                exit_button = tk.Button(root, text="Завершение работы", command=exit_program)
                exit_button.pack(padx=20, pady=10)

                root.mainloop()

            root_window()


        NLTK_method()

    __init__(1)

