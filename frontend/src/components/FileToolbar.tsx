import React from 'react';
import {
  FolderPlusIcon,
  DocumentPlusIcon,
  TrashIcon,
  ArrowPathIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline';

interface FileToolbarProps {
  onNewFolder: () => void;
  onUpload: () => void;
  onRefresh: () => void;
  onDelete: () => void;
  selectedFiles: number[];
}

const FileToolbar: React.FC<FileToolbarProps> = ({
  onNewFolder,
  onUpload,
  onRefresh,
  onDelete,
  selectedFiles,
}) => {
  return (
    <div className="file-toolbar flex items-center space-x-2 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      <button
        onClick={onNewFolder}
        className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        title="新建文件夹"
      >
        <FolderPlusIcon className="h-5 w-5" />
      </button>

      <button
        onClick={onUpload}
        className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        title="上传文件"
      >
        <ArrowUpTrayIcon className="h-5 w-5" />
      </button>

      <button
        onClick={onRefresh}
        className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        title="刷新"
      >
        <ArrowPathIcon className="h-5 w-5" />
      </button>

      {selectedFiles.length > 0 && (
        <button
          onClick={onDelete}
          className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          title="删除选中文件"
        >
          <TrashIcon className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};

export default FileToolbar; 