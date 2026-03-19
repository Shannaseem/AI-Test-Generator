import os
import re
import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml.shared import OxmlElement, qn
from lxml import etree
import base64

def clean_text(text):
    return re.sub(r'^\d+[\.\)]\s*', '', str(text)).strip()

def set_rtl_paragraph(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

def add_urdu_run(paragraph, text, font_size=12, bold=False):
    run = paragraph.add_run(text)
    run.font.name = 'Jameel Noori Nastaleeq'
    run.font.size = Pt(font_size)
    run.bold = bold
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:cs'), 'Jameel Noori Nastaleeq')
    return run

def add_bilingual_paragraph(doc, eng_text, urdu_text, indent=0.25, first_indent=-0.25,
                              space_after=4, num_prefix="", font_size=12, bold=False):
    p_eng = doc.add_paragraph()
    p_eng.paragraph_format.left_indent = Inches(indent)
    p_eng.paragraph_format.first_line_indent = Inches(first_indent)
    p_eng.paragraph_format.space_after = Pt(0)
    if num_prefix:
        r_num = p_eng.add_run(num_prefix)
        r_num.bold = True
        r_num.font.size = Pt(font_size)
    eng_run = p_eng.add_run(eng_text)
    eng_run.font.size = Pt(font_size)
    eng_run.bold = bold

    p_urdu = doc.add_paragraph()
    p_urdu.paragraph_format.left_indent = Inches(indent)
    p_urdu.paragraph_format.space_after = Pt(space_after)
    set_rtl_paragraph(p_urdu)
    add_urdu_run(p_urdu, urdu_text, font_size=font_size + 2, bold=bold)
    return p_eng, p_urdu

def split_bilingual(text):
    if '||' in str(text):
        parts = str(text).split('||', 1)
        return parts[0].strip(), parts[1].strip()
    return str(text).strip(), None

# ==========================================
# ✅ WATERMARK FUNCTION
# ==========================================
def add_watermark(doc, watermark_text):
    """Har page ke background mein diagonal watermark add karta hai"""
    for section in doc.sections:
        header = section.header
        # Header paragraph use karte hain watermark ke liye
        if not header.paragraphs:
            header.add_paragraph()
        para = header.paragraphs[0]

        # Watermark XML manually banana parta hai
        # SDT (Structured Document Tag) nahi, seedha drawing use karenge
        r = para.add_run()
        r_elem = r._r

        # Drawing XML for watermark
        drawing_xml = f'''
        <w:pict xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                xmlns:v="urn:schemas-microsoft-com:vml"
                xmlns:o="urn:schemas-microsoft-com:office:office"
                xmlns:w10="urn:schemas-microsoft-com:office:word">
          <v:shape id="watermark" type="#_x0000_t136"
            style="position:absolute;margin-left:0;margin-top:0;width:550pt;height:200pt;
                   z-index:-251654144;mso-position-horizontal:center;
                   mso-position-horizontal-relative:margin;
                   mso-position-vertical:center;
                   mso-position-vertical-relative:margin;
                   rotation:315"
            fillcolor="#d0d0d0" stroked="f">
            <v:fill on="t" focussize="0,0"/>
            <v:path textpathok="t"/>
            <v:textpath on="t" fitshape="t"
              style="font-family:Arial;font-size:1pt;font-weight:bold"
              string="{watermark_text}"/>
            <o:lock v:ext="edit" rotation="t"/>
          </v:shape>
        </w:pict>
        '''
        pict_elem = etree.fromstring(drawing_xml)
        r_elem.append(pict_elem)


# ==========================================
# ✅ LOGO IN HEADER FUNCTION
# ==========================================
def add_logo_to_header(header, logo_bytes, logo_mime):
    """Header mein logo image insert karta hai"""
    import io
    from docx.shared import Inches

    # Logo ko temp file ki tarah treat karte hain
    logo_stream = io.BytesIO(logo_bytes)

    # Header ki pehli paragraph mein logo add karo
    # Pehle ek nayi paragraph banao logo ke liye (upar)
    logo_para = header.paragraphs[0]
    logo_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = logo_para.add_run()
    try:
        run.add_picture(logo_stream, height=Inches(0.7))
    except Exception as e:
        print(f"Logo add karne mein masla: {e}")


# ==========================================
# ✅ ANSWER KEY PAGE FUNCTION
# ==========================================
def add_answer_key_page(doc, mcqs, short_qs, long_qs, bilingual="no"):
    """Test ke baad alag Answer Key page add karta hai"""
    is_bilingual = (bilingual == "yes")

    # Page break se nayi page shuru
    doc.add_page_break()

    # Answer Key heading
    ak_heading = doc.add_paragraph()
    ak_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ak_heading.paragraph_format.space_after = Pt(16)
    r_ak = ak_heading.add_run("✦ ANSWER KEY ✦")
    r_ak.bold = True
    r_ak.font.size = Pt(20)
    r_ak.font.color.rgb = RGBColor(0x30, 0x50, 0x60)

    # Divider line
    div_para = doc.add_paragraph()
    div_para.paragraph_format.space_after = Pt(12)
    pPr = div_para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '305060')
    pBdr.append(bottom)
    pPr.append(pBdr)

    # ---- MCQ ANSWERS ----
    if mcqs:
        mcq_ak_head = doc.add_paragraph()
        mcq_ak_head.paragraph_format.space_after = Pt(8)
        r_mh = mcq_ak_head.add_run("MCQ Answers:")
        r_mh.bold = True
        r_mh.font.size = Pt(14)
        r_mh.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

        # MCQ answers table
        cols_count = 5
        rows_needed = (len(mcqs) + cols_count - 1) // cols_count

        ak_table = doc.add_table(rows=rows_needed + 1, cols=cols_count * 2)
        ak_table.style = 'Table Grid'
        ak_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Header row
        hdr = ak_table.rows[0].cells
        col_width = Inches(7.67 / (cols_count * 2))
        for ci in range(cols_count):
            hdr[ci * 2].width = Inches(0.5)
            hdr[ci * 2 + 1].width = Inches(1.0)
            p_no = hdr[ci * 2].paragraphs[0]
            p_no.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_no = p_no.add_run("No.")
            r_no.bold = True
            r_no.font.size = Pt(11)

            p_ans = hdr[ci * 2 + 1].paragraphs[0]
            p_ans.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_ans = p_ans.add_run("Answer")
            r_ans.bold = True
            r_ans.font.size = Pt(11)

        # Fill answers
        for idx, m in enumerate(mcqs):
            row_idx = idx // cols_count + 1
            col_idx = (idx % cols_count) * 2

            cell_no = ak_table.rows[row_idx].cells[col_idx]
            cell_no.width = Inches(0.5)
            cell_no.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_n = cell_no.paragraphs[0].add_run(str(idx + 1))
            r_n.bold = True
            r_n.font.size = Pt(11)

            cell_ans = ak_table.rows[row_idx].cells[col_idx + 1]
            cell_ans.width = Inches(1.0)
            cell_ans.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            answer_letter = str(m.get('answer', '')).strip().upper()
            if not answer_letter:
                answer_letter = "A"
            r_a = cell_ans.paragraphs[0].add_run(answer_letter)
            r_a.bold = True
            r_a.font.size = Pt(12)
            r_a.font.color.rgb = RGBColor(0x16, 0xA3, 0x4A)

    # ---- SHORT Q KEY POINTS ----
    if short_qs:
        sq_ak_head = doc.add_paragraph()
        sq_ak_head.paragraph_format.space_before = Pt(14)
        sq_ak_head.paragraph_format.space_after = Pt(8)
        r_sh = sq_ak_head.add_run("Short Questions — Key Points:")
        r_sh.bold = True
        r_sh.font.size = Pt(14)
        r_sh.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

        for idx, sq in enumerate(short_qs, start=1):
            sq_eng, sq_urdu = split_bilingual(sq.get('text', ''))
            p_sq = doc.add_paragraph()
            p_sq.paragraph_format.left_indent = Inches(0.25)
            p_sq.paragraph_format.first_line_indent = Inches(-0.25)
            p_sq.paragraph_format.space_after = Pt(3)

            r_num = p_sq.add_run(f"{idx}. ")
            r_num.bold = True
            r_num.font.size = Pt(11)

            r_text = p_sq.add_run(clean_text(sq_eng))
            r_text.font.size = Pt(11)

            # Hint line
            p_hint = doc.add_paragraph()
            p_hint.paragraph_format.left_indent = Inches(0.5)
            p_hint.paragraph_format.space_after = Pt(6)
            r_hint = p_hint.add_run("Hint: _______________________________________________")
            r_hint.font.size = Pt(10)
            r_hint.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
            r_hint.font.italic = True

            if is_bilingual and sq_urdu:
                p_urdu = doc.add_paragraph()
                p_urdu.paragraph_format.left_indent = Inches(0.25)
                p_urdu.paragraph_format.space_after = Pt(4)
                set_rtl_paragraph(p_urdu)
                add_urdu_run(p_urdu, clean_text(sq_urdu), font_size=12)

    # ---- LONG Q KEY POINTS ----
    if long_qs:
        lq_ak_head = doc.add_paragraph()
        lq_ak_head.paragraph_format.space_before = Pt(14)
        lq_ak_head.paragraph_format.space_after = Pt(8)
        r_lh = lq_ak_head.add_run("Long Questions — Key Points:")
        r_lh.bold = True
        r_lh.font.size = Pt(14)
        r_lh.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

        for idx, lq in enumerate(long_qs, start=1):
            lq_eng, lq_urdu = split_bilingual(lq.get('text', ''))
            p_lq = doc.add_paragraph()
            p_lq.paragraph_format.left_indent = Inches(0.25)
            p_lq.paragraph_format.first_line_indent = Inches(-0.25)
            p_lq.paragraph_format.space_after = Pt(3)

            r_num = p_lq.add_run(f"{idx}. ")
            r_num.bold = True
            r_num.font.size = Pt(12)

            r_text = p_lq.add_run(clean_text(lq_eng))
            r_text.font.size = Pt(12)

            # Key points lines
            for line_num in range(3):
                p_line = doc.add_paragraph()
                p_line.paragraph_format.left_indent = Inches(0.5)
                p_line.paragraph_format.space_after = Pt(2)
                r_line = p_line.add_run(
                    f"  {'Key Point' if line_num == 0 else '         '} {line_num + 1}: "
                    f"_______________________________________________"
                )
                r_line.font.size = Pt(10)
                r_line.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
                r_line.font.italic = True

            if is_bilingual and lq_urdu:
                p_urdu = doc.add_paragraph()
                p_urdu.paragraph_format.left_indent = Inches(0.25)
                p_urdu.paragraph_format.space_after = Pt(6)
                set_rtl_paragraph(p_urdu)
                add_urdu_run(p_urdu, clean_text(lq_urdu), font_size=13)


