// document.getElementById("upload-form").addEventListener("submit", async function (e) {
//   e.preventDefault();
//   const formData = new FormData(this);
//   const res = await fetch("/upload", { method: "POST", body: formData });
//   const text = await res.text();
//   alert(text);
// });

// document.getElementById("question-form").addEventListener("submit", async function (e) {
//   e.preventDefault();
//   const question = document.getElementById("question-input").value;
//   const res = await fetch("/query", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ question }),
//   });
//   const data = await res.json();
//   document.getElementById("response-box").innerHTML = `
//     <strong>Answer (${data.source}):</strong><br>${data.answer}
//     ${data.title ? `<br><em>From: ${data.title}</em>` : ""}
//   `;
// });


// --------------------------------- Update-1 ---------------------------------

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const uploadStatus = document.getElementById("upload-status");
const loader = document.getElementById("loader");
const askBtn = document.getElementById("ask-btn");
const questionInput = document.getElementById("question-input");
const chatArea = document.getElementById("chat-area");
const historyList = document.getElementById("history");

// File Upload
uploadForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  loader.classList.remove("hidden");
  uploadStatus.textContent = "Uploading and processing...";

  const formData = new FormData();
  formData.append("file", file);

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((res) => res.text())
    .then((text) => {
      loader.classList.add("hidden");
      uploadStatus.textContent = `✅ File processed successfully: ${file.name}`;
    })
    .catch((err) => {
      loader.classList.add("hidden");
      uploadStatus.textContent = `❌ Upload failed: ${err}`;
    });
});

// Ask a question
askBtn.addEventListener("click", () => {
  const question = questionInput.value.trim();
  if (!question) return;

  fetch("/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  })
    .then((res) => res.json())
    .then((data) => {
      addChatBubble(question, data.answer);
      addToHistory(question);
      questionInput.value = "";
    })
    .catch((err) => {
      addChatBubble(question, "Something went wrong: " + err);
    });
});

function addChatBubble(question, answer) {
  const box = document.createElement("div");
  box.className = "chat-box";
  box.innerHTML = `<strong>Q:</strong> ${question}<br/><strong>A:</strong> ${answer}`;
  chatArea.appendChild(box);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function addToHistory(question) {
  const item = document.createElement("li");
  item.textContent = question;
  historyList.appendChild(item);
}