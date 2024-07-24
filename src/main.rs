mod reportstruct;

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
            worksheet.write_with_format(current_row, 0, data_block.name, &Format::new().set_bold()).expect("Can't write datablock name");
            current_row += 2;
            // First step - write simple rows from data block to sheet
            if let Some(sr) = data_block.simple_rows {
                sr.into_iter().for_each(|row| {
                    worksheet
                        .write_with_format(current_row, 0, row.header, &header_format)
                        .expect("Can't write header");
                    worksheet
                        .write_row(current_row, 1, row.data)
                        .expect("Can't write row");
                    current_row += 1;
                });
                current_row += 1;
            };
            // Second step - write table from data block to sheet
            if let Some(tb) = data_block.table {
                worksheet.write_row_with_format(current_row, 0, tb.headers, &header_format).expect("Can't write table header");
                current_row += 1;
                for row in tb.data{
                    worksheet.write_row(current_row, 0, row).expect("Can't write table data");
                    current_row += 1;
                }
            }
        }

        worksheet.autofit();
    }
    workbook.save(report_path).expect("Can't save workbook");
    Ok(())
}
