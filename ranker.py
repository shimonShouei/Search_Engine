import heapq

from pandas import DataFrame

import utils

"""
~~~~~~~~~~~~~~~~~~~~~~~~  Module Description ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    This Module Contains rank class , its part is to rank result and expand query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class Ranker:
    def __init__(self):
        self.matrix = dict(utils.load_obj('cor_mat_as_dict'))
        self.n = 3

    """
        Description : sort the results by their rank
    """
    @staticmethod
    def rank_relevant_doc(relevant_doc):
        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    """
        Description : return top k
    """
    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=1):
        return sorted_relevant_doc[:k]

    """
        Description : expand query with the association matrix of the global method
    """
    def expand_query(self, query_terms):
        res = []
        for term in query_terms:
            if not self.matrix.__contains__(term):
                continue
            k_keys_sorted = heapq.nlargest(self.n, self.matrix[term], self.matrix[term].get)
            res.extend(k_keys_sorted)
        query_terms.extend(res)
        return query_terms
