from pathlib import Path

from docx import Document


DOC_PATH = Path(r"D:\beauty\lw_before_reduce_before_gzcu_req.docx")


def main():
    doc = Document(str(DOC_PATH))
    paras = doc.paragraphs
    target = paras[242]  # 5.7 本章小结
    moving = paras[244:254]  # 5.6 block
    for para in moving:
        target._p.addprevious(para._p)
    doc.save(str(DOC_PATH))


if __name__ == "__main__":
    main()
