import React, { useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { DocumentUpload } from './DocumentUpload';
import { DocumentList } from './DocumentList';

export const DocumentsPage: React.FC = () => {
    return (
        <Layout>
            <div className="space-y-6 animate-fade-in">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Medical Documents</h1>
                    <p className="text-gray-600 mt-2">
                        Upload and manage your medical documents for AI analysis
                    </p>
                </div>

                <DocumentUpload />
                <DocumentList />
            </div>
        </Layout>
    );
};
