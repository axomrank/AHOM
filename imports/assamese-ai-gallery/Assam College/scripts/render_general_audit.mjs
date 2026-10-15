import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
const root = '/home/angsuman/extra_spac/Assam College';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(root + '/Assam_Colleges_Complete_Directory.xlsx'));
const sh = wb.worksheets.getItemAt(0);
const blob = await wb.render({ sheetName: sh.name, range: 'M65:N69', scale: 1.5 });
const out = '/tmp/assam_affiliation_qa.png';
await fs.writeFile(out, Buffer.from(await blob.arrayBuffer()));
console.log(out);
