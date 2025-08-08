# conftest.py
import sys
import os

# 현재 파일의 경로에서 두 단계 상위 디렉터리(프로젝트 루트)를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))