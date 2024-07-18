use std::collections::HashMap;
use std::path::PathBuf;
use std::fs;

#[warn(unused_imports)]
use rust_xlsxwriter::{Workbook, XlsxError};
use clap::Parser;
use serde_json;
#[derive(Parser)]
struct Cli {
    #[arg(long)]
    json_path: PathBuf
}


fn main() -> Result<(), XlsxError> {
    let cli = Cli::parse();

    let res = fs::read_to_string(cli.json_path);
    let json_file = match res {
        Ok(s) => s,
        Err(_) => panic!("Cant read file")
    };
    let json_data:serde_json::Value = serde_json::from_str(&json_file).expect("Cant parse json");

    println!("Data: {}", json_data);
    // let mut workbook = Workbook::new();
    // let worksheet = workbook.add_worksheet();
    // let expences =  vec![
    //     [1000, 2000],
    //     [999, 1000],
    //     [600, 500],
    // ];
    // worksheet.write_row_matrix(0, 0, expences)?;
    // workbook.save("hello.xlsx")?;
    Ok(())
}
