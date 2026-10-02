import streamlit as st
from datetime import datetime
import pandas as pd
import unicodedata
import os
from openai import OpenAI
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

.ai-badge {
    background-color: #f5e6dc;
    color: #8B4513;
    padding: 8px 15px;
    border-radius: 20px;
    display: inline-block;
    font-weight: bold;
    margin-bottom: 10px;
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
# QUY TẮC TƯ VẤN
# =========================================================

SWEETNESS = {
    "Trà sữa truyền thống":
        "ngọt vừa, vị trà sữa cân bằng",

    "Trà sữa matcha":
        "ngọt vừa, có vị matcha hơi đắng nhẹ",

    "Trà sữa socola":
        "khá ngọt, vị socola rõ",

    "Trà sữa khoai môn":
        "khá ngọt, béo và thơm",

    "Trà sữa dâu":
        "ngọt, có vị dâu trái cây",

    "Trà sữa ô long":
        "ít ngọt hơn, vị trà rõ",

    "Trà sữa caramel":
        "ngọt và béo, vị caramel rõ",

    "Trà sữa thái xanh":
        "ngọt vừa đến khá ngọt, thơm mùi trà Thái",
}


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
# LẤY API KEY
# =========================================================

def get_api_key():

    # Ưu tiên Streamlit Secrets
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass

    # Nếu chạy local thì đọc biến môi trường
    return os.getenv("OPENROUTER_API_KEY", "")


# =========================================================
# TẠO CLIENT OPENROUTER
# =========================================================

def get_ai_client():

    api_key = get_api_key()

    if not api_key:
        return None

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )


# =========================================================
# TẠO THÔNG TIN MENU CHO AI
# =========================================================

def create_menu_context():

    menu_text = "MENU TRÀ SỮA:\n"

    for name, price in MENU.items():

        menu_text += (
            f"- {name}: {format_money(price)}\n"
        )


    menu_text += "\nTOPPING:\n"

    for name, price in TOPPINGS.items():

        menu_text += (
            f"- {name}: {format_money(price)}\n"
        )


    menu_text += "\nGIÁ SIZE:\n"

    menu_text += "- Size S: +0 VNĐ\n"
    menu_text += "- Size M: +5.000 VNĐ\n"
    menu_text += "- Size L: +10.000 VNĐ\n"


    menu_text += "\nMỨC ĐƯỜNG:\n"

    for item in SUGAR:
        menu_text += f"- {item}\n"


    menu_text += "\nMỨC ĐÁ:\n"

    for item in ICE:
        menu_text += f"- {item}\n"


    menu_text += "\nĐỘ NGỌT TƯƠNG ĐỐI:\n"

    for name, description in SWEETNESS.items():

        menu_text += (
            f"- {name}: {description}\n"
        )


    menu_text += "\nGỢI Ý TOPPING:\n"

    for name, toppings in PAIRING.items():

        menu_text += (
            f"- {name}: "
            f"{', '.join(toppings)}\n"
        )


    return menu_text


# =========================================================
# THÔNG TIN HÓA ĐƠN HIỆN TẠI
# =========================================================

def create_cart_context():

    if len(st.session_state.cart) == 0:

        return "HÓA ĐƠN HIỆN TẠI: Chưa có món nào."


    text = "HÓA ĐƠN HIỆN TẠI:\n"

    total = 0

    for index, item in enumerate(
        st.session_state.cart,
        start=1
    ):

        text += f"""
{index}. {item["Tên món"]}
   Size: {item["Size"]}
   Đường: {item["Đường"]}
   Đá: {item["Đá"]}
   Topping: {item["Topping"]}
   Số lượng: {item["Số lượng"]}
   Đơn giá: {format_money(item["Đơn giá"])}
   Thành tiền: {format_money(item["Thành tiền"])}
"""

        total += item["Thành tiền"]


    text += (
        f"\nTỔNG HÓA ĐƠN: "
        f"{format_money(total)}"
    )

    return text


# =========================================================
# CHATBOT LUẬT DỰ PHÒNG
# =========================================================

