import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import io

st.set_page_config(page_title="Ad Placement Mockup Generator", layout="wide")

st.title("📱 Payment Screen & 300x250 Ad Mockup Tool")
st.write("Customize the transaction details and upload a banner to preview it inside the UI.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Image (300x250 / 6:5 ratio)", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. Sharpness & Scale Mode")
scale_mode = st.sidebar.radio(
    "Banner Rendering Mode",
    [
        "1:1 Exact 300x250 Slot (Zero Stretch / 100% Sharp)",
        "Full HD 1080p Frame (Best for 600x500+ Uploads)"
    ],
    index=0
)

fix_airtel_cta = st.sidebar.checkbox("Vector-Sharpen 'Register now' & 'T&C' (For upscaled 300x250)", value=False)

st.sidebar.header("3. Edit Transaction Details")
avatar_initials = st.sidebar.text_input("Avatar Initials", value="JL", max_chars=3)
recipient_name = st.sidebar.text_area("Recipient Name", value="JUST PARKING\nPRIVATE LIMITED", height=70)
upi_id = st.sidebar.text_input("UPI ID / Masked Number", value="paytm.d*******3175@pty")
amount = st.sidebar.text_input("Amount (without ₹ symbol)", value="150")
date_time_str = st.sidebar.text_input("Transaction Date & Time", value="04:32 pm on 12 Oct 2026")

st.sidebar.header("4. Ad Tag Settings")
show_info_tag = st.sidebar.checkbox("Show Ad Tag [ (i) ⋮ ]", value=True)
tag_position = st.sidebar.selectbox("Tag Corner", ["Top-Left", "Top-Right"])

# --- HELPER FOR GUARANTEED CRISP FONTS ---
def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, max(8, int(size)))
        except:
            continue
    try:
        return ImageFont.load_default(size=max(8, int(size)))
    except:
        return ImageFont.load_default()

# --- DRAW PHOTOREALISTIC [ (i) ⋮ ] ADCHOICES TAG (4X SUPERSAMPLED FOR ZERO JAGGED EDGES) ---
def draw_native_ad_tag(base_img, ad_w, ad_h, position="Top-Left"):
    ss = 4  # 4x supersampling so curves and dots look 100% native
    tag_w = max(32, int(ad_w * 0.105))
    tag_h = max(16, int(ad_h * 0.062))
    margin_x = max(2, int(ad_w * 0.012))
    margin_y = max(2, int(ad_h * 0.014))

    # Render tag at 4x resolution
    hi_w, hi_h = tag_w * ss, tag_h * ss
    tag_hi = Image.new("RGBA", (hi_w + 16, hi_h + 16), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag_hi)

    # Subtle ambient shadow behind the white tab (just like real Android WebView ad rendering)
    shadow = Image.new("RGBA", (hi_w + 16, hi_h + 16), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([8, 9, 8 + hi_w, 9 + hi_h], radius=int(hi_h * 0.22), fill=(0, 0, 0, 48))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=3))
    tag_hi = Image.alpha_composite(tag_hi, shadow)
    td = ImageDraw.Draw(tag_hi)

    # Crisp white semi-opaque pill tab
    td.rounded_rectangle(
        [8, 8, 8 + hi_w, 8 + hi_h],
        radius=int(hi_h * 0.22),
        fill=(255, 255, 255, 245)
    )

    # Left side: Cyan-blue circle with 'i' (#00AEEF)
    cx = 8 + int(hi_w * 0.34)
    cy = 8 + (hi_h // 2)
    r = int(hi_h * 0.34)
    stroke = max(4, int(hi_h * 0.075))
    td.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 174, 239, 255), width=stroke)

    # Draw geometric 'i' inside circle (dot + stem) so it's crisp at every pixel size
    dot_r = max(2, int(r * 0.16))
    td.ellipse([cx - dot_r, cy - int(r * 0.48) - dot_r, cx + dot_r, cy - int(r * 0.48) + dot_r], fill=(0, 174, 239, 255))
    stem_w = max(2, int(r * 0.15))
    td.rectangle([cx - stem_w, cy - int(r * 0.15), cx + stem_w, cy + int(r * 0.48)], fill=(0, 174, 239, 255))

    # Right side: Three vertical dark-grey dots (⋮)
    dx = 8 + int(hi_w * 0.77)
    dot_radius = max(2, int(hi_h * 0.068))
    spacing = int(hi_h * 0.22)
    for offset in (-spacing, 0, spacing):
        dy = cy + offset
        td.ellipse([dx - dot_radius, dy - dot_radius, dx + dot_radius, dy + dot_radius], fill=(75, 80, 88, 255))

    # Downsample 4x -> 1x with LANCZOS anti-aliasing
    final_tag = tag_hi.resize((tag_w + 4, tag_h + 4), Image.Resampling.LANCZOS)

    ad_rgba = base_img.convert("RGBA")
    if position == "Top-Left":
        paste_x, paste_y = margin_x, margin_y
    else:
        paste_x, paste_y = ad_w - tag_w - margin_x - 4, margin_y

    ad_rgba.paste(final_tag, (paste_x, paste_y), final_tag)
    return ad_rgba.convert("RGB")

