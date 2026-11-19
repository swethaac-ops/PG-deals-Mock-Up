import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

st.set_page_config(page_title="Real UI Ad Mockup Generator", layout="wide")

st.title("📱 Real-Template Ad Placement Mockup Tool")
st.write("Composites your 300x250 creative directly onto the real app screenshot so icons, fonts, and UPI branding remain 100% authentic.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative (300x250 / 6:5)")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Banner", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. Edit Transaction Details")
edit_text = st.sidebar.checkbox("Customize Name, Amount & Date", value=True)
recipient_name = st.sidebar.text_input("Recipient Name", value="Ramana")
masked_phone = st.sidebar.text_input("Phone / UPI ID", value="+91 ••••• •1592")
amount = st.sidebar.text_input("Amount (digits only)", value="1")
date_time_str = st.sidebar.text_input("Date & Time", value="05 October 2026 at 11:40 AM")
status_time = st.sidebar.text_input("Top Clock Time", value="11:40")

st.sidebar.header("3. Ad Tag Settings")
show_ad_tag = st.sidebar.checkbox("Overlay [ (i) ⋮ ] Ad Tag", value=True)
tag_corner = st.sidebar.selectbox("Tag Position", ["Top-Left", "Top-Right"])

# Optional fallback if user uploads template directly in app instead of GitHub
uploaded_template = st.sidebar.file_uploader("Optional: Upload Different Reference Screenshot", type=["png", "jpg", "jpeg"])

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, max(8, int(size)))
    return ImageFont.load_default()

