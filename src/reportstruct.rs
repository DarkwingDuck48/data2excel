use std::path::PathBuf;
use std::string::String;
use serde::{Deserialize, Serialize};


#[derive(Serialize, Deserialize, Debug)]
pub struct Report {
    pub workbook: WorkbookJson
}

#[derive(Serialize, Deserialize, Debug)]
pub struct WorkbookJson{
    pub path: PathBuf,
    pub sheets: Vec<SheetsJSON>
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SheetsJSON {
    pub name: String,
    pub data_blocks: Vec<DataBlockJSON>
}

#[derive(Serialize, Deserialize, Debug)]
pub struct DataBlockJSON {
    pub name: String,
    pub simple_rows: Option<Vec<SimpleRowsJSON>>,
    pub table: Option<TableJSON>
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SimpleRowsJSON{
    pub header: String,
    pub data: Vec<String>
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TableJSON {
    pub headers: Vec<String>,
    pub data: Vec<Vec<String>>
}
