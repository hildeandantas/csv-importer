from fastapi import  File, UploadFile, APIRouter, HTTPException
from app.services.importer import importer
router = APIRouter()

@router.post("/import")
async def import_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="O arquivo precisa ser um CSV.")
    
    await importer(file)

    return {
        "message": "Arquivo CSV salvo com sucesso!",
        "original_filename": file.filename,
    }
