from fpdf import FPDF
import markdown
from bs4 import BeautifulSoup

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '美业门店接待标准话术与流程', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, subtitle, 0, 1, 'L')
        self.ln(3)

    def paragraph(self, text):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(3)

    def list_item(self, text):
        self.set_font('Arial', '', 10)
        self.cell(10, 5, '•', 0, 0)
        self.multi_cell(0, 5, text)

    def code_block(self, text):
        self.set_font('Courier', '', 9)
        self.multi_cell(0, 4, text)
        self.ln(3)

def markdown_to_pdf(markdown_file, pdf_file):
    # 读取markdown文件
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 转换为HTML
    html_content = markdown.markdown(md_content)
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 创建PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 处理HTML内容
    for element in soup:
        if element.name == 'h1':
            pdf.chapter_title(element.get_text())
        elif element.name == 'h2':
            pdf.chapter_subtitle(element.get_text())
        elif element.name == 'h3':
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, element.get_text(), 0, 1, 'L')
            pdf.ln(2)
        elif element.name == 'p':
            pdf.paragraph(element.get_text())
        elif element.name == 'ul':
            for li in element.find_all('li'):
                pdf.list_item(li.get_text())
            pdf.ln(3)
        elif element.name == 'ol':
            for i, li in enumerate(element.find_all('li'), 1):
                pdf.set_font('Arial', '', 10)
                pdf.cell(10, 5, f'{i}.', 0, 0)
                pdf.multi_cell(0, 5, li.get_text())
            pdf.ln(3)
    
    # 保存PDF
    pdf.output(pdf_file)

if __name__ == '__main__':
    markdown_to_pdf('门店接待标准话术与流程.md', '门店接待标准话术与流程.pdf')
    print('PDF生成完成！')