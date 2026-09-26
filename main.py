from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from passporteye import read_mrz
from paddleocr import PaddleOCR
from mrz.checker.td3 import TD3CodeChecker
import shutil
import os

app = FastAPI(title="SIH Document Extraction API", version="1.0")

ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.get("/")
def home():
    return {"message": "Service A is running! Send POST request to /api/v1/extract"}

@app.post("/api/v1/extract")
async def extract_document(file: UploadFile = File(...)):
    temp_file = f"temp_{file.filename}"
    
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result_data = {
            "mrz_data": None,
            "mrz_valid": False,
            "ocr_text": []
        }

        mrz = read_mrz(temp_file)
        if mrz is not None:
            mrz_data = mrz.to_dict()
            result_data["mrz_data"] = mrz_data
            
            try:
                checker = TD3CodeChecker(mrz.mrz_type)
                result_data["mrz_valid"] = bool(checker)
            except Exception as e:
                result_data["mrz_valid"] = "Validation Error or Unsupported Format"

        ocr_result = ocr.ocr(temp_file, cls=True)
        extracted_text = []
        if ocr_result and ocr_result[0]:
            for line in ocr_result[0]:
                extracted_text.append(line[1][0])
        
        result_data["ocr_text"] = extracted_text

        return JSONResponse(content={"status": "success", "data": result_data})

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
