<div align="center">
<img src="./images/logo.png" alt="icon" width="50px"/>
<h1 align="center">GPT-API-free 한국어 가이드</h1>

GPT · DeepSeek · Claude · Gemini · Grok · Qwen 등을 무료/저가로 사용할 수 있는 OpenAI 호환 API

[무료 Key 발급](https://api.chatanywhere.tech/v1/oauth/free/render) / [활용 가이드](./USAGE.ko.md) / [공식 API 문서](https://docs.chatanywhere.tech/) / [잔액·사용량 조회](https://api.chatanywhere.tech/) / [서비스 상태](https://status.chatanywhere.tech/) / [中文 README](./README.md)

</div>

## 이 서비스가 뭔가요?

[ChatAnywhere](https://api.chatanywhere.tech/)가 운영하는 **OpenAI 호환 API 중계 서비스**입니다.
GitHub 계정만 있으면 무료 API Key를 발급받아, OpenAI API를 지원하는 모든 앱·라이브러리에서
GPT, DeepSeek 등의 모델을 바로 사용할 수 있습니다.

- 인터페이스가 OpenAI 공식 API와 100% 동일 → **Base URL과 Key만 바꾸면** 기존 코드/앱이 그대로 동작
- 별도 결제 수단 등록 없이 무료 Key만으로 시작 가능
- 무료 Key는 **개인 · 비상업 · 교육 · 연구 용도로만** 사용 가능 (상업적 사용 금지)

## 3분 빠른 시작

### 1. 무료 API Key 발급

👉 **[여기서 GitHub 계정으로 무료 Key 발급](https://api.chatanywhere.tech/v1/oauth/free/render)**

### 2. 엔드포인트(Base URL) 선택

| Base URL | 설명 |
| --- | --- |
| `https://api.chatanywhere.org/v1` | **해외(한국 포함)용 — 한국에서는 이쪽 권장** |
| `https://api.chatanywhere.tech/v1` | 중국 내 가속 회선 |

> 둘 다 같은 Key로 동작합니다. 응답이 느리면 다른 쪽으로 바꿔서 테스트해 보세요.

### 3. 동작 테스트 (curl)

```bash
curl https://api.chatanywhere.org/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 발급받은_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "안녕하세요!"}]
  }'
```

응답이 오면 성공입니다. 🎉

## 무료 Key 사용 한도

| 모델 | 하루 무료 한도 |
| --- | --- |
| gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano, gpt-5-mini, gpt-5-nano, gpt-3.5-turbo | **200회/일** |
| deepseek-r1, deepseek-v3, deepseek-v3-2-exp | 30회/일 |
| gpt-5 시리즈, gpt-4o, gpt-4.1 | 5회/일 |

주의사항:

- 무료 Key는 **IP당·Key당 200요청/일** 제한이 있습니다 (chat과 embedding은 각각 200회로 별도 계산).
  한 IP에서 여러 Key를 쓰거나, 한 Key를 여러 IP에서 써도 합산 200회를 넘을 수 없습니다.
- 무료 Key의 gpt-5 계열은 추론 능력이 제한되어 있습니다. 더 강한 추론이 필요하면 유료 Key를 고려하세요.
- 오류가 나면 먼저 [서비스 상태 페이지](https://status.chatanywhere.tech/)를 확인하세요.
- 남용이 감지된 Key는 예고 없이 차단될 수 있습니다.

### 용도별 추천 모델 (무료 Key 기준)

| 용도 | 추천 모델 | 이유 |
| --- | --- | --- |
| 일상 질문·요약·번역 | `gpt-4o-mini` | 하루 200회, 빠르고 무난한 품질 |
| 코딩·조금 더 나은 품질 | `gpt-5-mini` | 하루 200회, mini 중 최신 세대 |
| 깊은 추론이 필요할 때 | `deepseek-r1` | 하루 30회, 추론 특화 |
| 최고 품질 (아껴 쓰기) | `gpt-5`, `gpt-4o` | 하루 5회뿐이므로 중요한 질문에만 |

## 포함된 도구 — 설치 없이 바로 쓰기

이 저장소에는 터미널에서 바로 쓸 수 있는 도구 3종이 포함되어 있습니다.
자세한 활용법·레시피는 **[활용 가이드 (USAGE.ko.md)](./USAGE.ko.md)** 를 보세요.

```bash
pip install openai
export OPENAI_API_KEY="발급받은_KEY"   # Windows PowerShell: setx OPENAI_API_KEY "발급받은_KEY"
```

### [`chat.py`](./chat.py) — 대화형 채팅

```bash
python chat.py
```

| 명령어 | 기능 |
| --- | --- |
| `/new` | 대화 기록 초기화 (새 대화 시작) |
| `/model 모델명` | 사용 모델 변경 (예: `/model deepseek-r1`) |
| `/save [파일명]` | 대화를 마크다운 파일로 저장 |
| `/usage` | 오늘 사용량 확인 |
| `/help` / `/exit` | 도움말 / 종료 |

```bash
python chat.py --model gpt-5-mini                      # 다른 모델로 시작
python chat.py --system "당신은 친절한 코딩 튜터입니다."  # 시스템 프롬프트 지정
```

### [`ask.py`](./ask.py) — 원샷 질문 (파이프 지원)

```bash
python ask.py "파이썬에서 리스트 뒤집는 법"
cat 문서.txt | python ask.py -p 요약        # 프리셋: 번역/요약/교정/영작/설명/커밋
git diff | python ask.py -p 커밋            # diff로 커밋 메시지 생성
```

### [`usage.py`](./usage.py) — 사용량·한도 확인

```bash
python usage.py           # 오늘 사용량 + 남은 무료 한도 추정 (로컬 기록 기준)
python usage.py --remote  # 서버에서 잔액·최근 24시간 사용량 조회 (모든 앱 사용분 포함)
python usage.py --week    # 최근 7일
python usage.py --check   # Key 유효성 확인
```

## 코드에서 사용하기

### Python

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://api.chatanywhere.org/v1",
)

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "안녕하세요!"}],
)
print(resp.choices[0].message.content)
```

### Node.js

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: "https://api.chatanywhere.org/v1",
});

const resp = await client.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [{ role: "user", content: "안녕하세요!" }],
});
console.log(resp.choices[0].message.content);
```

