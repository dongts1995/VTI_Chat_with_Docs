"""Test đơn vị: chia đoạn, trích xuất PDF, truy xuất và sinh trích dẫn."""

from helpers import make_encrypted_pdf, make_pdf

from app.answering import ExtractiveAnswerGenerator, relevant_sentences
from app.chunking import passages_of, split_text
from app.config import MIN_TEXT_CHARS_PER_PAGE
from app.errors import PdfError
from app.models import Document, DocumentStatus, PageText, Passage
from app.pdf_text import extract_pages, has_extractable_text
from app.retrieval import PassageIndex, tokenize


def _passage(text: str, page: int = 1, doc: str = "d1") -> Passage:
    return Passage(document_id=doc, file_name=f"{doc}.pdf", page=page, text=text)


# --- chunking -------------------------------------------------------------


def test_split_text_keeps_short_text_whole() -> None:
    assert split_text("Mot cau. Hai cau.") == ["Mot cau. Hai cau."]


def test_split_text_respects_max_chars() -> None:
    sentences = [f"Cau so {i} co noi dung du dai de test." for i in range(60)]
    segments = split_text(" ".join(sentences), max_chars=200)
    assert len(segments) > 1
    assert all(len(s) <= 200 for s in segments)


def test_split_text_ignores_blank_input() -> None:
    assert split_text("   \n\n  ") == []


def test_passages_keep_page_numbers() -> None:
    document = Document(
        file_name="a.pdf",
        status=DocumentStatus.READY,
        pages=[PageText(1, "Trang mot."), PageText(2, "Trang hai.")],
    )
    passages = passages_of(document)
    assert [(p.page, p.text) for p in passages] == [(1, "Trang mot."), (2, "Trang hai.")]
    assert all(p.document_id == document.id for p in passages)


# --- pdf_text ----------------------------------------------------------------


def test_extract_pages_returns_text_per_page() -> None:
    pages = extract_pages(make_pdf(["Hop dong thanh toan 30 phan tram.", "Trang hai o day."]))
    assert [p.number for p in pages] == [1, 2]
    assert "thanh toan" in pages[0].text
    assert "Trang hai" in pages[1].text


def test_extract_pages_rejects_encrypted_pdf() -> None:
    try:
        extract_pages(make_encrypted_pdf("secret"))
    except PdfError as exc:
        assert exc.code == "PASSWORD"
    else:  # pragma: no cover - the test must fail if no error is raised
        raise AssertionError("expected PdfError")


def test_extract_pages_rejects_corrupt_pdf() -> None:
    try:
        extract_pages(b"%PDF-1.4 day khong phai pdf hop le")
    except PdfError as exc:
        assert exc.code == "CORRUPT"
    else:  # pragma: no cover
        raise AssertionError("expected PdfError")


def test_scanned_pdf_has_no_extractable_text() -> None:
    pages = extract_pages(make_pdf(["", ""]))
    assert not has_extractable_text(pages)


def test_text_threshold_is_per_page() -> None:
    enough = "x" * MIN_TEXT_CHARS_PER_PAGE
    assert has_extractable_text([PageText(1, enough)])
    assert not has_extractable_text([PageText(1, enough[:-1])])


# --- retrieval -----------------------------------------------------------------


def test_tokenize_folds_vietnamese_accents_and_drops_stopwords() -> None:
    assert tokenize("Hợp đồng thanh toán là gì?") == ["hop", "dong", "thanh", "toan"]


def test_index_ranks_passage_with_more_matches_first() -> None:
    weak = _passage("Gia thue van phong la 20 trieu.", doc="weak")
    strong = _passage("Thanh toan tien thue van phong moi thang.", doc="strong")
    index = PassageIndex([weak, strong])
    hits = index.search("thanh toan thue van phong", limit=2)
    assert hits[0] is strong
    assert hits[1] is weak


def test_index_returns_nothing_without_matches() -> None:
    index = PassageIndex([_passage("Noi dung khac hoan toan.")])
    assert index.search("luong nhan vien", limit=4) == []


def test_index_handles_empty_corpus_and_empty_query() -> None:
    assert PassageIndex([]).search("bat ky", limit=4) == []
    assert PassageIndex([_passage("abc def")]).search("   ", limit=4) == []


def test_index_respects_limit() -> None:
    index = PassageIndex([_passage(f"tu khoa so {i}", doc=f"d{i}") for i in range(6)])
    assert len(index.search("tu khoa", limit=3)) == 3


# --- answering --------------------------------------------------------------


def test_relevant_sentences_skips_unrelated_sentences() -> None:
    text = "Gio lam viec la 8 gio. Thanh toan 30 phan tram khi ky hop dong."
    assert relevant_sentences("thanh toan hop dong", text) == [
        "Thanh toan 30 phan tram khi ky hop dong."
    ]


def test_relevant_sentences_keeps_several_matches_in_original_order() -> None:
    text = "Hop dong thue van phong. Ban khac. Thanh toan 30 phan tram khi ky."
    assert relevant_sentences("hop dong thanh toan", text) == [
        "Hop dong thue van phong.",
        "Thanh toan 30 phan tram khi ky.",
    ]


def test_relevant_sentences_falls_back_to_first_sentence_without_match() -> None:
    assert relevant_sentences("zzz", "Cau mot. Cau hai.") == ["Cau mot."]


def test_relevant_sentences_respects_limit() -> None:
    text = "tu khoa a. tu khoa b. tu khoa c."
    assert len(relevant_sentences("tu khoa", text, limit=2)) == 2


def test_extractive_generator_tags_every_passage() -> None:
    passages = [_passage("Dong mot co tu khoa.", page=1), _passage("Dong hai khac.", page=2)]
    answer = ExtractiveAnswerGenerator().generate("tu khoa", passages)
    lines = answer.splitlines()
    assert lines == ["Dong mot co tu khoa. [1]", "Dong hai khac. [2]"]
