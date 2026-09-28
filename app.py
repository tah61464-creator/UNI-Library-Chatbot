from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
from google import genai

app = Flask(__name__)
app.secret_key = "uni-library-secret-key-2026"

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
# TẠO BẢNG LỊCH SỬ CHAT
# ==================================================

def create_chat_history_table():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
# ==================================================
# LƯU LỊCH SỬ CHAT
# ==================================================

def save_chat_history(question, answer):

    conn = get_db()

    conn.execute("""
        INSERT INTO chat_history (question, answer)
        VALUES (?, ?)
    """, (question, answer))

    conn.commit()
    conn.close()
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
# LỌC TỪ KHÓA TÌM KIẾM SÁCH
# ==================================================

def extract_book_keyword(question):

    question = question.lower().strip()

    # Các cụm từ thường xuất hiện trong câu hỏi
    stop_phrases = [
        "tìm kiếm cho tôi",
        "tìm kiếm giúp tôi",
        "tìm cho tôi",
        "tìm giúp tôi",
        "tìm kiếm",
        "tìm",
        "cho tôi",
        "cho mình",
        "giúp tôi",
        "giúp mình",
        "tôi muốn",
        "mình muốn",
        "hãy",
        "thông tin về",
        "thông tin",
        "giới thiệu về",
        "giới thiệu",
        "nói cho tôi biết",
        "nói cho mình biết",
        "bạn có",
        "bạn hãy",
        "xin",
        "vui lòng",
        "sách",
        "cuốn sách",
        "cuốn",
        "tài liệu",
        "về",
        "không"
    ]

    keyword = question

    # Xóa các cụm từ không mang ý nghĩa tìm kiếm
    for phrase in stop_phrases:
        keyword = keyword.replace(phrase, " ")

    # Xóa khoảng trắng thừa
    keyword = " ".join(keyword.split())

    return keyword.strip()

# ==================================================
# TÌM KIẾM SÁCH
# ==================================================

def search_books(keyword):

    conn = get_db()

    keyword = keyword.lower().strip()

    if not keyword:
        conn.close()
        return []

    search_pattern = f"%{keyword}%"

    books = conn.execute("""
        SELECT *
        FROM books
        WHERE LOWER(ten_sach) LIKE ?
           OR LOWER(tac_gia) LIKE ?
           OR LOWER(the_loai) LIKE ?
           OR LOWER(mo_ta) LIKE ?
        ORDER BY
            CASE
                WHEN LOWER(ten_sach) LIKE ? THEN 1
                WHEN LOWER(tac_gia) LIKE ? THEN 2
                WHEN LOWER(the_loai) LIKE ? THEN 3
                ELSE 4
            END,
            id DESC
    """, (
        search_pattern,
        search_pattern,
        search_pattern,
        search_pattern,
        search_pattern,
        search_pattern,
        search_pattern
    )).fetchall()

    conn.close()

    return books

# ==================================================
# KẾT NỐI GEMINI
# ==================================================

def ask_chatgpt(question, books=None):

    try:

        # Tạo dữ liệu sách để gửi cho Gemini
        book_context = ""

        if books:

            book_context = "\n\nDỮ LIỆU SÁCH TỪ THƯ VIỆN:\n"

            for book in books:

                book_context += f"""
Tên sách: {book['ten_sach']}
Tác giả: {book['tac_gia']}
Thể loại: {book['the_loai']}
Năm xuất bản: {book['nam_xuat_ban']}
Nhà xuất bản: {book['nha_xuat_ban']}
Vị trí: {book['vi_tri']}
Số lượng: {book['so_luong']}
Mô tả: {book['mo_ta']}
"""

        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=f"""
Bạn là UNI Library Chatbot của Thư viện Học viện Phụ nữ Việt Nam.

Nhiệm vụ của bạn là hỗ trợ người dùng tra cứu và giải đáp thông tin.

QUY TẮC:

- Trả lời bằng tiếng Việt.
- Trả lời tự nhiên, dễ hiểu.
- Có thể sử dụng emoji phù hợp.
- Nếu có dữ liệu sách từ thư viện được cung cấp bên dưới, chỉ sử dụng dữ liệu đó.
- Không được tự bịa tên sách, tác giả, năm xuất bản, vị trí hoặc số lượng sách.
- Nếu dữ liệu thư viện không có thông tin mà người dùng hỏi, hãy nói rõ rằng hệ thống chưa tìm thấy thông tin.
- Với câu hỏi kiến thức thông thường, có thể trả lời như một trợ lý AI.
- Không nhắc lại các quy tắc này trong câu trả lời.

DỮ LIỆU THƯ VIỆN:
{book_context}

CÂU HỎI CỦA NGƯỜI DÙNG:
{question}

Hãy trả lời trực tiếp câu hỏi của người dùng.
"""
        )

        return response.text

    except Exception as e:

        print("Lỗi Gemini:", e)

        return "Mình đang gặp vấn đề khi kết nối với Gemini. Bạn thử lại sau nhé."

