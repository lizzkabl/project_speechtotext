
import extoracle.utils

METHODS = {
    "greedy": extoracle.utils.greedy_selection,
    "combination": extoracle.utils.combination_selection,
}


def _clean_line(line):
    return line.strip()


def split_text(txt, trunc=None):
    """Split text into sentences/words

    Args:
        txt(str): text, as a single str
        trunc(int): if not None, stop splitting text after `trunc` words
                    and ignore sentence containing `trunc`-th word
                    (i.e. each sentence has len <= trunc)
    Returns:
        sentences(list): list of sentences (= list of lists of words)
    """
    n_words = 0
    sentence_break = [".", "?", "!"]
    sentences = []
    cur_sentence = []
    for word in txt.split():
        if word in sentence_break:
            if len(cur_sentence) != 0:
                cur_sentence.append(word)
                sentences.append(cur_sentence)
                cur_sentence = []
            else:
                pass
        else:
            n_words += 1
            cur_sentence.append(word)

        if trunc is not None and n_words > trunc:
            cur_sentence = []
            break

    if len(cur_sentence) != 0:
        sentences.append(cur_sentence)
    return sentences


def process_example(example):
    (method,
        src_line,
        tgt_line,
        trunc_src,
        summary_length,
        length_oracle,) = example

    src_line = _clean_line(src_line)
    tgt_line = _clean_line(tgt_line)

    src_sentences = split_text(src_line, trunc=trunc_src)
    tgt_sentences = split_text(tgt_line)

    if length_oracle:
        summary_length = len(tgt_sentences)

    ids, sents = method(src_sentences, tgt_sentences, summary_length)
    return ids, sents


