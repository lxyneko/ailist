import React, { useState } from 'react';

interface StorageConfigProps {
  type: string;
  config: any;
  onChange: (config: any) => void;
}

const StorageConfig: React.FC<StorageConfigProps> = ({
  type,
  config,
  onChange,
}) => {
  const [localConfig, setLocalConfig] = useState(config);

  const handleChange = (key: string, value: string) => {
    const newConfig = { ...localConfig, [key]: value };
    setLocalConfig(newConfig);
    onChange(newConfig);
  };

  const renderLocalConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">存储路径</label>
        <input
          type="text"
          value={localConfig.path || ''}
          onChange={(e) => handleChange('path', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
          placeholder="/path/to/storage"
        />
      </div>
    </div>
  );

  const renderS3Config = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Access Key</label>
        <input
          type="text"
          value={localConfig.accessKey || ''}
          onChange={(e) => handleChange('accessKey', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Secret Key</label>
        <input
          type="password"
          value={localConfig.secretKey || ''}
          onChange={(e) => handleChange('secretKey', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Bucket</label>
        <input
          type="text"
          value={localConfig.bucket || ''}
          onChange={(e) => handleChange('bucket', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Region</label>
        <input
          type="text"
          value={localConfig.region || ''}
          onChange={(e) => handleChange('region', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
    </div>
  );

  const renderWebDAVConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">服务器地址</label>
        <input
          type="text"
          value={localConfig.url || ''}
          onChange={(e) => handleChange('url', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
          placeholder="https://webdav.example.com"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">用户名</label>
        <input
          type="text"
          value={localConfig.username || ''}
          onChange={(e) => handleChange('username', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">密码</label>
        <input
          type="password"
          value={localConfig.password || ''}
          onChange={(e) => handleChange('password', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
    </div>
  );

  const renderAlibabaConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">刷新令牌</label>
        <input
          type="text"
          value={localConfig.refreshToken || ''}
          onChange={(e) => handleChange('refreshToken', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
    </div>
  );

  const renderBaiduConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">访问令牌</label>
        <input
          type="text"
          value={localConfig.accessToken || ''}
          onChange={(e) => handleChange('accessToken', e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        />
      </div>
    </div>
  );

  const renderConfig = () => {
    switch (type) {
      case 'local':
        return renderLocalConfig();
      case 's3':
        return renderS3Config();
      case 'webdav':
        return renderWebDAVConfig();
      case 'aliyun':
        return renderAlibabaConfig();
      case 'baidu':
        return renderBaiduConfig();
      default:
        return <div>不支持的存储类型</div>;
    }
  };

  return (
    <div className="storage-config">
      {renderConfig()}
    </div>
  );
};

export default StorageConfig; 