# ==================================================
# CHATBOT
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
🤖 Giải đáp câu hỏi

Bạn muốn tìm thông tin gì?
"""

    # ==================================================
    # TỔNG SỐ SÁCH
    # ==================================================

    if (
        "tổng số sách" in question
        or "bao nhiêu sách" in question
        or "có bao nhiêu cuốn" in question
        or "số lượng sách" in question
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
        or "có những sách nào" in question
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
    # TÌM KIẾM SÁCH
    # ==================================================

    keyword = extract_book_keyword(question)

    print("TỪ KHÓA TÌM KIẾM:", keyword)

    if keyword:

        books = search_books(keyword)

        if books:

            # Gửi dữ liệu sách cho Gemini
            return ask_chatgpt(question, books)

    # ==================================================
    # KHÔNG TÌM THẤY SÁCH
    # → GỬI CÂU HỎI CHO GEMINI
    # ==================================================

    return ask_chatgpt(question)
# ==================================================
# ADMIN - ĐĂNG NHẬP
# ==================================================

@app.route("/admin/login", methods=["GET"])
def admin_login_page():
    return render_template("login.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():

    try:

        data = request.get_json()

        username = data.get("username", "").strip()
        password = data.get("password", "")

        # Tài khoản admin dùng để test
        if username == "admin" and password == "123456":

            session["admin_logged_in"] = True
            session["admin_username"] = username

            return jsonify({
                "message": "Đăng nhập thành công."
            })

        return jsonify({
            "error": "Tên đăng nhập hoặc mật khẩu không đúng."
        }), 401

    except Exception as e:

        print("========== LỖI ĐĂNG NHẬP ==========")
        print("Lỗi:", e)
        print("====================================")

        return jsonify({
            "error": "Không thể đăng nhập."
        }), 500
# ==================================================
# ADMIN - ĐĂNG XUẤT
# ==================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)

    return redirect(url_for("admin_login_page"))
# ==================================================
# TRANG CHỦ
# ==================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login_page"))

    return render_template("admin.html")

# ==================================================
# API ADMIN - LẤY DANH SÁCH SÁCH
# ==================================================

@app.route("/admin/books", methods=["GET"])
def admin_get_books():

    try:

        conn = get_db()

        books = conn.execute("""
            SELECT
                id,
                ma_sach,
                ten_sach,
                tac_gia,
                the_loai,
                nam_xuat_ban,
                nha_xuat_ban,
                vi_tri,
                so_luong,
                mo_ta
            FROM books
            ORDER BY id DESC
        """).fetchall()

        conn.close()

        data = []

        for book in books:

            data.append({
                "id": book["id"],
                "ma_sach": book["ma_sach"],
                "ten_sach": book["ten_sach"],
                "tac_gia": book["tac_gia"],
                "the_loai": book["the_loai"],
                "nam_xuat_ban": book["nam_xuat_ban"],
                "nha_xuat_ban": book["nha_xuat_ban"],
                "vi_tri": book["vi_tri"],
                "so_luong": book["so_luong"],
                "mo_ta": book["mo_ta"]
            })

        return jsonify(data)

    except Exception as e:

        print("========== LỖI ADMIN BOOKS ==========")
        print("Lỗi:", e)
        print("======================================")

        return jsonify({
            "error": "Không thể lấy danh sách sách."
        }), 500


# ==================================================
# API ADMIN - THÊM SÁCH
# ==================================================

@app.route("/admin/books", methods=["POST"])
def admin_add_book():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Không nhận được dữ liệu sách."
            }), 400

        ma_sach = data.get("ma_sach", "").strip()
        ten_sach = data.get("ten_sach", "").strip()
        tac_gia = data.get("tac_gia", "").strip()
        the_loai = data.get("the_loai", "").strip()
        nam_xuat_ban = data.get("nam_xuat_ban")
        nha_xuat_ban = data.get("nha_xuat_ban", "").strip()
        vi_tri = data.get("vi_tri", "").strip()
        so_luong = data.get("so_luong")
        mo_ta = data.get("mo_ta", "").strip()

        if not ma_sach:
            return jsonify({
                "error": "Vui lòng nhập mã sách."
            }), 400

        if not ten_sach:
            return jsonify({
                "error": "Vui lòng nhập tên sách."
            }), 400

        if not tac_gia:
            return jsonify({
                "error": "Vui lòng nhập tác giả."
            }), 400

        if not the_loai:
            return jsonify({
                "error": "Vui lòng nhập thể loại."
            }), 400

        if not nam_xuat_ban:
            return jsonify({
                "error": "Vui lòng nhập năm xuất bản."
            }), 400

        if not nha_xuat_ban:
            return jsonify({
                "error": "Vui lòng nhập nhà xuất bản."
            }), 400

        if not vi_tri:
            return jsonify({
                "error": "Vui lòng nhập vị trí."
            }), 400

        if so_luong is None:
            return jsonify({
                "error": "Vui lòng nhập số lượng."
            }), 400

        conn = get_db()

        existing_book = conn.execute("""
            SELECT id
            FROM books
            WHERE ma_sach = ?
        """, (ma_sach,)).fetchone()

        if existing_book:

            conn.close()

            return jsonify({
                "error": "Mã sách đã tồn tại."
            }), 400

        conn.execute("""
            INSERT INTO books (
                ma_sach,
                ten_sach,
                tac_gia,
                the_loai,
                nam_xuat_ban,
                nha_xuat_ban,
                vi_tri,
                so_luong,
                mo_ta
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_sach,
            ten_sach,
            tac_gia,
            the_loai,
            int(nam_xuat_ban),
            nha_xuat_ban,
            vi_tri,
            int(so_luong),
            mo_ta
        ))

        conn.commit()

        new_id = conn.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        conn.close()

        return jsonify({
            "message": "Thêm sách thành công.",
            "id": new_id
        }), 201

    except ValueError:

        return jsonify({
            "error": "Năm xuất bản và số lượng phải là số."
        }), 400

    except Exception as e:

        print("========== LỖI THÊM SÁCH ==========")
        print("Lỗi:", e)
        print("====================================")

        return jsonify({
            "error": "Không thể thêm sách vào cơ sở dữ liệu."
        }), 500
# ==================================================
# API ADMIN - SỬA SÁCH
# ==================================================

@app.route("/admin/books/<int:book_id>", methods=["PUT"])
def admin_update_book(book_id):

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Không nhận được dữ liệu sách."
            }), 400

        ma_sach = data.get("ma_sach", "").strip()
        ten_sach = data.get("ten_sach", "").strip()
        tac_gia = data.get("tac_gia", "").strip()
        the_loai = data.get("the_loai", "").strip()
        nam_xuat_ban = data.get("nam_xuat_ban")
        nha_xuat_ban = data.get("nha_xuat_ban", "").strip()
        vi_tri = data.get("vi_tri", "").strip()
        so_luong = data.get("so_luong")
        mo_ta = data.get("mo_ta", "").strip()

        # Kiểm tra dữ liệu bắt buộc
        if not ma_sach:
            return jsonify({
                "error": "Vui lòng nhập mã sách."
            }), 400

        if not ten_sach:
            return jsonify({
                "error": "Vui lòng nhập tên sách."
            }), 400

        if not tac_gia:
            return jsonify({
                "error": "Vui lòng nhập tác giả."
            }), 400

        if not the_loai:
            return jsonify({
                "error": "Vui lòng nhập thể loại."
            }), 400

        if not nam_xuat_ban:
            return jsonify({
                "error": "Vui lòng nhập năm xuất bản."
            }), 400

        if not nha_xuat_ban:
            return jsonify({
                "error": "Vui lòng nhập nhà xuất bản."
            }), 400

        if not vi_tri:
            return jsonify({
                "error": "Vui lòng nhập vị trí."
            }), 400

        if so_luong is None:
            return jsonify({
                "error": "Vui lòng nhập số lượng."
            }), 400

        conn = get_db()

        # Kiểm tra sách có tồn tại không
        book = conn.execute("""
            SELECT id
            FROM books
            WHERE id = ?
        """, (book_id,)).fetchone()

        if not book:

            conn.close()

            return jsonify({
                "error": "Không tìm thấy sách cần sửa."
            }), 404

        # Kiểm tra mã sách có bị trùng với sách khác không
        duplicate = conn.execute("""
            SELECT id
            FROM books
            WHERE ma_sach = ?
            AND id != ?
        """, (ma_sach, book_id)).fetchone()

        if duplicate:

            conn.close()

            return jsonify({
                "error": "Mã sách đã tồn tại ở sách khác."
            }), 400

        # Cập nhật sách
        conn.execute("""
            UPDATE books
            SET
                ma_sach = ?,
                ten_sach = ?,
                tac_gia = ?,
                the_loai = ?,
                nam_xuat_ban = ?,
                nha_xuat_ban = ?,
                vi_tri = ?,
                so_luong = ?,
                mo_ta = ?
            WHERE id = ?
        """, (
            ma_sach,
            ten_sach,
            tac_gia,
            the_loai,
            int(nam_xuat_ban),
            nha_xuat_ban,
            vi_tri,
            int(so_luong),
            mo_ta,
            book_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Cập nhật sách thành công."
        })

    except ValueError:

        return jsonify({
            "error": "Năm xuất bản và số lượng phải là số."
        }), 400

    except Exception as e:

        print("========== LỖI SỬA SÁCH ==========")
        print("Lỗi:", e)
        print("===================================")

        return jsonify({
            "error": "Không thể cập nhật sách."
        }), 500
