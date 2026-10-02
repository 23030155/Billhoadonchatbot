import streamlit as st
from datetime import datetime
import pandas as pd
import re
import unicodedata
st.image("1.jpg")

# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Trà Sữa CTU",
    page_icon="🧋",
    layout="wide"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #fff8f5;
}

.title {
    text-align: center;
    color: #8B4513;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #777;
    font-size: 18px;
    margin-bottom: 30px;
}

.total-box {
    background-color: #fff0e8;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 2px solid #e8b49a;
    margin-top: 20px;
}

.total-money {
    color: #d35400;
    font-size: 32px;
    font-weight: bold;
}

.invoice {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    border: 1px solid #ddd;
    max-width: 700px;
    margin: auto;
    color: #222;
}

.invoice-title {
    text-align: center;
    font-size: 30px;
    font-weight: bold;
}

.invoice-center {
    text-align: center;
}

.chatbot-box {
    background-color: #fff4ee;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #f0c7b2;
}

.chat-title {
    color: #8B4513;
    font-size: 25px;
    font-weight: bold;
}

.success-box {
    padding: 15px;
    background-color: #e8f8ee;
    border-radius: 10px;
    color: #176b3a;
    text-align: center;
    font-weight: bold;
}

div[data-testid="stButton"] > button {
    border-radius: 10px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DỮ LIỆU MENU
# =========================================================

MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa matcha": 35000,
    "Trà sữa socola": 35000,
    "Trà sữa khoai môn": 35000,
    "Trà sữa dâu": 35000,
    "Trà sữa ô long": 32000,
    "Trà sữa caramel": 38000,
    "Trà sữa thái xanh": 35000,
}


TOPPINGS = {
    "Trân châu đen": 7000,
    "Trân châu trắng": 7000,
    "Thạch dừa": 6000,
    "Thạch trái cây": 6000,
    "Pudding trứng": 8000,
    "Kem cheese": 10000,
    "Trân châu hoàng kim": 9000,
    "Flan": 8000,
}


SIZE_PRICE = {
    "S": 0,
    "M": 5000,
    "L": 10000
}


SUGAR = [
    "100% đường",
    "70% đường",
    "50% đường",
    "30% đường",
    "0% đường"
]


ICE = [
    "100% đá",
    "70% đá",
    "50% đá",
    "30% đá",
    "Không đá"
]


# =========================================================
# QUY TẮC TƯ VẤN CHO CHATBOT
# =========================================================

# Mức độ ngọt tương đối của từng loại
SWEETNESS = {
    "Trà sữa truyền thống": "ngọt vừa, vị trà sữa cân bằng",
    "Trà sữa matcha": "ngọt vừa, có vị matcha hơi đắng nhẹ",
    "Trà sữa socola": "khá ngọt, vị socola rõ",
    "Trà sữa khoai môn": "khá ngọt, béo và thơm",
    "Trà sữa dâu": "ngọt, có vị dâu trái cây",
    "Trà sữa ô long": "ít ngọt hơn, vị trà rõ",
    "Trà sữa caramel": "ngọt và béo, vị caramel rõ",
    "Trà sữa thái xanh": "ngọt vừa đến khá ngọt, thơm mùi trà Thái",
}


# Topping được gợi ý theo từng loại trà sữa
PAIRING = {
    "Trà sữa truyền thống": [
        "Trân châu đen",
        "Trân châu trắng",
        "Pudding trứng"
    ],

    "Trà sữa matcha": [
        "Trân châu trắng",
        "Pudding trứng",
        "Kem cheese"
    ],

    "Trà sữa socola": [
        "Trân châu đen",
        "Pudding trứng",
        "Flan"
    ],

    "Trà sữa khoai môn": [
        "Trân châu trắng",
        "Pudding trứng",
        "Kem cheese"
    ],

    "Trà sữa dâu": [
        "Thạch trái cây",
        "Trân châu trắng",
        "Thạch dừa"
    ],

    "Trà sữa ô long": [
        "Trân châu đen",
        "Trân châu hoàng kim",
        "Thạch dừa"
    ],

    "Trà sữa caramel": [
        "Flan",
        "Pudding trứng",
        "Trân châu đen"
    ],

    "Trà sữa thái xanh": [
        "Trân châu đen",
        "Thạch dừa",
        "Pudding trứng"
    ],
}


