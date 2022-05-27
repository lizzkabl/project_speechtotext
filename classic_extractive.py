import typing
import networkx as nx
import spacy_stanza
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from spacy.tokens import Doc
from spacy import Language
import pytextrank
import torch
from navec import Navec
import numpy as np
import stanza
from spacy_stanza import Language

NUM_SENTENCES = 3
vector=[]

NAVEC_UNKNOWN_TOKEN = "<unk>"

path = r'C:\Users\user\Desktop\bot\navec_news_v1_1B_250K_300d_100q.tar'
navec_embeddings= Navec.load(path)

# better sentencebert model
SBERT_MODEL_NAME = "sentence-transformers/paraphrase-mpnet-base-v2"
SBERT_CONFIG = {
    "model": {
        "@architectures": "spacy-transformers.TransformerModel.v1",
        "name": SBERT_MODEL_NAME,
        "get_spans": {"@span_getters": "spacy-transformers.sent_spans.v1"},
    }
}


def build_classic_nlp_pipeline():
    stanza.download('ru')
    nlp = spacy_stanza.load_pipeline("ru")
    return nlp

class SentenceTextRank:
    def __init__(self, doc):
        self.doc = doc
        self.transformer_ranks = self.trfembeddings_textrank()
        self.wordembedding_ranks = self.wordembeddings_textrank()
        self.sentences = [sent for sent in doc.sents]

    def _sentence_rank(self, sentence_vectors):
        """Rank sentences by importance.

        Takes a list of sentence_vectors and computes pair-wise cosine similarity
        between all sentences. A graph is constructed with the sentence_vectors as
        nodes and cosine similarity as edges.
        Pagerank algorithm is run on the graph and scores returned.
        """
        cossims = cosine_similarity(sentence_vectors)
        # cosine similarity occasionally returns negative values
        # but pagerank doesn't work on negative values, so make them not negative.
        cossims[cossims < 0] = 0
        nx_graph = nx.from_numpy_array(cossims)
        return nx.pagerank(nx_graph)

    def trfembeddings_textrank(self):
        sentence_vectors = self.get_transformer_embeddings()
        try:
            return self._sentence_rank(np.array(sentence_vectors.cpu()))
        except (ValueError, AttributeError):
            return None

    def wordembeddings_textrank(self):
        sentence_vectors = self.get_sentence_embeddings()
        try:
            return self._sentence_rank(sentence_vectors)
        except ValueError:
            return None
    @staticmethod
    def navec_word_vectorizer(word):
        try:
            return navec_embeddings[word]
        except:
            return navec_embeddings[NAVEC_UNKNOWN_TOKEN]
    def get_transformer_embeddings(self):
        try:
            def get_navec_word_vectorizer(word):
                NAVEC_EMBEDDING_DIMENSION = navec_embeddings.get(NAVEC_UNKNOWN_TOKEN).shape[0]



                return self.navec_word_vectorizer(word)

            for word in self.doc:
                vector.append(get_navec_word_vectorizer(word))


            token_embeddings = torch.tensor(vector)
        except IndexError:
            # tokens may not exist if document is empty
            return None
        else:
            return token_embeddings

    def get_sentence_embeddings(self):
        try:
            # if using spaCy on GPU, convert cupy arr --> numpy arr with get()
            return [sent.vector.get() for sent in self.doc.sents]
        except:
            return [sent.vector for sent in self.doc.sents]

    def _mean_pooling(self, token_embeddings, attention_mask):
        """Take attention mask into account for correct averaging of sentence-bert tokens"""
        # This was adapted from a HuggingFace Model Repo example by the
        # Sentence-Transformer team for the model used here:
        # https://huggingface.co/sentence-transformers/paraphrase-mpnet-base-v2
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    def generate_summary(
            self,
            *,
            transformer_ranks=False,
            limit_sentences=5,
            preserve_order=True,
            return_scores=False
    ):
        """Generate an extractive summary of the doc."""
        if transformer_ranks:
            scores = self.transformer_ranks
        else:
            scores = self.wordembedding_ranks
        if scores:
            # order by rank
            ranked_sentences = sorted(
                ((scores[i], i, s) for i, s in enumerate(self.sentences)), reverse=True
            )
            summary = ranked_sentences[:limit_sentences]
            if preserve_order:
                # rerank by index in the doc
                summary = sorted(summary, key=lambda x: x[1])
            if return_scores:
                return [(s, str(sent)) for s, i, sent in summary]
            else:
                return " ".join([str(sent) for s, i, sent in summary])
        return None


def sentence_summary_trf(text: str, nlp: Language, **kwargs) -> str:
    """Generate a summary with a TextRank model constructed from sentences.

    This version of TextRank uses the PageRank algorithm on sentence embeddings
    (constructed SentenceBERT embeddings) and cosine similarities to
    determine the most important sentences in the document. The highest ranked
    sentences are extracted as the document summary.
    """
    doc = nlp(text)
    sent_tr = SentenceTextRank(doc)
    return sent_tr.generate_summary(
        transformer_ranks=True, limit_sentences=NUM_SENTENCES
    )


text1 = "Вопросы международного правопреемства регулируются Венской конвенцией о правопреемстве государств в " \
        "отношении договоров (1978 г.) и Венской конвенцией о правопреемстве государств в отношении государственной " \
        "собственности, государственных архивов и государственных долгов (1983 г.). В договоре о правопреемстве в " \
        "отношении внешнего государственного долга и активов Союза ССР от 4 декабря 1991 г. правопреемство " \
        "определяется следующим образом: «Статья 1… в) правопреемство государств означает смену одного государства " \
        "другим в несении ответственности за международные отношения какой-либо территории; г) " \
        "государство-предшественник означает государство, которое было сменено другим государством в случае " \
        "правопреемства государства; д) государство-преемник означает государство, которое сменило другое государство " \
        "в случае правопреемства государств; е) момент правопреемства государств означает дату смены " \
        "государством-преемником государства-предшественника в несении ответственности за международные отношения " \
        "применительно к территории, являющейся объектом правопреемства государств…»[28]. Такое определение впервые " \
        "было закреплено а в статье 2 Венской конвенции 1978 года. Оно также содержится в статье 2 Венской конвенции " \
        "1983 года[29]. "
nlp=build_classic_nlp_pipeline()

print(sentence_summary_trf(text=text1, nlp=nlp))
