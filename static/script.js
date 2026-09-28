let messageCounter = 0;


// =====================================================
// GỬI TIN NHẮN CHATBOT
// =====================================================

async function sendMessage() {

    const input = document.getElementById("user-input");

    if (!input) return;

    const question = input.value.trim();

    if (question === "") return;


    // Hiển thị câu hỏi người dùng
    addMessage(question, "user");

    input.value = "";


    // Hiển thị loading
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

            throw new Error(
                "Lỗi máy chủ: " + response.status
            );

        }


        const data = await response.json();


        // Xóa loading
        removeMessage(loadingId);


        // Hiển thị câu trả lời
        const messageId = addMessage(
            data.answer || "Không có câu trả lời.",
            "bot"
        );


        // Hiển thị nguồn
        const botMessage = document.getElementById(messageId);

        if (botMessage) {

            const source = document.createElement("div");

            source.className = "source-info";

            source.textContent =
                "📌 Nguồn: " +
                (data.source ||
                "Cơ sở dữ liệu thư viện + Gemini AI");

            botMessage.appendChild(source);

        }


    } catch (error) {

        console.error(
            "Lỗi gửi tin nhắn:",
            error
        );


        removeMessage(loadingId);


        addMessage(
            "❌ Không thể kết nối đến máy chủ. Bạn hãy kiểm tra Flask và thử lại.",
            "bot"
        );

    }

}



// =====================================================
// HIỂN THỊ TIN NHẮN
// =====================================================

function addMessage(message, sender) {

    const chatBox =
        document.getElementById("chat-box");

    if (!chatBox) return null;


    const messageDiv =
        document.createElement("div");


    const messageId =
        "message-" +
        Date.now() +
        "-" +
        messageCounter++;


    messageDiv.id = messageId;

    messageDiv.className =
        "message " + sender;


    let formattedMessage =
        String(message)
            .replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            )
            .replace(
                /\n/g,
                "<br>"
            );


    messageDiv.innerHTML =
        formattedMessage;


    chatBox.appendChild(messageDiv);


    // MathJax
    if (
        window.MathJax &&
        window.MathJax.typesetPromise
    ) {

        MathJax
            .typesetPromise([messageDiv])
            .catch(function(error) {

                console.error(
                    "Lỗi MathJax:",
                    error
                );

            });

    }


    chatBox.scrollTop =
        chatBox.scrollHeight;


    return messageId;

}



// =====================================================
// XÓA TIN NHẮN
// =====================================================

function removeMessage(id) {

    const element =
        document.getElementById(id);

    if (element) {

        element.remove();

    }

}



// =====================================================
// NÚT CÂU HỎI NHANH
// =====================================================

function quickQuestion(question) {

    const input =
        document.getElementById("user-input");

    if (!input) return;


    showChat();


    input.value = question;


    sendMessage();

}



// =====================================================
// HIỂN THỊ CHATBOT
// =====================================================

function showChat() {

    const welcome =
        document.querySelector(".welcome");

    const historyBox =
        document.getElementById(
            "chat-history-box"
        );

    const statisticsBox =
        document.getElementById(
            "library-statistics-box"
        );


    if (welcome) {

        welcome.style.display =
            "block";

    }


    if (historyBox) {

        historyBox.style.display =
            "none";

    }


    if (statisticsBox) {

        statisticsBox.style.display =
            "none";

    }

}



// =====================================================
// LỊCH SỬ CHAT
// =====================================================

async function showChatHistory() {

    const welcome =
        document.querySelector(".welcome");

    const historyBox =
        document.getElementById(
            "chat-history-box"
        );

    const statisticsBox =
        document.getElementById(
            "library-statistics-box"
        );

    const historyList =
        document.getElementById(
            "history-list"
        );


    if (!historyBox || !historyList) {

        console.error(
            "Không tìm thấy khu vực lịch sử chat"
        );

        return;

    }


    // Ẩn các phần khác
    if (welcome) {

        welcome.style.display =
            "none";

    }


    if (statisticsBox) {

        statisticsBox.style.display =
            "none";

    }


    // Hiện lịch sử
    historyBox.style.display =
        "block";


    historyList.innerHTML =
        "⏳ Đang tải lịch sử...";


    try {

        const response =
            await fetch(
                "/chat-history"
            );


        if (!response.ok) {

            throw new Error(
                "Không thể lấy lịch sử"
            );

        }


        const history =
            await response.json();


        // Không có lịch sử
        if (
            !history ||
            history.length === 0
        ) {

            historyList.innerHTML = `
                <div class="history-empty">
                    📝 Chưa có lịch sử trò chuyện.
                </div>
            `;

            return;

        }


        // Xóa loading
        historyList.innerHTML = "";


        // Hiển thị từng lịch sử
        history.forEach(function(item) {

            const historyItem =
                document.createElement("div");

            historyItem.className =
                "history-item";


            // Câu hỏi
            const question =
                document.createElement("div");

            question.className =
                "history-question";

            question.textContent =
                "👤 " +
                item.question;


            // Câu trả lời
            const answer =
                document.createElement("div");

            answer.className =
                "history-answer";

            answer.textContent =
                "🤖 " +
                item.answer;


            // Thời gian
            const time =
                document.createElement("div");

            time.className =
                "history-time";

            time.textContent =
                "🕐 " +
                item.created_at;


            historyItem.appendChild(
                question
            );

            historyItem.appendChild(
                answer
            );

            historyItem.appendChild(
                time
            );


            historyList.appendChild(
                historyItem
            );

        });


    } catch (error) {

        console.error(
            "Lỗi lịch sử:",
            error
        );


        historyList.innerHTML = `
            <div class="history-empty">
                ❌ Không thể tải lịch sử chat.
            </div>
        `;

    }

}



