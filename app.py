import streamlit as st
from datetime import datetime
import pandas as pd
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
# CSS GIAO DIỆN
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
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

if "invoice_code" not in st.session_state:
    st.session_state.invoice_code = ""


# =========================================================
# HÀM ĐỊNH DẠNG TIỀN
# =========================================================

def format_money(number):
    return f"{number:,.0f} VNĐ"


# =========================================================
# TIÊU ĐỀ
# =========================================================

st.markdown(
    '<div class="title">🧋 TRÀ SỮA CTU</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Hệ thống tính hóa đơn trà sữa</div>',
    unsafe_allow_html=True
)


# =========================================================
# THÔNG TIN KHÁCH HÀNG
# =========================================================

st.subheader("👤 Thông tin khách hàng")

customer_name = st.text_input(
    "Tên khách hàng",
    placeholder="Nhập tên khách hàng..."
)


# =========================================================
# CHỌN MÓN
# =========================================================

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


# =========================================================
# TÍNH GIÁ
# =========================================================

drink_price = MENU[drink]
size_price = SIZE_PRICE[size]

topping_price = sum(
    TOPPINGS[topping]
    for topping in toppings
)

unit_price = drink_price + size_price + topping_price
total_price = unit_price * quantity


st.markdown("### 💰 Chi tiết giá")

price_col1, price_col2, price_col3, price_col4 = st.columns(4)

with price_col1:
    st.metric("Giá trà sữa", format_money(drink_price))

with price_col2:
    st.metric("Giá size", format_money(size_price))

with price_col3:
    st.metric("Topping", format_money(topping_price))

with price_col4:
    st.metric("Thành tiền", format_money(total_price))


# =========================================================
# THÊM MÓN VÀO HÓA ĐƠN
# =========================================================

if st.button("➕ Thêm món vào hóa đơn", use_container_width=True):

    if not customer_name.strip():
        st.warning("⚠️ Vui lòng nhập tên khách hàng.")
    else:

        item = {
            "Tên món": drink,
            "Size": size,
            "Đường": sugar,
            "Đá": ice,
            "Topping": ", ".join(toppings) if toppings else "Không",
            "Số lượng": quantity,
            "Đơn giá": unit_price,
            "Thành tiền": total_price
        }

        st.session_state.cart.append(item)

        st.success(
            f"✅ Đã thêm {quantity} ly {drink} vào hóa đơn!"
        )


# =========================================================
# HIỂN THỊ GIỎ HÀNG
# =========================================================

st.divider()

st.subheader("🛒 Hóa đơn hiện tại")

if len(st.session_state.cart) == 0:

    st.info("Chưa có món nào trong hóa đơn.")

else:

    df = pd.DataFrame(st.session_state.cart)

    display_df = df.copy()

    display_df["Đơn giá"] = display_df["Đơn giá"].apply(
        format_money
    )

    display_df["Thành tiền"] = display_df["Thành tiền"].apply(
        format_money
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


# =========================================================
# XÓA HÓA ĐƠN
# =========================================================

if len(st.session_state.cart) > 0:

    st.write("")

    delete_col, payment_col = st.columns(2)

    with delete_col:

        if st.button(
            "🗑️ Xóa toàn bộ hóa đơn",
            use_container_width=True
        ):

            st.session_state.cart = []
            st.session_state.payment_done = False

            st.rerun()

    # =====================================================
    # THANH TOÁN
    # =====================================================

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

            st.success("✅ Thanh toán thành công!")


# =========================================================
# HÓA ĐƠN SAU KHI THANH TOÁN
# =========================================================

if st.session_state.payment_done:

    st.divider()

    st.subheader("🧾 HÓA ĐƠN THANH TOÁN")

    now = datetime.now()

    invoice_code = st.session_state.invoice_code

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
            <p>Mã hóa đơn: <b>{invoice_code}</b></p>
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
            <b>{index}. {item["Tên món"]}</b><br>
            Size: {item["Size"]}<br>
            Đường: {item["Đường"]}<br>
            Đá: {item["Đá"]}<br>
            Topping: {item["Topping"]}<br>
            Số lượng: {item["Số lượng"]}<br>
            Đơn giá: {format_money(item["Đơn giá"])}<br>
            Thành tiền:
            <b>{format_money(item["Thành tiền"])}</b>
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
            <p>💗 Cảm ơn quý khách!</p>
            <p>Hẹn gặp lại!</p>
        </div>

    </div>
    """

    st.markdown(
        invoice_html,
        unsafe_allow_html=True
    )


    # =====================================================
    # TẠO FILE HÓA ĐƠN TXT
    # =====================================================

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
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#888;">
        🧋 Trà Sữa CTU - Hệ thống quản lý hóa đơn
    </div>
    """,
    unsafe_allow_html=True
)
