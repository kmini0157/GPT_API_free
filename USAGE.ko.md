# 활용 가이드 — 이렇게 쓰면 좋습니다

무료 API Key(하루 200회)를 **일상에서 최대한 뽑아 쓰는 방법**을 정리한 문서입니다.
키 발급과 기본 개념은 [README.ko.md](./README.ko.md)를 먼저 보세요.

## 목차

1. [포함된 도구 3종](#1-포함된-도구-3종)
2. [최초 1회 설정](#2-최초-1회-설정)
3. [일상 활용 레시피](#3-일상-활용-레시피)
4. [alias 등록 — `gpt 질문` 한 단어로 쓰기](#4-alias-등록--gpt-질문-한-단어로-쓰기)
5. [하루 200회 쿼터 전략](#5-하루-200회-쿼터-전략)
6. [다른 앱에 연결하기](#6-다른-앱에-연결하기)
7. [문제가 생겼을 때](#7-문제가-생겼을-때)

## 1. 포함된 도구 3종

| 도구 | 언제 쓰나 | 실행 |
| --- | --- | --- |
| [`chat.py`](./chat.py) | 이어지는 대화가 필요할 때 (질문을 주고받으며 발전) | `python chat.py` |
| [`ask.py`](./ask.py) | 한 번 묻고 답만 받으면 될 때 (번역·요약·커밋 메시지 등) | `python ask.py "질문"` |
| [`usage.py`](./usage.py) | 오늘 몇 회 썼는지, 한도가 얼마나 남았는지 확인 | `python usage.py` |

- **chat.py**: 스트리밍 대화, `/model`로 모델 전환, `/save`로 대화를 마크다운 저장, `/usage`로 사용량 확인
- **ask.py**: 파이프 입력 지원(`cat 파일 | python ask.py ...`), 프리셋 6종(번역/요약/교정/영작/설명/커밋)
- **usage.py**: chat.py/ask.py가 자동 기록한 로컬 사용량을 무료 한도와 비교해서 보여줌.
  `--remote`를 붙이면 공식 잔액 조회 페이지와 같은 API로 **모든 앱에서의 사용량**을 서버에서 직접 조회

## 2. 최초 1회 설정

```bash
pip install openai
```

API Key를 **영구 등록**해 두면 매번 입력할 필요가 없습니다.

**macOS / Linux** — `~/.bashrc` 또는 `~/.zshrc`에 추가:

```bash
export OPENAI_API_KEY="발급받은_KEY"
```

추가 후 `source ~/.bashrc` (또는 새 터미널).

**Windows (PowerShell)** — 한 번만 실행하면 영구 등록:

```powershell
setx OPENAI_API_KEY "발급받은_KEY"
```

등록 후 **새 터미널**을 열어야 적용됩니다.

> 참고: 이 Key는 OpenAI 공식 Key가 아니므로, `OPENAI_API_KEY`를 공식 Key와 같이 써야 하는 환경이라면
> 대신 `CHATANYWHERE_API_KEY` 환경변수를 쓰면 됩니다 (이 저장소의 도구들이 우선 인식).

## 3. 일상 활용 레시피

### 번역 — 한↔영 자동

```bash
python ask.py -p 번역 "이 프로젝트는 아직 실험 단계입니다."
python ask.py -p 번역 "The quick brown fox jumps over the lazy dog."
cat 영어기사.txt | python ask.py -p 번역        # 파일 통째로 번역
```

### 요약 — 긴 글을 불릿으로

```bash
cat 회의록.md | python ask.py -p 요약
curl -s https://example.com/article | python ask.py -p 요약   # 웹페이지 요약(텍스트 위주 페이지)
```

### 글 교정 — 맞춤법·어색한 표현

```bash
python ask.py -p 교정 "오늘 회의에서 논의됬던 안건들을 정리해서 보내드리겠습니다"
cat 자기소개서.txt | python ask.py -p 교정
```

### 영어 이메일 작성

```bash
python ask.py -p 영작 "다음 주 화요일 미팅을 금요일로 옮길 수 있는지 정중하게 묻는 메일"
```

### 개발 작업

```bash
# 에러 원인 분석
python 내스크립트.py 2>&1 | python ask.py "이 에러 원인이 뭐야?"

# git diff로 커밋 메시지 자동 생성
git diff --staged | python ask.py -p 커밋

# 코드 설명
cat 복잡한코드.py | python ask.py -p 설명

# 쉘 명령어 물어보기
python ask.py "특정 확장자 파일만 찾아서 크기순 정렬하는 리눅스 명령어"
```

### 공부

```bash
python ask.py -p 설명 "파이썬 데코레이터"
python ask.py -m deepseek-r1 "이 수학 문제 풀이 과정을 보여줘: ..."   # 추론이 필요하면 deepseek-r1
```

### 이어지는 대화가 필요할 때

```bash
python chat.py --system "당신은 친절한 코딩 튜터입니다. 한국어로 답하세요."
```

대화 중 `/model deepseek-r1`로 모델을 바꾸고, 끝나면 `/save`로 기록을 남길 수 있습니다.

## 4. alias 등록 — `gpt 질문` 한 단어로 쓰기

매번 `python ask.py`를 치기 귀찮다면 alias를 등록하세요.
(아래에서 `~/GPT_API_free`는 이 저장소를 clone한 실제 경로로 바꾸세요.)

**macOS / Linux** — `~/.bashrc` 또는 `~/.zshrc`:

```bash
alias gpt='python3 ~/GPT_API_free/ask.py'
alias gptchat='python3 ~/GPT_API_free/chat.py'
alias 번역='python3 ~/GPT_API_free/ask.py -p 번역'
alias 요약='python3 ~/GPT_API_free/ask.py -p 요약'
```

이후:

```bash
gpt "점심 메뉴 추천해줘"
cat 문서.txt | 요약
번역 "안녕하세요"
```

**Windows (PowerShell)** — `notepad $PROFILE`로 프로필을 열고 추가:

```powershell
function gpt { python $HOME\GPT_API_free\ask.py @args }
function gptchat { python $HOME\GPT_API_free\chat.py @args }
```

## 5. 하루 200회 쿼터 전략

무료 Key는 모델별로 하루 한도가 다릅니다. **기본은 넉넉한 모델을 쓰고, 아까운 한도는 필요할 때만** 쓰는 게 요령입니다.

| 한도 | 모델 | 이렇게 쓰세요 |
| --- | --- | --- |
| 200회/일 | `gpt-4o-mini`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-3.5-turbo` | **기본값.** 번역·요약·일상 질문은 전부 이걸로 |
| 30회/일 | `deepseek-r1`, `deepseek-v3`, `deepseek-v3-2-exp` | 수학·논리·복잡한 추론이 필요할 때만 |
| 5회/일 | `gpt-5`, `gpt-4o`, `gpt-4.1` | 하루 5번뿐. 정말 중요한 질문에만 |

실전 팁:

- **한 번에 몰아서 묻기**: "A 해줘. 그리고 B도. 마지막으로 C까지" — 요청 1회로 계산되므로 관련 작업은 한 질문에 묶는 게 이득입니다.
- **대화가 길어질수록 무료 한도만 소모**되니, 새 주제는 `chat.py`에서 `/new`로 초기화하고 시작하세요 (요청당 횟수는 같지만 응답 속도·품질에 유리).
- 남은 횟수가 궁금하면:

```bash
python usage.py            # 오늘 로컬 사용량 + 남은 한도 추정 (이 컴퓨터의 chat.py/ask.py 기준)
python usage.py --remote   # 서버에서 잔액·최근 24시간 사용량 조회 (모든 앱 사용분 포함)
```

> 기본 표시는 **이 컴퓨터에서 chat.py/ask.py로 쓴 횟수**만 셉니다.
> 브라우저 확장 등 다른 앱에서 쓴 횟수까지 보려면 `--remote`를 쓰거나
> [api.chatanywhere.tech](https://api.chatanywhere.tech/)에서 Key를 입력해 확인하세요.
> (`--remote`는 조회 전용 API라 채팅 한도를 소모하지 않습니다.)

## 6. 다른 앱에 연결하기

OpenAI API를 지원하는 앱이라면 대부분 연결됩니다. 공통 원칙:

- **API Key**: 발급받은 chatanywhere Key
- **Base URL / API Host**: `https://api.chatanywhere.org` (앱에 따라 `/v1`까지 필요)

| 앱 | 설정 위치 | 입력값 |
| --- | --- | --- |
| Immersive Translate (몰입형 번역) | 설정 → 번역 서비스 → OpenAI → 사용자 정의 API 주소 | `https://api.chatanywhere.org/v1/chat/completions` (전체 경로 필요할 수 있음) + Key + 모델명 `gpt-4o-mini` |
| ChatBox | 설정 → 모델 제공자 → OpenAI API → API 호스트 | `https://api.chatanywhere.org` + Key |
| Open WebUI | 관리자 설정 → 연결 → OpenAI API | URL `https://api.chatanywhere.org/v1` + Key |
| VS Code Continue | `config.yaml`의 models 항목 | `provider: openai`, `apiBase: https://api.chatanywhere.org/v1`, `apiKey`, `model: gpt-4o-mini` |
| VS Code Cline | 설정 → API Provider → OpenAI Compatible | Base URL `https://api.chatanywhere.org/v1` + Key + 모델명 |

> 연결이 안 되면: ① URL 끝에 `/v1`을 붙이거나 빼 보기 ② 모델명을 직접 입력(`gpt-4o-mini`) ③ [상태 페이지](https://status.chatanywhere.tech/) 확인.
> 더 많은 앱 연동법: [공식 소프트웨어 사용 문서 (중국어)](https://docs.chatanywhere.tech/doc-5547696)

**주의**: 브라우저 확장(번역 등)은 페이지당 요청이 여러 번 나갈 수 있어 200회 한도가 금방 소진됩니다.
몰입형 번역을 많이 쓴다면 "단락당 요청 수" 같은 옵션을 조정하거나 유료 Key를 고려하세요.

## 7. 문제가 생겼을 때

| 증상 | 원인·해결 |
| --- | --- |
| `401 Unauthorized` | Key 오타, 또는 Base URL이 `api.openai.com`으로 되어 있음. chatanywhere 주소로만 동작 |
| `429` / 한도 초과 | 해당 모델 하루 한도 소진. `gpt-4o-mini` 등 200회 모델로 전환하거나 내일 재시도 |
| 응답이 느리거나 끊김 | Base URL을 `.org` ↔ `.tech`로 바꿔 테스트. [상태 페이지](https://status.chatanywhere.tech/) 확인 |
| 갑자기 Key가 안 됨 | 남용 감지로 차단됐을 수 있음. [원본 저장소 이슈](https://github.com/chatanywhere/GPT_API_free/issues) 또는 QQ 그룹으로 문의 |
| 모델을 못 찾는다는 오류 | 모델명 오타 확인. 무료 Key가 지원하는 모델인지 확인 (5절 표 참고) |