# ==========================================
# MAIN FUNCTION
# ==========================================
def generate_word_file(academy_name, subject, class_name, test_date, time_allowed,
                       syllabus, long_q_marks, ai_data, template_style,
                       short_total="8", short_attempt="5", short_groups="1",
                       long_total="3", long_attempt="2", bilingual="no",
                       generate_answer_key="no", add_watermark_flag="no",
                       logo_bytes=None, logo_mime=None):

    doc = Document()
    is_bilingual = (bilingual == "yes")

    try:
        short_groups_int = max(1, int(short_groups))
    except:
        short_groups_int = 1

    # --- PAGE SETUP ---
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.header_distance = Inches(0.2)
    section.footer_distance = Inches(0.0)
    section.top_margin = Inches(0.3)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.3)
    section.right_margin = Inches(0.3)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)

    mcqs = ai_data.get("mcqs", [])
    short_qs = ai_data.get("short_qs", [])
    long_qs = ai_data.get("long_qs", [])

    # --- MARKS CALCULATION ---
    mcq_marks = len(mcqs) * 1

    try:
        short_attempt_int = int(short_attempt)
    except:
        short_attempt_int = len(short_qs)

    short_marks_per_group = short_attempt_int * 2
    short_marks_total = short_marks_per_group * short_groups_int

    try:
        long_q_val = sum([int(m.strip()) for m in str(long_q_marks).split('+')])
    except:
        long_q_val = 9

    try:
        long_attempt_int = int(long_attempt)
    except:
        long_attempt_int = len(long_qs)

    long_marks = long_attempt_int * long_q_val
    total_marks = mcq_marks + short_marks_total + long_marks

    try:
        dt_obj = datetime.datetime.strptime(test_date, "%Y-%m-%d")
        formatted_date = dt_obj.strftime("%d %B %Y")
    except:
        formatted_date = test_date

    # --- HEADER ---
    header = section.header

    # ✅ Logo add karo agar diya gaya ho
    if logo_bytes and logo_mime:
        add_logo_to_header(header, logo_bytes, logo_mime)
        # Logo ke baad academy name
        p_title = header.add_paragraph()
    else:
        p_title = header.paragraphs[0]

    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run(academy_name.upper())
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(36)
    run_title.font.bold = True

    p_sub = header.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(4)
    tabs = p_sub.paragraph_format.tab_stops
    tabs.add_tab_stop(Inches(3.83), WD_TAB_ALIGNMENT.CENTER)
    tabs.add_tab_stop(Inches(7.67), WD_TAB_ALIGNMENT.RIGHT)
    run_sub = p_sub.add_run(f"{subject}\t{class_name}\t{syllabus}")
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(12)
    run_sub.font.bold = True

    pPr = p_sub._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '18')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '305060')
    pBdr.append(bottom)
    pPr.append(pBdr)

    # --- INFO ROW ---
    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_after = Pt(8)
    info_tabs = p_info.paragraph_format.tab_stops
    info_tabs.add_tab_stop(Inches(2.6), WD_TAB_ALIGNMENT.LEFT)
    info_tabs.add_tab_stop(Inches(4.6), WD_TAB_ALIGNMENT.LEFT)
    info_tabs.add_tab_stop(Inches(7.67), WD_TAB_ALIGNMENT.RIGHT)

    r_name = p_info.add_run("Name: ")
    r_name.bold = True
    r_name.font.size = Pt(14)
    p_info.add_run("________________\t")

    r_date = p_info.add_run("Date: ")
    r_date.bold = True
    r_date.font.size = Pt(14)
    p_info.add_run(f"{formatted_date}\t")

    r_time = p_info.add_run("Time: ")
    r_time.bold = True
    r_time.font.size = Pt(14)
    r_tval = p_info.add_run(f"{time_allowed}\t")
    r_tval.underline = True

    r_marks = p_info.add_run("Max Marks: ")
    r_marks.bold = True
    r_marks.font.size = Pt(14)
    r_mval = p_info.add_run(f" {total_marks} ")
    r_mval.underline = True

    # ==========================================
    # MCQs SECTION
    # ==========================================
    if template_style == "column":
        p_mcq_head = doc.add_paragraph()
        p_mcq_head.paragraph_format.space_after = Pt(6)
        run_l = p_mcq_head.add_run(f'Multiple Choice Questions ({mcq_marks} Marks)')
        run_l.bold = True
        run_l.font.size = Pt(14)

        section_2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
        sectPr2 = section_2._sectPr
        cols = sectPr2.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '360')

        for idx, m in enumerate(mcqs, start=1):
            q_eng, q_urdu = split_bilingual(m.get('question', ''))
            p_q = doc.add_paragraph()
            p_q.paragraph_format.left_indent = Inches(0.2)
            p_q.paragraph_format.first_line_indent = Inches(-0.2)
            p_q.paragraph_format.space_after = Pt(0)
            r_idx = p_q.add_run(f"{idx}. ")
            r_idx.bold = True
            r_q = p_q.add_run(clean_text(q_eng))
            r_q.bold = True

            if is_bilingual and q_urdu:
                p_urdu_q = doc.add_paragraph()
                p_urdu_q.paragraph_format.left_indent = Inches(0.2)
                p_urdu_q.paragraph_format.space_after = Pt(0)
                set_rtl_paragraph(p_urdu_q)
                add_urdu_run(p_urdu_q, clean_text(q_urdu), font_size=13, bold=True)

            opts = {'A': m.get('a',''), 'B': m.get('b',''), 'C': m.get('c',''), 'D': m.get('d','')}
            for key, val in opts.items():
                opt_eng, opt_urdu = split_bilingual(val)
                p_opt = doc.add_paragraph()
                p_opt.paragraph_format.left_indent = Inches(0.4)
                p_opt.paragraph_format.space_after = Pt(0)
                r_key = p_opt.add_run(f"{key}) ")
                r_key.bold = True
                p_opt.add_run(clean_text(opt_eng))
                if is_bilingual and opt_urdu:
                    p_opt_urdu = doc.add_paragraph()
                    p_opt_urdu.paragraph_format.left_indent = Inches(0.4)
                    p_opt_urdu.paragraph_format.space_after = Pt(0)
                    set_rtl_paragraph(p_opt_urdu)
                    add_urdu_run(p_opt_urdu, clean_text(opt_urdu), font_size=12)

            doc.paragraphs[-1].paragraph_format.space_after = Pt(2)

        section_3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
        sectPr3 = section_3._sectPr
        cols3 = sectPr3.xpath('./w:cols')[0]
        cols3.set(qn('w:num'), '1')

    else:
        p_mcq_head = doc.add_paragraph()
        p_mcq_head.paragraph_format.space_after = Pt(6)
        run_l = p_mcq_head.add_run(f'Multiple Choice Questions ({mcq_marks} Marks)')
        run_l.bold = True
        run_l.font.size = Pt(14)

        table = doc.add_table(rows=1, cols=6)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        widths = [Inches(0.4), Inches(3.87), Inches(0.85), Inches(0.85), Inches(0.85), Inches(0.85)]
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = width

        headers = ['No', 'Question', 'A', 'B', 'C', 'D']
        hdr_cells = table.rows[0].cells
        for i, text_h in enumerate(headers):
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text_h)
            run.bold = True
            run.font.size = Pt(13)

        for idx, m in enumerate(mcqs, start=1):
            q_eng, q_urdu = split_bilingual(m.get('question', ''))
            a_eng, a_urdu = split_bilingual(m.get('a', ''))
            b_eng, b_urdu = split_bilingual(m.get('b', ''))
            c_eng, c_urdu = split_bilingual(m.get('c', ''))
            d_eng, d_urdu = split_bilingual(m.get('d', ''))

            row_cells = table.add_row().cells
            for i, width in enumerate(widths):
                row_cells[i].width = width
                row_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
            for ci in range(2, 6):
                row_cells[ci].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            r_idx = row_cells[0].paragraphs[0].add_run(str(idx))
            r_idx.bold = True
            row_cells[1].paragraphs[0].add_run(clean_text(q_eng))
            if is_bilingual and q_urdu:
                p_u = row_cells[1].add_paragraph()
                set_rtl_paragraph(p_u)
                add_urdu_run(p_u, clean_text(q_urdu), font_size=13)

            option_pairs = [
                (row_cells[2], a_eng, a_urdu),
                (row_cells[3], b_eng, b_urdu),
                (row_cells[4], c_eng, c_urdu),
                (row_cells[5], d_eng, d_urdu),
            ]
            for cell, eng, urdu in option_pairs:
                cell.paragraphs[0].add_run(clean_text(eng))
                if is_bilingual and urdu:
                    p_u = cell.add_paragraph()
                    set_rtl_paragraph(p_u)
                    add_urdu_run(p_u, clean_text(urdu), font_size=12)

    # ==========================================
    # SHORT QUESTIONS — MULTIPLE GROUPS
    # ==========================================
    try:
        short_total_int = int(short_total)
    except:
        short_total_int = len(short_qs)

    for g in range(short_groups_int):
        group_start = g * short_total_int
        group_end = group_start + short_total_int
        group_qs = short_qs[group_start:group_end]
        if not group_qs:
            break

        q_number = g + 2
        short_heading = doc.add_paragraph()
        short_heading.paragraph_format.space_before = Pt(8)
        r_sq = short_heading.add_run(
            f'Q{q_number}. Short Questions (Attempt any {short_attempt} out of {short_total})'
        )
        r_sq.bold = True
        r_sq.font.size = Pt(14)
        tabs_sq = short_heading.paragraph_format.tab_stops
        tabs_sq.add_tab_stop(Inches(7.67), WD_TAB_ALIGNMENT.RIGHT)
        r_sq_marks = short_heading.add_run(f'\t{short_marks_per_group} Marks')
        r_sq_marks.bold = True

        for idx, sq in enumerate(group_qs, start=1):
            sq_eng, sq_urdu = split_bilingual(sq.get('text', ''))
            if is_bilingual and sq_urdu:
                add_bilingual_paragraph(
                    doc, clean_text(sq_eng), clean_text(sq_urdu),
                    indent=0.25, first_indent=-0.25,
                    space_after=4, num_prefix=f"{idx}. ", font_size=12
                )
            else:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                p.paragraph_format.first_line_indent = Inches(-0.25)
                p.paragraph_format.space_after = Pt(2)
                r_num = p.add_run(f"{idx}. ")
                r_num.bold = True
                p.add_run(clean_text(sq_eng))

    # ==========================================
    # LONG QUESTIONS
    # ==========================================
    long_heading = doc.add_paragraph()
    long_heading.paragraph_format.space_before = Pt(8)
    r_lq = long_heading.add_run(
        f'Long Questions (Attempt any {long_attempt} out of {long_total})'
    )
    r_lq.bold = True
    r_lq.font.size = Pt(14)
    tabs_lq = long_heading.paragraph_format.tab_stops
    tabs_lq.add_tab_stop(Inches(7.67), WD_TAB_ALIGNMENT.RIGHT)
    r_lq_marks = long_heading.add_run(f'\t{long_marks} Marks')
    r_lq_marks.bold = True

    for idx, lq in enumerate(long_qs, start=1):
        lq_eng, lq_urdu = split_bilingual(lq.get('text', ''))
        lq_eng = clean_text(lq_eng)
        eng_parts = lq_eng.split('\\n')

        for part_idx, part in enumerate(eng_parts):
            part = part.strip()
            if not part:
                continue
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.space_after = Pt(0 if part_idx < len(eng_parts) - 1 else 4)
            if part_idx == 0:
                r_num = p.add_run(f"{idx}. ")
                r_num.bold = True
            else:
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(0)
            p.add_run(part)

        if is_bilingual and lq_urdu:
            lq_urdu = clean_text(lq_urdu)
            urdu_parts = lq_urdu.split('\\n')
            for part_idx, part in enumerate(urdu_parts):
                part = part.strip()
                if not part:
                    continue
                p_u = doc.add_paragraph()
                p_u.paragraph_format.left_indent = Inches(0.25)
                p_u.paragraph_format.space_after = Pt(0 if part_idx < len(urdu_parts) - 1 else 6)
                set_rtl_paragraph(p_u)
                add_urdu_run(p_u, part, font_size=14)

    # ✅ WATERMARK
    if add_watermark_flag == "yes":
        add_watermark(doc, academy_name.upper())

    # ✅ ANSWER KEY PAGE
    if generate_answer_key == "yes":
        add_answer_key_page(doc, mcqs, short_qs, long_qs, bilingual)

    output_path = "generated_test.docx"
    doc.save(output_path)
    return output_path