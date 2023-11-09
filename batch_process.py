import os
import time
import requests

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# ToDo 设置API密钥和API基础URL
api_key = ""
api_base = ""

# ToDo 设置segment长度
segment_len = 3000

# ToDo 设置重试次数
max_retries = 10

# ToDo 设置重试sleep多少秒
sleep_sec = 120

# ToDo 设置输入文件夹和输出文件夹的相对路径
input_folder = os.path.join(script_dir, "input")
output_folder = os.path.join(script_dir, "output")

# ToDo 设置模型
model = "gpt-4"

# ToDo 设置prompt
prompt = "这是一场研讨会语音转文字的文稿, 可能有多个发言人, 很多口语化的内容, \
        很多激烈的讨论, 希望你改成语义通顺, 表达书面化的文章, 对于很长一段, 可以分段\
            很多可能是转文字的问题, 有些实在无法理解, 你可以选择舍弃\
                有些可能是错别字, 你可以选择修改"

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)

# 读取长文本文件
def read_long_text_file(file_path):
    with open(file_path, "r") as file:
        long_text = file.read()
    return long_text

# 使用GPT API生成文本
def generate_text(segment):
    system_intel = prompt
    url = f"{api_base}/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_intel},
            {"role": "user", "content": segment}
        ]
    }

    for i in range(max_retries):  # 尝试发送请求max_retries次
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                print(f"Request failed with status code {response.status_code}")
                print(f"Response body: {response.text}")
                if i < max_retries:  # 如果还没有尝试max_retries次，那么等待120秒然后重试
                    print("Waiting before retrying...")
                    time.sleep(sleep_sec)    
                continue
            return response.json()['choices'][0]['message']['content']

        except requests.exceptions.JSONDecodeError:
            print("Failed to decode the response as JSON.")
            if i < max_retries:  # 如果还没有尝试max_retries次，那么等待120秒然后重试
                print("Waiting before retrying...")
                time.sleep(sleep_sec)
                
        except Exception as e:
            print(f"Failed to get a successful response due to an unexpected error: {e}")
            if i < max_retries:  # 如果还没有尝试max_retries次，那么等待120秒然后重试
                print("Waiting before retrying...")
                time.sleep(sleep_sec)
            
    print("Failed to get a successful response after max retries")
    return ""


def process_long_text(input_folder, output_folder):
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 构建输入文件的完整路径
        input_file = os.path.join(input_folder, filename)

        # 读取输入文件的内容
        long_text = read_long_text_file(input_file)

        # 按照每segment_len个字符分隔长文本
        segments = [long_text[i:i+segment_len] for i in range(0, len(long_text), segment_len)]

        # 构建输出文件的完整路径
        output_file = os.path.join(output_folder, filename)

        # 打开输出文件
        with open(output_file, "w") as file:
            # 逐步处理分隔后的文本
            for segment in segments:
                # 使用GPT API生成文本
                generated_text = generate_text(segment)
                print("------------")
                print("Generated text[:300]:")
                print(generated_text[:300])

                # 将生成的文本写入到输出文件中
                file.write(generated_text)

        print(f"文件 {filename} 处理完成")

    print("所有文件处理完成")


# 执行长文本处理
process_long_text(input_folder, output_folder)
