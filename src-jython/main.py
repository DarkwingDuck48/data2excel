# -*- coding: utf-8 -*-
import os
import subprocess
from java import lang
from java.sql import Connection, DriverManager, Types
import codecs
from load_jars import loadsqldrivers

loadsqldrivers()

lang.Class.forName("org.sqlite.JDBC")
database_url = "jdbc:sqlite:D:\Work\GIT_work\data2excel\databases\develop.db"
conn = DriverManager.getConnection(database_url)

data_pass = '{ "data": ['

sql = "SELECT * from peoples"
statment = conn.prepareStatement(sql).executeQuery()
statment_meta = statment.getMetaData()
columns_count = statment_meta.getColumnCount()
table_data = []
while statment.next():
    json_like = '{' 
    for col_idx in range(1, columns_count+1):
        json_like += '"%s" : "%s"' % (statment_meta.getColumnName(col_idx), statment.getObject(col_idx))
        if col_idx != columns_count:
            json_like += ","
    json_like += "}"
    table_data.append(json_like)

all_data = ",".join(table_data)
data_pass += all_data
data_pass += "]}"


path_to_file = os.path.join(os.getcwd(), "src-jython", "data_json.json")

fp = codecs.open(path_to_file, "w", encoding="utf-8")
fp.write(data_pass)
fp.close()

command = 'D:\\Work\\GIT_work\data2excel\\target\\debug\\data2excel.exe --json-path %s' % path_to_file
p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdOutData, stdErrData = p.communicate(input=None)

print("OUTDATA: %s" % stdOutData)
print("ERRDATA: %s" % stdErrData)

conn.close()

