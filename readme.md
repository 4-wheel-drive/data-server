# FastAPI 프로젝트 실행 가이드

<br>
<br>


## 1. 가상환경 세팅
### 1-1. 가상환경 생성
```bash
.\venv\Scripts\Activate

Mac
python -m venv venv
```
venv 폴더가 생성됩니다. (깃허브에는 업로드하지 않습니다)

### 1-2. 가상환경 활성화
``` bash
Windows (PowerShell)
.\venv\Scripts\Activate


Windows (cmd)
venv\Scripts\activate.bat


Mac/Linux
source venv/bin/activate
```
활성화되면 터미널 앞에 (venv) 표시가 뜹니다.


### 1-3. 의존성 설치
```bash
pip install -r requirements.txt
```

<br>
<br>


## 2. 서버 실행
### 2-1. 개발 서버 실행
```bash
uvicorn app.main:app --reload
```

- app.main:app → app 폴더 안의 main.py에서 app 객체 실행
- --reload → 코드 변경 시 자동 재시작 (개발용 옵션)

### 2-2. 접속 방법
- 기본 주소: http://127.0.0.1:8000
- API 문서 (Swagger): http://127.0.0.1:8000/docs
- API 문서 (ReDoc): http://127.0.0.1:8000/redoc

### 3. 참고
- .env 파일은 환경 변수 관리용이며, 깃허브에 올리지 않습니다.
- 가상환경(venv) 폴더도 .gitignore에 반드시 포함되어야 합니다.
