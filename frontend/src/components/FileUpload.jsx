import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const FileUpload = ({ onUploadComplete }) => {
    const [dragActive, setDragActive] = useState(false);
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState(null); // 'success' | 'error'

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFiles(e.dataTransfer.files);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFiles(e.target.files);
        }
    };

    const handleFiles = (fileList) => {
        setFiles([...fileList]);
        setStatus(null);
    };

    const uploadFiles = async () => {
        if (files.length === 0) return;

        setUploading(true);
        setStatus(null);
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            await axios.post('http://127.0.0.1:8000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setStatus('success');
            setFiles([]);
            if (onUploadComplete) onUploadComplete();
        } catch (error) {
            console.error("Upload error:", error);
            setStatus('error');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-indigo-600" />
                Knowledge Base
            </h3>

            <div
                className={`relative border-2 border-dashed rounded-lg p-8 transition-all duration-200 ease-in-out text-center ${dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-slate-400 bg-slate-50'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    multiple
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    onChange={handleChange}
                    accept=".txt,.pdf"
                />

                <div className="flex flex-col items-center gap-2 text-slate-500">
                    <div className="p-3 bg-white rounded-full shadow-sm">
                        <FileText className="w-6 h-6 text-slate-400" />
                    </div>
                    <p className="text-sm font-medium">
                        <span className="text-indigo-600">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-slate-400">PDF or TXT files supported</p>
                </div>
            </div>

            {files.length > 0 && (
                <div className="mt-4 space-y-2">
                    {Array.from(files).map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between text-sm text-slate-600 bg-slate-50 px-3 py-2 rounded">
                            <span className="truncate max-w-[200px]">{file.name}</span>
                            <span className="text-xs text-slate-400">{(file.size / 1024).toFixed(0)} KB</span>
                        </div>
                    ))}

                    <button
                        onClick={uploadFiles}
                        disabled={uploading}
                        className="w-full mt-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {uploading ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Processing...
                            </>
                        ) : (
                            "Process Documents"
                        )}
                    </button>
                </div>
            )}

            {status === 'success' && (
                <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg flex items-center gap-2 text-sm animate-in fade-in slide-in-from-top-1">
                    <CheckCircle className="w-4 h-4" />
                    Documents successfully indexed!
                </div>
            )}

            {status === 'error' && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-center gap-2 text-sm animate-in fade-in slide-in-from-top-1">
                    <AlertCircle className="w-4 h-4" />
                    Failed to process documents.
                </div>
            )}
        </div>
    );
};

export default FileUpload;
