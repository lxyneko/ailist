import React, { useState } from 'react';
import { Card, Typography, Spin, Alert, Tabs } from 'antd';
import { FileTextOutlined, CodeOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface AIAnalysisPanelProps {
  storageId: number;
  file: any;
  onClose: () => void;
}

const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({ storageId, file, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);

  const analyzeFile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/ai/analyze/${storageId}/${file.path}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('分析文件失败');
      }
      
      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (file) {
      analyzeFile();
    }
  }, [file]);

  const renderTextAnalysis = () => (
    <div>
      <Title level={4}>文本摘要</Title>
      <Text>{analysis?.summary}</Text>
      
      <Title level={4} style={{ marginTop: 16 }}>关键词</Title>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {analysis?.keywords?.map((keyword: string, index: number) => (
          <Text key={index} code>{keyword}</Text>
        ))}
      </div>
    </div>
  );

  const renderCodeAnalysis = () => (
    <div>
      <Title level={4}>代码说明</Title>
      <Text>{analysis?.description}</Text>
      
      <Title level={4} style={{ marginTop: 16 }}>优化建议</Title>
      <ul>
        {analysis?.suggestions?.map((suggestion: string, index: number) => (
          <li key={index}><Text>{suggestion}</Text></li>
        ))}
      </ul>
    </div>
  );

  return (
    <Card
      title="AI 分析"
      extra={<a onClick={onClose}>关闭</a>}
      style={{ width: '100%', maxWidth: 800, margin: '0 auto' }}
    >
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" />
          <Text style={{ display: 'block', marginTop: 16 }}>正在分析文件...</Text>
        </div>
      )}

      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
        />
      )}

      {!loading && !error && analysis && (
        <Tabs defaultActiveKey="analysis">
          <TabPane
            tab={
              <span>
                {file.name.endsWith(('.py', '.js', '.java', '.cpp', '.go')) ? (
                  <CodeOutlined />
                ) : (
                  <FileTextOutlined />
                )}
                分析结果
              </span>
            }
            key="analysis"
          >
            {file.name.endsWith(('.py', '.js', '.java', '.cpp', '.go'))
              ? renderCodeAnalysis()
              : renderTextAnalysis()}
          </TabPane>
        </Tabs>
      )}
    </Card>
  );
};

export default AIAnalysisPanel; 