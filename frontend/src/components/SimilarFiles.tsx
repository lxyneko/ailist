import React, { useState, useEffect } from 'react';
import { Card, List, Typography, Spin, Alert, Space } from 'antd';
import { FileOutlined, LinkOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface SimilarFilesProps {
  storageId: number;
  file: any;
  onFileSelect: (file: any) => void;
}

const SimilarFiles: React.FC<SimilarFilesProps> = ({
  storageId,
  file,
  onFileSelect
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [similarFiles, setSimilarFiles] = useState<any[]>([]);

  const fetchSimilarFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/ai/similar/${storageId}/${file.path}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('获取相似文件失败');
      }
      
      const data = await response.json();
      setSimilarFiles(data.similar_files);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (file) {
      fetchSimilarFiles();
    }
  }, [file]);

  return (
    <Card title="相似文件推荐" style={{ marginTop: 16 }}>
      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" />
        </div>
      ) : error ? (
        <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
        />
      ) : similarFiles.length === 0 ? (
        <Text type="secondary">没有找到相似文件</Text>
      ) : (
        <List
          dataSource={similarFiles}
          renderItem={similarFile => (
            <List.Item>
              <Card
                hoverable
                style={{ width: '100%' }}
                onClick={() => onFileSelect(similarFile)}
              >
                <Space>
                  <FileOutlined />
                  <Text>{similarFile.name}</Text>
                  <Text type="secondary">({similarFile.path})</Text>
                  <LinkOutlined style={{ color: '#1890ff' }} />
                </Space>
              </Card>
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

export default SimilarFiles; 