# =========================================================
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

if "invoice_code" not in st.session_state:
    st.session_state.invoice_code = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# HÀM ĐỊNH DẠNG TIỀN
# =========================================================

def format_money(number):
    return f"{number:,.0f} VNĐ"


# =========================================================
# HÀM BỎ DẤU TIẾNG VIỆT
# =========================================================

def remove_accents(text):

    text = text.lower()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text


# =========================================================
# CHATBOT RULE-BASED
# =========================================================

def chatbot_response(question):

    original_question = question.strip()
    q = remove_accents(original_question)

    if not q:
        return "Bạn hãy nhập câu hỏi để mình tư vấn nhé 🧋"


    # -----------------------------------------------------
    # CHÀO HỎI
    # -----------------------------------------------------

    if any(word in q for word in [
        "xin chao",
        "hello",
        "hi",
        "chao chatbot",
        "chao ban"
    ]):

        return (
            "Xin chào! 👋 Mình là trợ lý Trà Sữa CTU.\n\n"
            "Mình có thể giúp bạn xem giá, tìm món đắt nhất/"
            "rẻ nhất, tư vấn độ ngọt và gợi ý topping."
        )


    # -----------------------------------------------------
    # GIÁ CAO NHẤT
    # -----------------------------------------------------

    if (
        "cao nhat" in q
        or "dat nhat" in q
        or "mac nhat" in q
        or "gia cao" in q
    ):

        max_price = max(MENU.values())

        highest = [
            name
            for name, price in MENU.items()
            if price == max_price
        ]

        result = ", ".join(highest)

        return (
            f"💰 Trà sữa có giá cao nhất là **{result}**, "
            f"giá {format_money(max_price)}/ly."
        )


    # -----------------------------------------------------
    # GIÁ THẤP NHẤT
    # -----------------------------------------------------

    if (
        "thap nhat" in q
        or "re nhat" in q
        or "gia thap" in q
        or "gia re" in q
    ):

        min_price = min(MENU.values())

        lowest = [
            name
            for name, price in MENU.items()
            if price == min_price
        ]

        result = ", ".join(lowest)

        return (
            f"💵 Trà sữa có giá thấp nhất là **{result}**, "
            f"giá {format_money(min_price)}/ly."
        )


    # -----------------------------------------------------
    # DANH SÁCH MENU
    # -----------------------------------------------------

    if (
        "menu" in q
        or "danh sach" in q
        or "co nhung loai" in q
        or "cac loai tra sua" in q
    ):

        response = "🧋 **Menu trà sữa hiện tại:**\n\n"

        for name, price in MENU.items():
            response += (
                f"- {name}: {format_money(price)}\n"
            )

        return response


    # -----------------------------------------------------
    # TOPPING
    # -----------------------------------------------------

    if (
        "topping" in q
        and (
            "co gi" in q
            or "nhung gi" in q
            or "danh sach" in q
        )
    ):

        response = "🍮 **Các loại topping:**\n\n"

        for name, price in TOPPINGS.items():
            response += (
                f"- {name}: {format_money(price)}\n"
            )

        return response


    # -----------------------------------------------------
    # TOPPING ĐẮT NHẤT
    # -----------------------------------------------------

    if (
        "topping" in q
        and (
            "dat nhat" in q
            or "cao nhat" in q
        )
    ):

        max_topping = max(TOPPINGS.values())

        result = [
            name
            for name, price in TOPPINGS.items()
            if price == max_topping
        ]

        return (
            f"🍮 Topping có giá cao nhất là "
            f"**{', '.join(result)}**, "
            f"giá {format_money(max_topping)}."
        )


    # -----------------------------------------------------
    # GIÁ CỦA MỘT MÓN CỤ THỂ
    # -----------------------------------------------------

    for name, price in MENU.items():

        name_without_accents = remove_accents(name)

        if name_without_accents in q:

            return (
                f"🧋 **{name}** có giá cơ bản "
                f"{format_money(price)}/ly.\n\n"
                f"Bạn có thể chọn size M (+5.000 VNĐ), "
                f"size L (+10.000 VNĐ) và thêm topping."
            )


    # -----------------------------------------------------
    # TRÀ SỮA NGỌT
    # -----------------------------------------------------

    if (
        "ngot nhat" in q
        or "ngot" in q
        or "vi ngot" in q
    ):

        return (
            "🍫 Nếu thích vị ngọt rõ, bạn có thể thử:\n\n"
            "• Trà sữa caramel – ngọt và béo\n"
            "• Trà sữa socola – vị socola rõ, khá ngọt\n"
            "• Trà sữa khoai môn – ngọt và béo\n"
            "• Trà sữa dâu – ngọt, có vị trái cây\n\n"
            "Bạn có thể chọn 50% đường nếu không muốn quá ngọt."
        )


    # -----------------------------------------------------
    # ÍT NGỌT
    # -----------------------------------------------------

    if (
        "it ngot" in q
        or "khong qua ngot" in q
        or "nhat" in q
        or "it duong" in q
    ):

        return (
            "🍵 Nếu thích vị thanh và ít ngọt, "
            "mình gợi ý **Trà sữa ô long** hoặc "
            "**Trà sữa matcha**.\n\n"
            "Bạn có thể chọn mức 30% hoặc 50% đường "
            "để dễ uống hơn."
        )


    # -----------------------------------------------------
    # TƯ VẤN TỔNG QUÁT
    # -----------------------------------------------------

    if (
        "tu van" in q
        or "goi y" in q
        or "nen uong" in q
        or "nen chon" in q
        or "chon mon" in q
    ):

        return (
            "🧋 **Gợi ý của mình:**\n\n"
            "• Thích vị truyền thống → Trà sữa truyền thống + trân châu đen\n"
            "• Thích thanh, vị trà rõ → Trà sữa ô long + trân châu hoàng kim\n"
            "• Thích vị béo → Trà sữa khoai môn + pudding trứng\n"
            "• Thích chocolate → Trà sữa socola + flan\n"
            "• Thích trái cây → Trà sữa dâu + thạch trái cây\n"
            "• Thích caramel → Trà sữa caramel + flan"
        )


    # -----------------------------------------------------
    # TÌM LOẠI TRÀ SỮA + TOPPING
    # -----------------------------------------------------

    for name, toppings in PAIRING.items():

        normalized_name = remove_accents(name)

        if normalized_name in q:

            topping_text = ", ".join(toppings)

            return (
                f"🧋 Với **{name}**, mình gợi ý dùng "
                f"kèm: **{topping_text}**.\n\n"
                f"Đây là các gợi ý phối vị được thiết lập "
                f"trong hệ thống menu."
            )


    # -----------------------------------------------------
    # SIZE
    # -----------------------------------------------------

    if "size" in q:

        return (
            "🥤 Giá theo size:\n\n"
            "• Size S: không cộng thêm\n"
            "• Size M: +5.000 VNĐ\n"
            "• Size L: +10.000 VNĐ"
        )


    # -----------------------------------------------------
    # TỔNG TIỀN HIỆN TẠI
    # -----------------------------------------------------

    if (
        "tong tien" in q
        or "thanh tien" in q
        or "hoa don" in q
    ):

        if len(st.session_state.cart) == 0:

            return (
                "🛒 Hiện tại hóa đơn chưa có món nào."
            )

        total = sum(
            item["Thành tiền"]
            for item in st.session_state.cart
        )

        return (
            f"🧾 Tổng tiền hiện tại của hóa đơn là "
            f"**{format_money(total)}**."
        )


    # -----------------------------------------------------
    # TRỢ GIÚP
    # -----------------------------------------------------

    if (
        "help" in q
        or "tro giup" in q
        or "ban lam duoc gi" in q
    ):

        return (
            "🤖 Mình có thể trả lời các câu hỏi như:\n\n"
            "• Trà sữa nào giá cao nhất?\n"
            "• Trà sữa nào rẻ nhất?\n"
            "• Trà sữa nào ngọt?\n"
            "• Trà sữa nào ít ngọt?\n"
            "• Matcha nên dùng topping nào?\n"
            "• Trà sữa caramel giá bao nhiêu?\n"
            "• Có những topping nào?\n"
            "• Size L thêm bao nhiêu tiền?\n"
            "• Tổng hóa đơn hiện tại bao nhiêu?\n"
            "• Gợi ý cho tôi một ly trà sữa."
        )


    # -----------------------------------------------------
    # KHÔNG HIỂU CÂU HỎI
    # -----------------------------------------------------

    return (
        "🤔 Mình chưa hiểu câu hỏi này.\n\n"
        "Bạn có thể thử hỏi:\n"
        "• Trà sữa nào giá cao nhất?\n"
        "• Trà sữa nào rẻ nhất?\n"
        "• Trà sữa nào ngọt?\n"
        "• Matcha nên dùng topping nào?\n"
        "• Có những topping nào?\n"
        "• Gợi ý trà sữa cho tôi."
    )


