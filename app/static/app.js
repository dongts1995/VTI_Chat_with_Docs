// Giao diện MVP: tải nhiều PDF, xem trạng thái, hỏi đáp có trích dẫn.
// Mọi nội dung từ máy chủ được gắn bằng textContent, không dùng innerHTML (chống XSS).
"use strict";

const fileInput = document.getElementById("file-input");
const docList = document.getElementById("doc-list");
const messages = document.getElementById("messages");
const askForm = document.getElementById("ask-form");
const questionBox = document.getElementById("question");
const askBtn = document.getElementById("ask-btn");

const STATUS_LABEL = {
  READY: "Sẵn sàng",
  NO_TEXT: "Không đọc được chữ",
  ERROR: "Lỗi",
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

async function problemMessage(response) {
  try {
    const body = await response.json();
    return body.detail || `Lỗi ${response.status}`;
  } catch {
    return `Lỗi ${response.status}`;
  }
}

function renderDocs(docs) {
  docList.replaceChildren();
  if (docs.length === 0) {
    docList.append(el("li", "", "Chưa có tài liệu nào."));
    return;
  }
  for (const doc of docs) {
    const item = el("li");
    item.append(el("div", "", doc.fileName));
    item.append(
      el("span", `status status-${doc.status}`, STATUS_LABEL[doc.status] || doc.status),
      el("span", "", doc.pageCount ? ` · ${doc.pageCount} trang` : ""),
    );
    if (doc.error) item.append(el("span", "reason", doc.error));
    docList.append(item);
  }
}

async function refreshDocs() {
  const response = await fetch("/api/v1/documents");
  if (response.ok) renderDocs(await response.json());
}

async function uploadFiles(files) {
  for (const file of files) {
    const form = new FormData();
    form.append("file", file, file.name);
    const response = await fetch("/api/v1/documents", { method: "POST", body: form });
    if (!response.ok) {
      const reason = await problemMessage(response);
      messages.append(el("div", "msg error", `${file.name}: ${reason}`));
    }
  }
  fileInput.value = "";
  await refreshDocs();
}

function renderAnswer(answer) {
  if (answer.status === "NOT_FOUND") {
    messages.append(el("div", "msg not-found", answer.text));
    return;
  }
  const bubble = el("div", "msg answer", answer.text);
  const list = el("ol", "citations");
  for (const c of answer.citations) {
    list.append(el("li", "", `[${c.index}] ${c.fileName} — trang ${c.page}`));
  }
  bubble.append(list);
  messages.append(bubble);
}

async function ask(text) {
  messages.append(el("div", "msg user", text));
  const response = await fetch("/api/v1/questions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    messages.append(el("div", "msg error", await problemMessage(response)));
    return;
  }
  renderAnswer(await response.json());
}

fileInput.addEventListener("change", () => uploadFiles([...fileInput.files]));

questionBox.addEventListener("input", () => {
  askBtn.disabled = questionBox.value.trim() === "";
});

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = questionBox.value.trim();
  if (!text) return;
  questionBox.value = "";
  askBtn.disabled = true;
  await ask(text);
});

refreshDocs();
