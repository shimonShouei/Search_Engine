import utils
import pandas as pd


class GlobalMethod:

    def __init__(self, inverted_index, stemming, config):
        self.config = config
        self.inverted_index = inverted_index
        self.stemming = stemming

    def create_new_inverted_index(self):

        sorted_index = sorted(self.inverted_index.items(), key=lambda item: item[1][0], reverse=True)
        new_inverted_index = sorted_index[6000:10000]
        self.inverted_index = dict(new_inverted_index)
        return new_inverted_index

    def create_global_matrix(self):
        online_posting = {}
        sorted_inverted_index = sorted(self.create_new_inverted_index())
        df = pd.DataFrame(-1, self.inverted_index, self.inverted_index).astype(float)
        docs_id_dict = {}
        i = 0
        while i in range(len(sorted_inverted_index)):
            term = sorted_inverted_index[i][0]
            if not online_posting.__contains__(term):
                posting_dict = self.load_posting_file(term)
                online_posting[term] = posting_dict[term]
            docs_id_dict[term] = {x[0]: x[1] for x in online_posting[term]}
            j = i + 1
            while j in range(len(sorted_inverted_index)):
                term2 = sorted_inverted_index[j][0]

                if term == term2:
                    continue
                if online_posting.__contains__(term2):
                    online_posting[term2] = online_posting[term2]
                elif posting_dict.__contains__(term2):
                    online_posting[term2] = posting_dict[term2]
                else:
                    posting_dict = self.load_posting_file(term2)

                    online_posting[term2] = posting_dict[term2]

                # calculate sij
                cij = 0
                cii = 0
                cjj = 0
                for doc_id in online_posting[term2]:
                    if docs_id_dict[term].__contains__(doc_id[0]):
                        tf1 = docs_id_dict[term][doc_id[0]]
                        tf2 = doc_id[1]
                        cij += tf1 * tf2
                        cii += tf1 ** 2
                        cjj += tf2 ** 2
                if cii + cjj - cij != 0:
                    sij = cij / (cii + cjj - cij)
                else:
                    sij = 0
                # update matrix
                df[term][term2] = sij
                if df[term2][term] == -1:
                    df[term2][term] = sij
                df[term][term] = 0
                j += 1
            i += 1
            online_posting[term] = []
            posting_dict = {}
        # write matrix
        file_name = self.generate_file_name('correlation_matrix')
        utils.save_obj(df.astype(pd.SparseDtype("float", 0)), file_name + "_sparsed")
        utils.save_obj(df, file_name)

    def load_posting_file(self, term):
        key = term.lower()[0]
        if key == 'x' or key == 'y' or key == 'z':
            key = 'xyz'
        if key.isdigit():
            key = 'num'

        file_name = self.generate_file_name(key)
        return utils.load_obj(file_name)

    def generate_file_name(self, key):
        if self.stemming:
            stemming = 'WithStem'
        else:
            stemming = 'WithoutStem'
        file_name = self.config.outputPath + "Posting_final_" + key + '_' + stemming
        return file_name