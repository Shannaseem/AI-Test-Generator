import os
import re
import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml.shared import OxmlElement, qn

def clean_text(text):
    return re.sub(r'^\d+[\.\)]\s*', '', str(text)).strip()

def generate_word_file(academy_name, subject, class_name, test_date, time_allowed, syllabus, long_q_marks, ai_data, template_style="table"):
    doc = Document()
    
    # --- 1. SETUP FIRST SECTION ---
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
    
    mcq_total = len(mcqs) * 1  
    short_total = len(short_qs) * 2  
    try:
        long_q_val = sum([int(m.strip()) for m in long_q_marks.split('+')])
    except:
        long_q_val = 9
    long_total = len(long_qs) * long_q_val
    total_marks = mcq_total + short_total + long_total

    try:
        dt_obj = datetime.datetime.strptime(test_date, "%Y-%m-%d")
        formatted_date = dt_obj.strftime("%d %B %Y")
    except:
        formatted_date = test_date

    # --- 2. HEADER & INFO ROW ---
    header = section.header
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

    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_after = Pt(8) 
    info_tabs = p_info.paragraph_format.tab_stops
    info_tabs.add_tab_stop(Inches(2.6), WD_TAB_ALIGNMENT.LEFT)
    info_tabs.add_tab_stop(Inches(4.6), WD_TAB_ALIGNMENT.LEFT)
    info_tabs.add_tab_stop(Inches(7.67), WD_TAB_ALIGNMENT.RIGHT)

    r_name = p_info.add_run("Name: ")
    r_name.bold = True; r_name.font.size = Pt(14)
    p_info.add_run("________________\t")

    r_date = p_info.add_run("Date: ")
    r_date.bold = True; r_date.font.size = Pt(14)
    p_info.add_run(f"{formatted_date}\t")

    r_time = p_info.add_run("Time: ")
    r_time.bold = True; r_time.font.size = Pt(14)
    r_tval = p_info.add_run(f"{time_allowed}\t")
    r_tval.underline = True

    r_marks = p_info.add_run("Max Marks: ")
    r_marks.bold = True; r_marks.font.size = Pt(14)
    r_mval = p_info.add_run(f" {total_marks} ")
    r_mval.underline = True

    # ==========================================
    # LOGIC: TABLE FORMAT VS 2-COLUMN FORMAT (Only for MCQs)
    # ==========================================
    if template_style == "column":
        p_mcq_head = doc.add_paragraph()
        p_mcq_head.paragraph_format.space_after = Pt(6) # Heading ke baad thori si space
        run_l = p_mcq_head.add_run(f'Multiple Choice Questions ({mcq_total} Marks)')
        run_l.bold = True; run_l.font.size = Pt(14) 

        # Yahan se Q1. Choose correct answer nikal diya gaya hai

        section_2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
        sectPr2 = section_2._sectPr
        cols = sectPr2.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '360')

        for idx, m in enumerate(mcqs, start=1):
            p_q = doc.add_paragraph()
            p_q.paragraph_format.left_indent = Inches(0.2)
            p_q.paragraph_format.first_line_indent = Inches(-0.2)
            p_q.paragraph_format.space_after = Pt(0) 
            
            r_idx = p_q.add_run(f"{idx}. ")
            r_idx.bold = True
            r_q = p_q.add_run(clean_text(m.get('question', '')))
            r_q.bold = True 

            opts_dict = {'A': m.get('a', ''), 'B': m.get('b', ''), 'C': m.get('c', ''), 'D': m.get('d', '')}
            for key, val in opts_dict.items():
                p_opt = doc.add_paragraph()
                p_opt.paragraph_format.left_indent = Inches(0.4)
                p_opt.paragraph_format.space_after = Pt(0) 
                r_key = p_opt.add_run(f"{key}) ")
                r_key.bold = True
                p_opt.add_run(clean_text(val))
            
            doc.paragraphs[-1].paragraph_format.space_after = Pt(2) 

        # Back to 1 Column BEFORE Short Questions
        section_3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
        sectPr3 = section_3._sectPr
        cols3 = sectPr3.xpath('./w:cols')[0]
        cols3.set(qn('w:num'), '1')

    else:
        # --- TABLE FORMAT (MCQs Only) ---
        p_mcq_head = doc.add_paragraph()
        p_mcq_head.paragraph_format.space_after = Pt(6) # Heading ke baad thori si space
        run_l = p_mcq_head.add_run(f'Multiple Choice Questions ({mcq_total} Marks)')
        run_l.bold = True; run_l.font.size = Pt(14) 

        # Yahan se bhi Q1. Choose correct answer nikal diya gaya hai

        table = doc.add_table(rows=1, cols=6)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        widths = [Inches(0.4), Inches(3.87), Inches(0.85), Inches(0.85), Inches(0.85), Inches(0.85)]
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = width

        headers = ['No', 'Question', 'A', 'B', 'C', 'D']
        hdr_cells = table.rows[0].cells
        for i, text in enumerate(headers):
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            run.bold = True; run.font.size = Pt(13)

        for idx, m in enumerate(mcqs, start=1):
            row_cells = table.add_row().cells
            for i, width in enumerate(widths):
                row_cells[i].width = width
                row_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            
            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER 
            row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT   
            row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER 
            row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER 
            row_cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER 
            row_cells[5].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER 
            
            r_idx = row_cells[0].paragraphs[0].add_run(str(idx))
            r_idx.bold = True
            row_cells[1].text = clean_text(m.get('question', ''))
            row_cells[2].text = clean_text(m.get('a', ''))
            row_cells[3].text = clean_text(m.get('b', ''))
            row_cells[4].text = clean_text(m.get('c', ''))
            row_cells[5].text = clean_text(m.get('d', ''))

    # ==========================================
    # COMMON SHORT QUESTIONS
    # ==========================================
    short_heading = doc.add_paragraph()
    short_heading.paragraph_format.space_before = Pt(8) 
    r_sq = short_heading.add_run(f'Short Questions (2 x {len(short_qs)} = {short_total})')
    r_sq.bold = True; r_sq.font.size = Pt(14) 
    
    for idx, sq in enumerate(short_qs, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(2)
        
        r_num = p.add_run(f"{idx}. ")
        r_num.bold = True
        p.add_run(clean_text(sq.get('text', '')))

    # ==========================================
    # COMMON LONG QUESTIONS
    # ==========================================
    long_heading = doc.add_paragraph()
    long_heading.paragraph_format.space_before = Pt(8) 
    r_lq = long_heading.add_run(f'Long Question ({long_q_marks} x {len(long_qs)} = {long_total})')
    r_lq.bold = True; r_lq.font.size = Pt(14) 
    
    for idx, lq in enumerate(long_qs, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(4)
        
        r_num = p.add_run(f"{idx}. ")
        r_num.bold = True
        p.add_run(clean_text(lq.get('text', '')))

    output_path = "generated_test.docx"
    doc.save(output_path)
    return output_path