# --- IMAGE GENERATION FUNCTION ---
def create_mockup():
    is_exact_300 = "1:1 Exact" in scale_mode

    if is_exact_300:
        ad_w, ad_h = 300, 250
        s = 300 / 504
        W, H = 322, 698
    else:
        ad_w, ad_h = 1008, 840
        s = 2.0
        W, H = 1080, 2340

    img = Image.new("RGB", (W, H), "#121115")
    draw = ImageDraw.Draw(img)

    font_amt = get_font(30 * s, bold=True)
    font_name = get_font(23 * s, bold=True)
    font_md = get_font(20 * s, bold=True)
    font_reg = get_font(18 * s, bold=False)
    font_sm = get_font(15 * s, bold=False)
    font_tag = get_font(11 * s, bold=True)

    # 1. Top Green Header Section
    header_h = int(265 * s)
    draw.rectangle([0, 0, W, header_h], fill="#2E8B3C")

    # White Checkmark Circle
    cx, cy = W // 2, int(92 * s)
    r_outer = int(44 * s)
    r_inner = int(33 * s)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill="#4FA35B")
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill="white")
    draw.line(
        [(cx - int(14 * s), cy), (cx - int(3 * s), cy + int(11 * s)), (cx + int(16 * s), cy - int(11 * s))],
        fill="#2E8B3C",
        width=max(2, int(5 * s))
    )

    # Payment Successful Text
    draw.text((W // 2, int(162 * s)), "Payment Successful", fill="white", font=font_md, anchor="mm")
    draw.text((W // 2, int(195 * s)), date_time_str, fill="#E0F2E3", font=font_reg, anchor="mm")

    # 2. Transaction Card
    card_x1, card_y1 = int(11 * s), int(232 * s)
    card_x2, card_y2 = W - int(11 * s), int(522 * s)
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=int(16 * s), fill="#1E1D22")

    # Yellow Rounded-Square Avatar Box with Initials
    av_x1, av_y1 = int(28 * s), int(265 * s)
    av_size = int(76 * s)
    draw.rounded_rectangle([av_x1, av_y1, av_x1 + av_size, av_y1 + av_size], radius=int(18 * s), fill="#D4B82C")
    draw.text((av_x1 + av_size // 2, av_y1 + av_size // 2), avatar_initials.upper(), fill="white", font=font_name, anchor="mm")

    # Recipient Name, UPI ID, and Amount
    text_x = int(124 * s)
    draw.multiline_text((text_x, int(265 * s)), recipient_name, fill="white", font=font_name, spacing=int(6 * s))

    line_count = len(recipient_name.split("\n"))
    upi_y = int(265 * s) + (line_count * int(30 * s)) + int(6 * s)
    amt_y = upi_y + int(34 * s)

    draw.text((text_x, upi_y), upi_id, fill="#B0AFB6", font=font_reg)
    draw.text((text_x, amt_y), f"₹{amount}", fill="white", font=font_amt)

    # Underlined "Split Expense"
    split_x, split_y = card_x2 - int(18 * s), amt_y + int(16 * s)
    draw.text((split_x, split_y), "Split Expense", fill="#A67CE8", font=font_sm, anchor="rm")
    text_w = draw.textlength("Split Expense", font=font_sm)
    draw.line([(split_x - text_w, split_y + int(10 * s)), (split_x, split_y + int(10 * s))], fill="#A67CE8", width=max(1, int(1 * s)))

    # Card Divider Lines & Bottom Actions
    div_y = int(432 * s)
    draw.line([(card_x1, div_y), (card_x2, div_y)], fill="#323038", width=max(1, int(2 * s)))
    draw.line([(W // 2, div_y + int(12 * s)), (W // 2, card_y2 - int(12 * s))], fill="#323038", width=max(1, int(2 * s)))

    # View Details & Share Receipt Buttons
    b1_x = int(50 * s)
    b_y = int(477 * s)
    r_btn = int(22 * s)
    draw.ellipse([b1_x - r_btn, b_y - r_btn, b1_x + r_btn, b_y + r_btn], fill="#382B47")
    draw.rectangle([b1_x - int(7 * s), b_y - int(9 * s), b1_x + int(7 * s), b_y + int(9 * s)], outline="#A67CE8", width=max(1, int(2 * s)))
    draw.text((b1_x + int(34 * s), b_y), "View Details", fill="#E2E1E6", font=font_sm, anchor="lm")

    b2_x = W // 2 + int(45 * s)
    draw.ellipse([b2_x - r_btn, b_y - r_btn, b2_x + r_btn, b_y + r_btn], fill="#382B47")
    draw.text((b2_x, b_y), "↗", fill="#A67CE8", font=font_md, anchor="mm")
    draw.text((b2_x + int(34 * s), b_y), "Share Receipt", fill="#E2E1E6", font=font_sm, anchor="lm")

    # 3. 300x250 Ad Banner Container (Exact 6:5 Ratio)
    ad_x = (W - ad_w) // 2
    ad_y = int(542 * s)

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

        if ad_rgb.size == (ad_w, ad_h):
            ad_display = ad_rgb.copy()
        else:
            ad_display = ImageOps.fit(ad_rgb, (ad_w, ad_h), method=Image.Resampling.LANCZOS)
            if ad_w > ad_rgb.width:
                ad_display = ad_display.filter(ImageFilter.UnsharpMask(radius=0.8, percent=140, threshold=1))
    else:
        ad_display = Image.new("RGB", (ad_w, ad_h), "#F5F5F7")
        ad_draw = ImageDraw.Draw(ad_display)
        ad_draw.text((ad_w // 2, ad_h // 2), "300 x 250 Ad Slot (6:5)\nUpload Image in Left Sidebar", fill="#666666", font=font_md, anchor="mm", align="center")

    # Optional Vector CTA & T&C Overlay
    if fix_airtel_cta and uploaded_ad is not None:
        ov_cta = ImageDraw.Draw(ad_display)
        btn_x1, btn_y1 = int(ad_w * 0.048), int(ad_h * 0.552)
        btn_x2, btn_y2 = int(ad_w * 0.258), int(ad_h * 0.632)
        ov_cta.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=int((btn_y2 - btn_y1) // 2), fill="#FFFFFF")
        cta_font = get_font(int(ad_h * 0.032), bold=True)
        ov_cta.text(((btn_x1 + btn_x2) // 2, (btn_y1 + btn_y2) // 2), "Register now", fill="#D9251D", font=cta_font, anchor="mm")

        tnc_font = get_font(int(ad_h * 0.022), bold=False)
        ov_cta.text((int(ad_w * 0.052), int(ad_h * 0.955)), "T&C Apply*", fill="#F0F4F8", font=tnc_font, anchor="lm")

    # 4. Exact [ (i) ⋮ ] Ad Tag on Top-Left Corner (matching Flipkart screenshot style)
    if show_info_tag:
        ad_display = draw_native_ad_tag(ad_display, ad_w, ad_h, position=tag_position)

    # Apply rounded corners to the Ad Banner
    mask = Image.new("L", (ad_w, ad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, ad_w, ad_h], radius=max(6, int(10 * s)), fill=255)
    img.paste(ad_display, (ad_x, ad_y), mask)

    # 5. Carousel Dots & UPI Footer
    dot_y = ad_y + ad_h + int(22 * s)
    start_dot_x = (W // 2) - int(42 * s)
    for i in range(6):
        if i == 0:
            draw.rounded_rectangle([start_dot_x, dot_y - int(4 * s), start_dot_x + int(22 * s), dot_y + int(4 * s)], radius=int(4 * s), fill="white")
            start_dot_x += int(30 * s)
        else:
            draw.ellipse([start_dot_x, dot_y - int(4 * s), start_dot_x + int(8 * s), dot_y + int(4 * s)], fill="#5E5C64")
            start_dot_x += int(16 * s)

    draw.text((W // 2, dot_y + int(46 * s)), "POWERED BY", fill="#88868E", font=font_tag, anchor="mm")
    draw.text((W // 2, dot_y + int(66 * s)), "UPI", fill="#D6D5DB", font=font_md, anchor="mm")

    # Bottom DONE Bar
    draw.rectangle([0, H - int(82 * s), W, H], fill="#1C1B20")
    draw.text((W // 2, H - int(44 * s)), "DONE", fill="#9C6ADE", font=font_md, anchor="mm")
    draw.rounded_rectangle([W // 2 - int(90 * s), H - int(14 * s), W // 2 + int(90 * s), H - int(9 * s)], radius=int(3 * s), fill="white")

    return img

# --- DISPLAY & DOWNLOAD ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Live Mockup Preview")
    final_img = create_mockup()
    st.image(final_img)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG", compress_level=0)
    st.download_button(
        label="⬇️ Download Lossless Mockup (PNG)",
        data=buf.getvalue(),
        file_name="payment_ad_mockup.png",
        mime="image/png"
    )

with col2:
    if uploaded_ad is not None:
        st.subheader("Original Uploaded Ad (1:1)")
        raw_preview = ImageOps.exif_transpose(Image.open(uploaded_ad)).convert("RGB")
        st.image(raw_preview, caption=f"Native size: {raw_preview.width}x{raw_preview.height} px")
