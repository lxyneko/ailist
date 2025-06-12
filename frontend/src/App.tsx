import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import FileList from './components/FileList';
import StorageSettings from './components/StorageSettings';
import './styles/main.scss';

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 从 localStorage 获取主题设置
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.setAttribute('data-theme', 'dark');
    }

    // 获取文件列表
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/files');
      if (!response.ok) {
        throw new Error('获取文件列表失败');
      }
      const data = await response.json();
      setFiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取文件列表失败');
      console.error('Error fetching files:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    document.documentElement.setAttribute(
      'data-theme',
      newTheme ? 'dark' : 'light'
    );
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
  };

  const handleFileClick = (file: any) => {
    if (file.type === 'directory') {
      // 处理目录点击
      console.log('Opening directory:', file.path);
    } else {
      // 处理文件点击
      console.log('Opening file:', file.path);
    }
  };

  return (
    <Router>
      <div className="min-h-screen">
        <Navigation isDarkMode={isDarkMode} onToggleTheme={toggleTheme} />
        
        <main className="container py-8">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">错误：</strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}
          
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
            </div>
          ) : (
            <Routes>
              <Route
                path="/"
                element={
                  <FileList
                    files={files}
                    onFileClick={handleFileClick}
                  />
                }
              />
              <Route
                path="/settings"
                element={<StorageSettings />}
              />
            </Routes>
          )}
        </main>
      </div>
    </Router>
  );
};

export default App; 