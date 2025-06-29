"""
Entry point script for the LangGraph Demo.
"""
import os
import sys
import shutil
import locale
import streamlit as st
from src.workflow import run_agent_workflow

# Set UTF-8 encoding for Korean input support
if sys.platform.startswith('win'):
    # Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'
else:
    # macOS/Linux
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            pass

def remove_artifact_folder(folder_path="./artifacts/"):
    """
    ./artifact/ 폴더가 존재하면 삭제하는 함수
    
    Args:
        folder_path (str): 삭제할 폴더 경로
    """
    if os.path.exists(folder_path):
        print(f"'{folder_path}' 폴더를 삭제합니다...")
        try:
            # 폴더와 그 내용을 모두 삭제
            shutil.rmtree(folder_path)
            print(f"'{folder_path}' 폴더가 성공적으로 삭제되었습니다.")
        except Exception as e:
            print(f"오류 발생: {e}")
    else:
        print(f"'{folder_path}' 폴더가 존재하지 않습니다.")

def execution(user_query):

    remove_artifact_folder()
    result = run_agent_workflow(
        user_input=user_query,
        debug=False
    )

    # Print the conversation history
    print("\n=== Conversation History ===")
    print ("result", result)
    for history in result["history"]:

        print ("===")
        print (f'agent: {history["agent"]}')
        print (f'message: {history["message"]}')

    return result
    

if __name__ == "__main__":

    remove_artifact_folder()

    if len(sys.argv) > 1: 
        user_query = " ".join(sys.argv[1:])
    else: 
        try:
            user_query = input("Enter your query (한국어 입력 가능): ")
        except UnicodeDecodeError:
            print("한국어 입력 오류가 발생했습니다. 다시 시도해주세요.")
            user_query = input("Enter your query: ")
        
    result = run_agent_workflow(user_input=user_query, debug=False)

    # Print the conversation history
    print("\n=== Conversation History ===")
    print ("result", result)
    for history in result["history"]:

        print ("===")
        print (f'agent: {history["agent"]}')
        print (f'message: {history["message"]}')