from typing import Callable, List, Optional
from dataclasses import dataclass
from langchain.text_splitter import TextSplitter
from dive.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE


@dataclass
class TextSplit:
    """Text split with overlap.

    Attributes:
        text_chunk: The text string.
        num_char_overlap: The number of overlapping characters with the previous chunk.
    """

    text_chunk: str
    num_char_overlap: Optional[int] = None


class TokenTextSplitter(TextSplitter):
    """Implementation of splitting text that looks at word tokens."""

    def __init__(
            self,
            separator: str = " ",
            chunk_size: int = DEFAULT_CHUNK_SIZE,
            chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
            tokenizer: Optional[Callable] = None,
            backup_separators: Optional[List[str]] = ["\n"]
    ):
        """Initialize with parameters."""
        if chunk_overlap > chunk_size:
            raise ValueError(
                f"Got a larger chunk overlap ({chunk_overlap}) than chunk size "
                f"({chunk_size}), should be smaller."
            )
        self._separator = separator
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self.tokenizer = tokenizer
        self._backup_separators = backup_separators

    def _reduce_chunk_size(
            self, start_idx: int, cur_idx: int, splits: List[str]
    ) -> int:
        """Reduce the chunk size by reducing cur_idx.

        Return the new cur_idx.

        """
        current_doc_total = len(
            self.tokenizer(self._separator.join(splits[start_idx:cur_idx]))
        )
        while current_doc_total > self._chunk_size:
            percent_to_reduce = (
                                        current_doc_total - self._chunk_size
                                ) / current_doc_total
            num_to_reduce = int(percent_to_reduce * (cur_idx - start_idx)) + 1
            cur_idx -= num_to_reduce
            current_doc_total = len(
                self.tokenizer(self._separator.join(splits[start_idx:cur_idx]))
            )
        return cur_idx

    def _preprocess_splits(self, splits: List[str], chunk_size: int) -> List[str]:
        """Process splits.

        Specifically search for tokens that are too large for chunk size,
        and see if we can separate those tokens more
        (via backup separators if specified, or force chunking).

        """
        new_splits = []
        for split in splits:
            num_cur_tokens = len(self.tokenizer(split))
            if num_cur_tokens <= chunk_size:
                new_splits.append(split)
            else:
                cur_splits = [split]
                if self._backup_separators:
                    for sep in self._backup_separators:
                        if sep in split:
                            cur_splits = split.split(sep)
                            break
                else:
                    cur_splits = [split]

                cur_splits2 = []
                for cur_split in cur_splits:
                    num_cur_tokens = len(self.tokenizer(cur_split))
                    if num_cur_tokens <= chunk_size:
                        cur_splits2.extend([cur_split])
                    else:
                        # split cur_split according to chunk size of the token numbers
                        cur_split_chunks = []
                        end_idx = len(cur_split)
                        while len(self.tokenizer(cur_split[0:end_idx])) > chunk_size:
                            for i in range(1, end_idx):
                                tmp_split = cur_split[0: end_idx - i]
                                if len(self.tokenizer(tmp_split)) <= chunk_size:
                                    cur_split_chunks.append(tmp_split)
                                    cur_split = cur_split[end_idx - i: end_idx]
                                    end_idx = len(cur_split)
                                    break
                        cur_split_chunks.append(cur_split)
                        cur_splits2.extend(cur_split_chunks)

                new_splits.extend(cur_splits2)
        return new_splits

    def _postprocess_splits(self, docs: List[TextSplit]) -> List[TextSplit]:
        """Post-process splits."""
        # TODO: prune text splits, remove empty spaces
        new_docs = []
        for doc in docs:
            if doc.text_chunk.replace(" ", "") == "":
                continue
            new_docs.append(doc)
        return new_docs

    def split_text(self, text: str, metadata_str: Optional[str] = None) -> List[str]:
        """Split incoming text and return chunks."""
        text_splits = self.split_text_with_overlaps(text, metadata_str=metadata_str)
        chunks = [text_split.text_chunk for text_split in text_splits]
        return chunks

    def split_text_with_overlaps(
            self, text: str, metadata_str: Optional[str] = None
    ) -> List[TextSplit]:
        """Split incoming text and return chunks with overlap size."""
        if text == "":
            return []
        # NOTE: Consider metadata info str that will be added to the chunk at query time
        #       This reduces the effective chunk size that we can have
        if metadata_str is not None:
            # NOTE: extra 2 newline chars for formatting when prepending in query
            num_extra_tokens = len(self.tokenizer(f"{metadata_str}\n\n")) + 1
            effective_chunk_size = self._chunk_size - num_extra_tokens

            if effective_chunk_size <= 0:
                raise ValueError(
                    "Effective chunk size is non positive after considering metadata"
                )
        else:
            effective_chunk_size = self._chunk_size

        # First we naively split the large input into a bunch of smaller ones.
        splits = text.split(self._separator)
        splits = self._preprocess_splits(splits, effective_chunk_size)
        # We now want to combine these smaller pieces into medium size
        # chunks to send to the LLM.
        docs: List[TextSplit] = []

        start_idx = 0
        cur_idx = 0
        cur_total = 0
        prev_idx = 0  # store the previous end index
        while cur_idx < len(splits):
            cur_token = splits[cur_idx]
            num_cur_tokens = max(len(self.tokenizer(cur_token)), 1)
            if num_cur_tokens > effective_chunk_size:
                raise ValueError(
                    "A single term is larger than the allowed chunk size.\n"
                    f"Term size: {num_cur_tokens}\n"
                    f"Chunk size: {self._chunk_size}"
                    f"Effective chunk size: {effective_chunk_size}"
                )
            # If adding token to current_doc would exceed the chunk size:
            # 1. First verify with tokenizer that current_doc
            # 1. Update the docs list
            if cur_total + num_cur_tokens > effective_chunk_size:
                # NOTE: since we use a proxy for counting tokens, we want to
                # run tokenizer across all of current_doc first. If
                # the chunk is too big, then we will reduce text in pieces
                cur_idx = self._reduce_chunk_size(start_idx, cur_idx, splits)
                overlap = 0
                # after first round, check if last chunk ended after this chunk begins
                if prev_idx > 0 and prev_idx > start_idx:
                    overlap = sum([len(splits[i]) for i in range(start_idx, prev_idx)])

                docs.append(
                    TextSplit(self._separator.join(splits[start_idx:cur_idx]), overlap)
                )
                prev_idx = cur_idx
                # 2. Shrink the current_doc (from the front) until it is gets smaller
                # than the overlap size
                # NOTE: because counting tokens individually is an imperfect
                # proxy (but much faster proxy) for the total number of tokens consumed,
                # we need to enforce that start_idx <= cur_idx, otherwise
                # start_idx has a chance of going out of bounds.
                while cur_total > self._chunk_overlap and start_idx < cur_idx:
                    # # call tokenizer on entire overlap
                    # cur_total = self.tokenizer()
                    cur_num_tokens = max(len(self.tokenizer(splits[start_idx])), 1)
                    cur_total -= cur_num_tokens
                    start_idx += 1
                # NOTE: This is a hack, make more general
                if start_idx == cur_idx:
                    cur_total = 0
            # Build up the current_doc with term d, and update the total counter with
            # the number of the number of tokens in d, wrt self.tokenizer

            # we reassign cur_token and num_cur_tokens, because cur_idx
            # may have changed
            cur_token = splits[cur_idx]
            num_cur_tokens = max(len(self.tokenizer(cur_token)), 1)

            cur_total += num_cur_tokens
            cur_idx += 1
        overlap = 0
        # after first round, check if last chunk ended after this chunk begins
        if prev_idx > start_idx:
            overlap = sum([len(splits[i]) for i in range(start_idx, prev_idx)]) + len(
                range(start_idx, prev_idx)
            )
        docs.append(TextSplit(self._separator.join(splits[start_idx:cur_idx]), overlap))

        # run postprocessing to remove blank spaces
        docs = self._postprocess_splits(docs)
        return docs

    def truncate_text(self, text: str) -> str:
        """Truncate text in order to fit the underlying chunk size."""
        if text == "":
            return ""
        # First we naively split the large input into a bunch of smaller ones.
        splits = text.split(self._separator)
        splits = self._preprocess_splits(splits, self._chunk_size)

        start_idx = 0
        cur_idx = 0
        cur_total = 0
        while cur_idx < len(splits):
            cur_token = splits[cur_idx]
            num_cur_tokens = max(len(self.tokenizer(cur_token)), 1)
            if cur_total + num_cur_tokens > self._chunk_size:
                cur_idx = self._reduce_chunk_size(start_idx, cur_idx, splits)
                break
            cur_total += num_cur_tokens
            cur_idx += 1
        return self._separator.join(splits[start_idx:cur_idx])


