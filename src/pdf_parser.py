import fitz  # PyMuPDF 在代码里的真实名字叫 fitz

def extract_text_from_pdf(file_bytes):
    """
    接收用户上传的 PDF 字节流，将其翻译成纯文本
    """
    text = ""
    try:
        # 直接读取内存里的文件流，不产生本地垃圾文件
        doc = fitz.open("pdf", file_bytes)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"PDF 解析失败，错误信息: {e}"