import re
import os
import statistics
import nltk
import tkinter as tk
from tkinter import *
from tkinter import messagebox as mb
from langdetect import detect
from langdetect import detect_langs
from langdetect import DetectorFactory
#import langid #альтернатива langdetect
import pyphen
from threading import Thread
from nltk.corpus import stopwords
from collections import Counter



#Скачивание модуля для фильтрации слов  (если запускаете в первый раз, необходимо его скачать
# nltk.download('stopwords')
#Решение для обнаружения пакета линуксом
# stopwords_path = nltk.data.find('corpora/stopwords.zip')
# print(f"stopwords path is {stopwords_path}")

class Text_analysis:
    def GUI_start():
        root = tk.Tk()
        root.title("Анализ текста")
        intro_label = tk.Label(root, text="Анализ текста", font=("Arial", 20))
        intro_label.pack(padx=150, pady=10)
        text = 0
        def opening_the_text():
            entered_text = entry.get("1.0",tk.END)
            if entered_text:
                print("Sent text:", entered_text)
            text = entered_text

            try:
                root.destroy()
            except Exception as e:
                root.destroy()
            result_window = tk.Tk()
            result_window.title("Результат")
            intro_label = tk.Label(result_window, text="Результат", font=("Arial", 20))
            intro_label.pack(padx=150, pady=10)

            #Начало работы скрипта по анализу текста
            #Создание отчета

            def text_analysis():

                words = re.findall(r'\w+', text)
                print(f"Все слова в тексте: {words}")
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
                print(f"Предложения в тексте: {sentences}")
                dic_ru = pyphen.Pyphen(lang='ru')
                dic_en = pyphen.Pyphen(lang='en')
                stop_words = set(stopwords.words('english'))  # Наименование пакетов может различаться (в линукс наименование пакетов идет с маленькой буквы)
                filtered_words = [word for word in words if word.lower() not in stop_words]
                total_words = len(filtered_words)
                total_not_filtered_words = len(words)
                words_freq = Counter(filtered_words)
                number_of_top_common_words = 10
                most_common_words = words_freq.most_common(number_of_top_common_words)
                words_frequency = words_freq.most_common()
                # Тесты Флеша–Кинкейда на читаемость

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
                    print('индекс FKRT',index)
                    return index

                fkrt_index = FKrt_index()
                def gunning_fog_index():
                    # Do not include proper nouns, familiar jargon, or compound words. Do not include common suffixes (such as -es, -ed, or -ing) as a syllable (информация требует проверки);
                    word_count = len(words)
                    sentence_count = len(sentences)
                    syllables_list = [dic_en.inserted(word).split('-') for word in words]
                    # Счет слогов
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
                print(gunning)
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

                smog = SMOG_index()
                def Coleman_Liau_index():
                    character_count = sum(len(word) for word in words)
                    # print('char count', character_count)
                    sentences = text.split('. ')
                    # print('tot words', total_not_filtered_words)
                    sentences_count = len(sentences)
                    # print('sent count',sentences_count)
                    # Среднее количество символов в 100 словах
                    l = (character_count / total_not_filtered_words) * 100
                    # print('l', l)
                    # Среднее количество предложений на 100 слов
                    s = (sentences_count / total_not_filtered_words) * 100
                    # print('s', s)
                    collind = 0.0588 * l - 0.296 * s - 15.8
                    print('Coleman_Liau_index: ', collind)
                    return collind

                coleman = Coleman_Liau_index()
                print(coleman)
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
                    ari_index = 4.71 * (character_count / total_not_filtered_words) + 0.5 * (
                                total_not_filtered_words / sentences_count) - 21.43
                    print('ARI IND', ari_index)
                    return ari_index

                ariindex = ARI_index()
                print(ariindex)
                # Индекс лексической плотностии - считается как отношение количества уникальных слов к общему количеству слов
                def lexical_density_index():  # Индекс лексической плотности
                    word_count = len(words)
                    unique_words = set(words)
                    unique_words_count = len(unique_words)
                    # print(unique_words_count)
                    # print(word_count)
                    # print(f'unique words {unique_words}')
                    ldi = unique_words_count / word_count
                    print(f"lexical_density_index: {ldi}")
                    return ldi

                lexical_density_index()
                avg_index = (fkrt_index + gunning + smog + coleman + ariindex) / 5
                print(f"Avg_index: {avg_index}")
                median_ind = (statistics.median([fkrt_index, gunning, smog, coleman, ariindex]))
                print(f"Median_index: {median_ind}")
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
                            # Нужно скорректировать индекс 1 и 5 (1 пересчитать, библиотека верно его считает, но выводит не в нужной шкале)
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

                label_1 = tk.Label(result_window, text=f"1) Flesch–Kincaid index: {round(fkrt_index, 3)}\n")
                label_2 = tk.Label(result_window, text=f"2) Gunning fog index: {round(gunning, 3)}\n")
                label_3 = tk.Label(result_window, text=f"3) SMOG index: {round(smog, 3)}\n")
                label_4 = tk.Label(result_window, text=f"4) Coleman_Liau_index: {round(coleman, 3)}\n")
                label_5 = tk.Label(result_window, text=f"5) ARI_index: {round(ariindex, 3)}\n")
                label_6 = tk.Label(result_window, text=f"Среднее значение по всем индексам: {round(avg_index, 3)}\n")
                label_7 = tk.Label(result_window, text=f"Медианное значение по всем индексам: {round(median_ind, 3)}\n")
                label_8 = tk.Label(result_window, text=f"Лексическая плотность: {round(lexical_density_index(), 3)}\n")
                label_9 = tk.Label(result_window,
                                   text=f"Среднее количество слов за предложение: {round(average_words_per_sentence, 3)}\n")
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

                create_report()

            text_analysis()

            return


        def exit_program():
            cap = None
            if cap is not None:
                cap.release()
            root.destroy()


        # Окно для текста
        entry = tk.Text(root, width=50, height=10)
        entry.pack(pady=10)

        # entry = tk.Entry(root, width=50)
        # entry.pack(pady=10)
        select_button = tk.Button(root, text="Обработать текст", command=opening_the_text, )
        select_button.pack(padx=10, pady=10)

        # Показываем кнопку "завершение работы"
        exit_button = tk.Button(root, text="Завершение работы", command=exit_program)
        exit_button.pack(padx=20, pady=10)

        root.mainloop()

    GUI_start()
