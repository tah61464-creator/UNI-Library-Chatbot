from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from google import genai

app = Flask(__name__)

DATABASE = "database.db"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
# ==================================================
# KẾT NỐI DATABASE
# ==================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==================================================
# LẤY TẤT CẢ SÁCH
# ==================================================

def get_all_books():
    conn = get_db()

    books = conn.execute("""
        SELECT *
        FROM books
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return books


# ==================================================
# ĐẾM SỐ SÁCH
# ==================================================

def count_books():
    conn = get_db()

    result = conn.execute("""
        SELECT COUNT(*) AS total
        FROM books
    """).fetchone()

    conn.close()

    return result["total"]


# ==================================================
# TÌM KIẾM SÁCH
# ==================================================

def search_books(keyword):

    conn = get_db()

    keyword = keyword.lower().strip()

    books = conn.execute("""
        SELECT *
        FROM books
        WHERE LOWER(ten_sach) LIKE ?
           OR LOWER(tac_gia) LIKE ?
           OR LOWER(the_loai) LIKE ?
           OR LOWER(mo_ta) LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    )).fetchall()

    conn.close()

    return books

# ==================================================
# KẾT NỐI GEMINI
# ==================================================

def ask_chatgpt(question):

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",

            contents=f"""
Bạn là chatbot hỗ trợ sinh viên của Thư viện Học viện Phụ nữ Việt Nam.

Hãy trò chuyện với người dùng một cách tự nhiên như một trợ lý AI.

Nguyên tắc:
- Trả lời bằng tiếng Việt.
- Không cần trả lời theo mẫu cố định.
- Không cần liệt kê các nguyên tắc hoặc nhiệm vụ của bạn.
- Có thể trả lời ngắn hoặc dài tùy theo câu hỏi.
- Nếu câu hỏi đơn giản thì trả lời ngắn gọn.
- Nếu người dùng hỏi cần giải thích thì giải thích rõ ràng.
- Có thể dùng emoji vừa phải khi phù hợp.
- Không tự bịa thông tin về sách trong thư viện.
- Nếu không có dữ liệu về một cuốn sách cụ thể, hãy nói rõ là chưa tìm thấy thông tin trong hệ thống thư viện.
- Với câu hỏi ngoài phạm vi thư viện nhưng là kiến thức thông thường, có thể trả lời như một chatbot AI.

Hãy trả lời trực tiếp câu hỏi của người dùng, không nhắc lại những hướng dẫn trên.

Câu hỏi:
{question}
"""
        )

        return response.text

    except Exception as e:

        print("Lỗi Gemini:", e)

        return "Mình đang gặp vấn đề khi kết nối với Gemini. Bạn thử lại sau nhé."


# ==================================================
# XỬ LÝ CÂU HỎI CHATBOT
# ==================================================

