import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { uploadDocument, fetchDocuments } from './documentsSlice';

export const DocumentUpload: React.FC = () => {
    const dispatch = useAppDispatch();
    const { isLoading, error } = useAppSelector((state) => state.documents);
    const [success, setSuccess] = useState(false);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            setSuccess(false);
            const result = await dispatch(uploadDocument(acceptedFiles[0]));

            if (uploadDocument.fulfilled.match(result)) {
                setSuccess(true);
                dispatch(fetchDocuments());
                setTimeout(() => setSuccess(false), 3000);
            }
        }
    }, [dispatch]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        },
        maxSize: 50 * 1024 * 1024, // 50MB
        multiple: false,
    });

    return (
        <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Medical Document</h3>

            <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${isDragActive
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                    }`}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center space-y-3">
                    {isLoading ? (
                        <>
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                            <p className="text-sm text-gray-600">Uploading and processing...</p>
                        </>
                    ) : (
                        <>
                            <Upload className="h-12 w-12 text-gray-400" />
                            <div>
                                <p className="text-lg font-medium text-gray-900">
                                    {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
                                </p>
                                <p className="text-sm text-gray-500 mt-1">
                                    or click to select a file
                                </p>
                            </div>
                            <p className="text-xs text-gray-400">
                                Supported: PDF, DOCX, TXT (Max 50MB)
                            </p>
                        </>
                    )}
                </div>
            </div>

            {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
                    <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-600">{error}</p>
                </div>
            )}

            {success && (
                <div className="mt-4 p-4 bg-medical-50 border border-medical-200 rounded-lg">
                    <p className="text-sm text-medical-700 font-medium">
                        ✓ Document uploaded and processed successfully!
                    </p>
                </div>
            )}
        </div>
    );
};
