import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Ad Placement Mockup Generator", layout="wide")

st.title("📱 Payment Screen & 300x250 Ad Mockup Tool")
st.write("Customize the transaction details and upload a banner to preview it inside the UI.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Image (Will resize to 300x250)", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. Edit Transaction Details")
status_time = st.sidebar.text_input("Top Bar Clock", value="1:12")
recipient_name = st.sidebar.text_input("Recipient Name", value="Deadpool")
masked_number = st.sidebar.text_input("Masked Account/Phone", value="XXXXXX0670")
amount = st.sidebar.text_input("Amount (without ₹ symbol)", value="1")
date_time_str = st.sidebar.text_input("Transaction Date & Time", value="08 January 2026 at 01:11 PM")

st.sidebar.header("3. Ad Tag Settings")
show_info_tag = st.sidebar.checkbox("Show Info 'i' Tag on Ad", value=True)
tag_position = st.sidebar.selectbox("Tag Position", ["Top-Right (Like Reference)", "Top-Left"])

# --- IMAGE GENERATION FUNCTION ---
def create_mockup():
    # Canvas dimensions (Mobile Portrait)
    W, H = 540, 1170
    img = Image.new("RGB", (W, H), "#1C1B20") # Dark background
    draw = ImageDraw.Draw(img)

    # Try loading default scalable font, fallback to basic if unavailable
    try:
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_md = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_reg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except:
        font_lg = font_md = font_reg = font_sm = ImageFont.load_default()

    # 1. Top Green Header Section
    header_h = 285
    draw.rectangle([0, 0, W, header_h], fill="#2E8B3C")

    # Top Status Bar
    draw.text((25, 12), status_time, fill="white", font=font_sm)
    draw.text((W - 65, 12), "90%", fill="white", font=font_sm)

    # White Checkmark Circle
    cx, cy = W // 2, 125
    draw.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill="#4FA35B") # Outer glow
    draw.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], fill="white")   # Inner circle
    # Green Checkmark Tick
    draw.line([(cx - 16, cy), (cx - 4, cy + 12), (cx + 18, cy - 12)], fill="#2E8B3C", width=6)

    # Payment Successful Text
    draw.text((W // 2, 195), "Payment Successful", fill="white", font=font_md, anchor="mm")
    draw.text((W // 2, 225), date_time_str, fill="#E0F2E3", font=font_sm, anchor="mm")

    # 2. Transaction Card
    card_x1, card_y1, card_x2, card_y2 = 20, 265, W - 20, 520
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill="#242228")

    # Purple Avatar Box
    av_x1, av_y1 = 45, 295
    draw.rounded_rectangle([av_x1, av_y1, av_x1 + 75, av_y1 + 75], radius=18, fill="#9C6ADE")
    # Simple User Icon inside Avatar
    draw.ellipse([av_x1 + 26, av_y1 + 16, av_x1 + 49, av_y1 + 39], outline="white", width=3)
    draw.arc([av_x1 + 16, av_y1 + 42, av_x1 + 59, av_y1 + 72], start=180, end=360, fill="white", width=3)

    # Recipient Details & Amount
    draw.text((145, 298), recipient_name, fill="white", font=font_md)
    draw.text((145, 330), masked_number, fill="#A09FA6", font=font_sm)
    draw.text((145, 368), f"₹{amount}", fill="white", font=font_lg)
    draw.text((card_x2 - 25, 378), "Split Expense", fill="#A67CE8", font=font_sm, anchor="rm")

    # Divider Line & Bottom Card Actions
    draw.line([(20, 425), (W - 20, 425)], fill="#36343B", width=2)
    draw.line([(W // 2, 435), (W // 2, 510)], fill="#36343B", width=2)
    
    # Action Buttons Placeholders
    draw.ellipse([75, 450, 119, 494], fill="#382B47")
    draw.text((135, 472), "View Details", fill="#D6D5DB", font=font_sm, anchor="lm")
    
    draw.ellipse([305, 450, 349, 494], fill="#382B47")
    draw.text((365, 472), "Share Receipt", fill="#D6D5DB", font=font_sm, anchor="lm")

    # 3. 300x250 Ad Banner Container (Aspect Ratio 6:5)
    # Scaled proportionally to fit the 540px screen nicely (or exact 300x250 centered)
    ad_w, ad_h = 480, 400 # Exact 6:5 ratio (scaled 1.6x to fit mobile width cleanly)
    ad_x = (W - ad_w) // 2
    ad_y = 545

    if uploaded_ad is not None:
        ad_img = Image.open(uploaded_ad).convert("RGB")
        # Resize/Crop to exact 300x250 first as requested, then fit slot
        ad_300x250 = ad_img.resize((300, 250), Image.Resampling.LANCZOS)
        ad_display = ad_300x250.resize((ad_w, ad_h), Image.Resampling.LANCZOS)
    else:
        # Placeholder white ad box if no image uploaded yet
        ad_display = Image.new("RGB", (ad_w, ad_h), "#F5F5F7")
        ad_draw = ImageDraw.Draw(ad_display)
        ad_draw.text((ad_w // 2, ad_h // 2), "300 x 250 Ad Slot\n(Upload Image on Left)", fill="#666666", font=font_md, anchor="mm", align="center")

    # Round the corners of the Ad Banner
    mask = Image.new("L", (ad_w, ad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, ad_w, ad_h], radius=18, fill=255)
    img.paste(ad_display, (ad_x, ad_y), mask)

    # 4. Small Circular 'i' Tag on the Ad Corner
    if show_info_tag:
        r = 12
        padding = 18
        if tag_position == "Top-Left":
            ix, iy = ad_x + padding, ad_y + padding
        else:
            ix, iy = ad_x + ad_w - padding, ad_y + padding

        draw.ellipse([ix - r, iy - r, ix + r, iy + r], fill="white", outline="#4A90E2", width=2)
        draw.text((ix, iy), "i", fill="#4A90E2", font=font_sm, anchor="mm")

    # 5. Carousel Dots & UPI Footer
    dot_y = ad_y + ad_h + 22
    start_dot_x = (W // 2) - 55
    for i in range(8):
        if i == 0:
            draw.rounded_rectangle([start_dot_x, dot_y - 4, start_dot_x + 22, dot_y + 4], radius=4, fill="white")
            start_dot_x += 30
        else:
            draw.ellipse([start_dot_x, dot_y - 4, start_dot_x + 8, dot_y + 4], fill="#5E5C64")
            start_dot_x += 16

    draw.text((W // 2, dot_y + 45), "POWERED BY", fill="#88868E", font=font_sm, anchor="mm")
    draw.text((W // 2, dot_y + 68), "UPI", fill="#D6D5DB", font=font_md, anchor="mm")

    # Bottom Done Bar
    draw.rectangle([0, H - 85, W, H], fill="#141317")
    draw.text((W // 2, H - 45), "Done", fill="#9C6ADE", font=font_md, anchor="mm")

    return img

# --- DISPLAY & DOWNLOAD ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Live Mockup Preview")
    final_img = create_mockup()
    st.image(final_img, width=360)

    # Convert to downloadable bytes
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
        raw_ad = Image.open(uploaded_ad).resize((300, 250))
        st.image(raw_ad, caption="Exact 300x250 px asset")
