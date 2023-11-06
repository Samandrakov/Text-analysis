import re
import statistics
import nltk
from langdetect import detect
from langdetect import detect_langs
import langid #альтернатива langdetect
from langdetect import DetectorFactory
import pyphen
from nltk.corpus import stopwords
from collections import Counter
from textstat import flesch_reading_ease
# nltk.download('stopwords')

class text_analyzer:
    def __init__(self):

        #нужно делать проверку каждого слова на принадлежность к языку с помощью комплексного сравнения (берем по 3-4 слова проводим анализ по каждому, потому по перебору, потом
        #берем среднюю и присваиваем итоговое значение языка слову

        # def englishOrRussian(string):
        #     res = detect_langs(string)
        #     for item in res:
        #         if item.lang == "ru" or item.lang == "en":
        #             return item.lang
        #     return None
        #
        # print(englishOrRussian("Привет, как дела у меня замечательно?"))
        # print(englishOrRussian("The quick brown fox"))  # en
        # print(englishOrRussian("Hallo, mein Freund"))  # Non
        # def englishOrFrench(string):
        #     res = detect_langs(string)
        #     for item in res:
        #         if item.lang == "ru" or item.lang == "en":
        #             return item.lang
        #     return None



        #Установка списков языков
        DetectorFactory.seed = 0
        # detect.set_languages
        #Открытие временного тхт (нужно заменить на 1) либо автоматический забор текста по юрл , либо окошком с возможностью загрузки текста
        with open('lorem.txt', 'r') as file:
            text = file.read()
        #Создание отчета
        report_file = 'report.txt'
        dic_ru = pyphen.Pyphen(lang='ru')
        dic_en = pyphen.Pyphen(lang='en')
        words = re.findall(r'\w+', text)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s',text)
        #Использование фильтрации частиц, артиклей, предлогов с помощью nltk
        stop_words = set(stopwords.words('English'))
        filtered_words = [word for word in words if word.lower() not in stop_words]
        filtered_words_list = []

        with open(report_file, 'w') as report:
            report.write('Отфильтрованные слова')
            for item in filtered_words:
                report.write(item + '\n')
        #Метод с фильтрацией
        def NLTK_method(a):
            total_words = len(filtered_words)
            total_not_filtered_words = len(words)
            words_freq = Counter(filtered_words)
            number_of_top_common_words = 10
            most_common_words = words_freq.most_common(number_of_top_common_words)
            #Тесты Флеша–Кинкейда на читаемость
            readability_score = flesch_reading_ease(text)
            average_words_per_sentence = total_not_filtered_words / len(sentences)
            # print(readability_score,type(readability_score))

            def difficulty_determination(index):
                if index > 100:
                    result = 'Уровень сложности текста - за рамками теста, слишком легкий'
                elif (90 < index) and (index < 100):
                    result = 'Уровень сложности текста - 5 класс \n(Very easy to read. Easily understood by an average 11-year-old student)'
                elif (80 < index) and (index < 90):
                    result = 'Уровень сложности текста - 6 класс \n(Easy to read. Conversational English for consumers)'
                elif (70 < index) and (index < 80):
                    result = 'Уровень сложности текста - 7 класс \n(Fairly easy to read)'
                elif (60 < index) and (index < 70):
                    result = 'Уровень сложности текста - 8-9 класс \n(Plain English. Easily understood by 13- to 15-year-old students)'
                elif (50 < index) and (index < 60):
                    result = 'Уровень сложности текста - 10-11 класс \n(Fairly difficult to read)'
                elif (30 < index) and (index < 50):
                    result = 'Уровень сложности текста - Колледж \n(Difficult to read)'
                elif (10 < index) and (index < 30):
                    result = 'Уровень сложности текста - Выпускник колледжа \n(Very difficult to read. Best understood by university graduates)'
                elif index < 10:
                    result = 'Уровень сложности текста - Профессиональный \n(Extremely difficult to read. Best understood by university graduates)'
                return result

            difficulty = difficulty_determination(readability_score)
            def gunning_fog_index():
                word_count = len(words)
                print(word_count)
                sentence_count = len(sentences)
                print(sentence_count)
                print(words)
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
                complex_word_count = 0
                for word_syllables in syllables_list:
                    word = ''.join(word_syllables)
                    if len(word_syllables) > 3:
                        complex_word_count += 1
                smog_ind = 1.0430 * (30 * (complex_word_count/ sentence_count)) ** 0.5 + 3.1291
                # print('SMOG index',smog_ind)
                return smog_ind
            smog = SMOG_index()

            def Coleman_Liau_index():

                character_count = sum(len(word) for word in words)
                print(character_count)
                sentences = text.split('. ')
                sentences_count = len(sentences)
                print(sentences_count)
                #Среднее количество символов в 100 словах
                l = (character_count/ total_not_filtered_words) * 100
                #Среднее количество предложений на 100 слов
                s = (sentences_count / total_not_filtered_words) * 100
                collind = 0.0588 * l * 0.296 * s - 15.8
                # print('Coleman_Liau_index: ', collind)
                return collind
            coleman = Coleman_Liau_index()

            def ARI_index():

                character_count = sum(len(word) for word in words)
                sentences = text.split('. ')
                sentences_count = len(sentences)
                # Среднее количество символов в 100 словах
                avg_char_per_wrd = (character_count / total_not_filtered_words) * 100
                print(avg_char_per_wrd)
                # Среднее количество предложений на 100 слов
                avg_wrd_per_sentence = (total_not_filtered_words / sentences_count) * 100
                print(average_words_per_sentence)
                ari_index = (4.71 * avg_char_per_wrd) + (0.5 * avg_wrd_per_sentence) - 21.43
                print('ARI IND',ari_index)
                return ari_index
            ariindex = ARI_index()
            #Среднее и медиана по всем индексам
            avg_index = (readability_score + gunning + smog + coleman + ariindex)/5
            median_ind = (statistics.median([readability_score, gunning, smog, coleman, ariindex]))
            with open(report_file, 'w') as report:
                report.write('===========================================\n')
                report.write('Показатели с NLTK\n')
                report.write('===========================================\n')
                report.write('Общее количество слов : ')
                report.write(str(f"{total_words}\n"))
                report.write('Частота :')
                report.write(str(f"{words_freq}\n"))
                report.write(f'Частоупотребляемые слова (топ {number_of_top_common_words}): ')
                for word, count in most_common_words:
                    report.write(f"{word}: {count} ")
                report.write("\n")
                report.write('Индексы читаемости: \n')
                report.write(str(f"1) Flesch–Kincaid readability tests: {round(readability_score, 3)}\n"))
                report.write(f"Интерпретация сложности: {difficulty}\n")
                report.write(str(f"2) Gunning fog index: {round(gunning, 3)}\n"))
                report.write(str(f"3) SMOG index: {round(smog, 3)}\n"))
                report.write(str(f"4) Coleman_Liau_index: {round(coleman, 3)}\n"))
                report.write(str(f"5) ARI_index: {round(ariindex, 3)}\n"))
                #Нужно скорректировать индекс 1 и 5 (1 пересчитать, библиотека верно его считает, но выводит не в нужной шкале)
                report.write(str(f"Среднее значение по всем индексам: {round(avg_index, 3)}\n"))
                report.write(str(f"Медианное значение по всем индексам: {round(median_ind, 3)}\n"))
                report.write('Среднее количество слов за предложение: ')

                report.write(str(f"{round(average_words_per_sentence, 3)}\n"))
                report.write('===========================================')
        NLTK_method(1)
        def Old_method(self):
            print('===========================================')
            print('Показатели без внедрения NLTK', end='\n')
            print('===========================================')
            total_words = len(words)
            print('Общее количество слов')
            print(total_words)
            words_freq = Counter(words)
            print('Частота')
            print(words_freq)
            most_common_words = words_freq.most_common
            print('Частоупотребляемые слова')
            print(most_common_words)
            readability_score = flesch_reading_ease(text)
            print('Индекс читаемости')
            print(readability_score)
            average_words_per_sentence = total_words / len(sentences)
            print('Среднее количество слов за предложение')
            print(average_words_per_sentence)
            print('===========================================', end='\n')
        # Old_method(1)

        def count_syllables(word):
            syllable_divided_word = len(dic_en.inserted(word).split('-'))
            print(dic_en.inserted(word).split('-'))
            if syllable_divided_word > 3:
                return 1
            # return len(dic_en.inserted(word).split('-'))
        print(count_syllables('catterpillar'))

        #Модуль определения языка - нужно вставить его в самое начало, чтобы он прогонял сначала весь текст (либо прогонял каждое слово)
        # my_blng_txt = 'the cat is great как you дела drug'
        # m_txt = my_blng_txt.split()
        # word_langs = {}
        # for word in m_txt:
        #     language = detect(word)
        #     word_langs[word] = language
        # for word, language in word_langs.items():
        #     print(f"'{word}'{language}'")
        # language = detect(my_wrd)
        # print(language)
    __init__(1)

