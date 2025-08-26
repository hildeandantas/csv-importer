import os
from fastapi import  File, UploadFile, APIRouter, HTTPException
from pathlib import Path
from app.utils.file_processor import process_csv_file  
router = APIRouter()

@router.post("/import")
async def import_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="O arquivo precisa ser um CSV.")

    base_dir = Path(__file__).resolve().parent
    temp_dir = base_dir / ".." / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    filepath = temp_dir / file.filename

    try:
        with open(filepath, "wb") as buffer:
            while chunk := await file.read(8192):
                buffer.write(chunk)
                
    except Exception as e:
        if filepath.exists():
            os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Não foi possível salvar o arquivo: {e}")
    finally:
        await file.close()

    process_csv_file(str(file.filename))

    return {
        "message": "Arquivo CSV salvo com sucesso!",
        "original_filename": file.filename,
        "saved_path": str(filepath)
    }
