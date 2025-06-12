import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  TrashIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface Storage {
  id: number;
  name: string;
  type: string;
  config: any;
}

interface StorageManagerProps {
  onStorageSelect: (storageId: number) => void;
  onStorageAdd: (storage: Omit<Storage, 'id'>) => Promise<void>;
  onStorageUpdate: (storage: Storage) => Promise<void>;
  onStorageDelete: (storageId: number) => Promise<void>;
}

const StorageManager: React.FC<StorageManagerProps> = ({
  onStorageSelect,
  onStorageAdd,
  onStorageUpdate,
  onStorageDelete,
}) => {
  const [storages, setStorages] = useState<Storage[]>([]);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newStorage, setNewStorage] = useState<Partial<Storage>>({
    name: '',
    type: 'local',
    config: {},
  });

  const storageTypes = [
    { id: 'local', name: '本地存储' },
    { id: 's3', name: 'S3 存储' },
    { id: 'webdav', name: 'WebDAV' },
    { id: 'aliyun', name: '阿里云盘' },
    { id: 'baidu', name: '百度网盘' },
  ];

  const handleAdd = async () => {
    if (!newStorage.name || !newStorage.type) return;
    
    try {
      await onStorageAdd(newStorage as Omit<Storage, 'id'>);
      setIsAdding(false);
      setNewStorage({ name: '', type: 'local', config: {} });
    } catch (error) {
      console.error('Failed to add storage:', error);
    }
  };

  const handleUpdate = async (storage: Storage) => {
    try {
      await onStorageUpdate(storage);
      setEditingId(null);
    } catch (error) {
      console.error('Failed to update storage:', error);
    }
  };

  const handleDelete = async (storageId: number) => {
    if (!confirm('确定要删除这个存储吗？')) return;
    
    try {
      await onStorageDelete(storageId);
    } catch (error) {
      console.error('Failed to delete storage:', error);
    }
  };

  return (
    <div className="storage-manager bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">存储管理</h2>
        <button
          onClick={() => setIsAdding(true)}
          className="btn btn-primary flex items-center space-x-1"
        >
          <PlusIcon className="h-5 w-5" />
          <span>添加存储</span>
        </button>
      </div>

      {isAdding && (
        <div className="mb-4 p-4 border rounded-lg">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">名称</label>
              <input
                type="text"
                value={newStorage.name}
                onChange={(e) => setNewStorage({ ...newStorage, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">类型</label>
              <select
                value={newStorage.type}
                onChange={(e) => setNewStorage({ ...newStorage, type: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg"
              >
                {storageTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setIsAdding(false)}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={handleAdd}
                className="btn btn-primary"
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {storages.map((storage) => (
          <div
            key={storage.id}
            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            {editingId === storage.id ? (
              <div className="flex-1 space-y-2">
                <input
                  type="text"
                  value={storage.name}
                  onChange={(e) => {
                    const updated = { ...storage, name: e.target.value };
                    setStorages(storages.map((s) => 
                      s.id === storage.id ? updated : s
                    ));
                  }}
                  className="w-full px-2 py-1 border rounded"
                />
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setEditingId(null)}
                    className="p-1 text-gray-500 hover:text-gray-700"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleUpdate(storage)}
                    className="p-1 text-green-500 hover:text-green-700"
                  >
                    <CheckIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div
                  className="flex-1 cursor-pointer"
                  onClick={() => onStorageSelect(storage.id)}
                >
                  <div className="font-medium">{storage.name}</div>
                  <div className="text-sm text-gray-500">
                    {storageTypes.find((t) => t.id === storage.type)?.name}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setEditingId(storage.id)}
                    className="p-1 text-gray-500 hover:text-gray-700"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(storage.id)}
                    className="p-1 text-red-500 hover:text-red-700"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StorageManager; 