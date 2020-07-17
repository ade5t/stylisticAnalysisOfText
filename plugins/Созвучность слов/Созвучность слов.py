import pymorphy2
import re
import textdistance
import nltk
from pymorphy2.tagset import OpencorporaTag
from .. import base


class ConsonanceWord(base.Plugin):
    """Класс плагина определения рядом стоящих созвучных слов.

    Attributes:
        text: Исследуемый текст.
        percent: Порогой процент созвучности слов.
        morph: Морфологический анализатор.
        progress: Текущий прогресс выполнения.
        num_of_sent: Число предложений в тексте.
        num_of_groups: Число групп созвучностей
    """

    def __init__(self):
        """Constructor"""
        self.text = ''
        self.percent = ''
        self.progress = 0
        self.num_of_sent = 0 
        self.num_of_groups = 0  
        self.morph = pymorphy2.MorphAnalyzer()

    def __is_services_word_or_pnct(self, word):
        """Метод проверки слова на то, является ли оно служебным или знаком препинания.

        Args:
            word: Проверяемое слово.
        
        Returns:
            Истинность или ложность проверяемого суждения.
        """
        services_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP', 'PNCT'}
        if re.search('[.,:;_%©?*,!@#$%^&()\d]|[+=]|[[]|[]]|[/]|"|\s{2,}|-', word):
            return True
        if word == ',':
            return True
        if (self.morph.parse(word)[0].tag.POS in services_pos) or (
                self.morph.parse(word)[0].tag == OpencorporaTag('PNCT')):
            return True
        else:
            return False

    def __get_list_of_con_words_in_n_sents(self, sentence, percent):
        """Метод получения индексов созвучных слов 

        Args:
            sentence: Группа анализируемых предложений.
            percent: Пороговый процент созвучности слов.
        
        Returns:
            Список индексов созвучных слов, например [[[1, 5], [7, 11]], [[10, 15], [27, 32]]] (2 группы созвучности по 2 слова).
        """
        words_all = nltk.word_tokenize(sentence, 'russian')
        words = []
        global_list_words = []
        local_list_words = []
        global_list_indexes = []
        local_list_indexes = []

        # Удаление из списка слов "ненужных" сервисных слов и знаков препинания
        for word in words_all:
            if not self.__is_services_word_or_pnct(word):
                words.append(word)
        words_all.clear()

        first_word_index = 0
        for word in words:
            if first_word_index == len(words):
                break
            local_list_words.append(word)
            cur_word_index = first_word_index + 1
            while cur_word_index < len(words):
                cur_word_normal = self.morph.parse(words[cur_word_index])
                first_word_normal = self.morph.parse(word)
                is_equal = False
                for cur_word_from_list in cur_word_normal:
                    for first_word_from_list in first_word_normal:
                        # То самое нахождение созвучности слов, возвращает результат в процентах
                        if textdistance.jaro(cur_word_from_list.normal_form,
                                             first_word_from_list.normal_form) > percent:
                            is_equal = True
                            break
                    if is_equal:
                        break
                if is_equal:  # Если слова созвучны, надо бы добавить его в список
                    local_list_words.append(words[cur_word_index])
                cur_word_index += 1
            if len(local_list_words) > 1:  # Вышенайденный "локальный" список добавляем в "глобальный"
                global_list_words.append(local_list_words)
            first_word_index += 1
            local_list_words = []

        # Тут ищутся уже именно координаты слов из "глобального" списка
        for local_list_words in global_list_words:
            index = 0
            for word in local_list_words:
                if len(local_list_indexes) == 0:
                    index = sentence.find(word, index)
                    if sentence[index + len(word)].isalpha():
                        index = sentence.find(word, index + len(word))
                else:
                    index = sentence.find(word, index + len(word))
                if sentence[index + len(word)].isalpha():
                    continue
                local_list_indexes.append([index, index + len(word) - 1])
            global_list_indexes.append(local_list_indexes)
            local_list_indexes = []
        return global_list_indexes

    @staticmethod
    def intersection(a, b):
        """Метод выделения пересечения двух спиков 

        Args:
            a: Первый список.
            b: Второй список.
        
        Returns:
            Список, являющийся пересечением списков a и b.
        """
        c = []
        for i in a:
            if i in c:
                continue
            for j in b:
                if i == j:
                    c.append(i)
                    break
        return c

    @staticmethod
    def merge_lists(a, b):
        """Метод слияния двух спиков 

        Args:
            a: Первый список.
            b: Второй список.
        
        Returns:
            Список, являющийся объединением списков a и b.
        """
        for i in b:
            if i not in a:
                a.append(i)
        return a

    def getProgress(self):
        """Метод получения текущего прогресса.

        Returns:
            Текущий прогресс в диапазоне от 0 до 100.
        """
        return self.progress*100

    def getStatistics(self):
        """Метод получения статистики.

        Returns:
            Статистика по тексту, состоящая из количества предложений и числа групп созвучных слов.
        """
        return 'Число предложений: ' + str(self.num_of_sent) + ', Число групп созвучных слов: ' +str(self.num_of_groups)

    def textAnalysis(self, text, options):
        """Метод текстового анализа.

        Определяет рядом стоящие (до соседнего предложения 1 порядка) созвучные слова по пороговому проценту созвучности слов во всём тексте.

        Args:
            text: Анализируемый текст.
            options: Строка с пороговым числом слов и запятых в формате 'пороговый_процент', например '90'.
                     Пороговое число слов и запятых должно быть больше 0 и меньше 100.

        Returns:
            Список индексов созвучных слов, например [[[1, 5], [7, 11]], [[10, 15], [27, 32]]] (2 группы созвучности по 2 слова).
        """
        self.text = text
        try:
            self.percent = float(options)
            if self.percent <= 0 or self.percent > 1:
                raise Exception() 
        except Exception:
            return 'invalid_options'
        sentences = nltk.sent_tokenize(self.text, 'russian')
        self.num_of_sent = len(sentences)
        index_of_group_sents = -1
        cur_sent_index = index_of_group_sents
        local_list = []
        global_list = []
        start_search = 0
        last_index = 0
        self.progress = 0
        while index_of_group_sents < len(sentences) - 1:
            index_of_group_sents += 1
            group_of_sents = ''

            # Ниже по двум условиям формируются индексы куска текста, состоящего из 2-х предложений
            if index_of_group_sents == 0:
                start_search = self.text.find(sentences[index_of_group_sents])
                last_index = self.text.find(sentences[index_of_group_sents], start_search) + len(
                    sentences[index_of_group_sents])
            else:
                start_search = self.text.find(sentences[index_of_group_sents],
                                              start_search + len(sentences[index_of_group_sents - 1]))
                last_index = self.text.find(sentences[index_of_group_sents], start_search) + len(
                    sentences[index_of_group_sents])

            if index_of_group_sents + 1 <= len(sentences) - 1:
                last_index = self.text.find(sentences[index_of_group_sents + 1], last_index) + len(
                    sentences[index_of_group_sents + 1])
            else:
                last_index = self.text.find(sentences[index_of_group_sents], start_search) + len(
                    sentences[index_of_group_sents])

            group_of_sents = self.text[start_search:last_index]

            local_list = self.__get_list_of_con_words_in_n_sents(group_of_sents, self.percent)

            # Функцией выше мы получили индексы созвучных слов, но они "локальные", теперь надо узнать эти индексы в
            # "глобальном" тексте
            if local_list != []:
                correction = self.text.find(sentences[index_of_group_sents], start_search)
                for group in local_list:
                    for word in group:
                        word[0] += correction
                        word[1] += correction + 1
                global_list.extend(local_list)
            self.progress = 0.8 * ((index_of_group_sents + 1) / len(sentences))

        # После вышепроделанных операций получили список групп созвучностей со всего текста, но из-за того, что группы
        # созвучности искались лишь в двух предложениях, одинаковые группы созвучности могли находиться в разных
        # группах. Необходимо их объединить.
        group_1 = 0
        old_local_progress = 0
        while group_1 < len(global_list):
            group_2 = group_1 + 1
            while group_2 < len(global_list):
                if self.intersection(global_list[group_1], global_list[group_2]):
                    global_list[group_1] = self.merge_lists(global_list[group_1], global_list[group_2])
                    global_list.pop(group_2)
                else:
                    group_2 += 1
            group_1 += 1
            local_progress = (group_1 / (len(global_list))) * 0.2
            self.progress += local_progress - old_local_progress
            old_local_progress = local_progress

        self.num_of_groups = len(global_list)
        return global_list