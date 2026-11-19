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
status_time = st.sidebar.text_input("Top Status Bar Time", value="11:40")
recipient_name = st.sidebar.text_input("Recipient Name", value="Ramana")
masked_phone = st.sidebar.text_input("Masked Number / UPI ID", value="+91 ••••• •1592")
amount = st.sidebar.text_input("Amount (without ₹ symbol)", value="1")
date_time_str = st.sidebar.text_input("Transaction Date & Time", value="05 October 2026 at 11:40 AM")

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

# --- VECTOR-DRAWN BOLD INDIAN RUPEE (₹) SYMBOL MATCHING REFERENCE ---
def draw_rupee_symbol(base_img, x, y, height, color=(28, 28, 30)):
    ss = 6
    w = max(10, int(height * 0.68))
    h = max(14, int(height))
    hw, hh = w * ss, h * ss

    sym = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sym)

    stroke = max(4, int(hh * 0.135))
    col = (*color, 255)

    # Top horizontal bar (full width)
    y_top = int(hh * 0.08)
    d.rectangle([0, y_top, hw - 1, y_top + stroke], fill=col)

    # Second horizontal bar (slightly shorter right end, matching official ₹ glyph)
    y_mid_bar = int(hh * 0.30)
    d.rectangle([0, y_mid_bar, int(hw * 0.88), y_mid_bar + stroke], fill=col)

    # Curved neck from top-left sweeping down-right and back to mid-left
    neck_x_start = int(hw * 0.18)
    neck_right = int(hw * 0.68)
    neck_bot = int(hh * 0.54)

    # Draw smooth arc for the right curve of ₹
    arc_box = [int(hw * 0.05), y_top, neck_right, neck_bot]
    d.arc(arc_box, start=275, end=85, fill=col, width=stroke)
    # Connect top bar into arc & arc back to left stem
    d.rectangle([neck_x_start, y_top, int(hw * 0.42), y_top + stroke], fill=col)
    d.rectangle([int(hw * 0.06), neck_bot - stroke, int(hw * 0.42), neck_bot], fill=col)

    # Diagonal leg sweeping from mid-left down to bottom-right
    y_leg_start = neck_bot - int(stroke * 0.45)
    y_leg_end = int(hh * 0.94)
    x_leg_start = int(hw * 0.06)
    x_leg_end = int(hw * 0.68)

    d.polygon([
        (x_leg_start, y_leg_start),
        (x_leg_start + int(stroke * 1.25), y_leg_start),
        (x_leg_end + int(stroke * 1.25), y_leg_end),
        (x_leg_end, y_leg_end)
    ], fill=col)

    final_sym = sym.resize((w, h), Image.Resampling.LANCZOS)
    base_rgba = base_img.convert("RGBA")
    base_rgba.paste(final_sym, (int(x), int(y)), final_sym)
    return base_rgba.convert("RGB"), w