def rule_based_response(question):

    q = question.lower()


    # Giá cao nhất
    if (
        "cao nhất" in q
        or "đắt nhất" in q
        or "mắc nhất" in q
    ):

        max_price = max(MENU.values())

        result = [
            name
            for name, price in MENU.items()
            if price == max_price
        ]

        return (
            f"💰 Món có giá cao nhất là "
            f"{', '.join(result)}, "
            f"giá {format_money(max_price)}/ly."
        )


    # Giá thấp nhất
    if (
        "thấp nhất" in q
        or "rẻ nhất" in q
    ):

        min_price = min(MENU.values())

        result = [
            name
            for name, price in MENU.items()
            if price == min_price
        ]

        return (
            f"💵 Món có giá thấp nhất là "
            f"{', '.join(result)}, "
            f"giá {format_money(min_price)}/ly."
        )


    # Ngọt
    if "ngọt" in q:

        return (
            "🍫 Nếu thích vị ngọt, bạn có thể thử "
            "trà sữa caramel, socola, khoai môn hoặc dâu. "
            "Bạn có thể giảm xuống 50% đường nếu sợ quá ngọt."
        )


    # Topping
    if "topping" in q:

        return (
            "🍮 Một số cách phối topping:\n\n"
            "• Matcha → trân châu trắng, pudding, kem cheese\n"
            "• Socola → trân châu đen, pudding, flan\n"
            "• Ô long → trân châu đen, hoàng kim, thạch dừa\n"
            "• Dâu → thạch trái cây, trân châu trắng"
        )


    return (
        "🤖 Mình chưa thể kết nối AI lúc này. "
        "Bạn có thể hỏi về giá, menu hoặc topping."
    )


# =========================================================
# AI CHATBOT
# =========================================================

