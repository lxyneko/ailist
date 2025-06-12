import React, { useState } from 'react';
import { Tag, Button, Spin, Alert, Space } from 'antd';
import { TagsOutlined, PlusOutlined } from '@ant-design/icons';

interface FileTagsProps {
  storageId: number;
  file: any;
  onTagsUpdate?: (tags: string[]) => void;
}

const FileTags: React.FC<FileTagsProps> = ({ storageId, file, onTagsUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tags, setTags] = useState<string[]>([]);

  const generateTags = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/ai/tags/${storageId}/${file.path}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('生成标签失败');
      }
      
      const data = await response.json();
      setTags(data.tags);
      onTagsUpdate?.(data.tags);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTagClick = (tag: string) => {
    // 可以在这里添加标签点击事件，例如跳转到标签搜索页面
    console.log('Tag clicked:', tag);
  };

  return (
    <div style={{ marginTop: 16 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <Button
            type="primary"
            icon={<TagsOutlined />}
            onClick={generateTags}
            loading={loading}
          >
            生成标签
          </Button>
          <Button
            icon={<PlusOutlined />}
            onClick={() => {
              // 这里可以添加手动添加标签的功能
              console.log('Add tag clicked');
            }}
          >
            添加标签
          </Button>
        </Space>

        {error && (
          <Alert
            message="错误"
            description={error}
            type="error"
            showIcon
          />
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '10px' }}>
            <Spin size="small" />
          </div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {tags.map((tag, index) => (
              <Tag
                key={index}
                color="blue"
                style={{ cursor: 'pointer' }}
                onClick={() => handleTagClick(tag)}
              >
                {tag}
              </Tag>
            ))}
          </div>
        )}
      </Space>
    </div>
  );
};

export default FileTags; 