import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

const AISettings: React.FC = () => {
  const [deepseekApiKey, setDeepseekApiKey] = useState('');
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchAIConfig();
  }, []);

  const fetchAIConfig = async () => {
    try {
      const response = await fetch('/api/ai/config');
      if (!response.ok) throw new Error('获取AI配置失败');
      const data = await response.json();
      setDeepseekApiKey(data.deepseek_api_key || '');
    } catch (error) {
      toast({
        title: '错误',
        description: error instanceof Error ? error.message : '获取AI配置失败',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/ai/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          deepseek_api_key: deepseekApiKey,
        }),
      });

      if (!response.ok) throw new Error('保存AI配置失败');

      toast({
        title: '成功',
        description: 'AI配置已保存',
      });
    } catch (error) {
      toast({
        title: '错误',
        description: error instanceof Error ? error.message : '保存AI配置失败',
        variant: 'destructive',
      });
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
    <Card>
      <CardHeader>
        <CardTitle>AI 设置</CardTitle>
        <CardDescription>配置 AI 服务相关的设置</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="deepseekApiKey">DeepSeek API 密钥</Label>
            <Input
              id="deepseekApiKey"
              type="password"
              value={deepseekApiKey}
              onChange={(e) => setDeepseekApiKey(e.target.value)}
              placeholder="输入 DeepSeek API 密钥"
            />
          </div>
          <Button type="submit">保存设置</Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default AISettings; 