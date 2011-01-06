#coding: utf-8

"""
PRE-PROCESSORS
=============================================================================

Preprocessors work on source text before we start doing anything too
complicated. 
"""

import re
import markdown

HTML_PLACEHOLDER_PREFIX = markdown.STX+"wzxhzdk:"
HTML_PLACEHOLDER = HTML_PLACEHOLDER_PREFIX + "%d" + markdown.ETX

class Processor:
    def __init__(self, markdown_instance=None):
        if markdown_instance:
            # 在 __init__.py 里面我们这样初始化：
            # self.preprocessors["html_block"] = \
            #     preprocessors.HtmlBlockPreprocessor(self)
            # 故 Preprocessor 的子类可以有 self.markdown 对象
            self.markdown = markdown_instance


class Preprocessor (Processor):
    """
    Preprocessor 类的对象在 source text 被分割为行时执行动作。
    每个 Preprocessor 派生类对象都有一个 "run" 方法，需要一个
    含有 "source text" 中所有行内容的列表作为方法参数。

    Preprocessors must extend markdown.Preprocessor.
    """

    def run(self, lines):
        """
        每个派生类都需要重新定义 "run" 方法，其中 "lines" 参数是一个 list，
        该 list 的每个元素是 "source text" 的一行。
        """
        pass


class HtmlStash:
    """
    This class is used for stashing HTML objects that we extract
    in the beginning and replace with place-holders.
    此类是为了隐藏 HTML 块，以后可以替换。
    """

    def __init__ (self):
        """ Create a HtmlStash. """
        self.html_counter = 0 # for counting inline html segments
        self.rawHtmlBlocks=[]

    def store(self, html, safe=False):
        """
        存储一个原始html块，返回一个placeholder，以后可以据此替换

        Saves an HTML segment for later reinsertion.  Returns a
        placeholder string that needs to be inserted into the
        document.

        Keyword arguments:

        * html: an html segment
        * safe: label an html segment as safe for safemode

        Returns : a placeholder string

        """
        self.rawHtmlBlocks.append((html, safe))
        placeholder = HTML_PLACEHOLDER % self.html_counter
        self.html_counter += 1
        return placeholder

    def reset(self):
        self.html_counter = 0
        self.rawHtmlBlocks = []


