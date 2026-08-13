# 中文：读取 TXT 文档内容
# 函数名：load_txt
# file_path：TXT 文件路径
# 返回值：文件中的全部文本内容
def load_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text