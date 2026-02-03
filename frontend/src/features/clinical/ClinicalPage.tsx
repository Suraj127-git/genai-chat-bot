import React, { useState, useEffect } from 'react';
import { Send, Loader } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Layout } from '@/components/layout/Layout';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { analyzeClinical } from './clinicalSlice';
import { fetchDocuments } from '../documents/documentsSlice';

export const ClinicalPage: React.FC = () => {
    const dispatch = useAppDispatch();
    const { currentDecision, isAnalyzing, error } = useAppSelector((state) => state.clinical);
    const { documents } = useAppSelector((state) => state.documents);

    const [query, setQuery] = useState('');
    const [selectedDocs, setSelectedDocs] = useState<string[]>([]);

    useEffect(() => {
        dispatch(fetchDocuments());
    }, [dispatch]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        await dispatch(analyzeClinical({
            query: query.trim(),
            document_ids: selectedDocs,
            include_history: true,
        }));
    };

    const toggleDocument = (docId: string) => {
        setSelectedDocs(prev =>
            prev.includes(docId)
                ? prev.filter(id => id !== docId)
                : [...prev, docId]
        );
    };

    return (
        <Layout>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
                {/* Main Chat Area */}
                <div className="lg:col-span-2 space-y-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Clinical AI Assistant</h1>
                        <p className="text-gray-600 mt-2">
                            Ask medical questions and get AI-powered clinical insights
                        </p>
                    </div>

                    {/* Query Form */}
                    <div className="card">
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                                    Medical Question or Case Description
                                </label>
                                <textarea
                                    id="query"
                                    rows={4}
                                    className="input-field resize-none"
                                    placeholder="Describe the patient case, symptoms, or ask a clinical question..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    disabled={isAnalyzing}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <p className="text-sm text-gray-500">
                                    {selectedDocs.length} document(s) selected
                                </p>
                                <button
                                    type="submit"
                                    disabled={isAnalyzing || !query.trim()}
                                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                                >
                                    {isAnalyzing ? (
                                        <>
                                            <Loader className="h-5 w-5 animate-spin" />
                                            <span>Analyzing...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Send className="h-5 w-5" />
                                            <span>Analyze</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>

                        {error && (
                            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                                <p className="text-sm text-red-600">{error}</p>
                            </div>
                        )}
                    </div>

                    {/* Clinical Decision Result */}
                    {currentDecision && (
                        <div className="card">
                            <div className="mb-4 pb-4 border-b border-gray-200">
                                <h3 className="text-lg font-semibold text-gray-900">Clinical Analysis</h3>
                                {currentDecision.confidence_score !== undefined && (
                                    <div className="mt-2">
                                        <div className="flex items-center justify-between text-sm mb-1">
                                            <span className="text-gray-600">Confidence Score</span>
                                            <span className="font-medium">
                                                {(currentDecision.confidence_score * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                            <div
                                                className="bg-medical-500 h-2 rounded-full transition-all"
                                                style={{ width: `${currentDecision.confidence_score * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="prose prose-sm max-w-none">
                                <ReactMarkdown>{currentDecision.decision}</ReactMarkdown>
                            </div>

                            {currentDecision.citations.length > 0 && (
                                <div className="mt-6 pt-6 border-t border-gray-200">
                                    <h4 className="text-sm font-semibold text-gray-900 mb-3">Citations</h4>
                                    <div className="space-y-2">
                                        {currentDecision.citations.map((citation, idx) => (
                                            <div key={idx} className="p-3 bg-gray-50 rounded-lg text-sm">
                                                <p className="font-medium text-gray-900">{citation.document_name}</p>
                                                <p className="text-gray-600 mt-1 italic">"{citation.excerpt}"</p>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    Relevance: {(citation.relevance_score * 100).toFixed(0)}%
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Sidebar - Document Selection */}
                <div className="lg:col-span-1">
                    <div className="card sticky top-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            Select Documents
                        </h3>

                        {documents.length === 0 ? (
                            <p className="text-sm text-gray-500 text-center py-4">
                                No documents available. Upload documents first.
                            </p>
                        ) : (
                            <div className="space-y-2">
                                {documents.filter(doc => doc.processed).map((doc) => (
                                    <label
                                        key={doc.id}
                                        className="flex items-start space-x-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedDocs.includes(doc.id)}
                                            onChange={() => toggleDocument(doc.id)}
                                            className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 truncate">
                                                {doc.filename}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                {doc.file_type.toUpperCase()}
                                            </p>
                                        </div>
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </Layout>
    );
};