def chatbot_answer(question):

    question = question.lower().strip()


    # ==================================================
    # CHÀO HỎI
    # ==================================================

    if any(x in question for x in [
        "xin chào",
        "chào",
        "hello",
        "hi",
        "alo"
    ]):

        return """
👋 Xin chào!

Mình là **UNI Library Chatbot** của Thư viện Học viện Phụ nữ Việt Nam.

Mình có thể hỗ trợ bạn:

📚 Tra cứu sách
🔎 Tìm sách theo tên
👤 Tìm sách theo tác giả
📂 Tìm sách theo thể loại
📊 Xem tổng số sách
📖 Xem danh sách sách
🤖 Hỗ trợ giải đáp câu hỏi về thư viện

Bạn muốn tìm sách gì?
"""


    # ==================================================
    # TỔNG SỐ SÁCH
    # ==================================================

    if (
        "tổng số sách" in question
        or "bao nhiêu sách" in question
        or "có bao nhiêu cuốn" in question
    ):

        total = count_books()

        return f"""
📚 **Tổng số sách trong thư viện**

Hiện tại thư viện có **{total} cuốn sách** trong cơ sở dữ liệu.
"""


    # ==================================================
    # XEM TẤT CẢ SÁCH
    # ==================================================

    if (
        "danh sách sách" in question
        or "tất cả sách" in question
        or "liệt kê sách" in question
    ):

        books = get_all_books()

        if not books:

            return "📚 Hiện tại chưa có sách trong cơ sở dữ liệu."

        answer = "📖 **DANH SÁCH SÁCH TRONG THƯ VIỆN**\n\n"

        for i, book in enumerate(books, 1):

            answer += (
                f"**{i}. {book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                f"🏢 Nhà xuất bản: {book['nha_xuat_ban']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return answer


    # ==================================================
    # SÁCH PYTHON
    # ==================================================

    if "python" in question:

        books = search_books("python")

        if not books:

            return "❌ Không tìm thấy sách liên quan đến Python."

        answer = "🐍 **SÁCH LIÊN QUAN ĐẾN PYTHON**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return answer


    # ==================================================
    # SÁCH MARKETING
    # ==================================================

    if "marketing" in question:

        books = search_books("marketing")

        if not books:

            return "❌ Không tìm thấy sách liên quan đến Marketing."

        answer = "📢 **SÁCH LIÊN QUAN ĐẾN MARKETING**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return answer


    # ==================================================
    # SÁCH TRÍ TUỆ NHÂN TẠO
    # ==================================================

    if (
        "trí tuệ nhân tạo" in question
        or "artificial intelligence" in question
        or question == "ai"
    ):

        books = search_books("trí tuệ nhân tạo")

        if not books:

            books = search_books("AI")

        if not books:

            return "❌ Không tìm thấy sách về Trí tuệ nhân tạo."

        answer = "🤖 **SÁCH VỀ TRÍ TUỆ NHÂN TẠO**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return answer


    # ==================================================
    # SÁCH VỀ PHỤ NỮ
    # ==================================================

    if "phụ nữ" in question:

        books = search_books("phụ nữ")

        if not books:

            return "❌ Không tìm thấy sách liên quan đến phụ nữ."

        answer = "👩 **SÁCH LIÊN QUAN ĐẾN PHỤ NỮ**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return answer


    # ==================================================
    # TÌM KIẾM SÁCH THEO TỪ KHÓA
    # ==================================================

    tu_khoa_bo_qua = [
        "tìm",
        "tìm sách",
        "cho tôi",
        "hãy tìm",
        "sách",
        "cuốn",
        "quyển",
        "thông tin",
        "về",
        "có",
        "không",
        "cho",
        "tôi",
        "mình",
        "xin",
        "hãy"
    ]

    keyword = question

    for tu in tu_khoa_bo_qua:

        keyword = keyword.replace(tu, " ")

    keyword = " ".join(keyword.split())


    if keyword:

        books = search_books(keyword)

        if books:

            answer = f"🔎 **KẾT QUẢ TÌM KIẾM: {keyword}**\n\n"

            for book in books:

                answer += (
                    f"📖 **{book['ten_sach']}**\n"
                    f"👤 Tác giả: {book['tac_gia']}\n"
                    f"📂 Thể loại: {book['the_loai']}\n"
                    f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                    f"🏢 Nhà xuất bản: {book['nha_xuat_ban']}\n"
                    f"📍 Vị trí: {book['vi_tri']}\n"
                    f"📦 Số lượng: {book['so_luong']}\n"
                    f"📝 {book['mo_ta']}\n\n"
                )

            return answer


    # ==================================================
    # KHÔNG TÌM THẤY → GỬI SANG CHATGPT
    # ==================================================

    return ask_chatgpt(question)


# ==================================================
# TRANG CHỦ
# ==================================================

@app.route("/")
def index():

    return render_template("index.html")


# ==================================================
# API CHAT
# ==================================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    question = data.get("message", "")

    if not question:

        return jsonify({
            "answer": "Bạn hãy nhập câu hỏi nhé! 😊"
        })

    answer = chatbot_answer(question)

    return jsonify({
        "answer": answer
    })


# ==================================================
# API CHO CÁC NÚT TRA CỨU NHANH
# ==================================================

@app.route("/library-info/<info_type>")
def library_info(info_type):


    # ==================================================
    # TỔNG SỐ SÁCH
    # ==================================================

    if info_type == "total":

        total = count_books()

        return jsonify({
            "answer":
                f"📚 **Tổng số sách trong thư viện**\n\n"
                f"Hiện tại thư viện có **{total} cuốn sách** "
                f"trong cơ sở dữ liệu."
        })


    # ==================================================
    # TẤT CẢ SÁCH
    # ==================================================

    elif info_type == "all":

        books = get_all_books()

        if not books:

            return jsonify({
                "answer": "📚 Hiện tại chưa có sách."
            })

        answer = "📖 **DANH SÁCH SÁCH TRONG THƯ VIỆN**\n\n"

        for i, book in enumerate(books, 1):

            answer += (
                f"**{i}. {book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📅 Năm xuất bản: {book['nam_xuat_ban']}\n"
                f"🏢 Nhà xuất bản: {book['nha_xuat_ban']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return jsonify({
            "answer": answer
        })


    # ==================================================
    # PYTHON
    # ==================================================

    elif info_type == "python":

        books = search_books("python")

        if not books:

            return jsonify({
                "answer": "❌ Không tìm thấy sách liên quan đến Python."
            })

        answer = "🐍 **SÁCH VỀ PYTHON**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return jsonify({
            "answer": answer
        })


    # ==================================================
    # MARKETING
    # ==================================================

    elif info_type == "marketing":

        books = search_books("marketing")

        if not books:

            return jsonify({
                "answer": "❌ Không tìm thấy sách Marketing."
            })

        answer = "📢 **SÁCH VỀ MARKETING**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return jsonify({
            "answer": answer
        })


    # ==================================================
    # AI
    # ==================================================

    elif info_type == "ai":

        books = search_books("trí tuệ nhân tạo")

        if not books:

            books = search_books("AI")

        if not books:

            return jsonify({
                "answer": "❌ Không tìm thấy sách về Trí tuệ nhân tạo."
            })

        answer = "🤖 **SÁCH VỀ TRÍ TUỆ NHÂN TẠO**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return jsonify({
            "answer": answer
        })


    # ==================================================
    # PHỤ NỮ
    # ==================================================

    elif info_type == "women":

        books = search_books("phụ nữ")

        if not books:

            return jsonify({
                "answer": "❌ Không tìm thấy sách liên quan đến phụ nữ."
            })

        answer = "👩 **SÁCH VỀ PHỤ NỮ**\n\n"

        for book in books:

            answer += (
                f"📖 **{book['ten_sach']}**\n"
                f"👤 Tác giả: {book['tac_gia']}\n"
                f"📂 Thể loại: {book['the_loai']}\n"
                f"📝 {book['mo_ta']}\n"
                f"📍 Vị trí: {book['vi_tri']}\n"
                f"📦 Số lượng: {book['so_luong']}\n\n"
            )

        return jsonify({
            "answer": answer
        })


    # ==================================================
    # KHÔNG TÌM THẤY CHỨC NĂNG
    # ==================================================

    return jsonify({
        "answer": "❌ Không tìm thấy chức năng này."
    })


# ==================================================
# CHẠY SERVER
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )