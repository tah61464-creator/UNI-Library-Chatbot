import sqlite3

DATABASE = "database.db"


def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Xóa bảng cũ nếu đã tồn tại
    cursor.execute("DROP TABLE IF EXISTS books")

    # Tạo bảng sách
    cursor.execute("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sach TEXT NOT NULL,
            ten_sach TEXT NOT NULL,
            tac_gia TEXT NOT NULL,
            the_loai TEXT NOT NULL,
            nam_xuat_ban INTEGER,
            nha_xuat_ban TEXT,
            vi_tri TEXT,
            so_luong INTEGER DEFAULT 0,
            mo_ta TEXT
        )
    """)

    # Dữ liệu sách mẫu
    books = [
        (
            "S001",
            "Giáo trình Công nghệ thông tin",
            "Nguyễn Văn An",
            "Công nghệ thông tin",
            2023,
            "Nhà xuất bản Đại học Quốc gia",
            "Kệ A1 - Tầng 1",
            5,
            "Giáo trình cung cấp kiến thức cơ bản về công nghệ thông tin."
        ),
        (
            "S002",
            "Lập trình Java cơ bản",
            "Trần Minh Đức",
            "Lập trình",
            2022,
            "Nhà xuất bản Khoa học và Kỹ thuật",
            "Kệ A2 - Tầng 1",
            4,
            "Tài liệu hướng dẫn lập trình Java từ cơ bản đến nâng cao."
        ),
        (
            "S003",
            "Cơ sở dữ liệu",
            "Lê Thị Mai",
            "Cơ sở dữ liệu",
            2023,
            "Nhà xuất bản Giáo dục",
            "Kệ A3 - Tầng 1",
            6,
            "Giới thiệu các khái niệm và kỹ thuật về cơ sở dữ liệu."
        ),
        (
            "S004",
            "Lập trình Python cơ bản",
            "Phạm Hoàng Long",
            "Lập trình",
            2024,
            "Nhà xuất bản Đại học Quốc gia",
            "Kệ C1 - Tầng 2",
            6,
            "Hướng dẫn lập trình Python dành cho người mới bắt đầu."
        ),
        (
            "S005",
            "Phân tích và thiết kế hệ thống",
            "Nguyễn Thị Hương",
            "Phân tích hệ thống",
            2022,
            "Nhà xuất bản Bách khoa",
            "Kệ B1 - Tầng 1",
            3,
            "Tài liệu về phân tích, thiết kế và xây dựng hệ thống thông tin."
        ),
        (
            "S006",
            "Quản trị kinh doanh hiện đại",
            "Đỗ Minh Quân",
            "Quản trị kinh doanh",
            2024,
            "Nhà xuất bản Lao động",
            "Kệ D1 - Tầng 2",
            5,
            "Cung cấp kiến thức về quản trị doanh nghiệp hiện đại."
        ),
        (
            "S007",
            "Marketing căn bản",
            "Nguyễn Thị Lan",
            "Marketing",
            2023,
            "Nhà xuất bản Kinh tế Quốc dân",
            "Kệ D2 - Tầng 2",
            7,
            "Kiến thức nền tảng về marketing và hoạt động tiếp thị."
        ),
        (
            "S008",
            "Tâm lý học đại cương",
            "Trần Thị Hoa",
            "Tâm lý học",
            2021,
            "Nhà xuất bản Đại học Quốc gia",
            "Kệ E1 - Tầng 2",
            4,
            "Giới thiệu các khái niệm cơ bản trong tâm lý học."
        ),
        (
            "S009",
            "Kỹ năng giao tiếp",
            "Lê Hoàng Nam",
            "Kỹ năng mềm",
            2022,
            "Nhà xuất bản Thanh niên",
            "Kệ E2 - Tầng 2",
            8,
            "Hướng dẫn các kỹ năng giao tiếp trong học tập và công việc."
        ),
        (
            "S010",
            "Phụ nữ Việt Nam trong thời đại mới",
            "Nguyễn Thu Hà",
            "Phụ nữ",
            2024,
            "Nhà xuất bản Phụ nữ Việt Nam",
            "Kệ F1 - Tầng 3",
            5,
            "Nội dung về vai trò và vị trí của phụ nữ Việt Nam trong xã hội hiện đại."
        ),
        (
            "S011",
            "Trí tuệ nhân tạo",
            "Phạm Đức Anh",
            "Trí tuệ nhân tạo",
            2025,
            "Nhà xuất bản Khoa học và Kỹ thuật",
            "Kệ C2 - Tầng 2",
            3,
            "Giới thiệu những kiến thức cơ bản về trí tuệ nhân tạo."
        ),
        (
            "S012",
            "An toàn và bảo mật thông tin",
            "Hoàng Văn Bình",
            "An toàn thông tin",
            2024,
            "Nhà xuất bản Thông tin và Truyền thông",
            "Kệ C3 - Tầng 2",
            4,
            "Kiến thức về bảo mật dữ liệu và an toàn thông tin."
        )
    ]

    # Thêm dữ liệu vào database
    cursor.executemany("""
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
    """, books)

    conn.commit()
    conn.close()

    print("=" * 50)
    print("Đã tạo database.db thành công!")
    print("Đã thêm 12 cuốn sách mẫu.")
    print("=" * 50)


if __name__ == "__main__":
    create_database()