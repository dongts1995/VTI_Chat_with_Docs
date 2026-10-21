"""Truy xuất đoạn văn bằng BM25 trên từ khoá đã bỏ dấu (ADR-0002: MVP không dùng embedding).

Bỏ dấu tiếng Việt để "hợp đồng" và "hop dong" khớp nhau; câu hỏi và tài liệu đi qua cùng một bước.
"""

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable

from app.models import Passage

_STOPWORDS = frozenset(
    {
        # Tiếng Anh
        "the",
        "a",
        "an",
        "of",
        "in",
        "on",
        "to",
        "for",
        "and",
        "or",
        "is",
        "are",
        "was",
        "what",
        "who",
        "when",
        "where",
        "how",
        "which",
        "does",
        "do",
        "with",
        "by",
        "about",
        # Tiếng Việt đã bỏ dấu
        "la",
        "va",
        "cua",
        "cac",
        "nhung",
        "co",
        "khong",
        "gi",
        "nao",
        "bao",
        "nhieu",
        "trong",
        "voi",
        "cho",
        "den",
        "tai",
        "duoc",
        "mot",
        "nay",
        "thi",
        "ve",
    }
)

_K1 = 1.5
_B = 0.75


def tokenize(text: str) -> list[str]:
    """Chuyển về chữ thường, bỏ dấu, tách từ, bỏ từ dừng và token một ký tự."""
    decomposed = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    folded = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return [t for t in re.findall(r"[a-z0-9]+", folded) if len(t) > 1 and t not in _STOPWORDS]


class PassageIndex:
    """Chỉ mục BM25 cho một tập đoạn văn; xây dựng một lần cho mỗi câu hỏi."""

    def __init__(self, passages: Iterable[Passage]) -> None:
        self._passages = list(passages)
        self._term_counts = [Counter(tokenize(p.text)) for p in self._passages]
        self._lengths = [sum(c.values()) for c in self._term_counts]
        self._avg_len = sum(self._lengths) / len(self._lengths) if self._lengths else 0.0
        self._doc_freq: Counter[str] = Counter()
        for counts in self._term_counts:
            self._doc_freq.update(counts.keys())

    def search(self, query: str, limit: int) -> list[Passage]:
        """Trả về tối đa `limit` đoạn có điểm > 0, xếp theo điểm giảm dần."""
        terms = set(tokenize(query))
        if not terms or not self._passages:
            return []
        n = len(self._passages)
        scored: list[tuple[float, int]] = []
        for i, counts in enumerate(self._term_counts):
            score = 0.0
            for term in terms:
                tf = counts.get(term, 0)
                if tf == 0:
                    continue
                df = self._doc_freq[term]
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                norm = (
                    tf * (_K1 + 1) / (tf + _K1 * (1 - _B + _B * self._lengths[i] / self._avg_len))
                )
                score += idf * norm
            if score > 0:
                scored.append((score, i))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [self._passages[i] for _, i in scored[:limit]]
