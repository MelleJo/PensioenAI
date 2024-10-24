from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

class DocumentGenerator:
    def __init__(self):
        self.logo_path_veldhuis = "assets/veldhuis_logo.png"
        self.logo_path_jip = "assets/jip_logo.png"

    def create_report(self, report_type, content, company_name, date, advisor_name):
        """Creates a formatted report document"""
        doc = Document()
        
        # Set margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Cm(2.54)
            section.bottom_margin = Cm(2.54)
            section.left_margin = Cm(2.54)
            section.right_margin = Cm(2.54)

        # Add logos in header
        header_table = doc.add_table(rows=1, cols=2)
        header_table.autofit = False
        header_table.allow_autofit = False
        
        # Add logos (currently using placeholders)
        header_cell_1 = header_table.cell(0, 0)
        header_cell_1.width = Inches(3)
        p1 = header_cell_1.paragraphs[0]
        try:
            r1 = p1.add_run()
            r1.add_picture(self.logo_path_veldhuis, width=Inches(2))
        except:
            r1.add_text("VELDHUIS ADVIES")  # Fallback if logo not found

        header_cell_2 = header_table.cell(0, 1)
        header_cell_2.width = Inches(3)
        p2 = header_cell_2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        try:
            r2 = p2.add_run()
            r2.add_picture(self.logo_path_jip, width=Inches(1))
        except:
            r2.add_text("JIP")  # Fallback if logo not found

        doc.add_paragraph()  # Spacing

        # Add blue title section
        title = "Advies pensioenregeling conform de Wet Toekomst Pensioenen" if report_type == "advice" else "Inventarisatie overstap naar de Wet Toekomst Pensioenen"
        title_paragraph = doc.add_paragraph()
        title_run = title_paragraph.add_run(title)
        title_run.font.size = Pt(16)
        title_run.font.bold = True
        
        # Add blue background to paragraph
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1B4E9C"/>')
        title_paragraph._p.get_or_add_pPr().append(shading_elm)
        title_run.font.color.rgb = RGBColor(255, 255, 255)

        # Add company name in red
        company_paragraph = doc.add_paragraph()
        company_run = company_paragraph.add_run(company_name)
        company_run.font.color.rgb = RGBColor(255, 0, 0)
        company_run.font.size = Pt(14)
        company_run.font.bold = True

        # Add report type, date and advisor
        info_paragraph = doc.add_paragraph()
        info_paragraph.add_run("Adviesrapportage\n" if report_type == "advice" else "Analyserapportage\n")
        info_paragraph.add_run(f"{date}\n")
        info_paragraph.add_run(f"{advisor_name}\n")
        info_paragraph.add_run("Veldhuis Advies / JIP Financieel")

        # Add content
        doc.add_heading('Samenvatting', level=1)
        doc.add_paragraph(content)

        # Add footer
        footer = doc.sections[0].footer
        footer_text = footer.paragraphs[0]
        footer_text.text = "Financiële planning | Pensioenen | Hypotheken | Verzekeringen | Risicomanagement"
        footer_text.style = doc.styles['Footer']

        return doc

    def save_document(self, doc, filename):
        doc.save(filename)