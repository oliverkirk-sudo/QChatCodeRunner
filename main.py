import base64
import logging
from markdown.extensions.tables import TableExtension
from markdown.extensions.admonition import AdmonitionExtension
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from mdx_math import MathExtension
from mirai import Image, Plain
from plugins.QChatCodeRunner.config.coderun_config import Config
from pkg.plugin.models import *
from pkg.plugin.host import EventContext, PluginHost
import markdown
import imgkit
from plugins.QChatCodeRunner.pkg.code_run import (
    code_runner,
    graph_generation,
    save_code,
    show_snippet,
)

_config = Config()


def resize_image(input_image_path, output_image_path, new_width):
    # 打开图像
    from PIL import Image

    image = Image.open(input_image_path)

    # 计算缩小后的新高度，以保持比例
    width, height = image.size
    if new_width and width > new_width:
        logging.debug("图片超过最大宽度，resize")
        new_height = int(height * (new_width / width))

        # 缩小图像
        resized_image = image.resize((new_width, new_height))

        # 保存缩小后的图像
        resized_image.save(output_image_path)


def markdown_to_image(md_text, width=None, height=None):
    try:
        logging.debug("将markdown文本转为图片")
        # 转换Markdown为HTML
        html = markdown.markdown(
            md_text,
            extensions=[
                TableExtension(),
                AdmonitionExtension(),
                MathExtension(enable_dollar_delimiter=True),
                FencedCodeExtension(),
                TocExtension(),
                CodeHiliteExtension(),
                ExtraExtension(),
            ],
        )
        html = (
            '<head><meta charset="UTF-8"></head>'
            + "<style>body {font-family: '微软雅黑', '宋体';}</style>"
            + html
        )
        options = {}
        if width:
            options["width"] = width
        if height:
            options["height"] = height

        # 配置imgkit，如果wkhtmltoimage不在你的PATH中，你需要提供路径
        imgkit_config = imgkit.config(
            wkhtmltoimage=_config.wkhtmltoimage_path
            if _config.wkhtmltoimage_path
            else None
        )

        # 转换HTML为图片
        image_file = "output.png"
        imgkit.from_string(html, image_file, config=imgkit_config, options=options)
        resize_image(image_file, image_file, width)

        # 将图片文件转换为Base64编码
        with open(image_file, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()
    except Exception:
        return md_text

    return base64_image


# 注册插件


@register(
    name="CodeRunner", description="根据你的输入运行代码创建图像", version="1.2", author="oliverkirk"
)
class HelloPlugin(Plugin):

    # 插件加载时触发
    # plugin_host (pkg.plugin.host.PluginHost) 提供了与主程序交互的一些方法，详细请查看其源码
    def __init__(self, plugin_host: PluginHost):
        pass

    @on(NormalMessageResponded)
    def process_message(self, event: EventContext, **kwargs):
        func_list = kwargs["funcs_called"]
        if any(
            [
                "CodeRunner-code_runner" in func_list,
                "CodeRunner-graph_generation" in func_list,
                "CodeRunner-show_snippet" in func_list,
            ]
        ):
            if _config.toMarkdownImg:
                b64 = markdown_to_image(
                    kwargs["response_text"],
                    width=_config.pic_width,
                    height=_config.pic_height,
                )
            else:
                b64 = kwargs["response_text"]
            if b64 == kwargs["response_text"]:
                event.add_return("reply", [Plain(text=b64)])
            else:
                event.add_return("reply", [Image(base64=b64)])
            event.prevent_default()
            event.prevent_postorder()
        pass

    @func(name="code_runner")
    def code_runner(code: str, language: str):
        """Call this function whenever there is code to run.
        - If the user asks you to run code, determine the code language and run it.
        - Supported languages have [c, c++, cpp, python, go lang, scala, c#, swift, r language, nodejs, java, javascript].
        - Markdown strictly follow the line break requirements.
        - Read the contents of the extra_response_instructions item and parse the result in the output.

        Args:
            code(str): Code text.
            language(str): Code language.

        Returns:
            json: Result and instruction.
        """

        return code_runner(code, language)

    @func(name="graph_generation")
    def graph_generation(chart_type: str, labels: str, datasets: list):
        """This function is called when a table or graph needs to be drawn.
        - Enter label and data with strict attention to their input form.
        - Read the contents of the extra_response_instructions item and parse the result in the output.
        - Markdown strictly follow the line break requirements.
        - Always return text in Markdown format, Image to Format output of ![title](url).

        Args:
            chart_type(str): Chart type,example: 'line'.
            labels(str): labels,example:'Monthly Sales Report'.
            datasets(list): List of dict for label and data,eg:[{"label": "label","data": []},...].

        Returns:
            json: Result and instruction.
        """

        return graph_generation(chart_type, labels, datasets)

    @func(name="save_code")
    def save_code(filename: str, code: str):
        """Call this function when user need to save code.
        - Enter filename with strict attention to their input form.
        - Markdown strictly follow the line break requirements.
        - Read the contents of the extra_response_instructions item and parse the result in the output.

        Args:
            filename(str): A file name with a suffix.
            code(str): Code text.

        Returns:
            json: Result and instruction.
        """

        return save_code(filename, code)

    @func(name="show_snippet")
    def show_snippet(
        code: str,
        language: str,
        title: str,
        theme: str,
        showNums: str = "true",
        opacity: int = 1,
        blurLines: str = "0",
    ):
        """Call this function when you need to show a snippet of code.
        - Enter label and data with strict attention to their input form.
        - Only return link, link to Format output of image tag : ![title](link).
        - Do not output code text and code blocks.
        - Always output an Image tag like ![title](link).
        - Read the contents of the extra_response_instructions item and parse the result in the output.

        Args:
            code(str): Code text.
            language(str): Code language:python,javascript,java,c,cpp,php,go,html,css,sql,kotlin.
            title(str): Code Title.
            theme(str): Available themes to pick from: dark-plus,dracula-soft,dracula,github-dark-dimmed,github-dark,github-light.
            showNums(str): Whether to show line numbers("true" or "false").
            opacity(int): Opacity(0-1).
            blurLines(str): Blur lines,eg:"6-9",default:"0".

        Returns:
            str: snippet_link.
        """
        return show_snippet(code, language, title, theme, showNums, opacity, blurLines)

    # 插件卸载时触发
    def __del__(self):
        pass
