# -*- coding: utf-8 -*-
"""
    Author: Maxim Britvin
    2024

    Модуль предназначеный для разбора объекта Java Result Set и выдачу результатов в различных форматах, подходящих под обработки
"""


def parse_block_to_jsonlike_string(block_name, rs):
    # type: (str, ResultSet) -> str
    """
        params: 
            block_name: str - имя блока данных для формирования отчета
            rs: jave.sql.ResultSet - результат выполненного запроса
        Разбирает переданный ResultSet и отдает в виде JSON-like строки
        "block_name" : {
            "headers" : [ имена колонок из запроса ],
            "values" : [
                {
                    "col1_name" : "col1_value",
                    ...
                    "colN_name": "colN_value"
                },
                ...
            ]
        }
        Для упрощения считаем все значения элементов текстовыми - чтобы пока что не определять тип данных.
        В теории его можно определить через getColumnType из метаданных, но конвертировать и приводить к одному JSON формату пока долго.
    """

    block_json = u'"%s": {' % block_name
    metadata = rs.getMetaData()
    columns_count = rs.getColumnCount()

    headers = ",".join(['"%s"' % metadata.getColumnLabel(col_id) for col_id in range(1, columns_count + 1)])
    values = []
    while rs.next():
        json_like = u'{'
        for col_idx in range(1, columns_count + 1):
            json_like += '"%s" : "%s"' % (metadata.getColumnLabel(col_idx), rs.getObject(col_idx))
            if col_idx != columns_count:
                json_like += ","
        json_like += "}"
        values.append(json_like)
    block_json += '"headers" : [%s],' % headers
    block_json += '"values" : [%s]' % ",".join(values)
    block_json += '}'
    return block_json
