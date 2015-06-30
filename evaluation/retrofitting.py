import numpy as np
from scipy import sparse
import pickle
from assoc_space import AssocSpace, LabelSet
from conceptnet5.builders.retrofit_glove import retrofit
from sklearn.preprocessing import normalize
from wordsim import test, text_to_vector

def save_csr_matrix(matrix, filename):
    np.savez(filename, data=matrix.data, indices=matrix.indices,
                indptr=matrix.indptr, shape=matrix.shape)

def load_csr_matrix(filename):
    matrix = np.load(filename)
    return sparse.csr_matrix((matrix['data'], matrix['indices'], matrix['indptr']), shape=matrix['shape'])

def sort_by_relavence(assoc, seq):
    return sorted(seq, key=lambda x: text_to_vector(x[0], assoc).dot(text_to_vector(x[1], assoc)))

def gen_assoc(normalize_sparse=True, normalize_vectors='l1', retrofit_vectors=False, normalize_intermediate=False):

    print("Loading labels")
    labels = pickle.load(open('/data/retrofitting/glove_labels.pickle', mode='rb'))
    labels = LabelSet(labels)

    print("Loading word vectors")
    vectors = np.load('/data/retrofitting/glove.npy')

    if normalize_vectors:
        print("%s Normalizing vectors"%normalize_vectors)
        vectors = normalize(vectors, norm=normalize_vectors, axis=0)

    if retrofit_vectors:

        print("Loading sparse matrix")
        sparse = load_csr_matrix('/data/retrofitting/conceptnet_sparse.npz')

        if normalize_sparse:
            #must be l1 normalized or diverges
            print("l1 Normalizing sparse matrix")
            sparse = normalize(sparse, norm='l1', axis=1)

        vectors = retrofit(vectors, sparse, labels, normalize_intermediate=normalize_intermediate)

    return AssocSpace(vectors, np.ones(len(vectors[0])), labels, assoc=vectors)

def main():
    test(gen_assoc())

if __name__ == '__main__':
    main()