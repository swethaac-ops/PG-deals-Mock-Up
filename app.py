import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import io

st.set_page_config(page_title="Ad Placement Mockup Generator", layout="wide")

st.title("📱 Payment Screen & 300x250 Ad Mockup Tool")
st.write("Customize the transaction details and upload a banner to preview it inside the UI.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("1. Upload Ad Creative")
uploaded_ad = st.sidebar.file_uploader("Upload Ad Image (300x250 / 6:5 ratio)", type=["png", "jpg", "jpeg", "webp"])

st.sidebar.header("2. Theme & Sharpness Mode")
ui_theme = st.sidebar.radio("App Theme", ["Dark Mode (Like Reference)", "Light Mode (White Card & Footer)"], index=0)
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
tag_position = st.sidebar.selectbox("Tag Corner", ["Top-Left", "Top-Right (Like Flipkart)"])

# --- HELPER FOR GUARANTEED CRISP FONTS ---
def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, max(6, int(size)))
        except:
            continue
    try:
        return ImageFont.load_default(size=max(6, int(size)))
    except:
        return ImageFont.load_default()

# --- DRAW AUTHENTIC "POWERED BY UPI" LOGO WITH ORANGE & GREEN TRIANGLES ---
def draw_upi_logo(base_img, center_x, top_y, scale_factor, is_dark=True):
    ss = 4
    w = max(90, int(115 * scale_factor))
    h = max(42, int(52 * scale_factor))
    hw, hh = w * ss, h * ss

    logo_hi = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(logo_hi)

    text_grey = (165, 165, 172, 255) if is_dark else (112, 115, 120, 255)
    sub_grey = (145, 145, 152, 255) if is_dark else (125, 128, 134, 255)

    # 1. "POWERED BY" top caption
    f_pow = get_font(int(hh * 0.14), bold=True)
    d.text((hw * 0.46, hh * 0.12), "POWERED BY", fill=sub_grey, font=f_pow, anchor="mm")

    # 2. Stylized Slanted Block "UPI" Letters
    # Coordinates for slanted italic U, P, I
    y_top = hh * 0.25
    y_bot = hh * 0.72
    slant = hh * 0.11  # Forward italic lean
    thick = hh * 0.105

    # Letter 'U'
    ux = hw * 0.12
    uw = hw * 0.17
    # Left vertical bar of U
    d.polygon([
        (ux + slant, y_top),
        (ux + slant + thick, y_top),
        (ux + thick, y_bot),
        (ux, y_bot)
    ], fill=text_grey)
    # Right vertical bar of U
    d.polygon([
        (ux + uw + slant, y_top),
        (ux + uw + slant + thick, y_top),
        (ux + uw + thick, y_bot),
        (ux + uw, y_bot)
    ], fill=text_grey)
    # Bottom bar of U
    d.polygon([
        (ux, y_bot - thick * 0.85),
        (ux + uw + thick, y_bot - thick * 0.85),
        (ux + uw + thick, y_bot),
        (ux, y_bot)
    ], fill=text_grey)

    # Letter 'P'
    px = hw * 0.41
    pw = hw * 0.17
    y_mid = (y_top + y_bot) * 0.52
    # Vertical stem of P
    d.polygon([
        (px + slant, y_top),
        (px + slant + thick, y_top),
        (px + thick, y_bot),
        (px, y_bot)
    ], fill=text_grey)
    # Top bar of P
    d.polygon([
        (px + slant, y_top),
        (px + pw + slant, y_top),
        (px + pw + slant - thick * 0.15, y_top + thick * 0.85),
        (px + slant, y_top + thick * 0.85)
    ], fill=text_grey)
    # Right vertical loop of P
    d.polygon([
        (px + pw + slant - thick * 0.9, y_top),
        (px + pw + slant, y_top),
        (px + pw + slant * 0.45, y_mid),
        (px + pw + slant * 0.45 - thick * 0.9, y_mid)
    ], fill=text_grey)
    # Middle bar of P
    d.polygon([
        (px + slant * 0.5, y_mid - thick * 0.8),
        (px + pw + slant * 0.45, y_mid - thick * 0.8),
        (px + pw + slant * 0.42, y_mid),
        (px + slant * 0.45, y_mid)
    ], fill=text_grey)

    # Letter 'I'
    ix = hw * 0.68
    d.polygon([
        (ix + slant, y_top),
        (ix + slant + thick, y_top),
        (ix + thick, y_bot),
        (ix, y_bot)
    ], fill=text_grey)

    # 3. Overlapping Green (back) and Saffron-Orange (front) Right-Pointing Triangles
    tri_x = hw * 0.78
    tri_w = hw * 0.13
    # Green triangle (slightly behind & to the right)
    d.polygon([
        (tri_x + tri_w * 0.35 + slant * 0.6, y_top),
        (tri_x + tri_w * 1.35, (y_top + y_bot) * 0.5),
        (tri_x + tri_w * 0.35, y_bot)
    ], fill=(19, 136, 8, 255))

    # Saffron-Orange triangle (in front)
    d.polygon([
        (tri_x + slant * 0.6, y_top),
        (tri_x + tri_w, (y_top + y_bot) * 0.5),
        (tri_x, y_bot)
    ], fill=(244, 121, 32, 255))

    # 4. "UNIFIED PAYMENTS INTERFACE" bottom caption
    f_sub = get_font(int(hh * 0.088), bold=True)
    d.text((hw * 0.49, hh * 0.84), "UNIFIED PAYMENTS INTERFACE", fill=sub_grey, font=f_sub, anchor="mm")

    final_logo = logo_hi.resize((w, h), Image.Resampling.LANCZOS)
    base_rgba = base_img.convert("RGBA")
    base_rgba.paste(final_logo, (int(center_x - w // 2), int(top_y)), final_logo)
    return base_rgba.convert("RGB")

# --- EXACT FLUSH GOOGLE/FLIPKART ADCHOICES CORNER TAB (4X SUPERSAMPLED) ---
def draw_native_ad_tag(base_img, ad_w, ad_h, position="Top-Left"):
    ss = 4
    tag_w = max(26, int(ad_w * 0.084))
    tag_h = max(14, int(ad_h * 0.052))

    hi_w, hi_h = tag_w * ss, tag_h * ss
    tag_hi = Image.new("RGBA", (hi_w, hi_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag_hi)

    is_left = "Left" in position
    inner_radius = int(hi_h * 0.24)
    corner_flags = (False, False, True, False) if is_left else (False, False, False, True)

    td.rounded_rectangle(
        [0, 0, hi_w - 1, hi_h - 1],
        radius=inner_radius,
        corners=corner_flags,
        fill=(248, 249, 251, 232),
        outline=(218, 222, 228, 180),
        width=max(2, ss // 2)
    )

    blue_col = (0, 148, 224, 255)
    cx = int(hi_w * 0.36)
    cy = hi_h // 2
    r = int(hi_h * 0.33)
    stroke = max(3, int(hi_h * 0.072))
    td.ellipse([cx - r, cy - r, cx + r, cy + r], outline=blue_col, width=stroke)

    dot_r = max(2, int(r * 0.16))
    td.ellipse([cx - dot_r, cy - int(r * 0.46) - dot_r, cx + dot_r, cy - int(r * 0.46) + dot_r], fill=blue_col)
    stem_w = max(2, int(r * 0.15))
    td.rectangle([cx - stem_w, cy - int(r * 0.14), cx + stem_w, cy + int(r * 0.48)], fill=blue_col)

    dot_col = (58, 108, 148, 245)
    dx = int(hi_w * 0.76)
    dot_radius = max(2, int(hi_h * 0.068))
    spacing = int(hi_h * 0.22)
    for offset in (-spacing, 0, spacing):
        dy = cy + offset
        td.ellipse([dx - dot_radius, dy - dot_radius, dx + dot_radius, dy + dot_radius], fill=dot_col)

    final_tag = tag_hi.resize((tag_w, tag_h), Image.Resampling.LANCZOS)

    ad_rgba = base_img.convert("RGBA")
    paste_x = 0 if is_left else (ad_w - tag_w)
    paste_y = 0

    ad_rgba.paste(final_tag, (paste_x, paste_y), final_tag)
    return ad_rgba.convert("RGB")

# --- IMAGE GENERATION FUNCTION ---
def create_mockup():
    is_dark = "Dark" in ui_theme
    is_exact_300 = "1:1 Exact" in scale_mode

    if is_exact_300:
        ad_w, ad_h = 300, 250
        s = 300 / 504
        W, H = 322, 698
    else:
        ad_w, ad_h = 1008, 840
        s = 2.0
        W, H = 1080, 2340

    bg_color = "#121115" if is_dark else "#F4F5F7"
    card_color = "#1E1D22" if is_dark else "#FFFFFF"
    primary_txt = "white" if is_dark else "#18181B"
    secondary_txt = "#B0AFB6" if is_dark else "#52525B"
    divider_col = "#323038" if is_dark else "#E4E4E7"
    action_txt = "#E2E1E6" if is_dark else "#27272A"
    icon_circle_bg = "#382B47" if is_dark else "#F3E8FF"
    purple_accent = "#A67CE8" if is_dark else "#6D28D9"
    footer_bar_bg = "#1C1B20" if is_dark else "#FFFFFF"
    dot_inactive = "#5E5C64" if is_dark else "#D4D4D8"
    dot_active = "white" if is_dark else "#3F3F46"

    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    font_amt = get_font(30 * s, bold=True)
    font_name = get_font(23 * s, bold=True)
    font_md = get_font(20 * s, bold=True)
    font_reg = get_font(18 * s, bold=False)
    font_sm = get_font(15 * s, bold=False)

    # 1. Top Green Header Section
    header_h = int(265 * s)
    header_green = "#2E8B3C" if is_dark else "#1B7A34"
    draw.rectangle([0, 0, W, header_h], fill=header_green)

    cx, cy = W // 2, int(92 * s)
    r_outer = int(44 * s)
    r_inner = int(33 * s)
    if is_dark:
        draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill="#4FA35B")
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill="white")
    draw.line(
        [(cx - int(14 * s), cy), (cx - int(3 * s), cy + int(11 * s)), (cx + int(16 * s), cy - int(11 * s))],
        fill=header_green,
        width=max(2, int(5 * s))
    )

    draw.text((W // 2, int(162 * s)), "Payment Successful", fill="white", font=font_md, anchor="mm")
    draw.text((W // 2, int(195 * s)), date_time_str, fill="#E0F2E3", font=font_reg, anchor="mm")

    # 2. Transaction Card
    card_x1, card_y1 = int(11 * s), int(232 * s)
    card_x2, card_y2 = W - int(11 * s), int(522 * s)
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=int(16 * s), fill=card_color)

    # Avatar Box
    av_x1, av_y1 = int(28 * s), int(265 * s)
    av_size = int(76 * s)
    av_bg = "#D4B82C" if is_dark else "#6D28D9"
    draw.rounded_rectangle([av_x1, av_y1, av_x1 + av_size, av_y1 + av_size], radius=int(18 * s), fill=av_bg)
    draw.text((av_x1 + av_size // 2, av_y1 + av_size // 2), avatar_initials.upper(), fill="white", font=font_name, anchor="mm")

    # Recipient Name, UPI ID, and Amount
    text_x = int(124 * s)
    draw.multiline_text((text_x, int(265 * s)), recipient_name, fill=primary_txt, font=font_name, spacing=int(6 * s))

    line_count = len(recipient_name.split("\n"))
    upi_y = int(265 * s) + (line_count * int(30 * s)) + int(6 * s)
    amt_y = upi_y + int(34 * s)

    draw.text((text_x, upi_y), upi_id, fill=secondary_txt, font=font_reg)
    draw.text((text_x, amt_y), f"₹{amount}", fill=primary_txt, font=font_amt)

    # Split Expense
    split_x, split_y = card_x2 - int(18 * s), amt_y + int(16 * s)
    draw.text((split_x, split_y), "Split Expense", fill=purple_accent, font=font_sm, anchor="rm")
    if is_dark:
        text_w = draw.textlength("Split Expense", font=font_sm)
        draw.line([(split_x - text_w, split_y + int(10 * s)), (split_x, split_y + int(10 * s))], fill=purple_accent, width=max(1, int(1 * s)))

    # Card Divider Lines & Bottom Actions
    div_y = int(432 * s)
    draw.line([(card_x1, div_y), (card_x2, div_y)], fill=divider_col, width=max(1, int(2 * s)))
    draw.line([(W // 2, div_y + int(12 * s)), (W // 2, card_y2 - int(12 * s))], fill=divider_col, width=max(1, int(2 * s)))

    b1_x = int(50 * s)
    b_y = int(477 * s)
    r_btn = int(22 * s)
    draw.ellipse([b1_x - r_btn, b_y - r_btn, b1_x + r_btn, b_y + r_btn], fill=icon_circle_bg)
    draw.rectangle([b1_x - int(7 * s), b_y - int(9 * s), b1_x + int(7 * s), b_y + int(9 * s)], outline=purple_accent, width=max(1, int(2 * s)))
    draw.text((b1_x + int(34 * s), b_y), "View Details", fill=action_txt, font=font_sm, anchor="lm")

    b2_x = W // 2 + int(45 * s)
    draw.ellipse([b2_x - r_btn, b_y - r_btn, b2_x + r_btn, b_y + r_btn], fill=icon_circle_bg)
    draw.text((b2_x, b_y), "↗", fill=purple_accent, font=font_md, anchor="mm")
    draw.text((b2_x + int(34 * s), b_y), "Share Receipt", fill=action_txt, font=font_sm, anchor="lm")

    # 3. 300x250 Ad Banner Container
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
        ad_display = Image.new("RGB", (ad_w, ad_h), "#E5E7EB")
        ad_draw = ImageDraw.Draw(ad_display)
        ad_draw.text((ad_w // 2, ad_h // 2), "300 x 250 Ad Slot (6:5)\nUpload Image in Left Sidebar", fill="#666666", font=font_md, anchor="mm", align="center")

    if fix_airtel_cta and uploaded_ad is not None:
        ov_cta = ImageDraw.Draw(ad_display)
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

    # 4. Exact Flush AdChoices Tab
    if show_info_tag:
        ad_display = draw_native_ad_tag(ad_display, ad_w, ad_h, position=tag_position)

    mask = Image.new("L", (ad_w, ad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, ad_w, ad_h], radius=max(6, int(10 * s)), fill=255)
    img.paste(ad_display, (ad_x, ad_y), mask)

    # 5. Carousel Dots & Official "POWERED BY UPI" Logo
    dot_y = ad_y + ad_h + int(22 * s)
    start_dot_x = (W // 2) - int(55 * s)
    for i in range(8):
        if i == 0:
            draw.rounded_rectangle([start_dot_x, dot_y - int(4 * s), start_dot_x + int(22 * s), dot_y + int(4 * s)], radius=int(4 * s), fill=dot_active)
            start_dot_x += int(30 * s)
        else:
            draw.ellipse([start_dot_x, dot_y - int(4 * s), start_dot_x + int(8 * s), dot_y + int(4 * s)], fill=dot_inactive)
            start_dot_x += int(16 * s)

    img = draw_upi_logo(img, center_x=W // 2, top_y=dot_y + int(24 * s), scale_factor=s, is_dark=is_dark)
    draw = ImageDraw.Draw(img)

    # Bottom DONE Bar
    draw.rectangle([0, H - int(82 * s), W, H], fill=footer_bar_bg)
    draw.text((W // 2, H - int(44 * s)), "DONE" if is_dark else "Done", fill=purple_accent, font=font_md, anchor="mm")
    if is_dark:
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
