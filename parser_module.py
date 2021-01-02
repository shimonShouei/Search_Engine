from nltk import TweetTokenizer, PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
import re

"""
~~~~~~~~~~~~~~~~~~~~~~~~  Module Description ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    This Module Contains Parse class , its part is to parse text in each document given from corpus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

def get_stop_words():
    stop_words_file = open("stopwords.txt")
    lines = stop_words_file.readlines()
    stop_words = set()
    for word in lines:
        word = word.replace('\n', '')
        stop_words.add(word)
    add_stop_words(stop_words)
    return stop_words

def add_stop_words(stop_words):
    for word in ["https", "www", "rt", "tco",'twitter','won’t','aren’t','didn’t','doesn’t','hadn’t','hasn’t','haven’t','isn’t'
                 'mightn’t','mustn’t','needn’t','shan’t','shouldn’t','wasn’t','weren’t','won’t','wouldn’t','twitter.com']:
        stop_words.add(word)


"""
    Class Description :
        This Class is used for tokenizing text of a doc and saving the occurrences of the tokens
"""
class Parse:

    """
       Description :
           initialize properties of Parse object
    """
    def __init__(self, is_stemming=False):
        self.is_stemming = is_stemming
        self.stop_words = get_stop_words()
        self.num_dict = {"K": "K", "M": "M", "B": "B", "k": "K", "m": "M", "b": "B", "thousand": "K", "million": "M",
                         "billion": "B", "dollar": "$", "dollars": "$", "percent": "%",
                         "percentage": "%"}
        self.text_tokens_list = ''
        self.no_stop_word_text_tokens_list = []
        self.current_index = 0
        self.is_stemming = is_stemming
        self.final_terms_doc = []
        self.reg_any_number = re.compile(r'^\d+[.,]?\d*million$|^\d+[.,]?\d*billion$|^\d+[.,]?\d*thousand$|'
                                         r'^\d+[.,]?\d*Million$|^\d+[.,]?\d*Billion$|^\d+[.,]?\d*Thousand$|'
                                         r'^\d+[.,]?\d*[m|b|k|M|B|K][%|$]?$|[%|$]?\d+[.,]?\d*[%|$]?')
        self.reg_decimal_number = re.compile(r'\d+[.]\d+')
        self.reg_natural_number = re.compile(r'\d+')
        self.reg_mixed_number = re.compile(r'\d+[ ]\d+[/]\d+')
        self.reg_fraction_number = re.compile(r'\d+[/]\d+')
        self.reg_numbers_with_letters = re.compile(
            r'million$|billion$|thousand$|^Million$|Billion$|Thousand$|'
            r'm$|b$|t$|M$|B$|T$')
        self.reg_url = re.compile(r'".*"[:]".*"')

        self.p_stemmer = PorterStemmer()

    def set_stemming_bool(self, is_stemming):
        self.is_stemming = is_stemming

    """
        Description: cleans the end and the beginning of the word from irrelevant chars
    """
    def clean_word(self, term: str): # clean'
        if len(term) == 0:
            return ""
        j = 0
        for i in range(len(term)):
            if term[i] == '-' or term[i] == '.' or term[i] == '\'':
                j = j + 1
            else:
                break
        term = term[j:]
        j = len(term)
        if len(term) == 0:
            return term
        for i in range(len(term) - 1, -1, -1):
            if term[i] == '-' or term[i] == '.' or term[i] == '\'':
                j = j - 1
            else:
                break
        term = term[0:j]
        return term

    """
        Description: return true if there is a sequence of uppercase letters
    """
    def check_contigous_uppercase(self, s):
        found = re.findall('[A-z]+', s)
        if len(found) > 0:
            if len(found[0]) > 1:
                return True
        return False

    """
        Description: add final term to final terms list
    """
    def add_term(self, term):
        if term is not None:
            input_term = self.clean_word(term)
        else:
            return
        if input_term is not None and len(input_term) > 0 \
                and not self.stop_words.__contains__(input_term.lower()):
            if self.is_stemming:
                if input_term[0].isdigit():
                    self.final_terms_doc.append(input_term)
                    return
                if input_term.__contains__(' '):
                    self.final_terms_doc.append(input_term)
                    return
                elif input_term[0] == '#' or input_term[0] == '@':
                    self.final_terms_doc.append(input_term)
                    return
                elif input_term[0].isupper():
                    input_term = self.p_stemmer.stem(input_term)
                    self.final_terms_doc.append(input_term.upper())
                    return
                else:
                    input_term = self.p_stemmer.stem(input_term)
                    self.final_terms_doc.append(input_term)
            else:
                self.final_terms_doc.append(input_term)

    """
         Description: split string by capital letters.
                      keep_contiguous (bool): flag to indicate we want to keep contiguous uppercase chars together
    """
    def split_on_uppercase(self, s, keep_contiguous=False):
        string_length = len(s)
        is_lower_around = (lambda: s[i - 1].islower() or
                                   string_length > (i + 1) and s[i + 1].islower())
        start = 0
        parts = []
        for i in range(1, string_length):
            if s[i].isupper() and (not keep_contiguous or is_lower_around()):
                word = s[start: i].lower()
                if self.is_stemming:
                    word = self.p_stemmer.stem(word)
                parts.append(word)
                start = i
        s = s.replace('\u2026', '')  # remove '...' from term
        word = ((s[start:]).strip('.')).lower()
        if len(word) > 0:
            parts.append(word)
        return parts

    """
        Description: parse hashtag terms. save hashtags terms only in lower case
    """
    def handle_hashtag(self, hashtag_str: str):
        result = []
        # separate by under score
        if hashtag_str.__contains__("_"):
            result.extend(w.lower() for w in hashtag_str[1:].split("_") if len(w) > 0)  # e.g #stay_at_home -> stay, at, home
            result.append(hashtag_str.lower().replace("_", ""))  # e.g #stay_at_home -> #stayathome
        # separate by uppercase letters
        else:
            contiguous = self.check_contigous_uppercase(hashtag_str)
            result = self.split_on_uppercase(hashtag_str[1:], contiguous)  # e.g stayAtHome -> stay, at, home
            result.append(hashtag_str.lower())  # e.g #stayAtHome -> #stayathome
        return result

    """
        Description: handle to parse any kind of numbers
    """
    def handle_any_kind_numbers(self, term, next_term, idx):
        term = self.reg_any_number.findall(term)[0]
        term = term.replace(',', '')
        num = None
        if self.reg_decimal_number.search(term):
            num = self.reg_decimal_number.findall(term)[0]
            num = str(round(float(num), 3))

        elif self.reg_natural_number.search(term):
            num = self.reg_natural_number.findall(term)[0]

        if next_term is not None and next_term.lower() in self.num_dict.keys():
            num += self.num_dict[next_term.lower()]
            idx += 1

        elif len(self.reg_numbers_with_letters.findall(term)) > 0:
            num += self.num_dict[(self.reg_numbers_with_letters.findall(term)[0]).lower()]

        elif len(re.findall('[%]', term)) == 1:
            self.add_term(self.numbers_over_1000(num))
            num += '%'

        elif next_term is not None and len(re.findall('[%]', next_term)) > 0:
            self.add_term(self.numbers_over_1000(num))
            num += '%'
            idx += 1

        elif len(re.findall('[$]', term)) == 1:
            self.add_term(self.numbers_over_1000(num))
            num += '$'

        elif next_term is not None and len(re.findall('[$]', next_term)) > 0:
            self.add_term(self.numbers_over_1000(num))
            num += '$'
            idx += 1

        elif next_term is not None and self.reg_mixed_number.match(term + ' ' + next_term):
            next_term = self.reg_fraction_number.findall(next_term)[0]
            fraction_split = next_term.split('/')
            if int(fraction_split[1]) == 0:
                return
            fraction = int(num) + int(fraction_split[0]) / int(fraction_split[1])
            self.add_term(fraction)
            num += ' ' + next_term
            idx += 1

        else:
            num = self.numbers_over_1000(num)

        self.add_term(num)
        return idx


    """
        Description: save terms that are suspected as an entity
    """
    def handle_entity(self, idx):
        term = self.text_tokens_list[idx]
        end_with = False
        if not term.endswith(',') and not term.endswith('.'):
            end_with = True
        entity = term
        if term.__contains__('-'):
            entity = self.handle_entity_hyphen(term)
            if entity == '':
                return idx
        entity_flag = False
        if entity != term:
            entity_flag = True
            if not end_with:
                self.add_term(entity)
                return idx
        if idx + 1 < len(self.text_tokens_list):
            next_term = self.text_tokens_list[idx + 1]
            if end_with and len(next_term) > 0 and next_term[0].isupper():
                if not entity_flag:
                    self.add_term(term)
                if next_term.__contains__('-'):
                    next_term_to_add = self.handle_entity_hyphen(next_term)
                else:
                    next_term_to_add = next_term.replace(".", "")
                    next_term_to_add = next_term_to_add.replace(",", "")
                    self.add_term(next_term_to_add)
                entity = entity + ' ' + next_term_to_add

                j = idx + 2
                while j < len(self.text_tokens_list):
                    term = next_term
                    next_term = self.text_tokens_list[j]
                    if not term.endswith(',') and not term.endswith('.') and len(next_term) > 0 and next_term[
                        0].isupper():
                        if next_term.__contains__('-'):
                            next_term_to_add = self.handle_entity_hyphen(next_term)
                        else:
                            next_term_to_add = next_term.replace(".", "")
                            next_term_to_add = next_term_to_add.replace(",", "")
                            self.add_term(next_term_to_add)
                        entity += ' ' + next_term_to_add
                        j += 1
                    else:
                        break

                self.add_term(entity)
                idx = j
                return idx
        if entity_flag:
            self.add_term(entity)
            idx += 1
        return idx

    def handle_entity_hyphen(self, term):
        term = term.split('-')
        entity = term[0]
        i = 0
        while i < len(term) - 1:
            term0 = term[i]
            term1 = term[i + 1]
            if (len(term1) > 0 and (not term1[0].isupper() and not term1[0].isdigit())) or len(term1) == 0:
                return ''
            entity = entity + ' ' + term1
            term0.replace(".", "")
            term1.replace(",", "")
            term0.replace(",", "")
            term1.replace(".", "")
            self.add_term(term0)
            self.add_term(term1)
            i = i + 2
        return entity

    """
        Description: The main function that responsible to parsing the document text
    """
    def parse_sentence(self, text: str):
        self.text_tokens_list = self.get_tokens(text)
        idx = 0
        while idx < len(self.text_tokens_list):
            term = self.text_tokens_list[idx]
            next_term = None
            # handle entity
            if len(term) > 0 and term[0].isupper():
                check_idx = self.handle_entity(idx)
                if check_idx - idx > 0:
                    idx = check_idx
                    continue
            term = term.replace(",", "")
            if len(term) > 0 and term is not None:
                if (term.lower()).replace('.','') not in self.stop_words:
                    # handle numbers
                    if self.reg_any_number.match(term):
                        if len(re.findall(r'\d[-]\d', term)) > 0:
                            term = term.split('-')
                            idx = self.handle_any_kind_numbers(term[0], term[1], idx)
                        else:
                            if idx + 1 < len(self.text_tokens_list):
                                next_term = self.text_tokens_list[idx + 1]
                            idx = self.handle_any_kind_numbers(term, next_term, idx)
                    # handle hashtag
                    elif term[0] == '#':
                        term = term.replace(".", "")
                        self.final_terms_doc.extend(self.handle_hashtag(term))

                    # handle @
                    elif term[0] == '@':
                        term = term.replace(".", "")
                        self.add_term(term)

                    # handle terms contains hyphen
                    elif term.__contains__("-"):
                        term = term.replace(".", "")
                        check_idx = idx
                        idx = self.handle_contain_hyphen(term, idx)
                        if idx == check_idx + 1:
                            continue
                    else:
                        term = term.replace(".", "")
                        if len(term) == 1 or not (term.isalpha()):
                            idx += 1
                            continue
                        self.add_term(term)
            idx += 1
        return self.final_terms_doc

    """
        Description: parse terms that separate by hyphen
    """
    def handle_contain_hyphen(self, term, idx):
        j = 0
        while j in range(len(term)):
            if term[j] == '-':
                j = j + 1
            else:
                break
        term = term[j:]
        if term == '':
            idx += 1
            return idx
        if term.__contains__("-"):
            words = term.split("-")
            if len(words) == 0:
                idx += 1
                return idx
            term = words[0]
            self.add_term(self.clean_word(term))
            i = 1
            while i in range(len(words)):
                if len(words[i]) == 0:
                    i += 1
                    continue
                word = words[i]
                if not len(word) == 0:
                    self.add_term(word)  # ??
                    term = term + "-" + words[i]
                i = i + 1
        elif term != "":
            if self.stop_words.__contains__(term):
                idx += 1
                return idx
        term = self.clean_word(term)
        self.add_term(term)
        return idx


    """
        Description: This method gets a document text and tokenizing it
    """
    def get_tokens(self, text):
        text = text.encode("ascii", "ignore").decode()  # remove emoji
        tokens = re.split(r'[ |+|\n|\u2026|:|;|?|!|"|\]|\[|~|/|&|(|)|*]', text)
        return tokens

    def fix_num(self, num):
        if float(num) == int(num):
            return int(num)
        else:
            return float(num)

    """
         Description: This function represents numbers over a 1000 with k, m and b respectively
     """
    def numbers_over_1000(self, num):
        if float(num) > 999:
            k = pow(10, 3)
            m = pow(10, 6)
            b = pow(10, 9)
            num = int(float(num))
            if k <= num < m:
                num = self.fix_num(num / k)
                return str(num) + "K"
            if m <= num < b:
                num = self.fix_num(num / m)
                return str(num) + "M"
            if num >= b:
                num = self.fix_num(num / b)
                return str(num) + "B"
        else:
            return num

    """
          Description : parse url 
    """
    def parse_url(self, url: str):
        url_terms = []
        if url is None or len(re.findall("http", url)) < 1:
            return
        splited_url = self.clean_url(url)

        for i in range(len(splited_url)):
            if i == len(splited_url) - 1 or (i == len(splited_url) - 2) and splited_url[i+1] == '':
                if splited_url[i].__contains__("-"):
                    url_terms.extend(re.split('-', splited_url[i]))
                if splited_url[i].__contains__("=") or splited_url[i].__contains__(":"):  # e.g "?igshid=o9kf0ugp1l8x"
                    url = re.split('=|:|', splited_url[i])
                    if len(url[0]) > 0:
                        if not url[0][0].isalpha():  # e.g "?igshid"
                            url_terms.append(url[0][1:len(url[0])])
                        else:
                            url_terms.append(url[0])
                        url_terms.append(url[1])
                        break
            url_terms.append(splited_url[i])
        return url_terms

    """
        Description : clean url from un-relevant terms 
    """
    def clean_url(self, url: str):
        reg_typical_url = self.reg_url
        url = url.replace("[", "")
        url = url.replace("]", "")
        url = url.replace("{", "")
        url = url.replace("}", "")
        final_url = []
        splited_url = url.split(',')
        for i in splited_url:
            if reg_typical_url.match(i):
                url = reg_typical_url.findall(i)[0]
                k = url.index('":"')
                url = url[k + 3:]
                url = url.replace('"', "")
                url = url.split(sep="://")
                url = url[1].split(sep="/")
                if url[0][0:3] == "www":
                    url[0] = url[0][4:len(url[0])]  # remove www
                final_url.extend(url)

        return final_url

    """
        Description : 
            creates the dictionary that contains for each term its number of occurrences in the document(tf) 
    """
    def final_terms_dict(self, tokenized_text):
        term_dict = {}
        for term in tokenized_text:
            if term not in term_dict.keys():
                if term.lower() in term_dict.keys():
                    term_dict[term.lower()] += 1
                elif term.upper() in term_dict.keys():
                    tf = term_dict[term.upper()]
                    del term_dict[term.upper()]
                    term_dict[term.lower()] = tf + 1
                elif term[0].upper() + term[1:] in term_dict.keys():
                    tf = term_dict[term[0].upper() + term[1:]]
                    del term_dict[term[0].upper() + term[1:]]
                    term_dict[term.lower()] = tf + 1
                else:
                    term_dict[term] = 1
            else:
                term_dict[term] += 1
        return term_dict

    """
       Description:
            This function takes a tweet document as list and break it into different fields
            :param doc_as_list: list re-preseting the tweet.
            :return: Document object with corresponding fields.
    """
    def parse_doc(self, doc_as_list):
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]

        if full_text.__contains__("t.co") and len(indices) > 4:
            if indices is not None and url is not None:
                indices = indices.replace("[[", '')
                indices = indices.replace("]]", '')
                splited_indices = indices.split(",")
                splited_indices = splited_indices
            if len(splited_indices) == 2 and full_text[int(splited_indices[0]):int(splited_indices[1])].startswith(
                    "http"):
                full_text = full_text[0:int(splited_indices[0])] + full_text[int(splited_indices[1]) + 1::]
        self.parse_sentence(full_text)

        if url is not None and len(url) > 2:
            parsed_url = self.parse_url(url)
            for term in parsed_url:
                self.add_term(term)

        doc_length = len(self.final_terms_doc)  # after text operations.
        term_dict = self.final_terms_dict(self.final_terms_doc)

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url
                            , term_dict, doc_length)
        self.final_terms_doc = []
        return document