# ==================================================
# API ADMIN - XÓA SÁCH
# ==================================================

@app.route("/admin/books/<int:book_id>", methods=["DELETE"])
def admin_delete_book(book_id):

    try:

        conn = get_db()

        # Kiểm tra sách có tồn tại không
        book = conn.execute("""
            SELECT id, ten_sach
            FROM books
            WHERE id = ?
        """, (book_id,)).fetchone()

        if not book:
            conn.close()

            return jsonify({
                "error": "Không tìm thấy sách cần xóa."
            }), 404

        # Xóa sách
        conn.execute("""
            DELETE FROM books
            WHERE id = ?
        """, (book_id,))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Xóa sách thành công.",
            "id": book_id
        })

    except Exception as e:

        print("========== LỖI XÓA SÁCH ==========")
        print("Lỗi:", e)
        print("===================================")

        return jsonify({
            "error": "Không thể xóa sách."
        }), 500
    
@app.route("/")
def index():

    return render_template("index.html")
# ==================================================
# API CHAT
# ==================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "answer": "❌ Không nhận được dữ liệu từ giao diện."
            }), 400

        question = data.get("message", "").strip()

        if not question:
            return jsonify({
                "answer": "Bạn hãy nhập câu hỏi nhé! 😊"
            }), 400

        print("====================================")
        print("CÂU HỎI:", question)
        print("====================================")

        answer = chatbot_answer(question)

        # Lưu lịch sử chat
        save_chat_history(question, answer)

        return jsonify({
            "answer": answer,
            "source": "Cơ sở dữ liệu thư viện + Gemini AI"
        })

    except Exception as e:

        print("========== LỖI /CHAT ==========")
        print("Lỗi:", e)
        print("===============================")

        return jsonify({
            "answer": "❌ Hệ thống gặp lỗi khi xử lý câu hỏi. Bạn hãy thử lại sau."
        }), 500


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
# LẤY LỊCH SỬ CHAT
# ==================================================