# --- VECTOR-ACCURATE OFFICIAL "POWERED BY UPI" MARK ---
def draw_upi_logo(base_img, center_x, top_y, scale_factor):
    ss = 6
    w = max(62, int(78 * scale_factor))
    h = max(30, int(38 * scale_factor))
    hw, hh = w * ss, h * ss

    logo_hi = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(logo_hi)

    main_grey = (112, 115, 120, 255)
    sub_grey = (124, 127, 132, 255)

    f_pow = get_font(int(hh * 0.145), bold=True)
    d.text((hw * 0.45, hh * 0.13), "POWERED BY", fill=sub_grey, font=f_pow, anchor="mm")

    upi_layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    ud = ImageDraw.Draw(upi_layer)

    y1 = int(hh * 0.25)
    y2 = int(hh * 0.71)
    letter_h = y2 - y1
    stroke = max(4, int(letter_h * 0.23))
    rad = max(2, int(stroke * 0.35))

    ux1, ux2 = int(hw * 0.14), int(hw * 0.35)
    ud.rounded_rectangle([ux1, y1, ux1 + stroke, y2], radius=rad, fill=main_grey)
    ud.rounded_rectangle([ux2 - stroke, y1, ux2, y2], radius=rad, fill=main_grey)
    ud.rounded_rectangle([ux1, y2 - stroke, ux2, y2], radius=rad, fill=main_grey)

    px1, px2 = int(hw * 0.40), int(hw * 0.60)
    p_mid = y1 + int(letter_h * 0.56)
    ud.rounded_rectangle([px1, y1, px1 + stroke, y2], radius=rad, fill=main_grey)
    ud.rounded_rectangle([px1, y1, px2, y1 + stroke], radius=rad, fill=main_grey)
    ud.rounded_rectangle([px2 - stroke, y1, px2, p_mid], radius=rad, fill=main_grey)
    ud.rounded_rectangle([px1, p_mid - stroke, px2, p_mid], radius=rad, fill=main_grey)

    ix1 = int(hw * 0.65)
    ud.rounded_rectangle([ix1, y1, ix1 + stroke, y2], radius=rad, fill=main_grey)

    shear = 0.28
    upi_slanted = upi_layer.transform(
        (hw, hh),
        Image.Transform.AFFINE,
        (1, shear, -shear * (y1 + y2) * 0.5, 0, 1, 0),
        resample=Image.Resampling.BICUBIC
    )
    logo_hi = Image.alpha_composite(logo_hi, upi_slanted)
    d = ImageDraw.Draw(logo_hi)

    tri_base_x = ix1 + stroke + int(hw * 0.025)
    tri_w = int(hw * 0.125)
    top_shift = int(letter_h * shear * 0.5)
    bot_shift = -top_shift

    g_shift = int(tri_w * 0.38)
    d.polygon([
        (tri_base_x + g_shift + top_shift, y1),
        (tri_base_x + g_shift + tri_w, (y1 + y2) // 2),
        (tri_base_x + g_shift + bot_shift, y2)
    ], fill=(19, 136, 8, 255))

    d.polygon([
        (tri_base_x + top_shift, y1),
        (tri_base_x + tri_w, (y1 + y2) // 2),
        (tri_base_x + bot_shift, y2)
    ], fill=(244, 121, 32, 255))

    sub_layer = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sub_layer)
    f_sub = get_font(int(hh * 0.088), bold=True)
    sub_y = int(hh * 0.84)
    sd.text((hw * 0.50, sub_y), "UNIFIED PAYMENTS INTERFACE", fill=sub_grey, font=f_sub, anchor="mm")
    sub_slanted = sub_layer.transform(
        (hw, hh),
        Image.Transform.AFFINE,
        (1, 0.22, -0.22 * sub_y, 0, 1, 0),
        resample=Image.Resampling.BICUBIC
    )
    logo_hi = Image.alpha_composite(logo_hi, sub_slanted)

    final_logo = logo_hi.resize((w, h), Image.Resampling.LANCZOS)
    base_rgba = base_img.convert("RGBA")
    base_rgba.paste(final_logo, (int(center_x - w // 2), int(top_y)), final_logo)
    return base_rgba.convert("RGB")

# --- EXACT FLUSH GOOGLE/FLIPKART ADCHOICES CORNER TAB ---
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
    is_exact_300 = "1:1 Exact" in scale_mode

    if is_exact_300:
        ad_w, ad_h = 300, 250
        s = 300 / 504
        W, H = 322, 718
    else:
        ad_w, ad_h = 1008, 840
        s = 2.0
        W, H = 1080, 2410

    # Authentic PhonePe Light Theme Colors from reference
    bg_color = "#F4F5F7"
    header_green = "#137A2D"
    card_color = "#FFFFFF"
    primary_txt = "#1C1C1E"
    secondary_txt = "#66686E"
    divider_col = "#ECEEF1"
    icon_circle_bg = "#F2E7FE"
    purple_main = "#671AE5"
    purple_text = "#5B16D1"

    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    font_status = get_font(13 * s, bold=True)
    font_status_sm = get_font(8 * s, bold=True)
    font_header = get_font(21 * s, bold=True)
    font_date = get_font(16 * s, bold=False)
    font_name = get_font(23 * s, bold=True)
    font_phone = get_font(17 * s, bold=False)
    font_amt = get_font(31 * s, bold=True)
    font_split = get_font(14 * s, bold=True)
    font_action = get_font(15 * s, bold=False)
    font_done = get_font(19 * s, bold=True)

    # 1. Top White Android Status Bar
    status_h = int(34 * s)
    draw.rectangle([0, 0, W, status_h], fill="#FFFFFF")
    draw.text((int(18 * s), status_h // 2), status_time, fill="#55575C", font=font_status, anchor="lm")

    # Right status indicators (VoLTE, 5G, Signal, Battery)
    rx = W - int(18 * s)
    # Battery icon
    bat_w, bat_h = int(11 * s), int(15 * s)
    draw.rounded_rectangle([rx - bat_w, (status_h - bat_h) // 2, rx, (status_h + bat_h) // 2], radius=max(1, int(2 * s)), fill="#55575C")
    draw.rectangle([rx - int(8 * s), (status_h - bat_h) // 2 - int(2 * s), rx - int(3 * s), (status_h - bat_h) // 2], fill="#55575C")
    # Signal bars
    sig_x = rx - bat_w - int(18 * s)
    for b in range(4):
        bh = int((4 + b * 2.5) * s)
        bx = sig_x + int(b * 3.5 * s)
        by2 = (status_h + bat_h) // 2
        draw.rectangle([bx, by2 - bh, bx + max(1, int(2 * s)), by2], fill="#55575C")
    # 5G & VoLTE text
    draw.text((sig_x - int(6 * s), status_h // 2), "5G", fill="#55575C", font=font_status_sm, anchor="rm")
    draw.text((sig_x - int(24 * s), status_h // 2), "Vo\nLTE", fill="#55575C", font=get_font(6.5 * s, bold=True), anchor="rm", spacing=0)

    # 2. Top Green Header Section (extends behind upper portion of white card)
    header_top = status_h
    header_bot = int(285 * s)
    draw.rectangle([0, header_top, W, header_bot], fill=header_green)

    # Payment Successful & Date/Time
    draw.text((W // 2, int(84 * s)), "Payment Successful", fill="#FFFFFF", font=font_header, anchor="mm")
    draw.text((W // 2, int(116 * s)), date_time_str, fill="#E3F5E7", font=font_date, anchor="mm")

    # 3. White Transaction Card (Overlapping the green header)
    card_x1, card_y1 = int(14 * s), int(152 * s)
    card_x2, card_y2 = W - int(14 * s), int(448 * s)
    # Subtle card shadow
    draw.rounded_rectangle([card_x1, card_y1 + int(2 * s), card_x2, card_y2 + int(2 * s)], radius=int(16 * s), fill="#E2E4E8")
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=int(16 * s), fill=card_color)

    # Vibrant Purple Rounded-Square Avatar with Person Outline Icon
    av_x1, av_y1 = int(38 * s), int(184 * s)
    av_size = int(78 * s)
    draw.rounded_rectangle([av_x1, av_y1, av_x1 + av_size, av_y1 + av_size], radius=int(20 * s), fill=purple_main)

    # White Person Silhouette inside Purple Squircle
    acx = av_x1 + av_size // 2
    head_cy = av_y1 + int(av_size * 0.36)
    head_r = int(av_size * 0.145)
    lw = max(2, int(2.6 * s))
    draw.ellipse([acx - head_r, head_cy - head_r, acx + head_r, head_cy + head_r], outline="#FFFFFF", width=lw)
    sh_box = [
        acx - int(av_size * 0.25),
        av_y1 + int(av_size * 0.56),
        acx + int(av_size * 0.25),
        av_y1 + int(av_size * 0.94)
    ]
    draw.arc(sh_box, start=185, end=355, fill="#FFFFFF", width=lw)

    # Recipient Name & Masked Phone Number
    text_x = int(140 * s)
    draw.text((text_x, int(184 * s)), recipient_name, fill=primary_txt, font=font_name)
    draw.text((text_x, int(222 * s)), masked_phone, fill=secondary_txt, font=font_phone)

    # Exact Vector-Drawn Bold ₹ Symbol + Amount Digits
    amt_y = int(268 * s)
    rupee_h = int(23 * s)
    img, rupee_w = draw_rupee_symbol(img, x=text_x, y=amt_y + int(4 * s), height=rupee_h, color=(28, 28, 30))
    draw = ImageDraw.Draw(img)
    draw.text((text_x + rupee_w + int(3 * s), amt_y), amount, fill=primary_txt, font=font_amt)

    # "Split Expense" on Right
    split_x, split_y = card_x2 - int(22 * s), amt_y + int(18 * s)
    draw.text((split_x, split_y), "Split Expense", fill=purple_text, font=font_split, anchor="rm")

    # Card Divider Lines
    div_y = int(344 * s)
    draw.line([(card_x1, div_y), (card_x2, div_y)], fill=divider_col, width=max(1, int(1.5 * s)))
    draw.line([(W // 2, div_y + int(14 * s)), (W // 2, card_y2 - int(14 * s))], fill=divider_col, width=max(1, int(1.5 * s)))

    # Bottom Card Actions: "View Details" (with receipt icon) & "Share Receipt" (with 3-node share icon)
    b_y = int(396 * s)
    r_btn = int(24 * s)
    icon_w = max(1, int(1.8 * s))

    # Left: View Details
    b1_x = int(66 * s)
    draw.ellipse([b1_x - r_btn, b_y - r_btn, b1_x + r_btn, b_y + r_btn], fill=icon_circle_bg)
    # Document/Receipt icon inside circle
    doc_w, doc_h = int(13 * s), int(16 * s)
    draw.rounded_rectangle([b1_x - doc_w // 2, b_y - doc_h // 2, b1_x + doc_w // 2, b_y + doc_h // 2], radius=max(1, int(2 * s)), outline=purple_main, width=icon_w)
    for line_off in (-int(3 * s), 0, int(3 * s)):
        draw.line([(b1_x - int(3 * s), b_y + line_off), (b1_x + int(3 * s), b_y + line_off)], fill=purple_main, width=max(1, int(1.4 * s)))
    draw.text((b1_x + int(34 * s), b_y), "View Details", fill=primary_txt, font=font_action, anchor="lm")

    # Right: Share Receipt
    b2_x = W // 2 + int(42 * s)
    draw.ellipse([b2_x - r_btn, b_y - r_btn, b2_x + r_btn, b_y + r_btn], fill=icon_circle_bg)
    # 3-node share icon inside circle
    nr = max(2, int(2.4 * s))
    p_left = (b2_x - int(5 * s), b_y)
    p_top = (b2_x + int(4 * s), b_y - int(5 * s))
    p_bot = (b2_x + int(4 * s), b_y + int(5 * s))
    draw.line([p_left, p_top], fill=purple_main, width=icon_w)
    draw.line([p_left, p_bot], fill=purple_main, width=icon_w)
    for pt in (p_left, p_top, p_bot):
        draw.ellipse([pt[0] - nr, pt[1] - nr, pt[0] + nr, pt[1] + nr], fill=purple_main)
    draw.text((b2_x + int(34 * s), b_y), "Share Receipt", fill=primary_txt, font=font_action, anchor="lm")

    # 4. 300x250 Ad Banner Container
    ad_x = (W - ad_w) // 2
    ad_y = int(472 * s)

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
        ad_draw.text((ad_w // 2, ad_h // 2), "300 x 250 Ad Slot (6:5)\nUpload Image in Left Sidebar", fill="#666666", font=font_header, anchor="mm", align="center")

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

    # 5. Exact Flush AdChoices Tab
    if show_info_tag:
        ad_display = draw_native_ad_tag(ad_display, ad_w, ad_h, position=tag_position)

    mask = Image.new("L", (ad_w, ad_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, ad_w, ad_h], radius=max(6, int(12 * s)), fill=255)
    img.paste(ad_display, (ad_x, ad_y), mask)

    # 6. Carousel Dots & Vector-Accurate Official "POWERED BY UPI" Logo
    dot_y = ad_y + ad_h + int(22 * s)
    start_dot_x = (W // 2) - int(55 * s)
    for i in range(8):
        if i == 0:
            draw.rounded_rectangle([start_dot_x, dot_y - int(4 * s), start_dot_x + int(22 * s), dot_y + int(4 * s)], radius=int(4 * s), fill="#3F3F46")
            start_dot_x += int(30 * s)
        else:
            draw.ellipse([start_dot_x, dot_y - int(4 * s), start_dot_x + int(8 * s), dot_y + int(4 * s)], fill="#C8CBD0")
            start_dot_x += int(16 * s)

    img = draw_upi_logo(img, center_x=W // 2, top_y=dot_y + int(24 * s), scale_factor=s)
    draw = ImageDraw.Draw(img)

    # 7. Bottom White "Done" Bar & Android Navigation Bar
    done_top = H - int(96 * s)
    nav_top = H - int(42 * s)
    draw.rectangle([0, done_top, W, nav_top], fill="#FFFFFF")
    draw.text((W // 2, (done_top + nav_top) // 2), "Done", fill=purple_text, font=font_done, anchor="mm")

    # Android
