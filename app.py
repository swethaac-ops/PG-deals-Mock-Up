import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

st.set_page_config(page_title="Ad Placement Mockup Generator", layout="wide")

st.title("📱 Payment Screen & 300x250 Ad Mockup Tool")
st.write("Customize the transaction details and upload a banner to preview it inside the UI.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Image (Will resize to 300x250)", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. Edit Transaction Details")
avatar_initials = st.sidebar.text_input("Avatar Initials", value="JL", max_chars=3)
recipient_name = st.sidebar.text_area("Recipient Name", value="JUST PARKING\nPRIVATE LIMITED", height=70)
upi_id = st.sidebar.text_input("UPI ID / Masked Number", value="paytm.d*******3175@pty")
amount = st.sidebar.text_input("Amount (without ₹ symbol)", value="150")
date_time_str = st.sidebar.text_input("Transaction Date & Time", value="04:32 pm on 12 Oct 2026")

st.sidebar.header("3. Ad Tag Settings")
show_info_tag = st.sidebar.checkbox("Show Blue 'i' Info Circle", value=True)
tag_position = st.sidebar.selectbox("Tag Position", ["Top-Left", "Top-Right"])

# --- IMAGE GENERATION FUNCTION ---
def create_mockup():
    # Outer Canvas Dimensions (Matching Navaratri Reference)
    W, H = 540, 1170
    img = Image.new("RGB", (W, H), "#121115")
    draw = ImageDraw.Draw(img)

    # Load clean scalable fonts
    try:
        font_amt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 23)
        font_md = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_reg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    except:
        font_amt = font_name = font_md = font_reg = font_sm = font_info = font_tag = ImageFont.load_default()

    # 1. Top Green Header Section (Clean outer layout without status bar)
    header_h = 265
    draw.rectangle([0, 0, W, header_h], fill="#2E8B3C")

    # White Checkmark Circle
    cx, cy = W // 2, 92
    draw.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill="#4FA35B")
    draw.ellipse([cx - 33, cy - 33, cx + 33, cy + 33], fill="white")
    draw.line([(cx - 14, cy), (cx - 3, cy + 11), (cx + 16, cy - 11)], fill="#2E8B3C", width=5)

    # Payment Successful Text
    draw.text((W // 2, 162), "Payment Successful", fill="white", font=font_md, anchor="mm")
    draw.text((W // 2, 195), date_time_str, fill="#E0F2E3", font=font_reg, anchor="mm")

    # 2. Transaction Card
    card_x1, card_y1, card_x2, card_y2 = 18, 232, W - 18, 522
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill="#1E1D22")

    # Yellow Rounded-Square Avatar Box with Initials
    av_x1, av_y1 = 42, 265
    av_size = 76
    draw.rounded_rectangle([av_x1, av_y1, av_x1 + av_size, av_y1 + av_size], radius=18, fill="#D4B82C")
    draw.text((av_x1 + av_size // 2, av_y1 + av_size // 2), avatar_initials.upper(), fill="white", font=font_name, anchor="mm")

    # Recipient Name, UPI ID, and Amount
    text_x = 142
    draw.multiline_text((text_x, 265), recipient_name, fill="white", font=font_name, spacing=6)

    line_count = len(recipient_name.split("\n"))
    upi_y = 265 + (line_count * 30) + 6
    amt_y = upi_y + 34

    draw.text((text_x, upi_y), upi_id, fill="#B0AFB6", font=font_reg)
    draw.text((text_x, amt_y), f"₹{amount}", fill="white", font=font_amt)

    # Underlined "Split Expense"
    split_x, split_y = card_x2 - 26, amt_y + 16
    draw.text((split_x, split_y), "Split Expense", fill="#A67CE8", font=font_sm, anchor="rm")
    text_w = draw.textlength("Split Expense", font=font_sm)
    draw.line([(split_x - text_w, split_y + 10), (split_x, split_y + 10)], fill="#A67CE8", width=1)

    # Card Divider Lines & Bottom Actions
    div_y = 432
    draw.line([(card_x1, div_y), (card_x2, div_y)], fill="#323038", width=2)
    draw.line([(W // 2, div_y + 12), (W // 2, card_y2 - 12)], fill="#323038", width=2)

    # View Details & Share Receipt Buttons
    draw.ellipse([65, 455, 109, 499], fill="#382B47")
    draw.rectangle([80, 468, 94, 486], outline="#A67CE8", width=2)
    draw.text((124, 477), "View Details", fill="#E2E1E6", font=font_sm, anchor="lm")

    draw.ellipse([300, 455, 344, 499], fill="#382B47")
    draw.text((322, 477), "↗", fill="#A67CE8", font=font_md, anchor="mm")
    draw.text((358, 477), "Share Receipt", fill="#E2E1E6", font=font_sm, anchor="lm")

    # 3. 300x250 Ad Banner Container (Exact 6:5 Aspect Ratio)
    ad_w, ad_h = 504, 420  # Exact 6:5 ratio (300x250 scaled 1.68x to fit outer card width)
    ad_x = (W - ad_w) // 2
    ad_y = 542

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

        # Resize to exact 300x250 (6:5) first, then scale smoothly into slot
        ad_300x250 = ad_rgb.resize((300, 250), Image.Resampling.LANCZOS)
        ad_display = ad_300x250.resize((ad_w, ad_h), Image.Resampling.LANCZOS)
    else:
        ad_display = Image.new("RGB", (ad_w, ad_h), "#F5F5F7")
        ad_draw = ImageDraw.Draw(ad_display)
        ad_draw.text((ad_w // 2, ad_h // 2), "300 x 250 Ad Slot (6:5)\nUpload Image in Left Sidebar", fill="#666666", font=font_md, anchor="mm", align="center")

    # Apply subtle rounded corners to the Ad Banner
    mask = Image.new("L", (ad_w, ad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, ad_w, ad_h], radius=10, fill=255)
    img.paste(ad_display, (ad_x, ad_y), mask)

    # 4. Circular Blue 'i' Info Tag on Ad Corner (Kept from original setting)
    if show_info_tag:
        r = 12
        padding = 18
        if tag_position == "Top-Left":
            ix, iy = ad_x + padding, ad_y + padding
        else:
            ix, iy = ad_x + ad_w - padding, ad_y + padding

        draw.ellipse([ix - r, iy - r, ix + r, iy + r], fill="white", outline="#1DA1F2", width=2)
        draw.text((ix, iy), "i", fill="#1DA1F2", font=font_info, anchor="mm")

    # 5. Carousel Dots & UPI Footer
    dot_y = ad_y + ad_h + 22
    start_dot_x = (W // 2) - 42
    for i in range(6):
        if i == 0:
            draw.rounded_rectangle([start_dot_x, dot_y - 4, start_dot_x + 22, dot_y + 4], radius=4, fill="white")
            start_dot_x += 30
        else:
            draw.ellipse([start_dot_x, dot_y - 4, start_dot_x + 8, dot_y + 4], fill="#5E5C64")
            start_dot_x += 16

    draw.text((W // 2, dot_y + 46), "POWERED BY", fill="#88868E", font=font_tag, anchor="mm")
    draw.text((W // 2, dot_y + 66), "UPI", fill="#D6D5DB", font=font_md, anchor="mm")

    # Bottom DONE Bar (Matching Navaratri Reference)
    draw.rectangle([0, H - 82, W, H], fill="#1C1B20")
    draw.text((W // 2, H - 44), "DONE", fill="#9C6ADE", font=font_md, anchor="mm")
    draw.rounded_rectangle([W // 2 - 90, H - 14, W // 2 + 90, H - 9], radius=3, fill="white")

    return img

# --- DISPLAY & DOWNLOAD ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Live Mockup Preview")
    final_img = create_mockup()
    st.image(final_img, width=360)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Download Full Mockup (PNG)",
        data=buf.getvalue(),
        file_name="payment_ad_mockup.png",
        mime="image/png"
    )

with col2:
    if uploaded_ad is not None:
        st.subheader("Resized 300x250 Ad Unit (6:5)")
        raw_preview = ImageOps.exif_transpose(Image.open(uploaded_ad)).convert("RGB").resize((300, 250))
        st.image(raw_preview, caption="Exact 300x250 px asset")
