from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import json, os

app = FastAPI(title="体重记录 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# ---------- 数据模型 ----------
class RecordIn(BaseModel):
    date: str   # dd.mm.yyyy，留空则自动取当前日期
    time: str   # hh:mm，留空则自动取当前时间
    weight: float


# ---------- 路由 ----------
@app.get("/records", summary="获取所有记录")
def get_records():
    return _read()


@app.post("/records", summary="新增记录")
def add_record(body: RecordIn):
    now = datetime.now()
    date = body.date.strip() or now.strftime("%d.%m.%Y")
    time = body.time.strip() or now.strftime("%H:%M")

    try:
        datetime.strptime(date, "%d.%m.%Y")
    except ValueError:
        raise HTTPException(400, "日期格式应为 dd.mm.yyyy")
    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        raise HTTPException(400, "时间格式应为 hh:mm")
    if body.weight <= 0:
        raise HTTPException(400, "体重必须是正数")

    record = {"date": date, "time": time, "weight": float(body.weight)}
    records = _read()
    records.append(record)
    _write(records)
    return record


@app.delete("/records/{index}", summary="按索引删除记录")
def delete_record(index: int):
    records = _read()
    if index < 0 or index >= len(records):
        raise HTTPException(404, f"索引 {index} 超出范围，当前共 {len(records)} 条记录")
    removed = records.pop(index)
    _write(records)
    return {"deleted": removed}


# ---------- 托管前端 ----------
# 把 index.html 放在同目录下即可通过 http://localhost:8000 访问
@app.get("/", include_in_schema=False)
def serve_index():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "请将 index.html 放在同目录下"}