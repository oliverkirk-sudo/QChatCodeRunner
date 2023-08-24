class Config:
    def __init__(self):
        self.domain = ""  # code_runner域名
        self.pic_width = 480
        self.pic_height = None
        self.toMarkdownImg = False
        self.proxy = None
        self.wkhtmltoimage_path = ""
        # self.proxy = {
        #     "http": "http://127.0.0.1:10809",
        #     "https": "http://127.0.0.1:10809",
        # }
