import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# ---------- 底层读写 ----------
def _read() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _write(records: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)


# ---------- 公开接口 ----------
def get_all() -> list:
    return _read()


def add_record(date: str, time: str, weight: float) -> dict:
    # 格式校验
    datetime.strptime(date, "%d.%m.%Y")   # 日期格式不对会抛出 ValueError
    datetime.strptime(time, "%H:%M")       # 时间格式不对会抛出 ValueError
    if not isinstance(weight, (int, float)) or weight <= 0:
        raise ValueError("weight 必须是正数")

    record = {"date": date, "time": time, "weight": float(weight)}
    records = _read()
    records.append(record)
    _write(records)
    return record


def delete_record(date: str, time: str) -> bool:
    records = _read()
    new_records = [r for r in records if not (r["date"] == date and r["time"] == time)]
    if len(new_records) == len(records):
        return False  # 未找到
    _write(new_records)
    return True


def delete_by_index(index: int) -> dict:
    records = _read()
    if index < 0 or index >= len(records):
        raise IndexError(f"索引 {index} 超出范围，当前共 {len(records)} 条记录")
    removed = records.pop(index)
    _write(records)
    return removed


# ---------- 使用示例 ----------
if __name__ == "__main__":
    print(get_all())

    now = datetime.now()
    newrecord = {
        "date": now.strftime("%d.%m.%Y"),
        "time": now.strftime("%H:%M"),
        "weight": float(input("请输入体重 (kg): ")),
    }
    added = add_record(newrecord["date"], newrecord["time"], newrecord["weight"])
    print("已添加记录:", added)