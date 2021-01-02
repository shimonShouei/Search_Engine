import math
import time
from datetime import datetime
from parser_module import Parse
from ranker import Ranker
import utils

"""
~~~~~~~~~~~~~~~~~~~~~~~~  Module Description ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    This Module Contains search class , its part is to send queries to parser, find relevant and calc tf idf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class Searcher:

    def __init__(self, inverted_index, config, total_num_of_docs):
        self.parser = Parse(config.toStem)
        self.ranker = Ranker()
        self.query_as_list = []
        self.inverted_index = inverted_index
        self.is_stemming = config.toStem
        self.config = config
        self.n = 4
        self.total_num_of_docs = total_num_of_docs
        self.relevant_docs = {}

    """
        Description : receive queries as list or as txt file, read them, parse them and return them in list of parsed
        queries. 
    """

    def handle_files(self, queries):
        try:
            my_file = open(queries, "r", encoding="utf8")
        except:
            my_file = ''
        if my_file != '':
            for line in my_file:
                if line == '\n':
                    continue
                line = line[line.index('.') + 1:]
                parsed_query = self.parser.parse_sentence(line)
                self.query_as_list.append(parsed_query)
                self.parser.final_terms_doc = []

        else:
            for i in range(len(queries)):
                parsed_query = self.parser.parse_sentence(queries[i])
                self.query_as_list.append(parsed_query)
                self.parser.final_terms_doc = []
        return self.query_as_list

    """
        Description : manage the files retrieve.
        classified the terms by their first letter and send each group of letter to 'generic_posting_reader'.
    """

    def relevant_docs_from_posting(self, query):

        self.relevant_docs = {}
        # query expansion --> global method from ranker
        all_terms_query = {}
        for term in query:
            if not self.inverted_index.__contains__(term) and not self.inverted_index.__contains__(term.lower()):
                continue
            key = self.init_relevant_keys(term)
            if all_terms_query.__contains__(key):  # donald trump president tov : t: trump tov, d: donald, p: president
                all_terms_query[key].append(term)
            else:
                all_terms_query[key] = []
                all_terms_query[key].append(term)
        for key in all_terms_query:
            self.generic_posting_reader(all_terms_query[key], key)
        return self.relevant_docs

    """
    Description : load the corresponding posting doc and calc tf idf for each doc for term and summing all to the 
    dot product of the doc
    """

    def generic_posting_reader(self, classified_terms_dict, key):
        start_load = time.time()
        if self.is_stemming:
            posting = utils.load_obj(
                self.config.outputPath + 'Posting_final_' + key.lower() + "_WithStem")  # e.g final_posting_a.pkl
        else:
            posting = utils.load_obj(self.config.outputPath + 'Posting_final_' + key.lower() + "_WithoutStem")
        print(key + ' load: ' + str(time.time() - start_load))
        for term in classified_terms_dict:  # loop on each term from query
            start = time.time()
            try:
                try:
                    docs_list = posting[term.lower()]
                except:
                    docs_list = posting[term.upper()]
                idf = math.log(self.total_num_of_docs / len(docs_list))
                for doc_tuple in docs_list:
                    doc_id = doc_tuple[0]
                    tf = float(doc_tuple[1])
                    try:
                        self.relevant_docs[doc_id] += (tf * idf)
                    except:
                        self.relevant_docs[doc_id] = (tf * idf)

            except:
                continue
            print(term + ': ' + str(time.time() - start))

    """
        Description : help func
        return the appropriate key
    """
    def init_relevant_keys(self, term):
        if term[0].isdigit():
            return 'num'
        elif term[0] == 'x' or term[0] == 'y' or term[0] == 'z' or \
                term[0] == 'X' or term[0] == 'Y' or term[0] == 'Z':
            return 'xyz'
        else:
            return term[0]
