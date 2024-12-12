from pydbml import PyDBML
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph

def generate_pdf(file_name, tables):
    pdf_file = "output.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    y = height - 50  # Start from the top

    # Register the regular and bold Arial fonts
    pdfmetrics.registerFont(TTFont('ArialUnicodeMS', r'C:\Windows\Fonts\arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialUnicodeMS-Bold', r'C:\Windows\Fonts\arialbd.ttf'))

    # Set the font to Arial Unicode MS for better diacritic support
    c.setFont('ArialUnicodeMS', 12)  # Use Arial Unicode MS

    # Create the title on the first page
    c.setFont("ArialUnicodeMS-Bold", 24)  # Large bold font for the title
    c.drawString(50, height - 100, "Modul Sales")
    y -= 50  # Move down after the title

    # Add a horizontal line under the title
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, y, width - 50, y)  # Draw the line
    y -= 20  # Space between the line and the next content

    # Define a style for Paragraphs with word wrapping
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_normal.fontName = 'ArialUnicodeMS'
    style_normal.fontSize = 12
    style_normal.leading = 14
    style_normal.wordWrap = 'CJK'  # For better word wrapping in different languages

    for table in tables:
        # Start a new page for each table
        c.showPage()
        y = height - 50  # Reset the Y position for the new page

        # Write the table name
        c.setFont("ArialUnicodeMS-Bold", 14)
        c.drawString(50, y, f"Table Name: {table.name}")
        y -= 20

        # Write the columns
        c.setFont("ArialUnicodeMS", 12)
        c.drawString(70, y, "Columns:")
        y -= 20

        color_switch = True  # Flag to alternate between colors (True for blue, False for red)

        for column in table.columns:
            if y < 50:  # Check if there's space for the column
                c.showPage()  # Create a new page if necessary
                c.setFont("ArialUnicodeMS", 12)
                y = height - 50

            # Prepare the column text and add a line break before long lines
            col_text = f"- {column.name} ({column.type}) - {column.note}"

            # Check if the text is too long and needs to be split
            max_line_length = 80  # Define a max line length for wrapping
            lines = []
            if len(col_text) > max_line_length:
                # Split the text into lines at spaces
                words = col_text.split(' ')
                line = ""
                for word in words:
                    if len(line + word) + 1 <= max_line_length:
                        line += " " + word if line else word
                    else:
                        lines.append(line)
                        line = word
                if line:
                    lines.append(line)
            else:
                lines = [col_text]

            # Create a list of lines where continuation lines are indented
            lines_with_indent = [lines[0]]  # First line is unchanged
            for line in lines[1:]:
                lines_with_indent.append("     " + line)  # Add indentation (5 spaces) for each subsequent line

            # Set the text color for the current row (alternating blue and red)
            text_color = colors.blue if color_switch else colors.red
            color_switch = not color_switch  # Toggle the color for the next row

            # Set the text color
            c.setFillColor(text_color)

            # Create a Paragraph for each line with word wrapping
            for line in lines_with_indent:
                paragraph = Paragraph(line, style_normal)
                paragraph_width = width - 100  # Leave some margin from the left (50px) and the right (50px)

                # Wrap the paragraph text to get the height
                paragraph.wrap(paragraph_width, 1000)  # 1000 is an arbitrary large height to just wrap the text

                paragraph_height = paragraph.height  # Get the height from the wrap

                # Draw the paragraph and update the Y position
                if y - paragraph_height < 50:  # Check if there's enough space for the paragraph
                    c.showPage()  # Create a new page if necessary
                    c.setFont("ArialUnicodeMS", 12)
                    y = height - 50

                # Draw the paragraph on the PDF canvas, with a left indentation (90 pixels)
                paragraph.drawOn(c, 90, y)  # Ensure the left margin is set by 90 px

                # Update the Y position after drawing the paragraph
                y -= paragraph_height
                y -= 10  # Extra space between columns

        y -= 10  # Extra space between tables

    c.save()
    print(f"PDF saved as {pdf_file}")

# Read the DBML file and parse tables
with open('erp_sales.dbml', 'r', encoding='utf-8') as f:
    dbml_content = f.read()

db = PyDBML(dbml_content)
generate_pdf("output.pdf", db.tables)
