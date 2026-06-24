# AutoContent — 0원 콘텐츠 자동화 파이프라인

주제 하나만 던지면 **리서치 → 글 작성 → 썸네일 → 내레이션 → 발행물**까지
한 번에 만들어주는 개인용 콘텐츠 생성 도구. LLM 키 하나를 빼면 전부 무료·무가입 서비스로 돌아간다.

```
주제 ─▶ ① 리서치(Jina, 키X) ─▶ ② 글 작성(무료 GPT키)
     ─▶ ③ 썸네일(Pollinations, 키X) ─▶ ④ 내레이션(edge-tts, 키X)
     ─▶ ⑤ article.md · index.html · narration.mp3 · meta.json
```

## 무엇을 쓰나 (전부 무료)

| 단계 | 서비스 | 키 필요? |
|------|--------|----------|
| 리서치 | [Jina Reader/Search](https://jina.ai) | ❌ |
| 글 작성 | [chatanywhere 무료 GPT API](https://api.chatanywhere.tech/v1/oauth/free/render) | ✅ (무료 발급) |
| 썸네일 | [Pollinations](https://pollinations.ai) | ❌ |
| 내레이션 | [edge-tts](https://github.com/rany2/edge-tts) | ❌ |

## 설치

```bash
cd autocontent
pip install -r requirements.txt
cp .env.example .env       # .env 에 무료 LLM 키 입력
```

무료 키 발급: https://api.chatanywhere.tech/v1/oauth/free/render

## 사용

```bash
python main.py "양자컴퓨터가 RSA 암호를 깨는 원리"
```

옵션:

```bash
python main.py "주제" --no-image      # 썸네일 건너뛰기
python main.py "주제" --no-voice      # 음성 건너뛰기
python main.py "주제" --no-research   # Jina 리서치 건너뛰기(LLM만)
```

결과는 `output/<주제>/` 에 생성된다. `index.html` 을 브라우저로 열면 글·썸네일·음성을 한 페이지에서 확인할 수 있다.

## 결과물

```
output/양자컴퓨터가-rsa-암호를-깨는-원리/
├── article.md      # 마크다운 글
├── index.html      # 공유용 미리보기 페이지 (글+이미지+음성)
├── thumbnail.jpg   # 썸네일
├── narration.mp3   # 내레이션 음성
└── meta.json       # 제목/요약/태그/스크립트/에셋 메타데이터
```

`meta.json` 은 다음 단계 자동화(블로그/유튜브 자동 발행 봇)가 그대로 읽어 쓸 수 있도록 구조화돼 있다.

## 다음 확장 (로드맵)

- **발행 자동화**: `meta.json` → Cloudflare Pages / 티스토리 / 유튜브 자동 업로드
- **스케줄링**: GitHub Actions 로 매일 트렌드 주제 자동 생성
- **벡터DB 연동**: 생성한 글을 Chroma/Qdrant 에 임베딩해 중복 방지·재활용
- **숏폼화**: 썸네일 + 내레이션 → ffmpeg 로 9:16 영상 합성
