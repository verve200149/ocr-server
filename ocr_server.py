import sys
import subprocess

# ✅ 自動安裝必要套件
required_packages = ["fastapi", "uvicorn", "ddddocr", "python-multipart"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"[INFO] Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# ✅ 正式引入模組
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ddddocr
import uvicorn
import base64
import traceback

app = FastAPI()
ocr = ddddocr.DdddOcr(show_ad=False)

# 加入 CORS Middleware，允許所有來源、所有方法、所有標頭
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 若只允許特定IP可改成 ["http://192.168.4.183"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OCRJsonPayload(BaseModel):
    image_data: str

@app.post("/ocr")
async def solve_captcha_json(payload: OCRJsonPayload):
    try:
        image_bytes = base64.b64decode(payload.image_data)
        print(f"[INFO] Received base64 image, size: {len(image_bytes)} bytes")

        result = ocr.classification(image_bytes)
        print(f"[INFO] OCR result: {result}")
        return JSONResponse(content={"result": result})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/ocr-file")
async def solve_captcha_file(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        print(f"[INFO] Received file: {file.filename}, size: {len(image_bytes)} bytes")

        result = ocr.classification(image_bytes)
        print(f"[INFO] OCR result: {result}")
        return JSONResponse(content={"result": result})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("ocr_server:app", host="0.0.0.0", port=16888)
