# Python 3.9 기반 이미지 사용
FROM python:3.9

# Python 인코딩으로 UTF-8 사용
ENV PYTHONIOENCODING=utf-8

# 컨테이너 내의 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리와 모든 파일을 /app으로 복사
COPY . .

# pip 업그레이드
RUN pip install --upgrade pip

# 의존성 설치
RUN pip install -r requirements.txt

# 앱 실행 명령어 설정
CMD ["python", "wsgi.py"]