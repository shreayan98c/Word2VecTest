#!/usr/bin/env python3
"""
Determine most similar words in terms of their word embeddings.
"""
# JHU NLP HW2
# Name: Shreayan Chaudhary
# Email: schaud31@jhu.edu
# Term: Fall 2022

from __future__ import annotations
import argparse
import logging
from pathlib import Path
from integerize import Integerizer  # look at integerize.py for more info

# For type annotations, which enable you to check correctness of your code:
from typing import List, Optional

try:
    # PyTorch is your friend. Not *using* it will make your program so slow.
    # And it's also required for this assignment. ;-)
    # So if you comment this block out instead of dealing with it, you're
    # making your own life worse.
    #
    # We made this easier by including the environment file in this folder.
    # Install Miniconda, then create and activate the provided environment.
    import torch as th
    import torch.nn as nn
except ImportError:
    print("\nERROR! Try installing Miniconda and activating it.\n")
    raise

log = logging.getLogger(Path(__file__).stem)  # The only okay global variable.


# Logging is in general a good practice to check the behavior of your code
# while it's running. Compared to calling `print`, it provides two benefits.
# - It prints to standard error (stderr), not standard output (stdout) by
#   default. This means it won't interfere with the real output of your
#   program. 
# - You can configure how much logging information is provided, by
#   controlling the logging 'level'. You have a few options, like
#   'debug', 'info', 'warning', and 'error'. By setting a global flag,
#   you can ensure that the information you want - and only that info -
#   is printed. As an example:
#        >>> try:
#        ...     rare_word = "prestidigitation"
#        ...     vocab.get_counts(rare_word)
#        ... except KeyError:
#        ...     log.error(f"Word that broke the program: {rare_word}")
#        ...     log.error(f"Current contents of vocab: {vocab.data}")
#        ...     raise  # Crash the program; can't recover.
#        >>> log.info(f"Size of vocabulary is {len(vocab)}")
#        >>> if len(vocab) == 0:
#        ...     log.warning(f"Empty vocab. This may cause problems.")
#        >>> log.debug(f"The values are {vocab}")
#   If we set the log level to be 'INFO', only the log.info, log.warning,
#   and log.error statements will be printed. You can calibrate exactly how 
#   much info you need, and when. None of these pollute stdout with things 
#   that aren't the real 'output' of your program.
#
# In `parse_args`, we provided two command line options to control the logging level.
# The default level is 'INFO'. You can lower it to 'DEBUG' if you pass '--verbose'
# and you can raise it to 'WARNING' if you pass '--quiet'. 


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("embeddings", type=Path, help="Path to word embeddings file.")
    parser.add_argument("word", type=str, help="Word to lookup")
    parser.add_argument("--minus", type=str, default=None)
    parser.add_argument("--plus", type=str, default=None)

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    verbosity.add_argument("-q", "--quiet", dest="verbose", action="store_const", const=logging.WARNING)

    args = parser.parse_args()
    if not args.embeddings.is_file():
        parser.error("You need to provide a real file of embeddings.")
    if (args.minus is None) != (args.plus is None):  # != is the XOR operation!
        parser.error("Must include both of `plus` and `minus` or neither.")

    return args