def ai_chatbot(question):

    client = get_ai_client()

    if client is None:

        return (
            "⚠️ Chưa tìm thấy API Key OpenRouter.\n\n"
            + rule_based_response(question)
        )


    menu_context = create_menu_context()

    cart_context = create_cart_context()


    system_prompt = f"""
Bạn là "Trợ lý Trà Sữa CTU", một chatbot AI tư vấn
cho ứng dụng bán trà sữa.

NHIỆM VỤ:

1. Tư vấn các loại trà sữa.
2. Tư vấn giá.
3. Tìm món có giá cao nhất hoặc thấp nhất.
4. Tư vấn topping phù hợp.
5. Tư vấn mức độ ngọt.
6. Tư vấn size.
7. Đọc và giải thích hóa đơn hiện tại.
8. Gợi ý món dựa trên sở thích của khách.
9. Trả lời bằng tiếng Việt.
10. Nói chuyện tự nhiên, thân thiện, ngắn gọn.
11. Có thể sử dụng emoji phù hợp.
12. Không được tự bịa món hoặc giá không có trong dữ liệu.

QUY TẮC QUAN TRỌNG:

- Khi khách hỏi giá, phải sử dụng đúng dữ liệu MENU.
- Khi khách hỏi món đắt nhất/rẻ nhất,
  hãy tính từ dữ liệu menu.
- Khi khách hỏi topping,
  ưu tiên các gợi ý trong dữ liệu PAIRING.
- Khi khách hỏi độ ngọt,
  sử dụng dữ liệu SWEETNESS.
- Nếu khách hỏi "món nào dưới X tiền",
  hãy tính từ MENU.
- Nếu khách hỏi "món nào khoảng X tiền",
  hãy tìm những món gần mức giá đó.
- Nếu khách hỏi về hóa đơn,
  sử dụng HÓA ĐƠN HIỆN TẠI.
- Không tự ý thay đổi giá.
- Không tự thêm sản phẩm không có trong menu.

DỮ LIỆU CỦA QUÁN:

{menu_context}

{cart_context}
"""


    # -----------------------------------------------------
    # LỊCH SỬ HỘI THOẠI
    # -----------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]


    # Chỉ gửi lịch sử gần đây để tránh quá dài
    recent_history = st.session_state.chat_history[-12:]


    for item in recent_history:

        role = item["role"]

        content = item["content"]

        messages.append(
            {
                "role": role,
                "content": content
            }
        )


    messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    try:

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            temperature=0.7,
            max_tokens=700
        )


        answer = response.choices[0].message.content

        if not answer:
            return rule_based_response(question)

        return answer


    except Exception as error:

        return (
            "⚠️ Không thể kết nối AI tại thời điểm này.\n\n"
            f"Chi tiết lỗi: {str(error)}\n\n"
            "Mình chuyển sang chế độ tư vấn cơ bản:\n\n"
            + rule_based_response(question)
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
    'Hệ thống bán hàng & trợ lý AI'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# TAB
# =========================================================

tab1, tab2 = st.tabs([
    "🧾 TÍNH HÓA ĐƠN",
    "🤖 CHATBOT AI"
])


# =========================================================
# TAB 1 - TÍNH HÓA ĐƠN
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
    # HÓA ĐƠN
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
        # XÓA HÓA ĐƠN
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
    # HIỂN THỊ HÓA ĐƠN
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

                <p>
                    HÓA ĐƠN THANH TOÁN
                </p>

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

Thời gian:
{now.strftime("%d/%m/%Y %H:%M:%S")}

Khách hàng:
{customer_name}


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

   Đơn giá:
   {format_money(item["Đơn giá"])}

   Thành tiền:
   {format_money(item["Thành tiền"])}

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
# TAB 2 - CHATBOT AI
# =========================================================

with tab2:

    st.markdown(
        """
        <div class="chatbot-box">

            <div class="chat-title">
                🤖 Trợ lý AI Trà Sữa CTU
            </div>

            <div class="ai-badge">
                ✨ AI CHATBOT
            </div>

            <p>
                Xin chào! Mình có thể tư vấn menu,
                giá cả, topping, độ ngọt và hóa đơn
                hiện tại của bạn.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # CÂU HỎI NHANH
    # -----------------------------------------------------

    st.write("### 💡 Câu hỏi nhanh")


    quick_col1, quick_col2, quick_col3 = st.columns(3)


    def add_quick_question(question):

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )

        answer = ai_chatbot(question)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


    with quick_col1:

        if st.button(
            "💰 Giá cao nhất?",
            use_container_width=True
        ):

            add_quick_question(
                "Trà sữa nào có giá cao nhất?"
            )

            st.rerun()


        if st.button(
            "💵 Giá thấp nhất?",
            use_container_width=True
        ):

            add_quick_question(
                "Trà sữa nào có giá thấp nhất?"
            )

            st.rerun()


    with quick_col2:

        if st.button(
            "🍫 Món nào ngọt?",
            use_container_width=True
        ):

            add_quick_question(
                "Loại trà sữa nào ngọt nhất?"
            )

            st.rerun()


        if st.button(
            "🍮 Gợi ý topping",
            use_container_width=True
        ):

            add_quick_question(
                "Trà sữa matcha nên dùng topping nào?"
            )

            st.rerun()


    with quick_col3:

        if st.button(
            "🧋 Gợi ý món",
            use_container_width=True
        ):

            add_quick_question(
                "Hãy gợi ý cho tôi một ly trà sữa."
            )

            st.rerun()


        if st.button(
            "📋 Xem menu",
            use_container_width=True
        ):

            add_quick_question(
                "Hãy cho tôi xem menu và giá."
            )

            st.rerun()


    st.divider()


    # -----------------------------------------------------
    # LỊCH SỬ CHAT
    # -----------------------------------------------------

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):

                st.markdown(
                    message["content"]
                )

        else:

            with st.chat_message("assistant"):

                st.markdown(
                    message["content"]
                )


    # -----------------------------------------------------
    # NHẬP CÂU HỎI
    # -----------------------------------------------------

    question = st.chat_input(
        "Hỏi trợ lý AI về trà sữa..."
    )


    if question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )


        with st.spinner(
            "🤖 AI đang suy nghĩ..."
        ):

            answer = ai_chatbot(question)


        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        st.rerun()


    # -----------------------------------------------------
    # XÓA CHAT
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

        🧋 Trà Sữa CTU

        <br>

        Hệ thống quản lý hóa đơn
        & trợ lý AI

    </div>
    """,
    unsafe_allow_html=True
)
