import React, { useEffect } from 'react';
import { FileText, Trash2, Eye } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { fetchDocuments, deleteDocument } from './documentsSlice';
import { formatDate, formatFileSize } from '@/utils/helpers';

export const DocumentList: React.FC = () => {
    const dispatch = useAppDispatch();
    const { documents, isLoading } = useAppSelector((state) => state.documents);

    useEffect(() => {
        dispatch(fetchDocuments());
    }, [dispatch]);

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this document?')) {
            await dispatch(deleteDocument(id));
        }
    };

    if (isLoading) {
        return (
            <div className="card">
                <div className="flex justify-center items-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
            </div>
        );
    }

    if (documents.length === 0) {
        return (
            <div className="card text-center py-12">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No documents yet</h3>
                <p className="text-sm text-gray-500">Upload your first medical document to get started</p>
            </div>
        );
    }

    return (
        <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Your Documents ({documents.length})
            </h3>

            <div className="space-y-3">
                {documents.map((doc) => (
                    <div
                        key={doc.id}
                        className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                            <FileText className="h-10 w-10 text-primary-600 flex-shrink-0" />

                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                    {doc.filename}
                                </p>
                                <div className="flex items-center space-x-3 text-xs text-gray-500 mt-1">
                                    <span>{formatFileSize(doc.file_size)}</span>
                                    <span>•</span>
                                    <span>{formatDate(doc.upload_date)}</span>
                                    <span>•</span>
                                    <span className={doc.processed ? 'text-medical-600' : 'text-yellow-600'}>
                                        {doc.processed ? '✓ Processed' : '⏳ Processing'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-2 ml-4">
                            <button
                                onClick={() => handleDelete(doc.id)}
                                className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                                title="Delete document"
                            >
                                <Trash2 className="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
