import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, LogOut, FileText, MessageSquare, History } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { logout } from '@/features/auth/authSlice';

export const Navbar: React.FC = () => {
    const dispatch = useAppDispatch();
    const navigate = useNavigate();
    const { user } = useAppSelector((state) => state.auth);

    const handleLogout = () => {
        dispatch(logout());
        navigate('/login');
    };

    return (
        <nav className="bg-white shadow-md border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/dashboard" className="flex items-center space-x-2">
                            <Activity className="h-8 w-8 text-primary-600" />
                            <span className="text-xl font-bold text-gray-900">Medical Chat Bot</span>
                        </Link>
                    </div>

                    <div className="flex items-center space-x-4">
                        <Link
                            to="/documents"
                            className="flex items-center space-x-1 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
                        >
                            <FileText className="h-5 w-5" />
                            <span className="hidden sm:inline">Documents</span>
                        </Link>

                        <Link
                            to="/clinical"
                            className="flex items-center space-x-1 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
                        >
                            <MessageSquare className="h-5 w-5" />
                            <span className="hidden sm:inline">Clinical AI</span>
                        </Link>

                        <Link
                            to="/history"
                            className="flex items-center space-x-1 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
                        >
                            <History className="h-5 w-5" />
                            <span className="hidden sm:inline">History</span>
                        </Link>

                        <div className="border-l border-gray-300 pl-4 flex items-center space-x-3">
                            <div className="hidden sm:block text-sm">
                                <p className="text-gray-900 font-medium">{user?.full_name}</p>
                                <p className="text-gray-500 text-xs">{user?.email}</p>
                            </div>

                            <button
                                onClick={handleLogout}
                                className="flex items-center space-x-1 px-3 py-2 rounded-md text-red-600 hover:bg-red-50 transition-colors"
                                title="Logout"
                            >
                                <LogOut className="h-5 w-5" />
                                <span className="hidden sm:inline">Logout</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};
