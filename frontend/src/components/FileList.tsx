import React from 'react';
import { FolderIcon, DocumentIcon } from '@heroicons/react/24/outline';

interface File {
  id: number;
  name: string;
  type: string;
  size: number;
  path: string;
}

interface FileListProps {
  files: File[];
  onFileClick: (file: File) => void;
}

const FileList: React.FC<FileListProps> = ({ files, onFileClick }) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <div className="file-list">
      {files.map((file) => (
        <div
          key={file.id}
          className="file-item"
          onClick={() => onFileClick(file)}
        >
          <div className="flex items-center space-x-2">
            {file.type === 'directory' ? (
              <FolderIcon className="h-6 w-6 text-yellow-500" />
            ) : (
              <DocumentIcon className="h-6 w-6 text-blue-500" />
            )}
            <div>
              <h3 className="text-sm font-medium truncate">{file.name}</h3>
              <p className="text-xs text-gray-500">
                {file.type === 'directory' ? '文件夹' : formatFileSize(file.size)}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FileList; 