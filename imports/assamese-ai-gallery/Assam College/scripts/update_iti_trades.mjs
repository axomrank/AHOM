import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const root = '/home/angsuman/extra_spac/Assam College';
const input = root + '/outputs/departments_20261001/Assam_Colleges_Verified_Departments.xlsx';
const output = root + '/outputs/iti_trades_20261001/Assam_Colleges_Departments_and_ITI_Trades.xlsx';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const sheet = wb.worksheets.getItemAt(0);
const source = sheet.getRange('A278:S319').values;
const rows = source.map((record, index) => {
  const rowNumber = 278 + index;
  if (record[2] !== 'ITI') throw new Error('Expected ITI at row ' + rowNumber);
  const match = String(record[14] ?? '').match(/^CTS Trades:\s*(.+)$/i);
  if (!match) throw new Error('Missing listed trades at row ' + rowNumber);
  const trades = match[1].split(',').map(x => x.trim()).filter(Boolean).join('; ');
  const height = Math.max(27, Math.ceil(trades.length / 88) * 23);
  sheet.getRange('Q' + rowNumber).format.rowHeight = height;
  return [trades, '', 'Trades from existing directory (O); institute list not independently verified'];
});
sheet.getRange('Q1').values = [['Departments / ITI trades']];
sheet.getRange('Q278:S319').values = rows;
sheet.getRange('Q278:Q319').format.wrapText = true;
sheet.getRange('S278:S319').format.wrapText = true;
sheet.getRange('S278:S319').format.columnWidth = 42;
wb.recalculate();
await fs.mkdir(root + '/outputs/iti_trades_20261001', { recursive: true });
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(output, rows.length);
