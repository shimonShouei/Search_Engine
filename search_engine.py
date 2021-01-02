from time import time
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils

"""
    Description : read parquet, parse each tweet, index it an write it to the appropriate posting doc.
    in the end merge it.
"""


def run_engine(config):
    # stemming, parser, reader and indexer initialize
    is_stemming = config.toStem
    reader = ReadFile(config.corpusPath)
    p = Parse(is_stemming)
    indexer = Indexer(config, is_stemming)
    files_names = reader.files_names.keys()  # get all parquet files names
    number_of_documents = 0

    for name_file in files_names:
        documents_list = reader.read_one_file(name_file)
        idx = 0
        for doc in documents_list:
            # parse the document
            parsed_document = p.parse_doc(doc)
            # index the document data
            indexer.add_new_doc(parsed_document)
            number_of_documents += 1
            indexer.posting_doc(parsed_document)
            idx += 1
    indexer.merge_posting_files()
    # write to disk the last docs from dict
    if len(indexer.posting_doc_dict) > 0:
        indexer.write_posting_doc(indexer.posting_doc_dict)
    return number_of_documents


"""
    Description : read the queries, parse them, expand them by the global method matrix, find the relevant docs by dot 
    product ranking and return top k results
"""


def search_and_rank_query(queries, inverted_index, k, data_size, config):
    final_ranked_results = []
    searcher = Searcher(inverted_index, config, data_size)
    # read and parse queries from input file
    parsed_queries = searcher.handle_files(queries)
    i = 1
    for query in parsed_queries:
        # expand query by global method matrix
        start = time()
        query = searcher.ranker.expand_query(query)
        print(str(i) + ' expand_time: ' + str(time() - start))
        relevant_docs_query = searcher.relevant_docs_from_posting(query)
        rank_start = time()
        ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs_query)
        ranked_docs = searcher.ranker.retrieve_top_k(ranked_docs, k)
        print(str(i) + ': rank time = ' + str(time() - rank_start))
        print(str(i) + ' toatal_time: ' + str(time() - start))
        i += 1
        for doc in ranked_docs:
            print('tweet id: {}, score: {}'.format(doc[0], doc[1]))
    return final_ranked_results


"""
    Description : main function for assignment system
"""


def main(corpus_path, output_path='', stemming=False, queries='', num_docs_to_retrieve=0):
    config = ConfigClass(corpus_path, output_path, stemming)
    # data_size = run_engine(config)
    data_size = 10000000
    inverted_index = utils.load_inverted_index()
    search_and_rank_query(queries, inverted_index, num_docs_to_retrieve, data_size, config)