# =========================================================
# TIÊU ĐỀ
# =========================================================

st.markdown(
    '<div class="title">🧋 TRÀ SỮA CTU</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Hệ thống bán hàng & trợ lý tư vấn trà sữa'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# CHIA TAB
# =========================================================

tab1, tab2 = st.tabs([
    "🧾 TÍNH HÓA ĐƠN",
    "🤖 CHATBOT TƯ VẤN"
])


# =========================================================
# TAB 1 - HÓA ĐƠN
# =========================================================

with tab1:

    st.subheader("👤 Thông tin khách hàng")

    customer_name = st.text_input(
        "Tên khách hàng",
        placeholder="Nhập tên khách hàng...",
        key="customer_name"
    )


    # -----------------------------------------------------
    # CHỌN MÓN
    # -----------------------------------------------------

    st.subheader("🧋 Chọn món")

    col1, col2 = st.columns(2)

    with col1:

        drink = st.selectbox(
            "Loại trà sữa",
            list(MENU.keys())
        )

        size = st.selectbox(
            "Size ly",
            ["S", "M", "L"]
        )

        quantity = st.number_input(
            "Số lượng",
            min_value=1,
            max_value=50,
            value=1,
            step=1
        )


    with col2:

        sugar = st.select_slider(
            "Mức độ đường",
            options=SUGAR,
            value="70% đường"
        )

        ice = st.select_slider(
            "Mức độ đá",
            options=ICE,
            value="70% đá"
        )

        toppings = st.multiselect(
            "Topping",
            list(TOPPINGS.keys())
        )


    # -----------------------------------------------------
    # TÍNH GIÁ
    # -----------------------------------------------------

    drink_price = MENU[drink]

    size_price = SIZE_PRICE[size]

    topping_price = sum(
        TOPPINGS[topping]
        for topping in toppings
    )

    unit_price = (
        drink_price
        + size_price
        + topping_price
    )

    total_price = unit_price * quantity


    st.markdown("### 💰 Chi tiết giá")

    price_col1, price_col2, price_col3, price_col4 = st.columns(4)

    with price_col1:
        st.metric(
            "Giá trà sữa",
            format_money(drink_price)
        )

    with price_col2:
        st.metric(
            "Giá size",
            format_money(size_price)
        )

    with price_col3:
        st.metric(
            "Topping",
            format_money(topping_price)
        )

    with price_col4:
        st.metric(
            "Thành tiền",
            format_money(total_price)
        )


    # -----------------------------------------------------
    # THÊM MÓN
    # -----------------------------------------------------

    if st.button(
        "➕ Thêm món vào hóa đơn",
        use_container_width=True
    ):

        if not customer_name.strip():

            st.warning(
                "⚠️ Vui lòng nhập tên khách hàng."
            )

        else:

            item = {
                "Tên món": drink,
                "Size": size,
                "Đường": sugar,
                "Đá": ice,
                "Topping": (
                    ", ".join(toppings)
                    if toppings
                    else "Không"
                ),
                "Số lượng": quantity,
                "Đơn giá": unit_price,
                "Thành tiền": total_price
            }

            st.session_state.cart.append(item)

            st.success(
                f"✅ Đã thêm {quantity} ly {drink}!"
            )


    # -----------------------------------------------------
    # GIỎ HÀNG
    # -----------------------------------------------------

    st.divider()

    st.subheader("🛒 Hóa đơn hiện tại")

    if len(st.session_state.cart) == 0:

        st.info(
            "Chưa có món nào trong hóa đơn."
        )

    else:

        df = pd.DataFrame(
            st.session_state.cart
        )

        display_df = df.copy()

        display_df["Đơn giá"] = (
            display_df["Đơn giá"]
            .apply(format_money)
        )

        display_df["Thành tiền"] = (
            display_df["Thành tiền"]
            .apply(format_money)
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        grand_total = sum(
            item["Thành tiền"]
            for item in st.session_state.cart
        )

        st.markdown(
            f"""
            <div class="total-box">
                <div>TỔNG THANH TOÁN</div>
                <div class="total-money">
                    {format_money(grand_total)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        delete_col, payment_col = st.columns(2)


        # -------------------------------------------------
        # XÓA
        # -------------------------------------------------

        with delete_col:

            if st.button(
                "🗑️ Xóa toàn bộ hóa đơn",
                use_container_width=True
            ):

                st.session_state.cart = []
                st.session_state.payment_done = False

                st.rerun()


        # -------------------------------------------------
        # THANH TOÁN
        # -------------------------------------------------

        with payment_col:

            if st.button(
                "💳 THANH TOÁN",
                use_container_width=True,
                type="primary"
            ):

                st.session_state.payment_done = True

                now = datetime.now()

                st.session_state.invoice_code = (
                    "HD"
                    + now.strftime("%Y%m%d")
                    + now.strftime("%H%M%S")
                )

                st.success(
                    "✅ Thanh toán thành công!"
                )


    # =====================================================
    # HÓA ĐƠN
    # =====================================================

    if st.session_state.payment_done:

        st.divider()

        st.subheader(
            "🧾 HÓA ĐƠN THANH TOÁN"
        )

        now = datetime.now()

        invoice_code = (
            st.session_state.invoice_code
        )

        grand_total = sum(
            item["Thành tiền"]
            for item in st.session_state.cart
        )


        invoice_html = f"""
        <div class="invoice">

            <div class="invoice-title">
                🧋 TRÀ SỮA CTU
            </div>

            <div class="invoice-center">

                <p>HÓA ĐƠN THANH TOÁN</p>

                <p>
                    Mã hóa đơn:
                    <b>{invoice_code}</b>
                </p>

                <p>
                    Thời gian:
                    {now.strftime("%d/%m/%Y %H:%M:%S")}
                </p>

            </div>

            <hr>

            <p>
                <b>Khách hàng:</b>
                {customer_name}
            </p>

            <hr>
        """


        for index, item in enumerate(
            st.session_state.cart,
            start=1
        ):

            invoice_html += f"""

            <div>

                <b>
                    {index}. {item["Tên món"]}
                </b>

                <br>

                Size: {item["Size"]}

                <br>

                Đường: {item["Đường"]}

                <br>

                Đá: {item["Đá"]}

                <br>

                Topping: {item["Topping"]}

                <br>

                Số lượng: {item["Số lượng"]}

                <br>

                Đơn giá:
                {format_money(item["Đơn giá"])}

                <br>

                Thành tiền:
                <b>
                    {format_money(item["Thành tiền"])}
                </b>

            </div>

            <hr>
            """


        invoice_html += f"""

            <div style="text-align:right;">

                <h2>
                    TỔNG CỘNG:
                    {format_money(grand_total)}
                </h2>

            </div>

            <div class="invoice-center">

                <p>
                    💗 Cảm ơn quý khách!
                </p>

                <p>
                    Hẹn gặp lại!
                </p>

            </div>

        </div>
        """


        st.markdown(
            invoice_html,
            unsafe_allow_html=True
        )


        # -------------------------------------------------
        # FILE TXT
        # -------------------------------------------------

        invoice_text = f"""
========================================
             TRÀ SỮA CTU
          HÓA ĐƠN THANH TOÁN
========================================

Mã hóa đơn: {invoice_code}
Thời gian: {now.strftime("%d/%m/%Y %H:%M:%S")}
Khách hàng: {customer_name}

----------------------------------------
CHI TIẾT ĐƠN HÀNG
----------------------------------------
"""


        for index, item in enumerate(
            st.session_state.cart,
            start=1
        ):

            invoice_text += f"""

{index}. {item["Tên món"]}
   Size: {item["Size"]}
   Đường: {item["Đường"]}
   Đá: {item["Đá"]}
   Topping: {item["Topping"]}
   Số lượng: {item["Số lượng"]}
   Đơn giá: {format_money(item["Đơn giá"])}
   Thành tiền: {format_money(item["Thành tiền"])}

----------------------------------------
"""


        invoice_text += f"""

TỔNG THANH TOÁN:
{format_money(grand_total)}

========================================
          CẢM ƠN QUÝ KHÁCH!
             HẸN GẶP LẠI
========================================
"""


        st.download_button(
            label="🖨️ Lưu / In hóa đơn",
            data=invoice_text,
            file_name=f"{invoice_code}.txt",
            mime="text/plain",
            use_container_width=True
        )


# =========================================================
# TAB 2 - CHATBOT
# =========================================================

with tab2:

    st.markdown(
        """
        <div class="chatbot-box">

        <div class="chat-title">
        🤖 Trợ lý Trà Sữa CTU
        </div>

        <p>
        Xin chào! Mình có thể tư vấn menu,
        giá cả và cách kết hợp trà sữa với topping.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.write("### 💡 Câu hỏi nhanh")


    # -----------------------------------------------------
    # CÂU HỎI NHANH
    # -----------------------------------------------------

    quick_col1, quick_col2, quick_col3 = st.columns(3)


    with quick_col1:

        if st.button(
            "💰 Giá cao nhất?",
            use_container_width=True
        ):

            answer = chatbot_response(
                "Trà sữa nào giá cao nhất?"
            )

            st.session_state.chat_history.append(
                ("Bạn", "Trà sữa nào giá cao nhất?")
            )

            st.session_state.chat_history.append(
                ("🤖 Chatbot", answer)
            )


        if st.button(
            "💵 Giá thấp nhất?",
            use_container_width=True
        ):

            answer = chatbot_response(
                "Trà sữa nào giá thấp nhất?"
            )

            st.session_state.chat_history.append(
                ("Bạn", "Trà sữa nào giá thấp nhất?")
            )

            st.session_state.chat_history.append(
                ("🤖 Chatbot", answer)
            )


    with quick_col2:

        if st.button(
            "🍫 Món nào ngọt?",
            use_container_width=True
        ):

            answer = chatbot_response(
                "Trà sữa nào ngọt?"
            )

            st.session_state.chat_history.append(
                ("Bạn", "Trà sữa nào ngọt?")
            )

            st.session_state.chat_history.append(
                ("🤖 Chatbot", answer)
            )


        if st.button(
            "🍮 Gợi ý topping",
            use_container_width=True
        ):

            answer = chatbot_response(
                "Matcha nên dùng topping nào?"
            )

            st.session_state.chat_history.append(
                ("Bạn", "Matcha nên dùng topping nào?")
            )

            st.session_state.chat_history.append(
                ("🤖 Chatbot", answer)
            )


    with quick_col3:

        if st.button(
            "🧋 Gợi ý món",
            use_container_width=True
        ):

            answer = chatbot_response(
                "Gợi ý cho tôi một ly trà sữa"
            )

            st.session_state.chat_history.append(
                ("Bạn", "Gợi ý cho tôi một ly trà sữa")
            )

            st.session_state.chat_history.append(
                ("🤖 Chatbot", answer)
            )


        if st.button(
            "📋 Xem menu",
            use_container_width=True
        ):

            answer = chatbot_response(
                "Cho tôi xem menu"
            )

            st.session_state.chat_history.append(
                ("Bạn", "Cho tôi xem menu")
            )

            st.session_state.chat_history.append(
                ("🤖 Chatbot", answer)
            )


    st.divider()


    # -----------------------------------------------------
    # HIỂN THỊ LỊCH SỬ CHAT
    # -----------------------------------------------------

    for sender, message in st.session_state.chat_history:

        if sender == "Bạn":

            st.markdown(
                f"""
                **👤 Bạn:**
                
                {message}
                """
            )

        else:

            st.markdown(
                f"""
                **{sender}:**
                
                {message}
                """
            )


    # -----------------------------------------------------
    # NHẬP CÂU HỎI
    # -----------------------------------------------------

    question = st.chat_input(
        "Nhập câu hỏi cho chatbot..."
    )


    if question:

        answer = chatbot_response(question)

        st.session_state.chat_history.append(
            ("Bạn", question)
        )

        st.session_state.chat_history.append(
            ("🤖 Chatbot", answer)
        )

        st.rerun()


    # -----------------------------------------------------
    # XÓA LỊCH SỬ
    # -----------------------------------------------------

    if len(st.session_state.chat_history) > 0:

        if st.button(
            "🗑️ Xóa lịch sử trò chuyện"
        ):

            st.session_state.chat_history = []

            st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#888;">
        🧋 Trà Sữa CTU - Hệ thống quản lý hóa đơn
        & trợ lý tư vấn
    </div>
    """,
    unsafe_allow_html=True
)
