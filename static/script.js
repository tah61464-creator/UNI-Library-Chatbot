// ================================
// GỬI CÂU HỎI
// ================================

async function sendMessage() {

    const input = document.getElementById("user-input");
    const question = input.value.trim();

    if (question === "") {
        return;
    }

    // Hiển thị câu hỏi người dùng
    addMessage(question, "user");

    // Xóa ô nhập
    input.value = "";

    // Hiển thị đang xử lý
    const loadingId = addMessage(
        "⏳ Đang tìm kiếm thông tin sách...",
        "bot"
    );

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: question
            })
        });

        if (!response.ok) {
            throw new Error("Lỗi máy chủ: " + response.status);
        }

       const text = await response.text();

console.log("Server response:", text);

let data;

try {
    data = JSON.parse(text);
} catch (error) {
    removeMessage(loadingId);
    addMessage("❌ Flask trả về lỗi:\n\n" + text, "bot");
    console.error("Server response:", text);
    return;
}

        // Xóa loading
        removeMessage(loadingId);

        // Hiển thị câu trả lời
        addMessage(data.answer, "bot");

    } catch (error) {

        removeMessage(loadingId);

        addMessage(
            "❌ Không thể kết nối đến máy chủ. Bạn hãy kiểm tra Flask.",
            "bot"
        );

        console.error(error);
    }
}


// ================================
// HIỂN THỊ TIN NHẮN
// ================================

let messageCounter = 0;

function addMessage(message, sender) {

    const chatBox = document.getElementById("chat-box");

    const messageDiv = document.createElement("div");

    const messageId =
        "message-" + Date.now() + "-" + messageCounter++;

    messageDiv.id = messageId;

    messageDiv.className = "message " + sender;

    // Xử lý chữ đậm và xuống dòng
    const formattedMessage = message
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");

    messageDiv.innerHTML = formattedMessage;

    // Thêm tin nhắn vào giao diện
    chatBox.appendChild(messageDiv);

    // Render công thức toán bằng MathJax
    if (window.MathJax && window.MathJax.typesetPromise) {

        MathJax.typesetPromise([messageDiv])
            .catch(function(error) {
                console.error("Lỗi MathJax:", error);
            });

    }

    // Cuộn xuống cuối
    chatBox.scrollTop = chatBox.scrollHeight;

    return messageId;
}

// ================================
// XÓA TIN NHẮN
// ================================

function removeMessage(id) {

    const element =
        document.getElementById(id);

    if (element) {
        element.remove();
    }
}


// ================================
// NHẤN ENTER ĐỂ GỬI
// ================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const input =
            document.getElementById("user-input");

        if (input) {

            input.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                        && !event.shiftKey
                    ) {

                        event.preventDefault();

                        sendMessage();
                    }
                }
            );
        }

    }
);
// ========================================
// NỘI DUNG CÁC NÚT TRA CỨU NHANH
// ========================================

async function showLibraryInfo(type) {

    const chatBox = document.getElementById("chat-box");

    // Hiển thị thông báo đang tải
    const loading = document.createElement("div");

    loading.className = "message bot";

    loading.innerHTML = "⏳ Đang lấy thông tin từ thư viện...";

    chatBox.appendChild(loading);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {

        const response = await fetch("/library-info/" + type);

        const data = await response.json();

        // Xóa thông báo đang tải
        loading.remove();

        // Hiển thị kết quả
        addMessage(data.answer, "bot");

    } catch (error) {

        loading.remove();

        addMessage(
            "❌ Không thể lấy dữ liệu thư viện.",
            "bot"
        );

        console.error(error);
    }
}