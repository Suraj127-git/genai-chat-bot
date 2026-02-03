import React from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { FileText, MessageSquare, History, Upload } from 'lucide-react';

export const Dashboard: React.FC = () => {
    return (
        <Layout>
            <div className="space-y-8 animate-fade-in">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <p className="text-gray-600 mt-2">
                        Welcome to your Medical Chat Bot workspace
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <Link to="/documents" className="card hover:shadow-xl transition-all group">
                        <FileText className="h-12 w-12 text-primary-600 mb-4 group-hover:scale-110 transition-transform" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Documents</h3>
                        <p className="text-gray-600 text-sm">
                            Upload and manage your medical documents for AI analysis
                        </p>
                    </Link>

                    <Link to="/clinical" className="card hover:shadow-xl transition-all group">
                        <MessageSquare className="h-12 w-12 text-medical-600 mb-4 group-hover:scale-110 transition-transform" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Clinical AI</h3>
                        <p className="text-gray-600 text-sm">
                            Get AI-powered clinical decision support and insights
                        </p>
                    </Link>

                    <Link to="/history" className="card hover:shadow-xl transition-all group">
                        <History className="h-12 w-12 text-primary-600 mb-4 group-hover:scale-110 transition-transform" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">History</h3>
                        <p className="text-gray-600 text-sm">
                            Review your past clinical decision analyses
                        </p>
                    </Link>
                </div>

                <div className="card bg-gradient-to-br from-primary-500 to-medical-500 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-2xl font-bold mb-2">Get Started</h3>
                            <p className="text-primary-100 mb-4">
                                Upload your first medical document to begin receiving AI-powered clinical insights
                            </p>
                            <Link
                                to="/documents"
                                className="inline-flex items-center space-x-2 bg-white text-primary-600 px-6 py-3 rounded-lg font-medium hover:bg-primary-50 transition-colors"
                            >
                                <Upload className="h-5 w-5" />
                                <span>Upload Document</span>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};
