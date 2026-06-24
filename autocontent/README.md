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

## 자동 발행 + 매일 스케줄링 (핵심)

"생성"에서 끝나지 않고, **매일 알아서 콘텐츠가 쌓이고 사이트로 배포**되게 만든다.

```
topics.txt 큐 ─▶ 매일 cron(GitHub Actions) ─▶ 미생성 주제 1건 생성
            ─▶ content/ 에 커밋(누적 보관) ─▶ build_site.py 로 site/ 빌드
            ─▶ Cloudflare Pages 자동 배포
```

- **`topics.txt`**: 주제 큐. 채워두면 매일 위에서부터 아직 안 만든 주제를 1건씩 처리.
- **`content/`**: 생성 결과가 누적되는 보관 폴더(레포에 커밋됨).
- **`build_site.py`**: `content/` → 갤러리형 정적 사이트 `site/` 빌드(의존성 0).

### 로컬에서 사이트 빌드

```bash
python main.py --from-queue topics.txt --out content   # 다음 주제 1건 생성
python build_site.py                                     # content/ → site/
# site/index.html 을 열면 전체 글 갤러리
```

### GitHub Actions 설정 (`.github/workflows/daily-content.yml`)

매일 06:00 KST 자동 실행. 활성화하려면 레포 **Settings → Secrets and variables → Actions** 에 등록:

| 종류 | 이름 | 값 |
|------|------|-----|
| Secret | `OPENAI_API_KEY` | chatanywhere 무료 키 |
| Secret | `OPENAI_BASE_URL` | `https://api.chatanywhere.tech/v1` (선택) |
| Secret | `CLOUDFLARE_API_TOKEN` | Cloudflare Pages 배포 토큰 (선택) |
| Secret | `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 계정 ID (선택) |
| Variable | `WRITER_MODEL` / `TTS_VOICE` | 모델/음성 오버라이드 (선택) |

> Cloudflare 시크릿이 없으면 **생성·커밋까지만** 수행하고 배포 단계는 자동으로 건너뛴다.
> 수동 실행은 Actions 탭의 **Run workflow** 로 가능.

### Cloudflare Pages 최초 1회 준비

```bash
npx wrangler pages project create autocontent   # 프로젝트 생성(1회)
```

## 다음 확장 (로드맵)

- **벡터DB 연동**: 생성한 글을 Chroma/Qdrant 에 임베딩해 주제 중복 방지·재활용
- **숏폼화**: 썸네일 + 내레이션 → ffmpeg 로 9:16 영상 합성 후 자동 업로드
- **트렌드 자동 수집**: 큐를 수동 관리 대신 트렌드 API/RSS 로 자동 채우기