class Lexicon:
    """
    Class that manages a lexicon and can compute similarity.

    >>> my_lexicon = Lexicon.from_file(my_file)
    >>> my_lexicon.find_similar_words(bagpipe)
    """

    def __init__(self) -> None:
        """Load information into coupled word-index mapping and embedding matrix."""
        # FINISH THIS FUNCTION
        # Store your stuff! Both the word-index mapping and the embedding matrix.

        # Initializing the Lexicon class variables
        self.n_dims = None
        self.n_words = None
        self.vocab = None
        self.word_list = []
        self.embeddings = []

        # Do something with this size info?
        # PyTorch's th.Tensor objects rely on fixed-size arrays in memory.
        # One of the worst things you can do for efficiency is
        # append row-by-row, like you would with a Python list.
        # Probably make the entire list all at once, then convert to a th.Tensor.
        # Otherwise, make the th.Tensor and overwrite its contents row-by-row.

    @classmethod
    def from_file(cls, file: Path) -> Lexicon:
        # FINISH THIS FUNCTION
        word_list = []
        embeddings = []

        # reading the file and storing the embeddings and the words
        with open(file) as f:
            first_line = next(f)  # Peel off the special first line.
            n_words, n_dims = map(int, first_line.split())
            for line in f:  # All of the other lines are regular.
                line = line.strip('\n')
                parse_line = line.split('\t')
                word = parse_line[0]
                word_embedding = list(map(float, parse_line[1:]))
                word_list.append(word)
                embeddings.append(word_embedding)

        # creating the lexicon object and assigning values to the class variables
        lexicon = Lexicon()  # Maybe put args here. Maybe follow Builder pattern.
        lexicon.n_words = n_words
        lexicon.n_dims = n_dims
        lexicon.word_list = word_list
        lexicon.vocab = Integerizer(word_list)
        lexicon.embeddings = th.Tensor(embeddings)
        return lexicon

    def find_similar_words(
            self, word: str, *, plus: Optional[str] = None, minus: Optional[str] = None
    ) -> List[str]:
        """Find most similar words, in terms of embeddings, to a query."""
        # FINISH THIS FUNCTION

        # The star above forces you to use `plus` and `minus` as
        # named arguments. This helps avoid mixups or readability
        # problems where you forget which comes first.

        # We've also given `plus` and `minus` the type annotation
        # Optional[str]. This means that the argument may be None, or
        # it may be a string. If you don't provide these, it'll automatically
        # use the default value we provided: None.
        if (minus is None) != (plus is None):  # != is the XOR operation!
            raise TypeError("Must include both of `plus` and `minus` or neither.")

        # Keep going!
        word_idx = self.vocab.index(word)
        vector_space = self.embeddings
        source_word_embedding = self.embeddings[word_idx]
        resultant_embedding = source_word_embedding

        # if user provides the plus and minus words
        if plus and minus:
            if plus not in self.vocab or minus not in self.vocab:
                raise Exception('Either plus or minus word not found in vocab!')
            plus_word_idx = self.vocab.index(plus)
            minus_word_idx = self.vocab.index(minus)
            plus_word_embedding = self.embeddings[plus_word_idx]
            minus_word_embedding = self.embeddings[minus_word_idx]
            resultant_embedding = th.add(th.subtract(source_word_embedding, minus_word_embedding), plus_word_embedding)

        # repeat the array for words and calc the product
        rpt_resultant_embedding = resultant_embedding.repeat(self.n_words, 1)

        # finding out the cosine similarities
        cos = nn.CosineSimilarity(dim=1)
        similarity = cos(rpt_resultant_embedding, vector_space)

        # Be sure that you use fast, batched computations
        # instead of looping over the rows. If you use a loop or a comprehension
        # in this function, you've probably made a mistake.

        # if user provides the plus and minus words, the most similar words will be handled differently
        if plus and minus:
            # if user has provided any plus or minus, return the 10 most similar words after removing the plus and
            # minus words from them
            most_similar_indices = th.topk(similarity, 13, largest=True, sorted=True)

            # index 0 will be the word given by the user and indexes 1-13 might contain the plus and the minus word
            # so we need to remove them
            most_similar_words = [self.vocab[idx] for idx in most_similar_indices.indices[1:] if
                                  (idx != plus_word_idx and idx != minus_word_idx)][:10]

        else:
            # if user hasn't provided any plus or minus, just return the 10 most similar words
            most_similar_indices = th.topk(similarity, 11, largest=True, sorted=True)

            # taking index 1 onwards because 0 index will be for the word itself, and we want to ignore that
            most_similar_words = [self.vocab[idx] for idx in most_similar_indices.indices[1:]][:10]

        return most_similar_words


def format_for_printing(word_list: List[str]) -> str:
    # We don't print out the list as-is; the handout
    # asks that you display it in a particular way.
    # FINISH THIS FUNCTION
    similar_words = ' '.join(word_list)
    return similar_words


def main():
    args = parse_args()
    logging.basicConfig(level=args.verbose)
    lexicon = Lexicon.from_file(args.embeddings)
    similar_words = lexicon.find_similar_words(args.word, plus=args.plus, minus=args.minus)
    print(format_for_printing(similar_words))


if __name__ == "__main__":
    main()
