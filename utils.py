import csv
import pickle

def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(name + '.pkl', 'wb') as f:
        # f = bz2.BZ2File(name)
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        f.close()

def save_obj_by_line(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(name + '.pkl', 'wb') as f:
        for val in obj.values():
            pickle.dump(val, f, pickle.HIGHEST_PROTOCOL)
        f.close()


def add_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open(name + '.pkl', 'ab') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_line(name, line):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open(name + '.pkl', 'rb') as f:
        line = pickle.load(f.readline(line))
        f.close()
        return line

def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open(name + '.pkl', 'rb') as f:
        obj = pickle.load(f)
        f.close()
        return obj

def load_appended_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open(name + '.pkl', 'rb') as f:
        objs = []
        while 1:
            try:
                objs.append(pickle.load(f))
            except EOFError:
                break
    return objs

def save_csv(name, obj):
    with open(name+'.csv', mode='a',newline='') as f:
        c = csv.writer(f)
        for elm in obj:
            print('tweet id: {}, score: {}'.format(elm[0], elm[1]))
            c.writerow(["{}".format(elm[0]),"{:f}".format(elm[1])])


def load_inverted_index():
    print('Load inverted index')
    inverted_index = load_obj("posting/inverted_index")
    return inverted_index