# -*- coding: utf-8 -*-
import os
import subprocess
from java import lang
from java.sql import Connection, DriverManager, Types
import codecs
from load_jars import loadsqldrivers


loadsqldrivers()
lang.Class.forName("org.sqlite.JDBC")
DATABASE_URL = "jdbc:sqlite:D:\Work\GIT_work\data2excel\databases\develop.db"
conn = DriverManager.getConnection(DATABASE_URL)

class ReportDataSheet:
    def __init__(self, name, data_blocks):
        #type: (str, list[str]) -> None
        self.name = name
        self.data_blocks = data_blocks

    def generate_sheet_json(self):
        """Метод для генерации данных листа"""
        sheet_json = u'{ "name": "%s", ' % self.name
        sheet_json += u'"data_blocks": [ '
        sheet_json += ",".join(self.data_blocks)
        sheet_json += "]"
        sheet_json += "}"
        return sheet_json

class ReportDataBlock:
    """Класс для хранения всех настроек блока данных отчета"""
    def __init__(self, name, simple_rows = None, sql_statement = None, need_agenda = False):
        # type: (str, list[list[str]], str, bool) -> None
        self.name = name
        self.simple_rows = simple_rows
        self.sql_statement = sql_statement
        self.need_agenda = need_agenda
        self.block_data = None

    def _get_block_data(self, db_connection):
        """Метод для получения данных из БД """
        result_set = db_connection.prepareStatement(self.sql_statement).executeQuery()
        return result_set

    def _format_simple_rows_to_json(self):
        """Метод для формирования данных, которые нужно расположить в одну строчку.
           В этом случае первый элемент в списке считаем заголовком, остальные - данными
           В итоговом файле, первый элемент будет выделен цветом, остальные просто расположены в отдельных ячейках строки
        """
        rows_json = u'"simple_rows": ['
        rows = []
        for row in self.simple_rows:
            data = u'{"header": "%s", \n' % row[0]
            data += u'"data": [%s]}' % ",".join([u'"%s"' % rv for rv in row[1:]])
            rows.append(data)
        rows_json += ",".join(rows)
        rows_json += ']'
        return rows_json

    def _format_column_value_to_type(self, typeid, value):
        # type: (int, str) -> str
        """
            Метод форматирует переданное значение, в соответствии с форматами JSON
            Строки должны быть заключены в ""
            Типы данных можно посмотреть по ссылке: https://docs.oracle.com/javase/8/docs/api/constant-values.html#java.sql.Types.BIT

        """
        if typeid in (1, -15, -9, 12):
            return '"%s"' % value
        return '"%s"' % value

    def _format_resultset_to_json(self, rs):
        """Метод для формирования данных в виде таблицы в Excel файле.
           Заголовки таблицы берем из данных запроса - они будут выделены цветом и жирным шрифтом.
           Остальные данные будут расположены в табличном виде, в соответствии с заголовками запроса
        """
        table_json = u'"table": {'
        metadata = rs.getMetaData()
        columns_count = rs.getColumnCount()
        headers = ",".join(['"%s"' % metadata.getColumnLabel(col_id) for col_id in range(1, columns_count + 1)])
        table_json += '"headers" : [%s],' % headers
        values = []
        while rs.next():
            row_values = []
            for col_idx in range(1, columns_count + 1):
                row_values.append('%s' % self._format_column_value_to_type(metadata.getColumnType(col_idx), rs.getObject(col_idx)))
            values.append("[%s]" % ",".join(row_values))
        table_json += '"data" : [%s]' % ",".join(values)
        table_json += '}'
        return table_json

    def parse_block_to_jsonlike_string(self, db_connection):
        """
            Для упрощения считаем все значения элементов текстовыми - чтобы пока что не определять тип данных.
            В теории его можно определить через getColumnType из метаданных, но конвертировать и приводить к одному JSON формату пока долго.
        """
        block_json = u'{"name": "%s",' % self.name
        if self.simple_rows is not None:
            block_json += self._format_simple_rows_to_json()
            block_json += "," if self.sql_statement is not None else ""
        if self.sql_statement is not None:
            rs = self._get_block_data(db_connection)
            block_json += self._format_resultset_to_json(rs)
            rs.close()
        block_json += "}"
        return "%s" % block_json


def create_report(db_connection):
    """ Создаем отчет со всеми настройками. Предполагается, что в данной функции будем настраивать весь отчет и получаем формируем из него файл"""
    # base report settings
    WORKBOOK_NAME = u"report.xlsx"
    REPORT_PATH = os.path.normpath(os.path.join(os.getcwd(), WORKBOOK_NAME)).replace("\\", "\\\\")

    print("REPORT PATH : %s" % REPORT_PATH)

    root_json = u'''
        { 
            "workbook" : { 
                "path" : "%s",
                "sheets" : [
    ''' % REPORT_PATH

    sql = "SELECT id as PK, name as PersonName, age as PersonAge from peoples"
    report_block = ReportDataBlock (
        name="TestReport",
        simple_rows=[["test", 1, 2,3], ["new", 1, 3, 4]],
        sql_statement=sql)

    report_block_info = ReportDataBlock(
        name="Load Info",
        simple_rows=[
            ["LOAID", 20304, 1231234],
            ["USERNAME", "MAXIM"]
        ]
    )

    sheet = ReportDataSheet(
        name="ALL_DATA",
        data_blocks=[
            report_block_info.parse_block_to_jsonlike_string(db_connection),
            report_block.parse_block_to_jsonlike_string(db_connection)
        ]
    )

    sheets_list = [sheet]
    sheets_data = []
    for sh in sheets_list:
        sheets_data.append("%s" % sh.generate_sheet_json())
    root_json += ",".join(sheets_data)
    root_json += "]"
    root_json += "}"    # close "workbook" section
    root_json += "}"    # close "root" section
    return root_json

data_pass = create_report(conn)

path_to_file = os.path.normpath(os.path.join(os.getcwd(), "src-jython", "data_json.json")).replace("\\", "\\\\")

# print(path_to_file)

fp = codecs.open(path_to_file, "w", encoding="utf-8")
fp.write(data_pass)
fp.close()

command = 'D:\\Work\\GIT_work\\data2excel\\target\\debug\\data2excel.exe --json-path %s' % path_to_file
p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdOutData, stdErrData = p.communicate(input=None)

print("OUTDATA: %s" % stdOutData)
print("ERRDATA: %s" % stdErrData)

conn.close()
