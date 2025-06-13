import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import AISettings from '@/components/AISettings';

const Logo = () => (
  <svg width="48" height="48" viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="brainGradient" x1="64" y1="40" x2="64" y2="88" gradientUnits="userSpaceOnUse">
        <stop stopColor="#38BDF8"/>
        <stop offset="1" stopColor="#34D399"/>
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <path d="M99.5 60C108 60 112 69.5 110.5 76.5C114.5 79.5 113.5 88.5 107 91.5C100.5 102 86.5 100 80.5 96.5C77.5 104.5 65.5 105 60.5 99C53.5 101.5 45.5 98.5 43 91.5C36 94 28 89.5 28.5 82C23 80 20.5 71.5 25 66.5C21.5 60 27.5 53 34.5 53C37.5 44.5 49 41.5 56.5 47.5C62.5 40.5 74.5 42 79.5 48.5C87.5 44 94 49 99.5 60Z" fill="transparent" stroke="#4B5563" strokeWidth="2"/>
    <g filter="url(#glow)">
      <path d="M64 54C61.2386 54 59 56.2386 59 59V64H54C51.2386 64 49 66.2386 49 69C49 71.7614 51.2386 74 54 74H59V79C59 81.7614 61.2386 84 64 84C66.7614 84 69 81.7614 69 79V74H74C76.7614 74 79 71.7614 79 69C79 66.2386 76.7614 64 74 64H69V59C69 56.2386 66.7614 54 64 54Z" fill="url(#brainGradient)"/>
      <path d="M64 40V49M64 89V98M88 64H97M40 64H49M80 48L85 43M48 80L43 85M80 80L85 85M48 48L43 43" stroke="url(#brainGradient)" strokeWidth="3" strokeLinecap="round"/>
    </g>
  </svg>
);

export default function Settings() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = React.useState('local');
  const [storages, setStorages] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetchStorages();
  }, []);

  const fetchStorages = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/storages');
      if (!response.ok) throw new Error('获取存储列表失败');
      const data = await response.json();
      setStorages(data);
    } catch (error) {
      toast({
        title: '错误',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const type = formData.get('type') as string;
    const name = formData.get('name') as string;
    let config = {};

    switch (type) {
      case 'local':
        config = {
          path: formData.get('path'),
        };
        break;
      case 'webdav':
        config = {
          url: formData.get('url'),
          username: formData.get('username'),
          password: formData.get('password'),
          path: formData.get('path') || '/',
        };
        break;
      case 's3':
        config = {
          endpoint: formData.get('endpoint'),
          access_key: formData.get('access_key'),
          secret_key: formData.get('secret_key'),
          bucket: formData.get('bucket'),
          region: formData.get('region') || 'us-east-1',
          path: formData.get('path') || '/',
        };
        break;
    }

    try {
      const response = await fetch('http://localhost:8000/api/storages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          type,
          config: JSON.stringify(config),
        }),
      });

      if (!response.ok) throw new Error('添加存储失败');
      
      toast({
        title: '成功',
        description: '存储后端添加成功',
      });
      
      fetchStorages();
      (e.target as HTMLFormElement).reset();
    } catch (error) {
      toast({
        title: '错误',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/storages/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('删除存储失败');
      
      toast({
        title: '成功',
        description: '存储后端删除成功',
      });
      
      fetchStorages();
    } catch (error) {
      toast({
        title: '错误',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-10">
      <div className="flex items-center space-x-4 mb-8">
        <Logo />
        <h1 className="text-3xl font-bold">设置</h1>
      </div>
      
      <div className="grid gap-6">
        <Tabs defaultValue="storage" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="storage">存储设置</TabsTrigger>
            <TabsTrigger value="ai">AI 设置</TabsTrigger>
          </TabsList>
          
          <TabsContent value="storage">
            <Card>
              <CardHeader>
                <CardTitle>添加存储后端</CardTitle>
                <CardDescription>配置新的存储后端以扩展存储能力</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="name">名称</Label>
                      <Input id="name" name="name" placeholder="输入存储后端名称" required />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="type">类型</Label>
                      <Select name="type" value={activeTab} onValueChange={setActiveTab}>
                        <SelectTrigger>
                          <SelectValue placeholder="选择存储类型" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="local">本地存储</SelectItem>
                          <SelectItem value="webdav">WebDAV</SelectItem>
                          <SelectItem value="s3">S3 兼容存储</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Tabs value={activeTab} onValueChange={setActiveTab}>
                      <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="local">本地存储</TabsTrigger>
                        <TabsTrigger value="webdav">WebDAV</TabsTrigger>
                        <TabsTrigger value="s3">S3 兼容存储</TabsTrigger>
                      </TabsList>
                      <TabsContent value="local" className="space-y-4">
                        <div className="grid gap-2">
                          <Label htmlFor="path">存储路径</Label>
                          <Input id="path" name="path" placeholder="输入本地存储路径" required />
                        </div>
                      </TabsContent>
                      <TabsContent value="webdav" className="space-y-4">
                        <div className="grid gap-2">
                          <Label htmlFor="url">服务器地址</Label>
                          <Input id="url" name="url" placeholder="输入 WebDAV 服务器地址" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="username">用户名</Label>
                          <Input id="username" name="username" placeholder="输入用户名" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="password">密码</Label>
                          <Input id="password" name="password" type="password" placeholder="输入密码" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="path">存储路径</Label>
                          <Input id="path" name="path" placeholder="输入存储路径" />
                        </div>
                      </TabsContent>
                      <TabsContent value="s3" className="space-y-4">
                        <div className="grid gap-2">
                          <Label htmlFor="endpoint">服务器地址</Label>
                          <Input id="endpoint" name="endpoint" placeholder="输入 S3 服务器地址" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="access_key">Access Key</Label>
                          <Input id="access_key" name="access_key" placeholder="输入 Access Key" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="secret_key">Secret Key</Label>
                          <Input id="secret_key" name="secret_key" type="password" placeholder="输入 Secret Key" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="bucket">Bucket</Label>
                          <Input id="bucket" name="bucket" placeholder="输入 Bucket 名称" required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="region">区域</Label>
                          <Input id="region" name="region" placeholder="输入区域" defaultValue="us-east-1" />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="path">存储路径</Label>
                          <Input id="path" name="path" placeholder="输入存储路径" />
                        </div>
                      </TabsContent>
                    </Tabs>
                  </div>
                  <Button type="submit">添加存储后端</Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>已配置的存储后端</CardTitle>
                <CardDescription>管理已添加的存储后端</CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-4">加载中...</div>
                ) : storages.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">暂无存储后端</div>
                ) : (
                  <div className="space-y-4">
                    {storages.map((storage: any) => (
                      <Card key={storage.id}>
                        <CardHeader>
                          <div className="flex justify-between items-start">
                            <div>
                              <CardTitle>{storage.name}</CardTitle>
                              <CardDescription>类型: {storage.type}</CardDescription>
                            </div>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDelete(storage.id)}
                            >
                              删除
                            </Button>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
                            {JSON.stringify(JSON.parse(storage.config), null, 2)}
                          </pre>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai">
            <AISettings />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 