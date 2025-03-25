import boto3
import codecs
import csv
import io
import os
import pandas as pd
from enum import Enum
from fastapi import Path, APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import pathlib

router = APIRouter()


# =========================================================
# Settings
# =========================================================

# S3 Client Setting
s3_client = boto3.client('s3')
bucket_name = os.getenv("AWS_S3_BUCKET_NAME", 'jonas-fastapi-master')  # Replace it to your real bucket 

# File Type
class FileType(Enum):
    CSV         = ("CSV",           ".csv")
    EXCEL       = ("EXCEL",         ".xlsx")
    POWERPOINT  = ("POWERPOINT",    ".pptx")

    def __new__(cls, key, extension):
        obj = object.__new__(cls)
        obj._value_ = key  # Use _value_ for the key
        obj.key = key
        obj.extension = extension
        return obj
    


# =========================================================
# API Request
# =========================================================
class FileDownloadChunkRequest(BaseModel):
    chunk_size: int = Field(default=1024 * 1024, ge=1024)

class FileDownloadChunkFromS3Request(FileDownloadChunkRequest):
    pass

class FileStreamingDownloadChunkFromS3Request(FileDownloadChunkRequest):
    pass

class FileGenerateCsvRequest(FileDownloadChunkRequest):
    pandas: bool = Field(default=False)


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

# File Multipart Upload to S3
@router.post("/multipart-upload-to-s3", response_model=FileUploadToS3Response)
async def file_multipart_upload_to_s3(file: UploadFile = File(...), s3_path: str = Form(..., min_length=1, max_length=500), chunk_size: int = 5 * 1024 * 1024):
    try:
        # Initiate Multipart Upload
        response = s3_client.create_multipart_upload(Bucket=bucket_name, Key=s3_path)
        upload_id = response["UploadId"]

        parts = []
        part_number = 1

        while True:
            # Read the file in chunks
            chunk = await file.read(chunk_size)
            if not chunk:
                break

            # Upload the chunk as a part
            response = s3_client.upload_part(
                Bucket=bucket_name,
                Key=s3_path,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=io.BytesIO(chunk)  # Convert chunk to stream
            )

            # Store part information
            parts.append({"ETag": response["ETag"], "PartNumber": part_number})
            part_number += 1

        # Complete Multipart Upload
        s3_client.complete_multipart_upload(
            Bucket=bucket_name,
            Key=s3_path,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts}
        )

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


# Download File from S3 in chunks
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


# File Streaming Download from S3 in chunks
@router.get("/stream-download-from-s3-in-chunk/{filename}")
async def file_stream_download_from_s3_in_chunk(filename: str, query: FileStreamingDownloadChunkFromS3Request = Depends()):
    try:
        def stream_s3_file(bucket_name: str, object_key: str):
            # Get the size of the object
            head_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            file_size = head_response['ContentLength']

            # Set the chunk size (e.g., 5MB)
            chunk_size = query.chunk_size

            # Start position
            start = 0

            while start < file_size:
                # Calculate the end position
                end = min(start + chunk_size - 1, file_size - 1)

                # Request only the specific range from S3
                range_header = f"bytes={start}-{end}"
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key, Range=range_header)
                
                # Get the response body
                body = response['Body']
                chunk = body.read()  # Read chunk data
                
                # Stream the data to the client
                yield chunk

                # Update the start position for the next chunk
                start += chunk_size

        return StreamingResponse(stream_s3_file(bucket_name=bucket_name, object_key=filename), media_type="application/octet-stream")
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# Generate Files
# =========================================================

# File Generate CSV
@router.get("/generate-csv/{filename}")
async def file_generate_csv(
    filename: str = Path(..., regex=r"^[\w,\s-]+\.[A-Za-z]{3}$"),
    query: FileGenerateCsvRequest = Depends()
):
    # validate filename length
    if len(filename) <= 4:
        raise HTTPException(status_code=400, detail="Filename too short. It must be longer than the extension.")

    # validate file extension name
    file_extension = pathlib.Path(filename).suffix.casefold()
    if file_extension != FileType.CSV.extension:
        raise HTTPException(status_code=400, detail="Invalid file extension. Only .csv files are allowed.")
    
    # writer
    output = io.BytesIO()
    # writer = csv.writer(io.TextIOWrapper(output, newline='', encoding='utf-8')) # This doesn't work for all characters "WHEN YOU OPEN THE FILE USING EXCEL"
    StreamWriter = codecs.getwriter('utf-8-sig')
    wrapper_file = StreamWriter(output)
    writer = csv.writer(wrapper_file)

    # chunk read generator
    def iter_file_chunks():
        
        # chunk read generator) data
        headers = ["이름", "Age", "City"] # "이름" means "Name" to see if the utf-8 character works "WHEN YOU OPEN THE FILE USING EXCEL"
        rows = [
            {
                headers[0]: "A",
                headers[1]: 30,
                headers[2]: "Los Angeles"
            },
            {
                headers[0]: "B",
                headers[1]: 24,
                headers[2]: "Seoul"
            },
            {
                headers[0]: "C",
                headers[1]: 40,
                headers[2]: "Paris"
            }
        ]
        
        # Max read line cnt
        max_read_line_cnt = 2

        # csv
        if not query.pandas:

            # The `output` using StringIO doesn't work for all characters "WHEN YOU OPEN THE FILE USING EXCEL"
            # output = io.StringIO()
            # writer = csv.writer(output)

            print("[CSV - `csv`] generating a csv file with csv lib ...")
            data = [headers]

            for row in rows:
                data_row = []
                for header in headers:
                    data_row.append(row.get(header))
                data.append(data_row)
            
            for i in range(0, len(data), max_read_line_cnt):
                writer.writerows(data[i:i+max_read_line_cnt])
                output.seek(0)
                yield output.read(query.chunk_size)
                output.seek(0)
                output.truncate(0)
        
        # pandas
        else:
            print("[CSV - `pandas`] generating a csv file with pandas lib ...")
            data = {}
            
            for header in headers:
                data_row = []
                for row in rows:
                    data_row.append(row.get(header))
                data[header] = data_row
            
            df = pd.DataFrame(data)

            for i in range(0, len(df), max_read_line_cnt):
                df.iloc[i:i+max_read_line_cnt].to_csv(output, index=False, header=i==0, encoding='utf-8-sig') # headers only for the first chunk
                output.seek(0)
                yield output.read(query.chunk_size)
                output.seek(0)
                output.truncate(0)
    try:
        return StreamingResponse(iter_file_chunks(), media_type="text/csv")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Internal Server Error")