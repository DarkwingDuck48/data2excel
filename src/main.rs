mod reportstruct;

#[cfg(test)]
mod tests;

use std::fs;
use std::path::PathBuf;

use clap::Parser;
use rust_xlsxwriter::Color;

use rust_xlsxwriter::{Format, Workbook, XlsxError};

use serde_json::from_str;

use reportstruct::Report;

#[derive(Parser)]
struct Cli {
    #[arg(long)]
    json_path: PathBuf,
}

fn main() -> Result<(), XlsxError> {
    let cli = Cli::parse();

    let res = fs::read_to_string(cli.json_path);

    let json_file = match res {
        Ok(s) => s,
        Err(_) => panic!("Cant read file"),
    };
    let report_data: Report = from_str::<Report>(&json_file).expect("Cant parse json");

    let report_path = report_data.workbook.path;
    println!("{:?}", report_path);

    let mut workbook = Workbook::new();
    let header_format = Format::new()
        .set_bold()
        .set_background_color(Color::Theme(3, 2));

    let sheets = report_data.workbook.sheets;

    for sheet in sheets {
        let worksheet = workbook.add_worksheet();
        worksheet
            .set_name(sheet.name)
            .expect("Can't set sheet name");
        let mut current_row = 0;

        for data_block in sheet.data_blocks {
            // Write block name to sheet
            worksheet
                .write_with_format(current_row, 0, data_block.name, &Format::new().set_bold())
                .expect("Can't write datablock name");
            current_row += 2;
            // First step - write simple rows from data block to sheet
            if let Some(sr) = data_block.simple_rows {
                sr.into_iter().for_each(|row| {
                    worksheet
                        .write_with_format(current_row, 0, row.header, &header_format)
                        .expect("Can't write header");
                    let mut col = 1;
                    for val in row.data {
                        let is_number = val.replace(',', ".").parse::<f64>();
                        if let Ok(value) = is_number{
                            println!("Find numeric value {:?}", &value);
                            worksheet.write(current_row, col, value).expect("Can't write number to column");
                        } else{
                            println!("Find string value {:?}", val);
                            worksheet.write(current_row, col, val).expect("Can't write string to column");
                        }
                        col += 1;
                    }
                    current_row += 1;
                });
                current_row += 1;
            };

            // Second step - write table from data block to sheet
            if let Some(tb) = data_block.table {
                let row_for_table_autofilter = current_row;
                let table_columns_count = tb.headers.len() - 1;
                worksheet
                    .write_row_with_format(current_row, 0, tb.headers, &header_format)
                    .expect("Can't write table header");
                current_row += 1;
                for row in tb.data {
                    for (col,val) in row.into_iter().enumerate() {
                        let is_number = val.replace(',', ".").parse::<f64>();
                        if let Ok(value) = is_number{
                            println!("Find numeric value {:?}", &value);
                            worksheet.write(current_row, col.try_into().unwrap(), value).expect("Can't write number to column");
                        } else{
                            println!("Find string value {:?}", val);
                            worksheet.write(current_row, col.try_into().unwrap(), val).expect("Can't write string to column");
                        }
                    }
                    current_row += 1;
                }
                
                // Autofilter will be applied only for last block
                worksheet
                    .autofilter(
                        row_for_table_autofilter,
                        0,
                        current_row - 1,
                        table_columns_count as u16,
                    )
                    .expect("Cant set autofilter on sheet");
            }
        }
        worksheet.autofit();
    }
    workbook.save(report_path).expect("Can't save workbook");
    Ok(())
}