class HtmlBlockPreprocessor(Preprocessor):
    """
    处理 html 块标签

    逐块处理（'\n\n'分割的即为一个 block），遇到 html 块时，用
    HtmlStash 对象转换保存。方便以后选择处理这个些对象。
    """

    # "</%s>" 形式的右标签很多： </pre> </h1>
    # "%>" 形式的右标签如： --> (html的注释)
    right_tag_patterns = ["</%s>", "%s>"]

    def _get_left_tag(self, block):
        '''返回形如 "<左标签>内容</右标签>" 里面的 "左标签"'''
        return block[1:].replace(">", " ", 1).split()[0].lower()

    def _get_right_tag(self, left_tag, block):
        '''返回右标签，及其在 block 里结尾的后一位位置'''
        for p in self.right_tag_patterns:
            tag = p % left_tag
            i = block.rfind(tag)
            if i > 2:
                # len(p)-2 意为 "</%s>" 和 "%s>" 中去掉 "%s" 的长度 2
                # len(left_tag) 即上面 "%s" 的被替换后的真实长度
                return tag.lstrip("<").rstrip(">"), i + len(p)-2 + len(left_tag)
        # 在当前 block 里未找到合法右标签，就返回下面两个值，以便继续查找
        # 第一个值和 left_tag 对比，可知非正确的 html 块标签对
        # 第二个值和 block 的程度对比，可知我们找到 block 尾部还没有找到
        # 比如我们在 <pre></pre> 标签对里面出现空行，程序就会处理到这里
        return block.rstrip()[-len(left_tag)-2:-1].lower(), len(block)

    def _equal_tags(self, left_tag, right_tag):
        ''' 判断 left_tag 和 right_tag 是否为正确的 html 标签对 '''
        if left_tag == 'div' or left_tag[0] in ['?', '@', '%']: # handle PHP, etc.
            return True
        if ("/" + left_tag) == right_tag:
            return True
        if (right_tag == "--" and left_tag == "--"):
            return True
        elif left_tag == right_tag[1:] \
            and right_tag[0] != "<":
            return True
        else:
            return False

    def _is_oneliner(self, tag):
        return (tag in ['hr', 'hr/'])

    def run(self, lines):
        text = "\n".join(lines)
        new_blocks = []
        text = text.split("\n\n")
        items = []
        left_tag = ''
        right_tag = ''
        in_tag = False # flag

        while text:
            block = text[0]
            text = text[1:]

            if not in_tag:

                if not block.startswith("<"):
                    new_blocks.append(block)
                    continue

                left_tag = self._get_left_tag(block)
                # data_index 是 right_tag 结束的地方
                right_tag, data_index = self._get_right_tag(left_tag, block)

                if block[1] == "!":
                    # 处理 "<!--html注释-->"
                    left_tag = "--"
                    right_tag, data_index = self._get_right_tag(left_tag, block)

                if data_index < len(block) and \
                        markdown.isBlockLevel(left_tag):
                    # 处理这样的 block： "<pre>内容</pre>其他"
                    # 这样 data_index 的值会小于 block 长度
                    # 需先将 pre 块后面的放回 text 列表，下次处理
                    text.insert(0, block[data_index:])
                    block = block[:data_index]

                if not markdown.isBlockLevel(left_tag) and \
                        block[1] not in ["!", "?", "@", "%"]:
                    # 既不是合法html块标签，又不是特殊标签
                    new_blocks.append(block)
                    continue

                if self._is_oneliner(left_tag):
                    # 处理 "<hr/>","<hr>" 这样的行分割符
                    new_blocks.append(block.strip())
                    continue

                if not block.rstrip().endswith(">") or not\
                        self._equal_tags(left_tag, right_tag) and\
                        markdown.isBlockLevel(left_tag) or\
                        left_tag == "--" :
                    # block 里的 html 标签对还未结束
                    items.append(block.strip())
                    in_tag = True
                    continue

                # 现在 block 里一定是 html 块处理
                new_blocks.append(self.markdown.htmlStash.store(block.strip()))

            else:
                # 进入跨 block 的 html 块标签
                right_tag, data_index = self._get_right_tag(left_tag, block)

                if data_index < len(block) and \
                        markdown.isBlockLevel(left_tag):
                    text.insert(0, block[data_index:])
                    block = block[:data_index]

                items.append(block.strip())

                if self._equal_tags(left_tag, right_tag):
                    # 如果左右标签成对，就准备结束 in_tag 情况
                    in_tag = False
                    new_blocks.append(self.markdown.htmlStash.store('\n\n'.join(items)))
                    items = []

        if items:
            # 如果 items 里面还有内容，说明有 html 块标签未配对，直接加上
            new_blocks.append(self.markdown.htmlStash.store('\n\n'.join(items)))
            new_blocks.append('\n')

        return "\n\n".join(new_blocks).split("\n")


class ReferencePreprocessor(Preprocessor):
    """ 从 text 中移除引用定义，以后在使用它
 
    引用类似： "[Google]:http://www.google.com"
    """

    # 下面的正则表示 Markdown 的引用应该怎样
    # a, 所在行必续以空白开头
    # b, 空白后面就是 "[id]"
    # c, "[id]"后紧接":"
    # d, ":"后可以有任意空白
    # e, 接着是其他内容
    RE = re.compile(r'^(\ ?\ ?\ ?)\[([^\]]*)\]:\s*([^ ]*)(.*)$', re.DOTALL)

    def run (self, lines):
        new_text = [];
        for line in lines:
            m = self.RE.match(line)
            if m:
                # 处理 "[Google]:http://www.google.com" 这样的块时
                id = m.group(2).strip().lower()
                t = m.group(4).strip()  # potential title
                if not t:
                    self.markdown.references[id] = (m.group(3), t)
                elif (len(t) >= 2
                      and (t[0] == t[-1] == "\""
                           or t[0] == t[-1] == "\'"
                           or (t[0] == "(" and t[-1] == ")") ) ):
                    self.markdown.references[id] = (m.group(3), t[1:-1])
                else:
                    new_text.append(line)
            else:
                new_text.append(line)

        return new_text #+ "\n"
