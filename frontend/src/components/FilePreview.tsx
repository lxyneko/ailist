import React, { useState } from 'react';
import { Card, Tabs, Button, Space, Modal } from 'antd';
import { RobotOutlined, TagsOutlined, SearchOutlined } from '@ant-design/icons';
import AIAnalysisPanel from './AIAnalysisPanel';
import FileTags from './FileTags';
import SimilarFiles from './SimilarFiles';

interface FilePreviewProps {
  storageId: number;
  file: any;
  onFileSelect: (file: any) => void;
}

const FilePreview: React.FC<FilePreviewProps> = ({
  storageId,
  file,
  onFileSelect
}) => {
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const [showTags, setShowTags] = useState(false);
  const [showSimilar, setShowSimilar] = useState(false);

  const renderPreview = () => {
    if (!file) return null;

    // 根据文件类型渲染不同的预览
    if (file.type === 'directory') {
      return <div>这是一个目录</div>;
    }

    // 这里可以添加更多文件类型的预览支持
    return <div>文件预览内容</div>;
  };

  return (
    <Card
      title={file?.name}
      extra={
        <Space>
          <Button
            icon={<RobotOutlined />}
            onClick={() => setShowAIAnalysis(true)}
          >
            AI 分析
          </Button>
          <Button
            icon={<TagsOutlined />}
            onClick={() => setShowTags(true)}
          >
            标签
          </Button>
          <Button
            icon={<SearchOutlined />}
            onClick={() => setShowSimilar(true)}
          >
            相似文件
          </Button>
        </Space>
      }
    >
      {renderPreview()}

      <Modal
        title="AI 分析"
        open={showAIAnalysis}
        onCancel={() => setShowAIAnalysis(false)}
        footer={null}
        width={800}
      >
        <AIAnalysisPanel
          storageId={storageId}
          file={file}
          onClose={() => setShowAIAnalysis(false)}
        />
      </Modal>

      <Modal
        title="文件标签"
        open={showTags}
        onCancel={() => setShowTags(false)}
        footer={null}
      >
        <FileTags
          storageId={storageId}
          file={file}
        />
      </Modal>

      <Modal
        title="相似文件"
        open={showSimilar}
        onCancel={() => setShowSimilar(false)}
        footer={null}
        width={800}
      >
        <SimilarFiles
          storageId={storageId}
          file={file}
          onFileSelect={(file) => {
            onFileSelect(file);
            setShowSimilar(false);
          }}
        />
      </Modal>
    </Card>
  );
};

export default FilePreview; 