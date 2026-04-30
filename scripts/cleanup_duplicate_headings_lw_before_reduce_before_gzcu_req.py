from pathlib import Path

from docx import Document


DOC_PATH = Path(r"D:\beauty\lw_before_reduce_before_gzcu_req.docx")


def delete_paragraph(paragraph):
    p = paragraph._element
    parent = p.getparent()
    if parent is not None:
        parent.remove(p)
    paragraph._p = paragraph._element = None


def main():
    doc = Document(str(DOC_PATH))
    paras = doc.paragraphs
    # Remove stale headings left from renumbering passes.
    stale_indices = [148, 152, 156, 160, 164, 168, 174, 179, 203, 220, 254, 259, 264]
    for idx in sorted(stale_indices, reverse=True):
        delete_paragraph(paras[idx])
    doc.save(str(DOC_PATH))


if __name__ == "__main__":
    main()
