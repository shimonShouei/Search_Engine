import math
import os
import string
from configuration import ConfigClass
from document import Document
import utils

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Module Description ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    This Module Contains Indexer class , its part is to saving the data on the terms and docs.
    It also used for creates the inverted index dictionary for terms and docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


"""
      Class Description :
          This Class is used for creating inverted index for terms and docs
          It also used for saving the data in files.
"""
class Indexer:

    """
          Description :initialize properties of Indexer object
    """
    def __init__(self, config: ConfigClass, stemming):
        self.inverted_idx = {}  # contains  all terms from different documents
        self.postingDict = {}
        self.pointers = {}
        self.config = config
        self.total_dicts = {}
        self.num_of_posting = {}
        for letter in string.ascii_lowercase:  # loop on a-z
            if letter == 'x':
                self.total_dicts['xyz'] = {}
                self.num_of_posting['xyz'] = 0
                self.pointers['xyz'] = [0, 'final_xyz']
                break
            self.total_dicts[letter] = {}
            self.num_of_posting[letter] = 0
            self.pointers[letter] = [0, 'final_' + letter]
        self.total_dicts['num'] = {}
        self.total_dicts['#'] = {}
        self.total_dicts['@'] = {}
        self.total_dicts['else'] = {}  # $fdkdkf$kfkfb
        self.num_of_posting['num'] = 0
        self.num_of_posting['#'] = 0
        self.num_of_posting['@'] = 0
        self.num_of_posting['else'] = 0
        self.pointers['num'] = [0, 'final_num']
        self.pointers['#'] = [0, 'final_#']
        self.pointers['@'] = [0, 'final_@']
        self.num_of_docs = 0
        self.counter_docs = 0
        self.chunk_posting_size = 250000  # how many docs in a temporary posting file
        self.chunk_terms = 1000
        self.stemming = stemming
        self.num_of_postingsFile = 0
        self.doc_pointer = 0
        self.posting_doc_dict = {}

    """
        Description: creates all the final posting files for docs 
    """
    def posting_doc(self, document: Document):
        if len(document.term_doc_dictionary) > 0:
            self.posting_doc_dict[document.tweet_id] = [document.max_tf, document.unique_terms_count,
                                                        document.doc_length]
            if self.counter_docs == self.chunk_posting_size:
                self.write_posting_doc(self.posting_doc_dict)
            else:
                self.counter_docs += 1

    def write_posting_doc(self, dict):
        file_name = self.generate_file_name('Documents')
        utils.add_obj(dict, file_name)
        self.posting_doc_dict = {}
        self.counter_docs = 0

    def generate_file_name(self, key):
        if key == 'inverted_index':
            write_file_name = key
            return write_file_name
        else:
            name = 'Posting_' + key
        if self.stemming:
            write_file_name = self.config.outputPath + name + '_WithStem'
        else:
            write_file_name = self.config.outputPath + name + '_WithoutStem'
        return write_file_name

    """
        Description: creates all the temporary posting files for terms 
    """
    def add_new_doc(self, document: Document):
        doc_terms_dict = document.term_doc_dictionary
        if len(doc_terms_dict.keys()) > 0:
            for term in doc_terms_dict.keys():
                if term[0] == "@" or term[0] == "#" or term[0].isdigit():
                    term_flag = " "
                    lower_term = term
                elif term.islower():
                    term_flag = "l"  # concat l to term that indicates is lowercase letter
                    lower_term = term.lower()
                elif term.__contains__(" "):
                    term_flag = "se"  # concat se to term that suspected as an entity
                    lower_term = term.lower()
                else:
                    term_flag = "u"  # concat u to term that indicates is uppercase letter
                    lower_term = term.lower()

                if lower_term[0].isdigit():
                    key = 'num'
                elif 'a' <= lower_term[0] <= 'w':
                    key = lower_term[0]
                elif 'x' <= lower_term[0] <= 'z':
                    key = 'xyz'
                elif lower_term[0] == '@' or lower_term[0] == '#':
                    key = lower_term[0]
                else:
                    key = 'else'

                tf_normal = doc_terms_dict[term] / document.max_tf
                # Update inverted index and posting
                if lower_term not in self.total_dicts[key].keys():
                    self.total_dicts[key][lower_term] = [[[document.tweet_id, tf_normal]], tf_normal, 1, term_flag]

                else:  # the term is already exists in the dict
                    value = self.total_dicts[key][lower_term]
                    # sorted_docs = self.insert_doc(value[0], [document.tweet_id, tf_normal])
                    value[0].append([document.tweet_id, tf_normal])
                    # value[0].sort(key = self.compare)
                    sorted_docs = value[0]
                    term_flag_in_dict = value[3]
                    total_tf = tf_normal + value[1]
                    df = value[2] + 1
                    if term_flag_in_dict != term_flag:
                        if term_flag_in_dict == "e":
                            term_flag = "e"
                        else:
                            term_flag = "l"
                    elif term_flag == "se":
                        term_flag = "e"
                    self.total_dicts[key][lower_term] = [sorted_docs, total_tf, df, term_flag]

            self.num_of_docs += 1
            if self.num_of_docs == self.chunk_posting_size:
                self.posting_terms()
                self.num_of_docs = 0

    def posting_terms(self, last=False):
        for key in self.total_dicts.keys():
            if key == 'else':
                continue
            if len(self.total_dicts[key]) > self.chunk_terms or (len(self.total_dicts[key]) > 0 and last):
                self.num_of_posting[key] += 1
                file_name = self.generate_file_name(key + str(self.num_of_posting[key]))
                utils.save_obj(self.total_dicts[key], file_name)
                self.total_dicts[key] = {}

    """
        Description: creates all the final posting files for terms
    """
    def merge_posting_files(self):
        # save remain dicts
        self.posting_terms(True)  # write last terms from last round
        for key in self.total_dicts.keys():
            if key == "else":
                continue
            str1 = ''
            str2 = ''
            if self.stemming:
                str2 += "S"
            else:
                str2 += "R"
            num_of_merge_file = 1
            self.num_of_postingsFile = self.num_of_posting[key]
            if self.num_of_postingsFile == 1:
                self.handle_one_posting_file(key + str(1), self.pointers[key][1])
                continue

            while self.num_of_postingsFile > 2:
                new_num_of_postingsFile = math.ceil(self.num_of_postingsFile / 2)

                idx = 1
                while idx in range(self.num_of_postingsFile):
                    file_name1 = self.generate_file_name(key + str(idx) + str1)
                    file1 = utils.load_obj(file_name1)

                    file_name2 = self.generate_file_name(key + str(idx + 1) + str1)
                    file2 = utils.load_obj(file_name2)

                    merged_dict = self.merge_files(file1, file2)

                    self.remove_old_files(file_name1)
                    self.remove_old_files(file_name2)

                    write_file_name = self.generate_file_name(key + str(num_of_merge_file) + str2)
                    utils.save_obj(merged_dict, write_file_name)

                    num_of_merge_file += 1
                    idx = idx + 2

                if new_num_of_postingsFile > num_of_merge_file - 1:
                    self.handle_one_posting_file(key + str(idx) + str1, key + str(num_of_merge_file) + str2)

                # Promotes while
                self.num_of_postingsFile = new_num_of_postingsFile
                num_of_merge_file = 1
                str1 = str2
                if self.stemming:
                    str2 += "S"
                else:
                    str2 += "R"
            # end while

            # merge the two temporary last files and create the inverted index and the final posting files
            file_name1 = self.generate_file_name(key + str(1) + str1)
            file1 = utils.load_obj(file_name1)
            file_name2 = self.generate_file_name(key + str(2) + str1)
            file2 = utils.load_obj(file_name2)

            if len(file1.keys()) < len(file2.keys()):
                shorter_dict = file1
                longer_dict = file2
            else:
                shorter_dict = file2
                longer_dict = file1

            for (key1, val) in shorter_dict.items():
                self.pointers[key][0] += 1
                exists = longer_dict.__contains__(key1)
                if exists:  # the term in file 1 is equal to the term in file 2
                    # update values
                    updated_value = self.update(val, longer_dict[key1])
                    del longer_dict[key1]
                    # insert to inverted index
                    self.insert_to_inverted_index(key1, self.pointers[key][0], updated_value)
                else:  # the term in file 1 is not equal to the term in file 2
                    # insert to inverted index
                    self.insert_to_inverted_index(key1, self.pointers[key][0], val)

            # merge the remain keys in the longer dict
            for (key2, val) in longer_dict.items():
                self.pointers[key][0] += 1
                self.insert_to_inverted_index(key2, self.pointers[key][0], val)

            # write to final file
            write_file_name = self.generate_file_name(self.pointers[key][1])
            utils.save_obj(self.postingDict, write_file_name)
            self.postingDict = {}

            # remove old files
            self.remove_old_files(file_name1)
            self.remove_old_files(file_name2)

        # write inverted index to the disk
        write_file_name = self.generate_file_name('inverted_index')
        utils.save_obj(self.inverted_idx, write_file_name)
        self.inverted_idx = {}


    def handle_one_posting_file(self, file_name, write_file_name):
        file_name = self.generate_file_name(file_name)
        write_file_name = self.generate_file_name(write_file_name)
        file = utils.load_obj(file_name)
        utils.save_obj(file, write_file_name)
        self.remove_old_files(file_name)

    """
         Description: get two posting files and creates a new merged posting file 
    """
    def merge_files(self, file1, file2):
        merged_dict = {}
        if len(file1.keys()) < len(file2.keys()):
            shorter_dict = file1
            longer_dict = file2
        else:
            shorter_dict = file2
            longer_dict = file1

        for (key, val) in shorter_dict.items():
            exists = longer_dict.__contains__(key)

            if exists:  # the term in file 1 is equal to the term in file 2
                # update values
                updated_value = self.update(val, longer_dict[key])
                del longer_dict[key]
                merged_dict[key] = updated_value

            else:  # the term in file 1 is not equal to the term in file 2
                merged_dict[key] = val

        # merge the remain keys
        merged_dict.update(longer_dict)
        return merged_dict

    """
        Description: get to values and creates an updated new value
            updated_value[0] is the documents the term exist in and its tf in each document
            updated_value[1] is the total tf - sum of tf in each document in all the corpus
            updated_value[2] is the df- in how many docs the term exist
            updated_value[3] is one from the flags:  se- Suspected as an entity, u- upper letter, l - lower letter
    """
    def update(self, val, val2):
        if val[3] == "e" or val2[3] == "e":
            term_flag = "e"
        elif val[3] == val2[3]:  # is the same flag (e,e  se,se l,l u,u "" ,"")
            if val[3] == "e" or val[3] == "se":
                term_flag = "e"
            else:
                term_flag = val[3]
        else:
            term_flag = "l"

        total_tf = int(val[1]) + int(val2[1])
        df = int(val[2]) + int(val2[2])
        val[0].extend(val2[0])
        merged_docs = val[0]
        updated_value = [merged_docs, total_tf, df, term_flag]
        return updated_value

    """
        Description: insert final terms to inverted index dict with pointer to their posting file
    """
    def insert_to_inverted_index(self, term, pointer, value):
        final_term = ''
        if value[3] == "l":
            final_term = term.lower()
        elif value[3] == "e" or value[3] == "u":
            final_term = term.upper()
        elif value[3] == " ":
            final_term = term
        if final_term != '':
            self.inverted_idx[final_term] = [value[1], value[2], pointer]
            self.postingDict[final_term] = value[0]

    """
        Description: get file name and remove it
    """
    def remove_old_files(self, file_name):
        file_to_remove = file_name + ".pkl"
        os.remove(file_to_remove)
