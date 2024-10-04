import boto3
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter()

# S3 Client Setting
s3_client = boto3.client('s3')
bucket_name = 'jonas-fastapi-master'  # Replace it to your real bucket 

# =========================================================
# API Request
# =========================================================
class FileDownloadChunkRequest(BaseModel):
    chunk_size: int = Field(default=1024 * 1024, ge=1024)

class FileDownloadChunkFromS3Request(FileDownloadChunkRequest):
    pass


# =========================================================
# API Response
# =========================================================

class FileUploadResponse(BaseModel):
    status: str
    filename: str

class FileUploadToS3Response(FileUploadResponse):
    s3_path: str


# =========================================================
# File Upload
# =========================================================

# Common File Upload
@router.post("/upload", response_model=FileUploadResponse)
async def file_upload(file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return FileUploadResponse(
            status="File uploaded successfully",
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Upload to S3
@router.post("/upload-to-s3", response_model=FileUploadToS3Response)
async def file_upload_to_s3(file: UploadFile = File(...), s3_path: str = Form(..., min_length=1, max_length=500)):
    try:
        # Upload Files to S3
        s3_client.upload_fileobj(Fileobj=file.file, Bucket=bucket_name, Key=s3_path)
        return FileUploadToS3Response(
            status="File uploaded to S3 successfully",
            filename=file.filename,
            s3_path=s3_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# File Download
# =========================================================

# Common File Download
@router.get("/download/{filename}")
async def file_download(filename: str):
    try:
        return StreamingResponse(open(filename, "rb"), media_type="application/octet-stream")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


# Chunk File Download
@router.get("/download-in-chunk/{filename}")
async def file_download_in_chunk(filename: str, query: FileDownloadChunkRequest = Depends()): # 1MB chunks
    try:
        def iter_file():
            with open(filename, "rb") as file:
                while chunk := file.read(query.chunk_size):
                    yield chunk

        return StreamingResponse(iter_file(), media_type="application/octet-stream")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


# File Download from S3
@router.get("/download-from-s3/{filename}")
async def file_download_from_s3(filename: str):
    try:
        # Get Files from S3
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=filename)
        return StreamingResponse(s3_object['Body'], media_type="application/octet-stream")
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# File Download from S3 in chunks
@router.get("/download-from-s3-in-chunk/{filename}")
async def file_download_from_s3_in_chunk(filename: str, query: FileDownloadChunkFromS3Request = Depends()):
    try:
        # Get Files from S3
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=filename)
        # Stream the file in chunks
        def iterfile():
            for chunk in s3_object['Body'].iter_chunks(query.chunk_size):
                yield chunk
        return StreamingResponse(iterfile(), media_type="application/octet-stream")
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))