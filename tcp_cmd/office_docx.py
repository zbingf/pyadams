"""
    
    基于python-docx
    生成 docx文档
    
    部分基于 win32com 操作
"""
import win32com.client as win32


import os.path
import logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('office_docx')


# ===========================================================================
# win32com 操作
# ===========================================================================

# 合并操作 - 包含图片
def combind_words_win32(main_path, file_paths):
    """
        调用 win32com 模块
    """

    logging.info('combind_words_win32 win32com调用')

    main_path = os.path.abspath(main_path)

    file_paths.reverse() # 顺序调反

    #打开word软件
    word = win32.gencache.EnsureDispatch('Word.Application')
    #非可视化运行
    word.Visible = False
    file_paths[0] = os.path.abspath(file_paths[0])
    output = word.Documents.Open(file_paths[0])

    for path in file_paths[1:]:
        path = os.path.abspath(path)
        output.Application.Selection.Range.InsertFile(path)#拼接文档

    #获取合并后文档的内容
    # doc = output.Range(output.Content.Start, output.Content.End)
    # doc.Font.Name = "黑体"  #设置字体

    output.SaveAs(main_path)
    output.Close()

    return None


# docx 转 PDF 
def doc2pdf(doc_path, pdf_path=None):
    """
        调用 win32com 模块
    """
    logging.info('doc2pdf win32com调用')

    doc_path = os.path.abspath(doc_path)

    
    #打开word软件
    try:
        word = win32.Dispatch("Word.Application")
    except:
        word = win32.gencache.EnsureDispatch('Word.Application')
    #非可视化运行
    word.Visible = False
    output = word.Documents.Open(doc_path)
    if pdf_path==None:
        pdf_path = doc_path[:-4]+'pdf'

    pdf_path = os.path.abspath(pdf_path)
    output.SaveAs(pdf_path, FileFormat = 17)

    output.Close()

    return pdf_path


# 文档编辑
class WordEdit:
    """
        指定word文件内柔替换
        wps适用
        $test$ 文字替换
        #TEST# 图片替换
    """
    def __init__(self,word_path):
        
        logging.info('WordEdit win32com调用')

        word_path = os.path.abspath(word_path)

        word = win32.Dispatch("Word.Application")
        word.Visible = 0
        word.DisplayAlerts = 0
        document = word.Documents.Open(word_path)
        content = document.Content
        selection = word.Selection

        self.file_path = word_path
        self.word = word
        self.document = document
        self.content = content
        self.selection = selection

    def replace_edit(self,oldList,newList): # 指定替换 文字及图片
        """
            $ 开头为文字替换
            # 开头为图片替换
        """

        for oldStr,newStr in zip(oldList,newList):
            if oldStr[0] == "$":
                self.replace_str(oldStr,newStr)

            elif oldStr[0] == "#":
                self.add_picture(oldStr,newStr)

    def save(self,targetAdr=None): # 另存为
        """ 保存 word"""
        if targetAdr!=None:
            targetAdr = os.path.abspath(targetAdr)
            self.document.SaveAs2(targetAdr,12,False,"",True,"",False,False,False,False,False,15)
        else:
            self.document.SaveAs2(self.file_path,12,False,"",True,"",False,False,False,False,False,15)

        logging.info(f'保存word:{self.file_path}')

    def close(self):
        """ 关闭 word"""
        self.document.Close()
        logging.info(f'关闭word:{self.file_path}')

    def replace_str(self, oldStr, newStr):
        """
            文字替换形式添加
        """
        selection = self.selection

        selection.Find.ClearFormatting()
        selection.Find.Replacement.ClearFormatting()
        selection.Find.Execute(oldStr,False,False,False,False,False,True,1,True,newStr,2)

        logging.info(f'文字替换:{oldStr} --> {newStr}')

    def add_picture(self, oldStr, fig_path):
        """
            图片添加
            以文字替换形式添加
        """
        selection = self.selection
        fig_path = os.path.abspath(fig_path)
        selection.Find.ClearFormatting()
        selection.Find.Replacement.ClearFormatting()
        while True:
            selection.start = 0
            if (selection.Find.Execute(oldStr,False,False,False,False,False,True,1,True,"none",0)):
                selection.Text = ""
                selection.InlineShapes.AddPicture(fig_path,False,True)
            else:
                break

        logging.info(f'图片替换:{oldStr} --> {fig_path}')


