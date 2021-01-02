import search_engine
from configuration import ConfigClass


if __name__ == '__main__':
    search_engine.main('Data','posting', stemming=False, queries='queries.txt',num_docs_to_retrieve=2000)
