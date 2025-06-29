import time
import pickle
import base64
import random
import logging
import functools
import sys
import io
from textwrap import dedent
from IPython.display import Markdown, HTML, display
from botocore.exceptions import ClientError

logging.basicConfig()
logger = logging.getLogger('retry-bedrock-invocation')
logger.setLevel(logging.INFO)

def safe_input(prompt=""):
    """한국어 입력을 안전하게 처리하는 함수"""
    try:
        # stdin 인코딩을 UTF-8로 설정 (이미 읽기 작업이 시작된 경우 예외 처리)
        try:
            if hasattr(sys.stdin, 'reconfigure'):
                sys.stdin.reconfigure(encoding='utf-8')
        except (UnicodeDecodeError, io.UnsupportedOperation):
            # 이미 stdin이 사용 중인 경우 무시
            pass
        
        if prompt:
            print(prompt, end='', flush=True)
        
        # input() 함수 사용으로 변경 (더 안정적)
        user_input = input()
        
        return user_input
        
    except UnicodeDecodeError as e:
        print(f"한국어 입력 오류가 발생했습니다: {e}")
        print("다시 시도해주세요.")
        return safe_input(prompt)
    except Exception as e:
        print(f"입력 오류: {e}")
        # fallback to regular input
        return input(prompt if prompt else "")

def retry(total_try_cnt=5, sleep_in_sec=5, retryable_exceptions=(ClientError,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for cnt in range(total_try_cnt):
                logger.info(f"trying {func.__name__}() [{cnt+1}/{total_try_cnt}]")
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"in retry(), {func.__name__}() returned '{result}'")
                    if result: return result
                except retryable_exceptions as e:
                    # Throttling 에러인지 확인
                    if isinstance(e, ClientError):
                        error_code = e.response['Error']['Code']
                        if error_code == 'ThrottlingException':
                            logger.info(f"in retry(), {func.__name__}() raised ThrottlingException")
                            time.sleep(sleep_in_sec)
                            continue
                    logger.info(f"in retry(), {func.__name__}() raised retryable exception '{e}'")
                    pass
                except Exception as e:
                    logger.info(f"in retry(), {func.__name__}() raised {e}")
                    raise e
                time.sleep(sleep_in_sec)
            logger.info(f"{func.__name__} finally has been failed")
        return wrapper
    return decorator

def to_pickle(obj, path):

    with open(file=path, mode="wb") as f:
        pickle.dump(obj, f)

    print (f'To_PICKLE: {path}')
    
def load_pickle(path):
    
    with open(file=path, mode="rb") as f:
        obj=pickle.load(f)

    print (f'Load from {path}')

    return obj

def to_markdown(obj, path):

    with open(file=path, mode="w") as f:
        f.write(obj)

    print (f'To_Markdown: {path}')
    
def print_html(input_html):

    html_string=""
    html_string = html_string + input_html

    display(HTML(html_string))
    
def get_message_from_string(role, string, imgs=None):
        
    message = {
        "role": role,
        "content": []
    }

    if imgs is not None:
        for img in imgs:
            img_message = {
                "image": {
                    "format": 'png',
                    "source": {"bytes": img}
                }
            }
            message["content"].append(img_message)

    message["content"].append({"text": dedent(string)})

    return message

def _message_format(role, message):

    if role == "user":
         message_format = {
            "role": "user",
            "content": [{"text": dedent(message)}]
        }
    elif role == "assistant":

        message_format = {
            "role": "assistant",
            'content': [{'text': dedent(message)}]
        }

    return message_format
    
    
def _png_to_bytes(file_path):
    """Convert a PNG file to binary data and base64 string.

    Args:
        file_path: Path to the PNG file.

    Returns:
        tuple: (binary_data, base64_string) or error message.
    """
    try:
        with open(file_path, "rb") as image_file:
            # Read file in binary mode
            binary_data = image_file.read()

            # Encode binary data to base64
            base64_encoded = base64.b64encode(binary_data)

            # Decode bytes to string
            base64_string = base64_encoded.decode('utf-8')

            return binary_data, base64_string

    except FileNotFoundError:
        print ("Error: 파일을 찾을 수 없습니다.")
    except Exception as e:
        print (f"Error: {str(e)}")


