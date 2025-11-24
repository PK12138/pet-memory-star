import pandas as pd
import re
import os


def extract_8digit_numbers(file_path):
    """提取Excel文件中的八位数字"""
    try:
        # 获取桌面路径
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        excel_file = os.path.join(desktop, "林创.xlsx")

        if not os.path.exists(excel_file):
            print(f"错误: 文件 {excel_file} 不存在")
            return

        print(f"正在处理: {excel_file}")

        # 读取Excel文件
        xl_file = pd.ExcelFile(excel_file)
        all_results = {}

        for sheet_name in xl_file.sheet_names:
            print(f"\n处理工作表: {sheet_name}")

            # 读取sheet数据
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, dtype=str)
            sheet_results = []

            # 遍历所有单元格
            for row_idx, row in df.iterrows():
                for col_idx, cell_value in enumerate(row):
                    if pd.notna(cell_value):
                        # 查找八位数字
                        numbers = re.findall(r'\b\d{8}\b', str(cell_value))
                        for number in numbers:
                            # 转换为Excel坐标
                            col_letter = chr(65 + col_idx)  # A=65, B=66, ...
                            cell_address = f"{col_letter}{row_idx + 1}"
                            sheet_results.append({
                                'cell': cell_address,
                                'number': number
                            })

            all_results[sheet_name] = sheet_results
            print(f"找到 {len(sheet_results)} 个八位数字")

        # 输出结果
        print("\n" + "=" * 40)
        print("提取结果:")
        print("=" * 40)

        for sheet_name, numbers in all_results.items():
            print(f"\n{sheet_name}:")
            for item in numbers:
                print(f"  {item['cell']}: {item['number']}")

        # 保存结果到桌面
        output_file = os.path.join(desktop, "八位数字提取结果.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for sheet_name, numbers in all_results.items():
                f.write(f"{sheet_name}:\n")
                for item in numbers:
                    f.write(f"  {item['cell']}: {item['number']}\n")
                f.write("\n")

        print(f"\n结果已保存到: {output_file}")

    except Exception as e:
        print(f"处理过程中出错: {e}")


# 运行程序
if __name__ == "__main__":
    extract_8digit_numbers("1.xlsx")