@app.route("/chat-history")
def chat_history():

    conn = get_db()

    history = conn.execute("""
        SELECT id, question, answer, created_at
        FROM chat_history
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    data = []

    for item in history:
        data.append({
            "id": item["id"],
            "question": item["question"],
            "answer": item["answer"],
            "created_at": item["created_at"]
        })

    return jsonify(data)
# ==================================================
# API THỐNG KÊ THƯ VIỆN
# ==================================================

@app.route("/library-statistics")
def library_statistics():

    try:

        conn = get_db()

        # ==========================================
        # 1. TỔNG SỐ SÁCH
        # ==========================================

        total_books = conn.execute("""
            SELECT COUNT(*) AS total
            FROM books
        """).fetchone()["total"]


        # ==========================================
        # 2. SỐ TÁC GIẢ
        # ==========================================

        total_authors = conn.execute("""
            SELECT COUNT(DISTINCT tac_gia) AS total
            FROM books
            WHERE tac_gia IS NOT NULL
            AND TRIM(tac_gia) != ''
        """).fetchone()["total"]


        # ==========================================
        # 3. SỐ THỂ LOẠI
        # ==========================================

        total_categories = conn.execute("""
            SELECT COUNT(DISTINCT the_loai) AS total
            FROM books
            WHERE the_loai IS NOT NULL
            AND TRIM(the_loai) != ''
        """).fetchone()["total"]


        # ==========================================
        # 4. SỐ NHÀ XUẤT BẢN
        # ==========================================

        total_publishers = conn.execute("""
            SELECT COUNT(DISTINCT nha_xuat_ban) AS total
            FROM books
            WHERE nha_xuat_ban IS NOT NULL
            AND TRIM(nha_xuat_ban) != ''
        """).fetchone()["total"]


        # ==========================================
        # 5. THỐNG KÊ SÁCH THEO THỂ LOẠI
        # ==========================================

        category_rows = conn.execute("""
            SELECT
                the_loai,
                COUNT(*) AS so_luong
            FROM books
            WHERE the_loai IS NOT NULL
            AND TRIM(the_loai) != ''
            GROUP BY the_loai
            ORDER BY so_luong DESC
        """).fetchall()


        categories = []

        for row in category_rows:

            categories.append({
                "name": row["the_loai"],
                "count": row["so_luong"]
            })


        conn.close()


        # ==========================================
        # TRẢ DỮ LIỆU VỀ JAVASCRIPT
        # ==========================================

        return jsonify({

            "total_books": total_books,

            "total_authors": total_authors,

            "total_categories": total_categories,

            "total_publishers": total_publishers,

            "categories": categories

        })


    except Exception as e:

        print("========== LỖI THỐNG KÊ ==========")
        print("Lỗi:", e)
        print("===================================")

        return jsonify({

            "error": "Không thể lấy dữ liệu thống kê.",

            "total_books": 0,

            "total_authors": 0,

            "total_categories": 0,

            "total_publishers": 0,

            "categories": []

        }), 500

@app.route("/health")
def health():

    status = {
        "flask": "OK",
        "database": "OK",
        "gemini": "OK"
    }

    # Kiểm tra Database
    try:

        conn = get_db()

        conn.execute("SELECT 1").fetchone()

        conn.close()

    except Exception as e:

        status["database"] = "ERROR"
        status["database_error"] = str(e)

    # Kiểm tra Gemini API Key
    try:

        if not os.getenv("GEMINI_API_KEY"):

            status["gemini"] = "ERROR"
            status["gemini_error"] = "Chưa cấu hình GEMINI_API_KEY"

    except Exception as e:

        status["gemini"] = "ERROR"
        status["gemini_error"] = str(e)

    # Kiểm tra tổng thể
    if (
        status["flask"] == "OK"
        and status["database"] == "OK"
        and status["gemini"] == "OK"
    ):

        status["status"] = "OK"

    else:

        status["status"] = "ERROR"

    return jsonify(status)
# ==================================================
# CHẠY SERVER
# ==================================================

if __name__ == "__main__":

    create_chat_history_table()

    app.run(debug=True)