class SentenceSplitter(TextSplitter):
    """Split text with a preference for complete sentences.

    In general, this class tries to keep sentences and paragraphs together. Therefore
    compared to the original TokenTextSplitter, there are less likely to be
    hanging sentences or parts of sentences at the end of the node chunk.
    """

    def __init__(
            self,
            separator: str = " ",
            chunk_size: int = DEFAULT_CHUNK_SIZE,
            chunk_overlap: int = 200,
            tokenizer: Optional[Callable] = None,
            backup_separators: Optional[List[str]] = ["\n"],
            paragraph_separator: Optional[str] = "\n\n\n",
            chunking_tokenizer_fn: Optional[Callable[[str], List[str]]] = None,
            secondary_chunking_regex: Optional[str] = "[^,.;。]+[,.;。]?"
    ):
        """Initialize with parameters."""
        if chunk_overlap > chunk_size:
            raise ValueError(
                f"Got a larger chunk overlap ({chunk_overlap}) than chunk size "
                f"({chunk_size}), should be smaller."
            )
        self._separator = separator
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self.tokenizer = tokenizer
        self._backup_separators = backup_separators
        if chunking_tokenizer_fn is None:
            import nltk.tokenize.punkt as pkt

            class CustomLanguageVars(pkt.PunktLanguageVars):
                _period_context_fmt = r"""
                    %(SentEndChars)s             # a potential sentence ending
                    (\)\"\s)\s*                  # other end chars and
                                                 # any amount of white space
                    (?=(?P<after_tok>
                        %(NonWord)s              # either other punctuation
                        |
                        (?P<next_tok>\S+)     # or whitespace and some other token
                    ))"""

            custom_tknzr = pkt.PunktSentenceTokenizer(lang_vars=CustomLanguageVars())

            chunking_tokenizer_fn = custom_tknzr.tokenize
        self.paragraph_separator = paragraph_separator
        self.chunking_tokenizer_fn = chunking_tokenizer_fn
        self.second_chunking_regex = secondary_chunking_regex
        """
        By default we use the second chunking regex "[^,.;]+[,.;]?".
        This regular expression will split the sentences into phrases,
        where each phrase is a sequence of one or more non-comma,
        non-period, and non-semicolon characters, followed by an optional comma,
        period, or semicolon. The regular expression will also capture the
        delimiters themselves as separate items in the list of phrases.
        """

    def _postprocess_splits(self, docs: List[TextSplit]) -> List[TextSplit]:
        """Post-process splits."""
        # TODO: prune text splits, remove empty spaces
        new_docs = []
        for doc in docs:
            if doc.text_chunk.replace(" ", "") == "":
                continue
            new_docs.append(doc)
        return new_docs

    def split_text_with_overlaps(
            self, text: str, metadata_str: Optional[str] = None
    ) -> List[TextSplit]:
        """
        Split incoming text and return chunks with overlap size.

        Has a preference for complete sentences, phrases, and minimal overlap.
        """
        if text == "":
            return []

        # NOTE: Consider metadata info str that will be added to the chunk at query time
        #       This reduces the effective chunk size that we can have
        if metadata_str is not None:
            # NOTE: extra 2 newline chars for formatting when prepending in query
            num_extra_tokens = len(self.tokenizer(f"{metadata_str}\n\n")) + 1
            effective_chunk_size = self._chunk_size - num_extra_tokens

            if effective_chunk_size <= 0:
                raise ValueError(
                    "Effective chunk size is non positive after considering metadata"
                )
        else:
            effective_chunk_size = self._chunk_size

        # First we split paragraphs using separator
        splits = text.split(self.paragraph_separator)

        # Merge paragraphs that are too small.

        idx = 0
        while idx < len(splits):
            if idx < len(splits) - 1 and len(splits[idx]) < effective_chunk_size:
                splits[idx] = "\n\n".join([splits[idx], splits[idx + 1]])
                splits.pop(idx + 1)
            else:
                idx += 1

        # Next we split the text using the chunk tokenizer fn,
        # which defaults to the sentence tokenizer from nltk.
        chunked_splits = [self.chunking_tokenizer_fn(text) for text in splits]
        splits = [chunk for split in chunked_splits for chunk in split]

        # Check if any sentences exceed the chunk size. If they do, split again
        # using the second chunk separator. If it any still exceed,
        # use the default separator (" ").
        @dataclass
        class Split:
            text: str  # the split text
            is_sentence: bool  # save whether this is a full sentence

        new_splits: List[Split] = []
        for split in splits:
            split_len = len(self.tokenizer(split))
            if split_len <= effective_chunk_size:
                new_splits.append(Split(split, True))
            else:
                if self.second_chunking_regex is not None:
                    import re

                    # Default regex is "[^,\.;]+[,\.;]?"
                    splits2 = re.findall(self.second_chunking_regex, split)

                else:
                    splits2 = [split]
                for split2 in splits2:
                    if len(self.tokenizer(split2)) <= effective_chunk_size:
                        new_splits.append(Split(split2, False))
                    else:
                        splits3 = split2.split(self._separator)
                        new_splits.extend([Split(split3, False) for split3 in splits3])

        # Create the list of text splits by combining smaller chunks.
        docs: List[TextSplit] = []
        cur_doc_list: List[str] = []
        cur_tokens = 0
        while len(new_splits) > 0:
            cur_token = new_splits[0]
            cur_len = len(self.tokenizer(cur_token.text))
            if cur_len > effective_chunk_size:
                raise ValueError("Single token exceed chunk size")
            if cur_tokens + cur_len > effective_chunk_size:
                docs.append(TextSplit("".join(cur_doc_list).strip()))
                cur_doc_list = []
                cur_tokens = 0
            else:
                if (
                        cur_token.is_sentence
                        or cur_tokens + cur_len < effective_chunk_size - self._chunk_overlap
                ):
                    cur_tokens += cur_len
                    cur_doc_list.append(cur_token.text)
                    new_splits.pop(0)
                else:
                    docs.append(TextSplit("".join(cur_doc_list).strip()))
                    cur_doc_list = []
                    cur_tokens = 0

        docs.append(TextSplit("".join(cur_doc_list).strip()))

        # run postprocessing to remove blank spaces
        docs = self._postprocess_splits(docs)
        return docs

    def split_text(self, text: str, metadata_str: Optional[str] = None) -> List[str]:

        text_splits = self.split_text_with_overlaps(text, metadata_str=metadata_str)
        chunks = [text_split.text_chunk for text_split in text_splits]

        return chunks


class ParagraphSplitter(TextSplitter):
    """Split text into paragraphs.
    """

    def __init__(
            self,
            paragraph_separator: Optional[str] = "\n\n",
    ):
        """Initialize with parameters."""

        self.paragraph_separator = paragraph_separator

    def split_text(self, text: str, metadata_str: Optional[str] = None) -> List[str]:
        chunks = text.split(self.paragraph_separator)
        chunks = [x for x in chunks if x]
        return chunks
