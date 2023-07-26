import numpy as np
from scipy.sparse.csgraph import connected_components
import nltk
nltk.download('punkt')

def _power_method(transition_matrix, increase_power=True):
    eigenvector = np.ones(len(transition_matrix))

    if len(eigenvector) == 1:
        return eigenvector

    transition = transition_matrix.transpose()

    while True:
        eigenvector_next = np.dot(transition, eigenvector)

        if np.allclose(eigenvector_next, eigenvector):
            return eigenvector_next

        eigenvector = eigenvector_next

        if increase_power:
            transition = np.dot(transition, transition)


def connected_nodes(matrix):
    _, labels = connected_components(matrix)

    groups = []

    for tag in np.unique(labels):
        group = np.where(labels == tag)[0]
        groups.append(group)

    return groups


def create_markov_matrix(weights_matrix):
    n_1, n_2 = weights_matrix.shape
    if n_1 != n_2:
        raise ValueError('\'weights_matrix\' should be square')

    row_sum = weights_matrix.sum(axis=1, keepdims=True)

    return weights_matrix / row_sum


def create_markov_matrix_discrete(weights_matrix, threshold):
    discrete_weights_matrix = np.zeros(weights_matrix.shape)
    ixs = np.where(weights_matrix >= threshold)
    discrete_weights_matrix[ixs] = 1

    return create_markov_matrix(discrete_weights_matrix)


def graph_nodes_clusters(transition_matrix, increase_power=True):
    clusters = connected_nodes(transition_matrix)
    clusters.sort(key=len, reverse=True)

    centroid_scores = []

    for group in clusters:
        t_matrix = transition_matrix[np.ix_(group, group)]
        eigenvector = _power_method(t_matrix, increase_power=increase_power)
        centroid_scores.append(eigenvector / len(group))

    return clusters, centroid_scores


def stationary_distribution(
        transition_matrix,
        increase_power=True,
        normalized=True,
):
    n_1, n_2 = transition_matrix.shape
    if n_1 != n_2:
        raise ValueError('\'transition_matrix\' should be square')

    distribution = np.zeros(n_1)

    grouped_indices = connected_nodes(transition_matrix)

    for group in grouped_indices:
        t_matrix = transition_matrix[np.ix_(group, group)]
        eigenvector = _power_method(t_matrix, increase_power=increase_power)
        distribution[group] = eigenvector

    if normalized:
        distribution /= n_1

    return distribution


def degree_centrality_scores(
        similarity_matrix,
        threshold=None,
        increase_power=True,
):
    if not (
            threshold is None
            or isinstance(threshold, float)
            and 0 <= threshold < 1
    ):
        raise ValueError(
            '\'threshold\' should be a floating-point number '
            'from the interval [0, 1) or None',
        )

    if threshold is None:
        markov_matrix = create_markov_matrix(similarity_matrix)

    else:
        markov_matrix = create_markov_matrix_discrete(
            similarity_matrix,
            threshold,
        )

    scores = stationary_distribution(
        markov_matrix,
        increase_power=increase_power,
        normalized=False,
    )

    return scores


def sentence_transformer_summarize(text):
    import_err_msg = (
        "`sentence_transformers` package not found, please run `pip install sentence_transformers==2.2.2`"
    )
    try:
        from sentence_transformers import SentenceTransformer, util
    except ImportError:
        raise ImportError(import_err_msg)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = nltk.sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences]
    embeddings = model.encode(sentences, convert_to_tensor=True)
    cos_scores = util.cos_sim(embeddings, embeddings).numpy()
    centrality_scores = degree_centrality_scores(cos_scores, threshold=None)
    most_central_sentence_indices = np.argsort(-centrality_scores)
    summary_text = ""
    for idx in most_central_sentence_indices[0:5]:
        summary_text += sentences[idx].strip() + '\n'
    return summary_text