def draw_authentic_ad_tag(banner_img, bw, bh, corner="Top-Left"):
    ss = 4
    tw = max(28, int(bw * 0.086))
    th = max(15, int(bh * 0.054))
    hi_w, hi_h = tw * ss, th * ss

    tag = Image.new("RGBA", (hi_w, hi_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    is_left = "Left" in corner
    corners = (False, False, True, False) if is_left else (False, False, False, True)

    td.rounded_rectangle(
        [0, 0, hi_w - 1, hi_h - 1],
        radius=int(hi_h * 0.24),
        corners=corners,
        fill=(248, 249, 251, 235),
        outline=(215, 220, 226, 180),
        width=2
    )

    blue = (0, 148, 224, 255)
    cx, cy = int(hi_w * 0.36), hi_h // 2
    r = int(hi_h * 0.33)
    td.ellipse([cx - r, cy - r, cx + r, cy + r], outline=blue, width=max(3, int(hi_h * 0.072)))
    dot_r = max(2, int(r * 0.16))
    td.ellipse([cx - dot_r, cy - int(r * 0.46) - dot_r, cx + dot_r, cy - int(r * 0.46) + dot_r], fill=blue)
    stem_w = max(2, int(r * 0.15))
    td.rectangle([cx - stem_w, cy - int(r * 0.14), cx + stem_w, cy + int(r * 0.48)], fill=blue)

    dot_col = (58, 108, 148, 245)
    dx = int(hi_w * 0.76)
    dr = max(2, int(hi_h * 0.068))
    sp = int(hi_h * 0.22)
    for off in (-sp, 0, sp):
        td.ellipse([dx - dr, cy + off - dr, dx + dr, cy + off + dr], fill=dot_col)

    tag_small = tag.resize((tw, th), Image.Resampling.LANCZOS)
    out = banner_img.convert("RGBA")
    out.paste(tag_small, (0 if is_left else bw - tw, 0), tag_small)
    return out.convert("RGB")

def build_real_mockup(base_img):
    W, H = base_img.size
    canvas = base_img.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Sample exact colors directly from the real screenshot so patches are 100% invisible
    status_bg = canvas.getpixel((int(W * 0.5), int(H * 0.015)))
    header_bg = canvas.getpixel((int(W * 0.15), int(H * 0.11)))
    card_bg = canvas.getpixel((int(W * 0.5), int(H * 0.17)))
    is_light_card = sum(card_bg) > 380

    txt_primary = (28, 28, 30) if is_light_card else (255, 255, 255)
    txt_secondary = (102, 104, 110) if is_light_card else (175, 175, 182)
    txt_date = (227, 245, 231)
    txt_status = (85, 87, 92) if sum(status_bg) > 380 else (240, 240, 240)

    if edit_text:
        # 1. Cleanly patch & update Top Clock
        draw.rectangle([int(W * 0.04), int(H * 0.012), int(W * 0.15), int(H * 0.036)], fill=status_bg)
        draw.text((int(W * 0.055), int(H * 0.024)), status_time, fill=txt_status, font=get_font(H * 0.015, bold=True), anchor="lm")

        # 2. Cleanly patch & update Date/Time under "Payment Successful"
        draw.rectangle([int(W * 0.15), int(H * 0.092), int(W * 0.85), int(H * 0.125)], fill=header_bg)
        draw.text((W // 2, int(H * 0.108)), date_time_str, fill=txt_date, font=get_font(H * 0.017, bold=False), anchor="mm")

        # 3. Cleanly patch & update Recipient Name, Phone, and Amount (keeping original ₹ symbol intact!)
        # Patch Name & Phone area
        draw.rectangle([int(W * 0.31), int(H * 0.172), int(W * 0.92), int(H * 0.242)], fill=card_bg)
        draw.text((int(W * 0.345), int(H * 0.180)), recipient_name, fill=txt_primary, font=get_font(H * 0.024, bold=True))
        draw.text((int(W * 0.345), int(H * 0.215)), masked_phone, fill=txt_secondary, font=get_font(H * 0.018, bold=False))

        # Keep the authentic ₹ glyph at x=0.345..0.382 untouched, only replace the digits to its right!
        draw.rectangle([int(W * 0.382), int(H * 0.248), int(W * 0.64), int(H * 0.305)], fill=card_bg)
        draw.text((int(W * 0.384), int(H * 0.252)), amount, fill=txt_primary, font=get_font(H * 0.032, bold=True))

    # 4. Exact 6:5 (300x250) Ad Banner Slot Coordinates matching the real screenshot
    ad_x1 = int(W * 0.036)
    ad_x2 = int(W * 0.964)
    ad_w = ad_x2 - ad_x1
    ad_h = int(ad_w * (250 / 300))  # Exact 6:5 ratio
    ad_y1 = int(H * 0.443)
    ad_y2 = ad_y1 + ad_h

    if uploaded_ad is not None:
        raw_ad = ImageOps.exif_transpose(Image.open(uploaded_ad)).convert("RGB")
        ad_fitted = ImageOps.fit(raw_ad, (ad_w, ad_h), method=Image.Resampling.LANCZOS)

        if show_ad_tag:
            ad_fitted = draw_authentic_ad_tag(ad_fitted, ad_w, ad_h, corner=tag_corner)

        # Rounded corner mask matching the native PhonePe ad container
        mask = Image.new("L", (ad_w, ad_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, ad_w, ad_h], radius=int(W * 0.028), fill=255)
        canvas.paste(ad_fitted, (ad_x1, ad_y1), mask)

    return canvas

# Load template from GitHub or sidebar upload
template_img = None
if uploaded_template is not None:
    template_img = ImageOps.exif_transpose(Image.open(uploaded_template))
elif os.path.exists("template.jpg"):
    template_img = ImageOps.exif_transpose(Image.open("template.jpg"))
elif os.path.exists("template.png"):
    template_img = ImageOps.exif_transpose(Image.open("template.png"))

if template_img is None:
    st.warning("⚠️ Please upload `template.jpg` (your reference screenshot) to your GitHub repo or use the 'Upload Different Reference Screenshot' button in the left sidebar.")
else:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("Authentic Mockup Output")
        result = build_real_mockup(template_img)
        st.image(result, width=380)

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        st.download_button("⬇️ Download Authentic Mockup (PNG)", data=buf.getvalue(), file_name="authentic_ad_mockup.png", mime="image/png")

    with col2:
        if uploaded_ad is not None:
            st.subheader("Exact 300x250 Ad Creative (6:5)")
            raw_ad = ImageOps.exif_transpose(Image.open(uploaded_ad)).convert("RGB")
            st.image(ImageOps.fit(raw_ad, (300, 250), method=Image.Resampling.LANCZOS), caption="300x250 px asset")
