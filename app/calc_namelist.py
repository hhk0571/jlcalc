#! /usr/bin/env python
# coding: utf-8
from __future__ import print_function
import argparse
import re
import sys
import textwrap
import numpy as np
import functools


class OrdersParser(object):
    def __init__(self, price, classes=None, file=sys.stdout):
        self.price = price
        self.classes = classes
        self.file = file
        self.fprint = functools.partial(print, file=file)

    def load_list(self, orders_txt):
        '''load names list from raw string
        parameters:
        ----------
        orders_txt: raw string with descriptions and names list

        return:
        -------
        names_list: a list with orginal index, name, and amount
        descr:      description text
        '''
        names_list = [x.strip() for x in orders_txt.splitlines() if x.strip()]
        remove_list=[]
        descr_list=[]
        for line in names_list:
            if '@所有人' in line:
                remove_list.append(line)
            elif re.match(r'^\s*\d+.*$', line):
                break
            else:
                descr_list.append(line)
                remove_list.append(line)
        for x in remove_list:
            names_list.remove(x)
        descr = '\n'.join(descr_list)
        return names_list, descr


    def strip_leading_number(self, line):
        '''strip leading number and punctuation of each element in list
        原始信息中的行首序号没啥用处, 只是在接龙时方便查看有几人接龙而已.
        e.g. '20、刘小西1斤' --> '刘小西1斤'
        '''
        return re.sub(r'^\s*\d+[\s\.,;:、，；：。]*', '', line)


    def single_class_parse(self, names_list, price):
        '''解析单类别接龙列表中的姓名和数量
        例如: '20、刘小西1斤' --> '刘小西' 1
        参数:
        ------
        names_list:     去掉行首序号和标点之后的列表
        price:          物品单价

        返回值:
        ------
        orders:     订单列表
        nok_list:   解析错误列表, 用于提示, 然后人工校对
        '''
        header_labels = ['原始信息', '姓名', '数量']
        orders=[]
        nok_list=[]
        for orig_line in names_list:
            line = self.strip_leading_number(orig_line)
            numbers = re.findall(r'\d+', line)
            if numbers:
                amount = numbers[-1]
                name = line[:line.rindex(amount)].strip()
                orders.append([orig_line, name, int(amount)])
            else:
                nok_list.append(orig_line)
        return orders, nok_list, header_labels


    def rfind_class(self, line, number, class_num):
        '''从右向左, 按类别在数字右侧的原则来读取类别的数量
        e.g. '20、张三2成人1儿童' --> '张三' 成人:2 儿童:1
        参数:
        ------
        line:       去掉行首序号和标点之后的行
        numbers:    line中的所有数字
        class_num:  字典{类别A:数量, 类别B:数量, ...}

        返回值:
        ------
        是否找到:   True: 找到, False: 未找到
        line:      去掉已解析的类别数量之后剩下的字符串, 若未找到类别数量, 则为None    
        '''
        for labels in self.classes:
            cls_name = labels[0]
            for label in labels:
                if label in line[line.rindex(number):]:
                    class_num[cls_name] = int(number)
                    return True, line[:line.rindex(number)]
        return False, None

    def lfind_class(self, line, number, class_num):
        '''从右向左, 按类别在数字左侧的原则来读取类别的数量
        e.g. '20、张三成人2儿童1' --> '张三' 成人:2 儿童:1
        参数:
        ------
        line:       去掉行首序号和标点之后的行
        numbers:    line中的所有数字
        class_num:  字典{类别A:数量, 类别B:数量, ...}

        返回值:
        ------
        是否找到:   True: 找到, False: 未找到
        line:      去掉已解析的类别数量之后剩下的字符串, 若未找到类别数量, 则为None    
        '''
        for labels in self.classes:
            cls_name = labels[0]
            for label in labels:
                m = re.match(r'^.*(%s)\s*(%s)[\s,\.;，、；。]*$' % (label, number), line)
                if m:
                    class_num[cls_name] = int(number)
                    # print('L: group(1):', m.group(1), ':group(2):', m.group(2))
                    return True, line[:line.rindex(m.group(1))]
        return False, None


    def parse_classes(self, line, numbers):
        '''从右往左读取行中所有类别的数量
        参数:
        ------
        line:       去掉行首序号和标点之后的行
        numbers:    line中的所有数字

        返回值:
        ------
        name:       从line中解析出来的姓名
        class_num:  字典{类别A:数量, 类别B:数量, ...}
        '''
        class_num={}
        # print(line)
        for num in numbers[::-1]:
            # print('R: line:', line)
            ok, ret_line = self.rfind_class(line, num, class_num)
            # print('R: ret: ', ret_line)
            if ok:
                line = ret_line
            else:
                # print('L: line:', line)
                ok, ret_line= self.lfind_class(line, num, class_num)
                # print('L: ret: ', ret_line)
                if ok:
                    line = ret_line
        name = line.strip()
        # print('>>>\t', name, class_num)
        return name, class_num

    def multi_class_parse(self, names_list, price):
        '''解析多类别接龙列表中的姓名以及各个类别的数量
        例如: 
            类别分为两类: 成人, 儿童
            成人标签可以包含: 成人, 大人, 大, ...
            儿童标签可以包含: 儿童, 小孩, 小, ...
        解析示例:
            '20、张三2大1小' --> '张三' 成人:2 儿童:1
            '21、李四大2小1' --> '李四' 成人:2 儿童:1
            '22、王五成人2儿童1' --> '王五' 成人:2 儿童:1
            '23、王五儿童1' --> '王五' 儿童:1

        参数:
        ------
        names_list:     去掉行首序号和标点之后的列表
        price:          物品单价

        返回值:
        ------
        orders:     订单列表
        nok_list:   解析错误列表, 用于提示, 然后人工校对
        '''
        cls_labels = [x[0] for x in self.classes]
        header_labels = ['原始信息', '姓名'] + cls_labels
        orders=[]
        nok_list=[]
        for orig_line in names_list:
            line = self.strip_leading_number(orig_line)
            numbers = re.findall(r'\d+', line)
            if numbers:
                name, class_num = self.parse_classes(line, numbers) # 获取各个类别的数量
                if sum(class_num.values()) == 0: # sum == 0 means wrong format
                    nok_list.append(orig_line)
                else:
                    orders.append([orig_line, name] + [class_num.get(x, 0) for x in cls_labels])
            else: # no number means wrong format
                nok_list.append(orig_line)
        return orders, nok_list, header_labels


    def parse_namelist(self, txt):
        names_list, descr = self.load_list(txt)

        if self.classes is not None:
            orders, nok, headers = self.multi_class_parse(names_list, self.price)
        else:
            orders, nok, headers = self.single_class_parse(names_list, self.price)

        self.fprint(descr)
        self.print_excel_fmt(headers, orders, self.price)

        order_table = self.make_order_table(headers, orders)
        self.fprint('Order Tables')
        self.fprint('-'*80)
        for order in order_table:
            self.fprint(order)

        if nok:
            # print('\nWARNING: following lines were not parsed successfully!')
            self.fprint('\n警告: 下列行无法正确解析')
            self.fprint('='*50)
            for elem in nok:
                self.fprint(elem)
            self.fprint('='*50)
            self.fprint('共发现 %d 个错误, 请人工校对!' % len(nok))
        
        amount_array = np.array([x[2:] for x in orders])
        line_sum = np.c_[amount_array, np.sum(amount_array * self.price, axis=1)]
        summary = np.sum(line_sum, axis=0)
        summary = np.hstack((len(orders), summary))
        summary = summary.tolist()

        for i in range(len(summary)-1):
            summary[i] = int(summary[i])

        self.fprint('-'*80)
        self.fprint('Summary:')
        summary_header = ['人数'] + headers[2:] + ['总金额']
        self.fprint(summary_header)
        self.fprint(summary)
        self.fprint('-'*80)

        return orders, nok, descr, order_table, summary, summary_header

    def make_order_table(self, headers, orders):
        if orders is None:
            return None

        line_sum = np.sum(np.array([x[2:] for x in orders]), axis=1) * self.price

        cls_labels = headers[2:]
        order_table = [['姓名'] + cls_labels + ['金额', '原始信息']]
        for order, subtot in zip(orders, line_sum.tolist()):
            order_table.append(order[1:]+[subtot]+[order[0]])
        
        return order_table


    def print_excel_fmt(self, headers, orders, price):
        '''将订单列表打印为Excel格式
        参数:
        ------
        headers:    表头标签
        orders:     订单列表
        price:      物品单价

        返回值:     无
        ------
        '''
        cls_labels = headers[2:]
        columns = [chr(ord('C')+i) for i in range(len(cls_labels))]
        excel_fmt_list=[
            ['单价', '人数'] + cls_labels + ['总金额'],
            ['%.2f' % price,'"=COUNTA(B4:B200)"'] + ['"=SUM(%(col)s4:%(col)s200)"' % {'col':c} for c in columns] + ['"=SUM(%s2:%s2)*$A$2"' %(columns[0], columns[-1]) ],
            ['序号', '姓名'] + cls_labels + ['金额', '原始信息'],
            ]
        for row, order in enumerate(orders,start=1):
            excel_fmt_list.append([str(row), '"'+order[1]+'"'] + [str(x) for x in order[2:]] + ['"=SUM(%s%d:%s%d)*$A$2"' % (columns[0],row+3, columns[-1], row+3), '"'+order[0]+'"'])

        self.fprint('-'*80)
        for line in excel_fmt_list:
            self.fprint(' '.join(line))
        self.fprint('-'*80)


