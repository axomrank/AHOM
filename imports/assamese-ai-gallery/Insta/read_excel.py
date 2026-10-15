import zipfile
import xml.etree.ElementTree as ET

namespaces = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

with zipfile.ZipFile('/home/angsuman/extra_spac/Assam_Data/Insta/AxomRank_Instagram_Carousel_Calendar_Oct-Dec_2026.xlsx', 'r') as z:
    for filename in z.namelist():
        if filename.startswith('xl/worksheets/sheet'):
            print(f"--- {filename} ---")
            xml_content = z.read(filename)
            root = ET.fromstring(xml_content)
            for row in root.findall('.//main:row', namespaces):
                row_data = []
                for c in row.findall('./main:c', namespaces):
                    # Check if it has a v element (value)
                    v = c.find('./main:v', namespaces)
                    is_inline = c.find('./main:is/main:t', namespaces)
                    
                    if is_inline is not None:
                        row_data.append(is_inline.text)
                    elif v is not None:
                        # might be a number, or a shared string index if t="s"
                        # but sharedStrings was empty
                        t_attr = c.get('t')
                        if t_attr == 'inlineStr':
                            t_elem = c.find('./main:is/main:t', namespaces)
                            if t_elem is not None:
                                row_data.append(t_elem.text)
                        else:
                            row_data.append(v.text)
                    else:
                        row_data.append("")
                if any(row_data):
                    print(" | ".join(str(x) for x in row_data))
