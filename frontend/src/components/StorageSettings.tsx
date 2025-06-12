import React, { useState, useEffect } from 'react';
import { FolderIcon } from '@heroicons/react/24/outline';

interface StorageConfig {
  type: 'local' | 'webdav';
  path?: string;
  webdav?: {
    url: string;
    username: string;
    password: string;
  };
}

const StorageSettings: React.FC = () => {
  const [config, setConfig] = useState<StorageConfig>({
    type: 'local',
    path: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch('/api/storage/config');
      if (!response.ok) {
        throw new Error('获取存储配置失败');
      }
      const data = await response.json();
      setConfig(data);
      
      // 如果没有配置，自动创建一个本地存储池
      if (!data || !data.path) {
        const defaultPath = './storage';
        await handleSubmit({
          preventDefault: () => {},
        } as React.FormEvent, {
          type: 'local',
          path: defaultPath,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取存储配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent, defaultConfig?: StorageConfig) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      const configToSubmit = defaultConfig || config;
      const response = await fetch('/api/storage/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configToSubmit),
      });

      if (!response.ok) {
        throw new Error('保存存储配置失败');
      }

      if (!defaultConfig) {
        setSuccess('存储配置已保存');
      }
      
      // 如果是默认配置，更新当前配置
      if (defaultConfig) {
        setConfig(defaultConfig);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存存储配置失败');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">存储设置</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">错误：</strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">成功：</strong>
          <span className="block sm:inline">{success}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            存储类型
          </label>
          <select
            value={config.type}
            onChange={(e) => setConfig({ ...config, type: e.target.value as 'local' | 'webdav' })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="local">本地存储</option>
            <option value="webdav">WebDAV</option>
          </select>
        </div>

        {config.type === 'local' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              存储路径
            </label>
            <div className="flex">
              <input
                type="text"
                value={config.path || ''}
                onChange={(e) => setConfig({ ...config, path: e.target.value })}
                placeholder="请输入存储路径"
                className="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <FolderIcon className="h-5 w-5 mr-2" />
                浏览
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                WebDAV URL
              </label>
              <input
                type="url"
                value={config.webdav?.url || ''}
                onChange={(e) => setConfig({
                  ...config,
                  webdav: { ...config.webdav, url: e.target.value }
                })}
                placeholder="https://example.com/webdav"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                用户名
              </label>
              <input
                type="text"
                value={config.webdav?.username || ''}
                onChange={(e) => setConfig({
                  ...config,
                  webdav: { ...config.webdav, username: e.target.value }
                })}
                placeholder="请输入用户名"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <input
                type="password"
                value={config.webdav?.password || ''}
                onChange={(e) => setConfig({
                  ...config,
                  webdav: { ...config.webdav, password: e.target.value }
                })}
                placeholder="请输入密码"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            保存设置
          </button>
        </div>
      </form>
    </div>
  );
};

export default StorageSettings; 