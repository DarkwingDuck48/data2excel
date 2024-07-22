# -*- coding: utf-8 -*-

import os
import subprocess
from java import lang
from java.sql import Connection, DriverManager, Types
import codecs
from load_jars import loadsqldrivers
from resultsetutils import parse_block_to_jsonlike_string

loadsqldrivers()
lang.Class.forName("org.sqlite.JDBC")
DATABASE_URL = "jdbc:sqlite:/Users/mbritvin/Documents/Personal/data2excel/databases/develop.db"
conn = DriverManager.getConnection(DATABASE_URL)

class ReportDataSheet:
    def __init__(self, name, data_blocks):
        #type: (str, list[ReportDataBlock]) -> None
        self.name = name
        self.data_blocks = data_blocks
    
    def generate_sheet_json(self):
        """Метод для генерации данных листа"""
        sheet_json = u'"%s": {' % self.name
        


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
            data = ",".join([u'"%s"' % rv for rv in row[1:]])
            rows.append(u'{"%s" : [%s]}' % (row[0], data))
        rows_json += ",".join(rows)
        rows_json += ']'
        return rows_json

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
            json_like = u'{'
            for col_idx in range(1, columns_count + 1):
                json_like += '"%s" : "%s"' % (metadata.getColumnLabel(col_idx), rs.getObject(col_idx))
                if col_idx != columns_count:
                    json_like += ","
            json_like += "}"
            values.append(json_like)
        table_json += '"data" : [%s]' % ",".join(values)
        table_json += '}'
        return table_json

    def parse_block_to_jsonlike_string(self, db_connection):
        # type: (ResultSet) -> str
        """
            params: 
                block_name: str - имя блока данных для формирования отчета
                rs: jave.sql.ResultSet - результат выполненного запроса
            Разбирает переданный ResultSet и отдает в виде JSON-like строки
            {
                "block1": {
                    "simple_rows": [
                        {
                            "row_header": [
                                1,
                                2,
                                3
                            ]
                        },
                        {
                            "row_header2": [
                                1,
                                2,
                                3
                            ]
                        }
                    ],
                    "table": {
                        "headers": [],
                        "data": []
                    }
                }
            }
            Для упрощения считаем все значения элементов текстовыми - чтобы пока что не определять тип данных.
            В теории его можно определить через getColumnType из метаданных, но конвертировать и приводить к одному JSON формату пока долго.
        """
        block_json = u'"%s": {' % self.name
        if self.simple_rows is not None:
            block_json += self._format_simple_rows_to_json()
            block_json += ","
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
    REPORT_PATH = os.path.join(os.getcwd(), WORKBOOK_NAME)

    print("REPORT PATH : %s" % REPORT_PATH)

    root_json = u'''
        { 
            "workbook" : { 
                "path" : "%s",
                "sheets" : {
    ''' % REPORT_PATH

    sql = "SELECT id as PK, name as PersonName, age as PersonAge from Persons"
    report_block = ReportDataBlock(
        name="TestReport",
        simple_rows=[["test", 1, 2,3], ["new", 1, 3, 4]],
        sql_statement=sql)

    report_block_info = ReportDataBlock(
        name="Load Info",
        simple_rows=[
            ["LOAID", 20304],
            ["USERNAME", "MAXIM"]
        ]
    )

    root_json += u'"testSheet": {'
    root_json += report_block_info.parse_block_to_jsonlike_string(db_connection)
    root_json += ","
    root_json += report_block.parse_block_to_jsonlike_string(db_connection)
    root_json += "}"
    root_json += "}"
    return root_json


print(create_report(conn))

# path_to_file = os.path.join(os.getcwd(), "src-jython", "data_json.json")

# fp = codecs.open(path_to_file, "w", encoding="utf-8")
# fp.write(data_pass)
# fp.close()

# command = '/Users/mbritvin/Documents/Personal/data2excel/target/debug/data2excel --json-path %s' % path_to_file
# p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# stdOutData, stdErrData = p.communicate(input=None)

# print("OUTDATA: %s" % stdOutData)
# print("ERRDATA: %s" % stdErrData)

conn.close()

