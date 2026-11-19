import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import io
import os
import glob

st.set_page_config(page_title="Real UI Ad Mockup Generator", layout="wide")

st.title("📱 Real-Template Ad Placement Mockup Tool")
st.write("Composites your 300x250 creative directly onto the real app screenshot with full HD and sharpness controls.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative (300x250 / 6:5)")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Banner", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. HD & Clarity Controls")
scale_mode = st.sidebar.radio(
    "Output Resolution Mode",
    [
        "Full HD 1080p (Crisp High-Res Export)",
        "1:1 Exact 300x250 Slot (Zero Banner Stretch)"
    ],
    index=0
)
banner_sharpness = st.sidebar.slider("Banner & Fine-Text Sharpness", min_value=0, max_value=250, value=140, step=10)
fix_airtel_cta = st.sidebar.checkbox("Vector-Sharpen 'Register now' & 'T&C' (For upscaled 300x250)", value=False)

st.sidebar.header("3. Edit Transaction Details")
edit_text = st.sidebar.checkbox("Customize Name, Amount & Date", value=True)
recipient_name = st.sidebar.text_input("Recipient Name", value="Ramana")
masked_phone = st.sidebar.text_input("Phone / UPI ID", value="+91 ••••• •1592")
amount = st.sidebar.text_input("Amount (digits only)", value="1")
date_time_str = st.sidebar.text_input("Date & Time", value="05 October 2026 at 11:40 AM")
status_time = st.sidebar.text_input("Top Clock Time", value="11:40")

st.sidebar.header("4. Ad Tag Settings")
show_ad_tag = st.sidebar.checkbox("Overlay [ (i) ⋮ ] Ad Tag", value=True)
tag_corner = st.sidebar.selectbox("Tag Position", ["Top-Left", "Top-Right"], index=0)

uploaded_template = st.sidebar.file_uploader("Optional: Upload Different Reference Screenshot", type=["png", "jpg", "jpeg"])

# --- GUARANTEED SCALABLE FONT LOADER ---
def get_font(size, bold=False):
    px = max(10, int(size))
    search_patterns = [
        "/usr/share/fonts/**/*Bold*.ttf" if bold else "/usr/share/fonts/**/*Regular*.ttf",
        "/usr/share/fonts/**/*.ttf",
    ]
    for pattern in search_patterns:
        matches = sorted(glob.glob(pattern, recursive=True))
        for m in matches:
            if bold and "Bold" not in os.path.basename(m):
                continue
            try:
                return ImageFont.truetype(m, px)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=px)
    except TypeError:
        return ImageFont.load_default()

# --- MULTI-STEP FINE-TEXT UPSCALER ---
def crisp_fit_banner(raw_rgb, target_w, target_h, clarity_amount):
    src_w, src_h = raw_rgb.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if abs(src_ratio - target_ratio) > 0.01:
        cropped = ImageOps.fit(
            raw_rgb,
            (src_w, int(src_w / target_ratio)) if src_ratio < target_ratio else (int(src_h * target_ratio), src_h),
            method=Image.Resampling.LANCZOS
        )
    else:
        cropped = raw_rgb

    if cropped.size == (target_w, target_h):
        final_banner = cropped.copy()
    else:
        curr = cropped
        while curr.width * 1.5 < target_w:
            next_w = int(curr.width * 1.4)
            next_h = int(curr.height * 1.4)
            curr = curr.resize((next_w, next_h), Image.Resampling.BICUBIC)
            if clarity_amount > 0:
                curr = curr.filter(ImageFilter.UnsharpMask(radius=0.8, percent=int(clarity_amount * 0.45), threshold=1))
        final_banner = curr.resize((target_w, target_h), Image.Resampling.LANCZOS)

    if clarity_amount > 0:
        final_banner = final_banner.filter(
            ImageFilter.UnsharpMask(radius=0.75, percent=clarity_amount, threshold=1)
        )
    return final_banner

