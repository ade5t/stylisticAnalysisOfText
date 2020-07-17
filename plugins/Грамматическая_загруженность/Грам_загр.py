import nltk
import urllib
import xml.etree
import pymorphy2
from pymorphy2.tagset import OpencorporaTag
from .. import base


class FunCapacity(base.Plugin):
    """Класс плагина определения грамматически загруженных предложений.

    Attributes:
        NUM_MARK: Пороговое число запятых.
        NUM_WORD: Пороговое число слов.
        morph: Морфологический анализатор.
        progress: Текущий прогресс выполнения.
        num_of_words: Число слов в тексте.
    """
    def __init__(self):
        """Инициализация FunCapacity."""
        self.text = ''
        self.NUM_MARK = 7 
        self.NUM_WORD = 10
        self.morph = pymorphy2.MorphAnalyzer()
        self.progress = 0
        self.num_of_words = 0

    def __is_services_word_or_pnct(self, word):
        """Метод проверки слова на то, является ли оно служебным или знаком препинания.

        Args:
            word: Проверяемое слово.
        
        Returns:
            Истинность или ложность проверяемого суждения.
        """
        
        services_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP', 'PNCT'}
        if word == ',':
            return True
        if (self.morph.parse(word)[0].tag.POS in services_pos) or (
                self.morph.parse(word)[0].tag == OpencorporaTag('PNCT')):
            return True
        else:
            return False

    def __count_cur_sent(self, sentence):
        """Метод подсчёта количества слов изапятых в предложении.

        Args:
            sentence: Анализируемое предложение.

        Returns:
            Список, состоящий их 2 элементов: количества слов и количества запятых.
        """
        words_all = nltk.word_tokenize(sentence, 'russian')
        self.num_of_words += len(words_all)
        words = []
        num_pnct = 0
        for word in words_all:
            if not self.__is_services_word_or_pnct(word):
                words.append(word)
            else:
                if word == ',':
                    num_pnct += 1
        words_all.clear()
        num_words = len(words)
        return [num_words, num_pnct]

    def getProgress(self):
        """Метод получения текущего прогресса.

        Returns:
            Текущий прогресс в диапазоне от 0 до 100.
        """
        return self.progress

    def getStatistics(self):
        """Метод получения статистики.

        Returns:
            Статистика по тексту, состоящая из количества слов.
        """
        return 'Число слов: ' + str(self.num_of_words)

    def textAnalysis(self, text, options):
        """Метод текстового анализа.

        Определяет грамматически загруженные предложения по пороговому количеству слов и запятых во всём тексте.

        Args:
            text: Анализируемый текст.
            options: Строка с пороговым числом слов и запятых в формате 'количество_слов количество_запятых', например '20 4'.
                     Пороговое число слов и запятых должно быть больше 1.

        Returns:
            Список индексов грамматически загруженных предложений, например [[[15, 30]], [[40, 60]]]
        """
        self.text = text
        try:
            optins_str = options.split()
            self.NUM_WORD = int(optins_str[0])
            self.NUM_MARK = int(optins_str[1])
            if self.NUM_WORD <= 1 or self.NUM_MARK <= 1:
                raise Exception() 
        except Exception:
            return 'invalid_options'
        global_list = []
        start_search = 0
        sentences = nltk.sent_tokenize(self.text, 'russian')
        self.progress = 0
        i = 1
        for sentence in sentences:
            rez_sent = self.__count_cur_sent(sentence)
            if rez_sent[0] > self.NUM_WORD or rez_sent[1] > self.NUM_MARK:
                index = self.text.find(sentence, start_search)
                global_list.append([[index, index + len(sentence)]])
                start_search += len(sentence) + 1
            self.progress = i / len(sentences)
            i += 1
        return global_list