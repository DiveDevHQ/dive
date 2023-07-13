from dive.vector_db.power_method import create_markov_matrix, create_markov_matrix_discrete, stationary_distribution
from sentence_transformers import SentenceTransformer, util
import nltk
import numpy as np


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


def get_text_summarization(text_list, llm):
    text = ''
    for t in text_list:
        text += t + '\n'

    model = SentenceTransformer(llm or 'all-MiniLM-L6-v2')

    sentences = nltk.sent_tokenize(text)
    sentences = [sentence.strip() for sentence in sentences]

    embeddings = model.encode(sentences, convert_to_tensor=True)

    cos_scores = util.cos_sim(embeddings, embeddings).numpy()

    centrality_scores = degree_centrality_scores(cos_scores, threshold=None)

    most_central_sentence_indices = np.argsort(-centrality_scores)
    summary_list = []
    for idx in most_central_sentence_indices[0:5]:
        summary_list.append(sentences[idx].strip())
    return summary_list