스트리밍을 포함한 전체 예제는 [`demo/`](./demo) 폴더를 참고하세요
(Python · Node.js · Java · Go).

## 다른 앱·도구에 연결하기

OpenAI API를 지원하는 앱이라면 설정에서 아래 두 값만 바꾸면 됩니다.

| 설정 항목 | 값 |
| --- | --- |
| API Key | 발급받은 Key |
| Base URL (API Host / Endpoint / 프록시 주소) | `https://api.chatanywhere.org` 또는 `.../v1` |

> 앱에 따라 `/v1`까지 입력해야 하는 경우와 도메인만 입력하는 경우가 있습니다.
> 연결이 안 되면 `/v1`을 붙였다 떼어 보세요.

자주 쓰이는 도구: ChatBox, LobeChat, Open WebUI, 沉浸式翻译(Immersive Translate),
utools, VS Code 확장 등 — 자세한 방법은 [공식 소프트웨어 연동 문서](https://docs.chatanywhere.tech/doc-5547696) 참고.

## 유료 Key

무료 한도가 부족하면 [유료 Key](https://api.chatanywhere.tech/#/shop/)를 쓸 수 있습니다.

- 요청 횟수 제한 없음, 더 빠르고 안정적
- OpenAI 공식과 동일한 토큰 기준 과금, 공식보다 저렴
- 잔액 유효기간 없음 (영구)
- Claude, Gemini, Grok, Qwen, Kimi 등 더 많은 모델 지원
- 전체 모델·가격표: [中文 README의 가격표](./README.md#付费版支持模型) 또는 [공식 가격 문서](https://docs.chatanywhere.tech/doc-2694962)

## 문제 해결 (FAQ)

**Q. 응답이 없거나 오류가 나요.**
[status.chatanywhere.tech](https://status.chatanywhere.tech/)에서 서비스 상태를 먼저 확인하세요.
정상인데도 안 되면 Base URL(`.org` ↔ `.tech`)을 바꿔 보세요.

**Q. `401 Unauthorized` 오류가 나요.**
Key 오타이거나 Base URL이 `api.openai.com`으로 되어 있는 경우입니다.
이 Key는 **chatanywhere 주소로만** 동작하며 OpenAI 공식 주소로는 사용할 수 없습니다.

**Q. `429` 또는 한도 초과 오류가 나요.**
해당 모델의 하루 무료 한도를 소진한 것입니다. 다음 날까지 기다리거나, 한도가 넉넉한
모델(`gpt-4o-mini` 등)로 바꾸거나, 유료 Key를 사용하세요.

**Q. 사용량은 어디서 확인하나요?**
[api.chatanywhere.tech](https://api.chatanywhere.tech/)에서 Key를 입력하면 잔액·사용 기록을 볼 수 있습니다. 공지사항도 이곳에 올라옵니다.

**Q. 내 대화 내용이 저장되나요?**
이 프로젝트는 입력/출력 텍스트를 수집·저장하지 않는다고 명시하고 있습니다.
단, OpenAI 공식 정책에 따라 OpenAI 측에서 30일간 데이터를 보관할 수 있습니다.

## 링크 모음

- 🔑 [무료 Key 발급](https://api.chatanywhere.tech/v1/oauth/free/render)
- 📖 [공식 API 문서](https://docs.chatanywhere.tech/)
- 💰 [잔액·사용량 조회 및 공지](https://api.chatanywhere.tech/)
- 🛒 [유료 Key 구매](https://api.chatanywhere.tech/#/shop/)
- 📡 [서비스 상태](https://status.chatanywhere.tech/)
- 🐛 [이슈 제보 (원본 저장소)](https://github.com/chatanywhere/GPT_API_free/issues)
