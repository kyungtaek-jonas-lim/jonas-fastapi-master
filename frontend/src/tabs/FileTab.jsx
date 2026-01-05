import React, { useState } from 'react';
import useAxios from '../hooks/useAxios';
import { CONTENT_TYPES } from '../utils/contentTypes';  // Import content types

function FileTab() {
  const [file, setFile] = useState(null);
  const [chunkSize, setChunkSize] = useState(1024 * 1024); // Default chunk size 1MB
  const [downloadPath, setDownloadPath] = useState('');  // State for the download path

  const { data, loading, error, post, get } = useAxios();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // data = await post('/v1/file/upload', formData, CONTENT_TYPES.FORM_DATA);
    // if (data) {
    //   alert(data.status);
    // }

    const response = await post(
      '/v1/file/upload',
      formData,
      CONTENT_TYPES.FORM_DATA
    );

    if (response?.data) {
      alert(response.data.status);
    }
  };

  const handleFileDownload = async () => {
    if (!downloadPath) {
      alert("Please enter a download path.");
      return;
    }
  
    const url = `/v1/file/download/${encodeURIComponent(downloadPath)}`;
    
    try {
      const response = await get(url, null, { responseType: 'blob' });
  
      if (response && response.data) {
        const blob = new Blob([response.data]);
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = downloadPath.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error("File download failed:", error);
    }
  };

  const handleFileDownloadInChunks = async () => {
    if (!downloadPath) {
      alert("Please enter a download path.");
      return;
    }
  
    const url = `/v1/file/download-in-chunk/${encodeURIComponent(downloadPath)}`;
  
    try {
      const response = await get(url, null, {
        params: { chunk_size: chunkSize },
        responseType: 'blob',
      });
  
      if (response && response.data) {
        const blob = new Blob([response.data]);
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = downloadPath.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error("Chunked file download failed:", error);
    }
  };  

  return (
    <div>
      <h2>File Operations</h2>
      <input type="file" onChange={handleFileChange} />
      
      {/* Chunk Size Input */}
      <div>
        <label>Chunk Size (in bytes):</label>
        <input type="number" value={chunkSize} onChange={(e) => setChunkSize(Number(e.target.value))} />
      </div>
      
      {/* Download Path Input */}
      <div>
        <label>Download Path:</label>
        <input
          type="text"
          value={downloadPath}
          onChange={(e) => setDownloadPath(e.target.value)}
          placeholder="Enter download path"
        />
      </div>
      
      {/* Action Buttons */}
      <button onClick={handleFileUpload} disabled={loading}>
        {loading ? 'Uploading...' : 'Upload File'}
      </button>
      <button onClick={handleFileDownload} disabled={loading}>
        {loading ? 'Downloading...' : 'Download File'}
      </button>
      <button onClick={handleFileDownloadInChunks} disabled={loading}>
        {loading ? 'Downloading in Chunks...' : 'Download in Chunks'}
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {data && <pre>Response: {JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}

export default FileTab;
