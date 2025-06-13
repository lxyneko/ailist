import requests
import json
import time

def test_ai_config():
    # 测试配置API
    config_url = 'http://localhost:5000/ai/config'
    
    try:
        # 设置API密钥
        api_key = input("请输入你的DeepSeek API密钥: ")
        print(f"正在发送配置请求到 {config_url}...")
        response = requests.post(
            config_url,
            json={'deepseek_api_key': api_key},
            timeout=10
        )
        print("配置API响应状态码:", response.status_code)
        print("配置API响应:", response.json())
        
        # 获取配置
        print(f"正在获取配置从 {config_url}...")
        response = requests.get(config_url, timeout=10)
        print("获取配置响应状态码:", response.status_code)
        print("当前配置:", response.json())
        
    except requests.exceptions.ConnectionError as e:
        print("连接错误:", str(e))
        print("请确保后端服务正在运行，并且监听在 http://localhost:5000")
    except requests.exceptions.Timeout as e:
        print("请求超时:", str(e))
    except requests.exceptions.RequestException as e:
        print("请求错误:", str(e))
    except Exception as e:
        print("未知错误:", str(e))

def test_file_analysis():
    # 测试文件分析API
    file_id = 1  # 假设文件ID为1
    analysis_url = f'http://localhost:5000/ai/analyze/{file_id}'
    result_url = f'http://localhost:5000/ai/analysis/{file_id}'
    
    try:
        print(f"正在发送文件分析请求到 {analysis_url}...")
        response = requests.post(analysis_url, timeout=30)
        print("文件分析响应状态码:", response.status_code)
        print("文件分析响应:", response.json())
        
        # 等待分析完成
        print("等待分析完成...")
        time.sleep(2)
        
        # 获取分析结果
        print(f"正在获取分析结果从 {result_url}...")
        response = requests.get(result_url, timeout=10)
        print("获取分析结果响应状态码:", response.status_code)
        print("分析结果:", response.json())
        
    except requests.exceptions.ConnectionError as e:
        print("连接错误:", str(e))
        print("请确保后端服务正在运行，并且监听在 http://localhost:5000")
    except requests.exceptions.Timeout as e:
        print("请求超时:", str(e))
    except requests.exceptions.RequestException as e:
        print("请求错误:", str(e))
    except Exception as e:
        print("未知错误:", str(e))

if __name__ == '__main__':
    print("=== 开始测试 AI 配置 ===")
    test_ai_config()
    
    print("\n=== 开始测试文件分析 ===")
    test_file_analysis() 