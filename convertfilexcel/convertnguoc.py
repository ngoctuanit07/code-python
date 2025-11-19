import win32com.client as win32

input_path = r"D:\tools\dv\convertfilexcel\KQ_HBV_converted.xls"
output_path = r"D:\tools\dv\convertfilexcel\KQ_HBV_oledb.xls"

excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(input_path)
wb.SaveAs(output_path, FileFormat=56)  # 56 = Excel 97-2003 Workbook
wb.Close()
excel.Quit()

print(f"✅ File Excel 97-2003 thật đã được tạo: {output_path}")
