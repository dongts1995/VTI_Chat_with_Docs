"""Sinh câu trả lời có trích dẫn từ các đoạn đã truy xuất (US-302, US-303).

`AnswerGenerator` là port (ADR-0002). Bản mặc định không gọi LLM: mỗi đoạn đóng góp đúng một
câu có nhiều từ khoá nhất, kèm dấu [n]. Khi có LLM, chỉ cần một lớp mới cài đặt port này.
"""

import re
from typing import Protocol

from app.models import Passage
from app.retrieval import tokenize

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class AnswerGenerator(Protocol):
    def generate(self, question: str, passages: list[Passage]) -> str:
        """Trả về văn bản; mỗi đoạn trong `passages` (theo thứ tự 1..n) phải có dấu [n]."""
        ...


def relevant_sentences(question: str, text: str, limit: int = 2) -> list[str]:
    """Tối đa `limit` câu của `text` có từ khoá trùng với câu hỏi, giữ nguyên thứ tự trong đoạn.

    Không câu nào trùng thì trả về câu đầu tiên. Lấy nhiều câu để không bỏ sót đáp án nằm ở câu
    kế bên (US-302).
    """
    query_terms = set(tokenize(question))
    sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()] or [text]
    overlaps = [(len(query_terms & set(tokenize(s))), i) for i, s in enumerate(sentences)]
    ranked = sorted((o for o in overlaps if o[0] > 0), key=lambda o: (-o[0], o[1]))[:limit]
    if not ranked:
        return [sentences[0]]
    return [sentences[i] for i in sorted(i for _, i in ranked)]


class ExtractiveAnswerGenerator:
    def generate(self, question: str, passages: list[Passage]) -> str:
        lines = [
            f"{' '.join(relevant_sentences(question, passage.text))} [{index}]"
            for index, passage in enumerate(passages, start=1)
        ]
        return "\n".join(lines)