# --- EXACT FLUSH GOOGLE/FLIPKART ADCHOICES CORNER TAB ---
def draw_authentic_ad_tag(banner_img, bw, bh, corner="Top-Left"):
    ss = 4
    tw = max(28, int(bw * 0.084))
    th = max(15, int(bh * 0.052))
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
    orig_w, orig_h = base_img.size
    is_exact_300 = "1:1 Exact" in scale_mode

    target_w = 324 if is_exact_300 else 1080
    scale_factor = target_w / orig_w
    target_h = int(orig_h * scale_factor)

    canvas = base_img.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    if target_w > orig_w:
        canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.0, percent=110, threshold=2))

    W, H = canvas.size
    draw = ImageDraw.Draw(canvas)

    status_bg = canvas.getpixel((int(W * 0.5), int(H * 0.015)))
    header_bg = canvas.getpixel((int(W * 0.15), int(H * 0.11)))
    card_bg = canvas.getpixel((int(W * 0.5), int(H * 0.17)))
    page_bg = canvas.getpixel((int(W * 0.015), int(H * 0.60)))
    is_light_card = sum(card_bg) > 380

    txt_primary = (28, 28, 30) if is_light_card else (255, 255, 255)
    txt_secondary = (102, 104, 110) if is_light_card else (175, 175, 182)
    txt_date = (227, 245, 231)
    txt_status = (85, 87, 92) if sum(status_bg) > 380 else (240, 240, 240)

    if edit_text:
        # 1. Top Clock
        draw.rectangle([int(W * 0.04), int(H * 0.010), int(W * 0.155), int(H * 0.036)], fill=status_bg)
        draw.text((int(W * 0.052), int(H * 0.023)), status_time, fill=txt_status, font=get_font(H * 0.015, bold=True), anchor="lm")

        # 2. Date/Time under "Payment Successful"
        draw.rectangle([int(W * 0.15), int(H * 0.092), int(W * 0.85), int(H * 0.125)], fill=header_bg)
        draw.text((W // 2, int(H * 0.108)), date_time_str, fill=txt_date, font=get_font(H * 0.0175, bold=False), anchor="mm")

        # 3. Recipient Name & Phone
        draw.rectangle([int(W * 0.31), int(H * 0.172), int(W * 0.92), int(H * 0.242)], fill=card_bg)
        draw.text((int(W * 0.345), int(H * 0.178)), recipient_name, fill=txt_primary, font=get_font(H * 0.0245, bold=True))
        draw.text((int(W * 0.345), int(H * 0.214)), masked_phone, fill=txt_secondary, font=get_font(H * 0.0185, bold=False))

        # 4. Amount digits next to the authentic ₹ glyph
        draw.rectangle([int(W * 0.382), int(H * 0.246), int(W * 0.64), int(H * 0.305)], fill=card_bg)
        draw.text((int(W * 0.385), int(H * 0.250)), amount, fill=txt_primary, font=get_font(H * 0.033, bold=True))

    # 5. Exact Full Ad Slot Bounds (Eliminates any peeking edges from the original Flipkart banner!)
    ad_x1 = int(W * 0.035)
    ad_x2 = int(W * 0.965)
    ad_y1 = int(H * 0.440)
    ad_y2 = int(H * 0.788)
    ad_w = ad_x2 - ad_x1
    ad_h = ad_y2 - ad_y1

    if uploaded_ad is not None:
        # First erase the entire original ad slot with the exact page background color
        draw.rectangle([ad_x1 - 2, ad_y1 - 2, ad_x2 + 2, ad_y2 + 2], fill=page_bg)

        raw_ad = Image.open(uploaded_ad)
        raw_ad = ImageOps.exif_transpose(raw_ad)
        if raw_ad.mode in ("RGBA", "P"):
            bg = Image.new("RGB", raw_ad.size, (255, 255, 255))
            raw_ad = raw_ad.convert("RGBA")
            bg.paste(raw_ad, mask=raw_ad.split()[3])
            ad_rgb = bg
        else:
            ad_rgb = raw_ad.convert("RGB")

        ad_fitted = crisp_fit_banner(ad_rgb, ad_w, ad_h, banner_sharpness)

        if fix_airtel_cta:
            ov_cta = ImageDraw.Draw(ad_fitted)
            btn_x1 = int(ad_w * 0.048)
            btn_y1 = int(ad_h * 0.552)
            btn_x2 = int(ad_w * 0.258)
            btn_y2 = int(ad_h * 0.632)
            btn_r = int((btn_y2 - btn_y1) // 2)
            ov_cta.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=btn_r, fill="#FFFFFF")
            cta_font = get_font(int(ad_h * 0.032), bold=True)
            ov_cta.text(((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2), "Register now", fill="#D9251D", font=cta_font, anchor="mm")

            tnc_font = get_font(int(ad_h * 0.022), bold=False)
            ov_cta.text((int(ad_w * 0.052), int(ad_h * 0.955)), "T&C Apply*", fill="#F0F4F8", font=tnc_font, anchor="lm")

        if show_ad_tag:
            ad_fitted = draw_authentic_ad_tag(ad_fitted, ad_w, ad_h, corner=tag_corner)

        mask = Image.new("L", (ad_w, ad_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, ad_w, ad_h], radius=int(W * 0.028), fill=255)
        canvas.paste(ad_fitted, (ad_x1, ad_y1), mask)

    return canvas

template_img = None
if uploaded_template is not None:
    template_img = ImageOps.exif_transpose(Image.open(uploaded_template))
elif os.path.exists("template.jpg"):
    template_img = ImageOps.exif_transpose(Image.open("template.jpg"))
elif os.path.exists("template.png"):
    template_img = ImageOps.exif_transpose(Image.open("template.png"))

if template_img is None:
    st.warning("⚠️ Please upload `template.jpg` to your GitHub repo or use the sidebar uploader.")
else:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader(f"Authentic Mockup Output ({scale_mode.split(' (')[0]})")
        result = build_real_mockup(template_img)
        st.image(result, use_container_width=True)

        buf = io.BytesIO()
        result.save(buf, format="PNG", compress_level=0)
        st.download_button(
            "⬇️ Download Lossless Mockup (PNG)",
            data=buf.getvalue(),
            file_name="authentic_ad_mockup.png",
            mime="image/png"
        )

    with col2:
        if uploaded_ad is not None:
            st.subheader("Exact 300x250 Ad Creative (6:5)")
            raw_ad = ImageOps.exif_transpose(Image.open(uploaded_ad)).convert("RGB")
            exact_300 = crisp_fit_banner(raw_ad, 300, 250, banner_sharpness)
            st.image(exact_300, caption="300x250 px asset")
