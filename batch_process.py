import os
import time
import requests

# 获取当前脚本所在的目录
script_directory = os.path.dirname(os.path.abspath(__file__))

# ToDo 设置API密钥和API基础URL
api_key = ""
api_base_url = ""

# ToDo 设置文本分段长度
text_segment_length = 3000

# TODO 设置最大重试次数
max_retry_attempts = 10

# TODO 设置重试之间的等待时间（秒）
retry_wait_time_seconds = 120

# TODO 设置输入文件夹和输出文件夹的相对路径
input_folder_path = os.path.join(script_directory, "input")
output_folder_path = os.path.join(script_directory, "output")

# TODO 设置使用的模型
model_name = "gpt-3.5-turbo"

# TODO 设置提示信息
prompt_message = ("这是一场研讨会语音转文字的文稿, 可能有多个发言人, 很多口语化的内容, "
                  "很多激烈的讨论, 希望你改成语义通顺, 表达书面化的文章, 对于很长一段, 可以分段"
                  "很多可能是转文字的问题, 有些实在无法理解, 你可以选择舍弃"
                  "有些可能是错别字, 你可以选择修改")

# 创建输出文件夹
os.makedirs(output_folder_path, exist_ok=True)

# 读取长文本文件
def read_long_text_file(file_path):
    with open(file_path, "r") as file:
        long_text = file.read()
    return long_text

# 使用GPT API生成文本
def generate_text_with_api(segment):
    request_url = f"{api_base_url}/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key
    }
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": prompt_message},
            {"role": "user", "content": segment}
        ]
    }

    for attempt in range(max_retry_attempts):  # 尝试发送请求max_retry_attempts次
        try:
            response = requests.post(request_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
        except Exception as e:
            print(f"An unexpected error: {e}")
        
        if attempt < max_retry_attempts - 1:  # 如果还没有尝试max_retry_attempts次，那么等待retry_wait_time_seconds秒然后重试
            print("Waiting before retrying...")
            time.sleep(retry_wait_time_seconds)

    print("Failed to get a successful response after max retries")
    return ""

def process_long_text(input_folder, output_folder):
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 构建输入文件的完整路径
        input_file_path = os.path.join(input_folder, filename)

        # 读取输入文件的内容
        long_text = read_long_text_file(input_file_path)

        # 按照每text_segment_length个字符分隔长文本
        text_segments = [long_text[i:i+text_segment_length] for i in range(0, len(long_text), text_segment_length)]

        # 构建输出文件的完整路径
        output_file_path = os.path.join(output_folder, filename)

        # 打开输出文件
        with open(output_file_path, "w") as file:
            # 逐步处理分隔后的文本
            for segment in text_segments:
                # 使用GPT API生成文本
                generated_text = generate_text_with_api(segment)
                print("------------")
                print("Generated text[:300]:")
                print(generated_text[:300])

                # 将生成的文本写入到输出文件中
                file.write(generated_text)

        print(f"文件 {filename} 处理完成")

    print("所有文件处理完成")


# 执行长文本处理
process_long_text(input_folder_path, output_folder_path)
