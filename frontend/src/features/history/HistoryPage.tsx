import React, { useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { Clock, FileText } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { fetchHistory } from '../clinical/clinicalSlice';
import { formatDate, truncateText } from '@/utils/helpers';

export const HistoryPage: React.FC = () => {
    const dispatch = useAppDispatch();
    const { history, isLoadingHistory } = useAppSelector((state) => state.clinical);

    useEffect(() => {
        dispatch(fetchHistory({ limit: 50, skip: 0 }));
    }, [dispatch]);

    return (
        <Layout>
            <div className="space-y-6 animate-fade-in">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Decision History</h1>
                    <p className="text-gray-600 mt-2">
                        View your past clinical decision analyses
                    </p>
                </div>

                {isLoadingHistory ? (
                    <div className="card flex justify-center items-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                ) : history.length === 0 ? (
                    <div className="card text-center py-12">
                        <Clock className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                        <h3 className="text-lg font-medium text-gray-900 mb-1">No history yet</h3>
                        <p className="text-sm text-gray-500">
                            Your clinical decision analyses will appear here
                        </p>
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {history.map((item) => (
                            <div key={item.id} className="card hover:shadow-lg transition-shadow">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                            {truncateText(item.query, 100)}
                                        </h3>
                                        <p className="text-sm text-gray-600 mb-3">
                                            {item.decision_summary}
                                        </p>
                                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                                            <span className="flex items-center space-x-1">
                                                <Clock className="h-4 w-4" />
                                                <span>{formatDate(item.created_at)}</span>
                                            </span>
                                            <span className="flex items-center space-x-1">
                                                <FileText className="h-4 w-4" />
                                                <span>{item.document_count} document(s)</span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
};
