# class PDF(FPDF):
# def header(self):
#     # Select Arial bold 15
#     self.set_font('Arial', 'I', 8)
#     # Move to the right
#     self.cell(80)
#     # Framed title
#     self.cell(30, 5, 'Test Terminal', 0, 0, 'C')
#     # Line break
#     self.ln(20)

# def footer(self):
#     self.set_y(-15)
#     self.set_font('Arial', 'I', 8)
#     pdf.set_text_color(*[0]*3)
#     self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

from fpdf import FPDF

page_width = 210
page_height = 297

page_left_margin = 10
page_right_margin = 10
page_top_margin = 10
page_bottom_margin = 10

page_x_area = page_width - page_left_margin - page_right_margin
page_y_area = page_height - page_top_margin - page_bottom_margin

pdf = FPDF(orientation='P', unit='mm', format='A4')

pdf.set_author("Author Test Terminal")
pdf.set_creator("Creator Test Terminal")
pdf.set_subject("Exam Results")

pdf.add_page(orientation='P', format='A4', same=False)
pdf.set_left_margin(margin=10)
pdf.set_right_margin(margin=10)

pdf.alias_nb_pages()

# Draw border
pdf.line(10, 10, 200, 10)
pdf.line(10, 277, 200, 277)
pdf.line(10, 10, 10, 277)
pdf.line(200, 10, 200, 277)

# Title
pdf.set_font('Arial', 'B', 12)  # Italics I, underline U
color = [0, 0, 0]
pdf.set_text_color(*color)
pdf.cell(w=page_x_area, h=20, txt='Exam Results', border=1, align='C')

# Stats

# Export the pdf to file
#  F: Save local, I or D: standard out
pdf.output(name='tuto1.pdf', dest='F')

# Close
pdf.close()

# pdf.add_font(family: str, style = '', fname = '', uni = False)
# pdf.cell(w, h = 0, txt = '', border = 0, ln = 0, align = '', fill = False, link = '')
# pdf.multi_cell(w: float, h: float, txt: str, border = 0, align: str = 'J', fill: bool = False)
# pdf.line(x1, y1, x2, y2)
# pdf.dashed_line(x1, y1, x2, y2, dash_length = 1, space_length = 1)

# pdf.load_resource(reason: string, filename: string)
# pdf.image(name, x = None, y = None, w = 0, h = 0, type = '', link = '')
