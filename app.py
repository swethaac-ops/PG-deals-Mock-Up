import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

st.set_page_config(page_title="Ad Placement Mockup Generator", layout="wide")

st.title("📱 Payment Screen & 300x250 Ad Mockup Tool")
st.write("Customize the transaction details and upload a banner to preview it inside the UI.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Image (6:5 / 300x250 ratio)", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. Edit Transaction Details")
avatar_initials = st.sidebar.text_input("Avatar Initials", value="JL", max_chars=3)
recipient_name = st.sidebar.text_area("Recipient Name", value="JUST PARKING\nPRIVATE LIMITED", height=70)
upi_id = st.sidebar.text_input("UPI ID / Masked Number", value="paytm.d*******3175@pty")
amount = st.sidebar.text_input("Amount (without ₹ symbol)", value="150")
date_time_str = st.sidebar.text_input("Transaction Date & Time", value="04:32 pm on 12 Oct 2026")

st.sidebar.header("3. Ad Tag Settings")
show_info_tag = st.sidebar.checkbox("Show Ad Info 'i' Tag", value=True)
tag_position = st.sidebar.selectbox("Tag Corner", ["Top-Left", "Top-Right"])

# --- HELPER FOR GUARANTEED CRISP FONTS ---
def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    try:
        return ImageFont.load_default(size=size)
    except:
        return ImageFont.load_default()

# --- IMAGE GENERATION FUNCTION (FULL HD 1080x2340) ---
def create_mockup():
    W, H = 1080, 2340
    img = Image.new("RGB", (W, H), "#121115")
    draw = ImageDraw.Draw(img)

    font_amt = get_font(60, bold=True)
    font_name = get_font(46, bold=True)
    font_md = get_font(40, bold=True)
    font_reg = get_font(36, bold=False)
    font_sm = get_font(30, bold=False)
    font_info = get_font(22, bold=True)
    font_tag = get_font(22, bold=True)

    # 1. Top Green Header Section
    header_h = 530
    draw.rectangle([0, 0, W, header_h], fill="#2E8B3C")

    # White Checkmark Circle
    cx, cy = W // 2, 184
    draw.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], fill="#4FA35B")
    draw.ellipse([cx - 66, cy - 66, cx + 66, cy + 66], fill="white")
    draw.line([(cx - 28, cy), (cx - 6, cy + 22), (cx + 32, cy - 22)], fill="#2E8B3C", width=10)

    # Payment Successful Text
    draw.text((W // 2, 324), "Payment Successful", fill="white", font=font_md, anchor="mm")
    draw.text((W // 2, 390), date_time_str, fill="#E0F2E3", font=font_reg, anchor="mm")

    # 2. Transaction Card
    card_x1, card_y1, card_x2, card_y2 = 36, 464, W - 36, 1044
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=32, fill="#1E1D22")

    # Yellow Rounded-Square Avatar Box with Initials
    av_x1, av_y1 = 84, 530
    av_size = 152
    draw.rounded_rectangle([av_x1, av_y1, av_x1 + av_size, av_y1 + av_size], radius=36, fill="#D4B82C")
    draw.text((av_x1 + av_size // 2, av_y1 + av_size // 2), avatar_initials.upper(), fill="white", font=font_name, anchor="mm")

    # Recipient Name, UPI ID, and Amount
    text_x = 284
    draw.multiline_text((text_x, 530), recipient_name, fill="white", font=font_name, spacing=12)

    line_count = len(recipient_name.split("\n"))
    upi_y = 530 + (line_count * 60) + 12
    amt_y = upi_y + 68

    draw.text((text_x, upi_y), upi_id, fill="#B0AFB6", font=font_reg)
    draw.text((text_x, amt_y), f"₹{amount}", fill="white", font=font_amt)

    # Underlined "Split Expense"
    split_x, split_y = card_x2 - 52, amt_y + 32
    draw.text((split_x, split_y), "Split Expense", fill="#A67CE8", font=font_sm, anchor="rm")
    text_w = draw.textlength("Split Expense", font=font_sm)
    draw.line([(split_x - text_w, split_y + 20), (split_x, split_y + 20)], fill="#A67CE8", width=2)

    # Card Divider Lines & Bottom Actions
    div_y = 864
    draw.line([(card_x1, div_y), (card_x2, div_y)], fill="#323038", width=4)
    draw.line([(W // 2, div_y + 24), (W // 2, card_y2 - 24)], fill="#323038", width=4)

    # View Details & Share Receipt Buttons
    draw.ellipse([130, 910, 218, 998], fill="#382B47")
    draw.rectangle([160, 936, 188, 972], outline="#A67CE8", width=4)
    draw.text((248, 954), "View Details", fill="#E2E1E6", font=font_sm, anchor="lm")

    draw.ellipse([600, 910, 688, 998], fill="#382B47")
    draw.text((644, 954), "↗", fill="#A67CE8", font=font_md, anchor="mm")
    draw.text((716, 954), "Share Receipt", fill="#E2E1E6", font=font_sm, anchor="lm")

    # 3. High-Resolution 6:5 Ad Banner Container (1008x840 = exact 6:5 ratio)
    ad_w, ad_h = 1008, 840
    ad_x = (W - ad_w) // 2
    ad_y = 1084

    if uploaded_ad is not None:
        raw_img = Image.open(uploaded_ad)
        raw_img = ImageOps.exif_transpose(raw_img)
        if raw_img.mode in ("RGBA", "P"):
            bg = Image.new("RGB", raw_img.size, (255, 255, 255))
            raw_img = raw_img.convert("RGBA")
            bg.paste(raw_img, mask=raw_img.split()[3])
            ad_rgb = bg
        else:
            ad_rgb = raw_img.convert("RGB")

        ad_display = ImageOps.fit(ad_rgb, (ad_w, ad_h), method=Image.Resampling.LANCZOS)
    else:
        ad_display = Image.new("RGB", (ad_w, ad_h), "#F5F5F7")
        ad_draw = ImageDraw.Draw(ad_display)
        ad_draw.text((ad_w // 2, ad_h // 2), "300 x 250 Ad Slot (6:5)\nUpload Image in Left Sidebar", fill="#666666", font=font_md, anchor="mm", align="center")

    # 4. Authentic Flush Corner AdChoices 'i' Tab (Drawn directly onto ad corner before rounding)
    if show_info_tag:
        ad_rgba = ad_display.convert("RGBA")
        overlay = Image.new("RGBA", (ad_w, ad_h), (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)

        tab_w, tab_h = 46, 42
        r = 14
        if tag_position == "Top-Left":
            # Flush top-left translucent light-grey tab with rounded bottom-right corner
            ov_draw.rounded_rectangle(
                [0, 0, tab_w, tab_h],
                radius=10,
                corners=(False, False, True, False),
                fill=(242, 242, 245, 225)
            )
            ix, iy = tab_w // 2, tab_h // 2
        else:
            # Flush top-right translucent light-grey tab with rounded bottom-left corner
            ov_draw.rounded_rectangle(
                [ad_w - tab_w, 0, ad_w, tab_h],
                radius=10,
                corners=(False, False, False, True),
                fill=(242, 242, 245, 225)
            )
            ix, iy = ad_w - (tab_w // 2), tab_h // 2

        # Thin cyan-blue ring + 'i' icon matching original Oppo screenshot
        ov_draw.ellipse([ix - r, iy - r, ix + r, iy + r], outline=(0, 174, 239, 255), width=3)
        ov_draw.text((ix, iy), "i", fill=(0, 174, 239, 255), font=font_info, anchor="mm")

        ad_display = Image.alpha_composite(ad_rgba, overlay).convert("RGB")

    # Apply rounded corners to the Ad Banner so the flush tab follows the banner corner cleanly
    mask = Image.new("L", (ad_w, ad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, ad_w, ad_h], radius=20, fill=255)
    img.paste(ad_display, (ad_x, ad_y), mask)

    # 5. Carousel Dots & UPI Footer
    dot_y = ad_y + ad_h + 44
    start_dot_x = (W // 2) - 84
    for i in range(6):
        if i == 0:
            draw.rounded_rectangle([start_dot_x, dot_y - 8, start_dot_x + 44, dot_y + 8], radius=8, fill="white")
            start_dot_x += 60
        else:
            draw.ellipse([start_dot_x, dot_y - 8, start_dot_x + 16, dot_y + 8], fill="#5E5C64")
            start_dot_x += 32

    draw.text((W // 2, dot_y + 92), "POWERED BY", fill="#88868E", font=font_tag, anchor="mm")
    draw.text((W // 2, dot_y + 132), "UPI", fill="#D6D5DB", font=font_md, anchor="mm")

    # Bottom DONE Bar
    draw.rectangle([0, H - 164, W, H], fill="#1C1B20")
    draw.text((W // 2, H - 88), "DONE", fill="#9C6ADE", font=font_md, anchor="mm")
    draw.rounded_rectangle([W // 2 - 180, H - 28, W // 2 + 180, H - 18], radius=6, fill="white")

    return img

# --- DISPLAY & DOWNLOAD ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Live Mockup Preview (HD)")
    final_img = create_mockup()
    st.image(final_img, width=380)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Download Full HD Mockup (PNG)",
        data=buf.getvalue(),
        file_name="payment_ad_mockup_hd.png",
        mime="image/png"
    )

with col2:
    if uploaded_ad is not None:
        st.subheader("Exact 300x250 Export (6:5)")
        raw_preview = ImageOps.exif_transpose(Image.open(uploaded_ad)).convert("RGB")
        exact_300 = ImageOps.fit(raw_preview, (300, 250), method=Image.Resampling.LANCZOS)
        st.image(exact_300, caption="300x250 px asset")