// =====================================================
// THỐNG KÊ THƯ VIỆN
// =====================================================

async function showLibraryStatistics() {

    const welcome =
        document.querySelector(".welcome");

    const historyBox =
        document.getElementById(
            "chat-history-box"
        );

    const statisticsBox =
        document.getElementById(
            "library-statistics-box"
        );


    if (!statisticsBox) {

        console.error(
            "Không tìm thấy library-statistics-box"
        );

        return;

    }


    // Ẩn các phần khác
    if (welcome) {

        welcome.style.display =
            "none";

    }


    if (historyBox) {

        historyBox.style.display =
            "none";

    }


    // Hiện thống kê
    statisticsBox.style.display =
        "block";


    // Loading
    const totalBooks =
        document.getElementById(
            "stat-total-books"
        );

    const totalAuthors =
        document.getElementById(
            "stat-total-authors"
        );

    const totalCategories =
        document.getElementById(
            "stat-total-categories"
        );

    const totalPublishers =
        document.getElementById(
            "stat-total-publishers"
        );


    if (totalBooks)
        totalBooks.textContent = "…";

    if (totalAuthors)
        totalAuthors.textContent = "…";

    if (totalCategories)
        totalCategories.textContent = "…";

    if (totalPublishers)
        totalPublishers.textContent = "…";


    const categoryList =
        document.getElementById(
            "category-list"
        );


    if (categoryList) {

        categoryList.innerHTML = `
            <div class="history-empty">
                ⏳ Đang tải dữ liệu...
            </div>
        `;

    }


    try {

        const response =
            await fetch(
                "/library-statistics"
            );


        if (!response.ok) {

            throw new Error(
                "Không thể lấy dữ liệu thống kê"
            );

        }


        const data =
            await response.json();


        console.log(
            "DỮ LIỆU THỐNG KÊ:",
            data
        );


        // ==========================================
        // 4 Ô THỐNG KÊ
        // ==========================================

        if (totalBooks) {

            totalBooks.textContent =
                data.total_books ?? 0;

        }


        if (totalAuthors) {

            totalAuthors.textContent =
                data.total_authors ?? 0;

        }


        if (totalCategories) {

            totalCategories.textContent =
                data.total_categories ?? 0;

        }


        if (totalPublishers) {

            totalPublishers.textContent =
                data.total_publishers ?? 0;

        }


        // ==========================================
        // THỐNG KÊ THEO THỂ LOẠI
        // ==========================================

        if (categoryList) {

            categoryList.innerHTML = "";


            if (
                !data.categories ||
                data.categories.length === 0
            ) {

                categoryList.innerHTML = `
                    <div class="history-empty">
                        📚 Chưa có dữ liệu thể loại sách.
                    </div>
                `;

                return;

            }


            data.categories.forEach(
                function(category) {

                    const item =
                        document.createElement(
                            "div"
                        );

                    item.className =
                        "category-item";


                    const name =
                        document.createElement(
                            "span"
                        );

                    name.textContent =
                        category.name ||
                        "Không xác định";


                    const count =
                        document.createElement(
                            "strong"
                        );

                    count.textContent =
                        (category.count ?? 0) +
                        " sách";


                    item.appendChild(
                        name
                    );

                    item.appendChild(
                        count
                    );


                    categoryList.appendChild(
                        item
                    );

                }
            );

        }


    } catch (error) {

        console.error(
            "Lỗi thống kê:",
            error
        );


        if (totalBooks)
            totalBooks.textContent = "—";

        if (totalAuthors)
            totalAuthors.textContent = "—";

        if (totalCategories)
            totalCategories.textContent = "—";

        if (totalPublishers)
            totalPublishers.textContent = "—";


        if (categoryList) {

            categoryList.innerHTML = `
                <div class="history-empty">
                    ❌ Không thể tải dữ liệu thống kê.
                </div>
            `;

        }

    }

}



// =====================================================
// THÔNG TIN THƯ VIỆN - NÚT BÊN TRÁI
// =====================================================

async function showLibraryInfo(type) {

    const chatBox =
        document.getElementById(
            "chat-box"
        );


    if (!chatBox) return;


    showChat();


    const loading =
        document.createElement(
            "div"
        );


    loading.className =
        "message bot";


    loading.innerHTML =
        "⏳ Đang lấy thông tin từ thư viện...";


    chatBox.appendChild(
        loading
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;


    try {

        const response =
            await fetch(
                "/library-info/" +
                encodeURIComponent(type)
            );


        if (!response.ok) {

            throw new Error(
                "Lỗi máy chủ"
            );

        }


        const data =
            await response.json();


        loading.remove();


        const messageId =
            addMessage(
                data.answer ||
                "Không có dữ liệu.",
                "bot"
            );


        const botMessage =
            document.getElementById(
                messageId
            );


        if (botMessage) {

            const source =
                document.createElement(
                    "div"
                );


            source.className =
                "source-info";


            source.textContent =
                "📌 Nguồn: Cơ sở dữ liệu thư viện";


            botMessage.appendChild(
                source
            );

        }


    } catch (error) {

        console.error(
            "Lỗi thông tin thư viện:",
            error
        );


        loading.remove();


        addMessage(
            "❌ Không thể lấy dữ liệu thư viện.",
            "bot"
        );

    }

}



// =====================================================
// ENTER ĐỂ GỬI
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const input =
            document.getElementById(
                "user-input"
            );


        if (!input) return;


        input.addEventListener(
            "keydown",
            function(event) {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendMessage();

                }

            }
        );

    }
);