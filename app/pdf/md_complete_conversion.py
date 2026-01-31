import logging
import re
from markdown_it import MarkdownIt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    ListFlowable, ListItem, Image, Preformatted, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from app.enums.templates import PDFTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MDCompleteConverter:
    def __init__(self, template_choice: PDFTemplate = PDFTemplate.CLASSIC):
        self.md = MarkdownIt("commonmark", {"breaks": True, "html": True}).enable("table")
        self.width, self.height = A4
        self.margin = 50
        self.styles = self._get_styles(template_choice)
        self.story = []

    def _get_styles(self, template_choice: PDFTemplate):
        styles = getSampleStyleSheet()
        
        # Base Font mapping based on template
        # Simple mapping for now, can be expanded
        font_map = {
            PDFTemplate.CLASSIC: ("Times-Roman", "Times-Bold"),
            PDFTemplate.MODERN: ("Helvetica", "Helvetica-Bold"),
            PDFTemplate.MINIMAL: ("Courier", "Courier-Bold"),
        }
        
        body_font, head_font = font_map.get(template_choice, ("Helvetica", "Helvetica-Bold"))
        
        # Heading Styles
        styles.add(ParagraphStyle(name='MD_H1', parent=styles['Heading1'], fontName=head_font, fontSize=24, spaceAfter=16, spaceBefore=24, keepWithNext=True))
        styles.add(ParagraphStyle(name='MD_H2', parent=styles['Heading2'], fontName=head_font, fontSize=20, spaceAfter=12, spaceBefore=20, keepWithNext=True))
        styles.add(ParagraphStyle(name='MD_H3', parent=styles['Heading3'], fontName=head_font, fontSize=16, spaceAfter=10, spaceBefore=16, keepWithNext=True))
        styles.add(ParagraphStyle(name='MD_H4', parent=styles['Heading4'], fontName=head_font, fontSize=14, spaceAfter=8, spaceBefore=12, keepWithNext=True))
        
        # Body Style
        styles.add(ParagraphStyle(
            name='MD_Body', 
            fontName=body_font, 
            fontSize=11, 
            leading=14, 
            spaceAfter=10, 
            alignment=TA_LEFT # TA_JUSTIFY causes issues with simple spacing sometimes
        ))
        
        # Code/Preformatted Style
        styles.add(ParagraphStyle(
            name='MD_Code',
            fontName='Courier',
            fontSize=9,
            leading=12,
            backColor=colors.whitesmoke,
            borderColor=colors.lightgrey,
            borderWidth=1,
            borderPadding=10,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=15
        ))
        
        return styles

    def convert(self, text: str, output_path: str):
        tokens = self.md.parse(text)
        self._process_tokens(tokens)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        doc.build(self.story)
        logger.info(f"PDF generated at {output_path}")

    def _process_tokens(self, tokens):
        """
        Iterate through tokens and build the story.
        A state machine or recursive approach is often needed for nested lists/tables.
        Here we use a simplified iterative approach with buffers for complex blocks.
        """
        i = 0
        while i < len(tokens):
            token = tokens[i]
            type_ = token.type
            
            if type_ == 'heading_open':
                # heading_open -> inline -> heading_close
                level = token.tag  # h1, h2...
                content = tokens[i+1].content
                self._add_heading(level, content)
                i += 3 # skip inline and close
                continue
                
            elif type_ == 'paragraph_open':
                # paragraph_open -> inline -> paragraph_close
                # Check for if it's inside a list item? 
                # (Simple approach: just render text)
                if tokens[i+1].type == 'inline':
                    content = tokens[i+1].content
                    # Apply inline formatting (bold/italic) conversion if needed
                    # ReportLab supports basic XML like <b>, <i>. 
                    # MarkdownIt returns raw text or nested tokens for inline.
                    # For robust inline support, we would need to map children.
                    # As a quick fix, let's just use the rendered HTML or simple text.
                    # Actually, we can use the `children` of the inline token to reconstruct with tags.
                    formatted_text = self._render_inline(tokens[i+1])
                    self.story.append(Paragraph(formatted_text, self.styles['MD_Body']))
                i += 3
                continue
            
            elif type_ == 'bullet_list_open' or type_ == 'ordered_list_open':
                # Delegate to list handler which returns the consumed count
                consumed = self._handle_list(tokens, i)
                i += consumed
                continue
                
            elif type_ == 'table_open':
                consumed = self._handle_table(tokens, i)
                i += consumed
                continue
                
            elif type_ == 'fence' or type_ == 'code_block':
                content = token.content
                self.story.append(Preformatted(content, self.styles['MD_Code']))
                i += 1
                continue
            
            elif type_ == 'hr':
                self.story.append(Spacer(1, 12))
                # Add a line drawing if desired
                i += 1
                continue
                
            i += 1

    def _render_inline(self, inline_token):
        """
        Reconstructs text with ReportLab XML tags (<b>, <i>) from inline token children.
        """
        if not inline_token.children:
            return inline_token.content
            
        result = ""
        for child in inline_token.children:
            if child.type == 'text':
                result += child.content
            elif child.type == 'softbreak':
                result += " "
            elif child.type == 'strong_open':
                result += "<b>"
            elif child.type == 'strong_close':
                result += "</b>"
            elif child.type == 'em_open':
                result += "<i>"
            elif child.type == 'em_close':
                result += "</i>"
            elif child.type == 'code_inline':
                result += f"<font face='Courier' backColor='lightgrey'>{child.content}</font>"
            # Handle links, images if needed
            elif child.type == 'image':
                # For now just alt text; image handling is complex
                result += f" [Image: {child.content}] "
        
        return result

    def _add_heading(self, tag, text):
        style_name = 'MD_H1'
        if tag == 'h2': style_name = 'MD_H2'
        elif tag == 'h3': style_name = 'MD_H3'
        elif tag == 'h4': style_name = 'MD_H4'
        elif tag == 'h5': style_name = 'MD_Body' # Fallback
        
        self.story.append(Paragraph(text, self.styles[style_name]))

    def _handle_list(self, tokens, start_index):
        """
        Handles lists. Returns number of tokens consumed.
        """
        # Finds the matching close token
        current_type = tokens[start_index].type # bullet_list_open
        close_type = current_type.replace('open', 'close')
        
        # Collect list items
        list_items = []
        i = start_index + 1
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == close_type:
                # End of list
                break
                
            if token.type == 'list_item_open':
                # Parse list item content
                # For simplicity, we assume the immediate next is formatting or paragraph
                # Complex nested lists would require recursion here.
                # Let's verify what's inside.
                item_content = []
                j = i + 1
                while j < len(tokens) and tokens[j].type != 'list_item_close':
                    if tokens[j].type == 'inline':
                        text = self._render_inline(tokens[j])
                        item_content.append(Paragraph(text, self.styles['MD_Body']))
                    # Recursive: if we see another list_open, we should recurse. (Skipping for MVP stability)
                    j += 1
                
                if item_content:
                    list_items.append(ListItem(item_content))
                
                i = j # Move to close tag
            
            i += 1
            
        # Create ListFlowable
        # Determine bullet type
        bullet_type = '1' if 'ordered' in current_type else 'bullet'
        
        list_flowable = ListFlowable(
            list_items,
            bulletType=bullet_type,
            start='circle' if bullet_type == 'bullet' else None,
            bulletFontSize=6 if bullet_type == 'bullet' else 11,
            leftIndent=20,
            spaceAfter=10
        )
        self.story.append(list_flowable)
        
        return (i - start_index) + 1

    def _handle_table(self, tokens, start_index):
        """
        Handles tables. Consumes tokens until table_close.
        """
        # Gather rows and cells
        rows = []
        current_row = []
        
        i = start_index + 1
        while i < len(tokens):
            token = tokens[i]
            if token.type == 'table_close':
                break
            
            if token.type == 'tr_open':
                current_row = []
            elif token.type == 'tr_close':
                rows.append(current_row)
            elif token.type in ['th_open', 'td_open']:
                # Next is inline
                # If next is inline, grab it
                if tokens[i+1].type == 'inline':
                    text = self._render_inline(tokens[i+1])
                    # Wrap in Paragraph for text wrapping in cells
                    current_row.append(Paragraph(text, self.styles['MD_Body']))
                else:
                    current_row.append("")
            
            i += 1
            
        if rows:
            # Create Table
            col_count = len(rows[0])
            # Auto-calculate widths? Or equal split?
            avail_width = self.width - (2 * self.margin)
            col_width = avail_width / col_count if col_count > 0 else 0
            
            t = Table(rows, colWidths=[col_width] * col_count)
            t.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), # Header bg
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Header font
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            # Wrap table in KeepTogether to prevent splitting or orphaned headers
            self.story.append(KeepTogether([t, Spacer(1, 12)]))
            
        return (i - start_index) + 1


def convert_md_complete(text: str, output_path: str, template: PDFTemplate):
    converter = MDCompleteConverter(template)
    converter.convert(text, output_path)