def set_io_utf8():
    import sys, io
    if str.lower(sys.stdout.encoding) != 'utf-8':
        # print('change stdout encoding from %s to utf-8' % sys.stdout.encoding)
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if str.lower(sys.stdin.encoding) != 'utf-8':
        # print('change stdin encoding from %s to utf-8' % sys.stdin.encoding)
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')


def main():
    # set_io_utf8()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        解析接龙列表, 获取接龙名单以及商品数量.

        若未指定输入文件, 则从标准输入读取数据, 输入完毕请敲s组合键 -- Linux:Ctrl-D, Windows: Ctrl-Z + ENTER
        若商品有多个类别, 请修改本程序开头 classes 列表中的标签, 然后用 -m 选项进行解析.
        '''),)
    parser.add_argument("infile", metavar='FILE', nargs='?', type=argparse.FileType('r', encoding='UTF-8'), 
        default=sys.stdin, help='接龙列表的输入文件 (默认: 标准输入)')    
    parser.add_argument("-m", '--mclass', action='store_true', help='按多类别解析接龙列表' )
    parser.add_argument("-p", '--price', nargs='?', type=float, default=88, help='物品单价' )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')

    args = parser.parse_args()

    # # 肉松
    # classes = [
    #     ['原味', '原'],
    #     ['海苔味', '海苔'],
    # ]

    # 奶酪
    classes = [
        ['原味', '原'],
        ['水果味', '水果'],
    ]

    # # 益生菌
    # classes = [
    #     ['原味', '原'],
    #     ['奶味', '奶'],
    # ]

    # # 韩国海苔_02
    # classes = [
    #     ['糙米', ],
    #     ['杏仁', ],
    #     ['海鱼', ],
    # ]

    # # 日本足贴
    # classes = [
    #     ['艾草', '绿'],
    #     ['唐幸', '红'],
    #     ['西柚', '橙'],
    #     ['薰衣草', '紫'],
    #     ['活力肽', '粉'],
    #     ['生姜', '黄'],
    #     ['玫瑰', '蓝'],
    # ]

    # # 牛奶
    # classes = [
    #     ['清甜','清',],
    #     ['金装','金',],
    # ]

    # # 坚果
    # classes = [
    #     ['成人','大人', '棕', '大'],
    #     ['儿童','绿', '小'],
    # ]

    orderparser = OrdersParser(price=args.price, classes=classes if args.mclass else None )
    orderparser.parse_namelist(args.infile.read())


if __name__ == '__main__':
    main()
