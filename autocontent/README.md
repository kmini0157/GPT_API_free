# AutoContent — 0원 콘텐츠 자동화 파이프라인

주제 하나만 던지면 **리서치 → 글 작성 → 썸네일 → 내레이션 → 발행물**까지
한 번에 만들어주는 개인용 콘텐츠 생성 도구. LLM 키 하나를 빼면 전부 무료·무가입 서비스로 돌아간다.

```
트렌드 수집 ─▶ ⓪ 중복검사(벡터DB) ─▶ ① 리서치(Jina, 키X) ─▶ ② 글 작성(무료 GPT키)
        ─▶ ③ 썸네일(Pollinations, 키X) ─▶ ④ 내레이션(edge-tts, 키X)
        ─▶ ⑤ 숏폼 영상(ffmpeg, 9:16) ─▶ ⑥ article.md · index.html · short.mp4 · meta.json
```

## 무엇을 쓰나 (전부 무료)

| 단계 | 서비스 | 키 필요? |
|------|--------|----------|
| 트렌드 수집 | Google Trends RSS / Hacker News | ❌ |
| 중복 방지 | 무료 임베딩 API + [Chroma](https://www.trychroma.com)(없으면 JSON 폴백) | ✅ (LLM 키 재사용) |
| 리서치 | [Jina Reader/Search](https://jina.ai) | ❌ |
| 글 작성 | [chatanywhere 무료 GPT API](https://api.chatanywhere.tech/v1/oauth/free/render) | ✅ (무료 발급) |
| 썸네일 | [Pollinations](https://pollinations.ai) | ❌ |
| 내레이션 | [edge-tts](https://github.com/rany2/edge-tts) | ❌ |
| 숏폼 영상 | ffmpeg (썸네일+내레이션 → 9:16 mp4) | ❌ |

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
python main.py "주제" --dedupe        # 벡터DB로 유사 주제 중복 방지
python main.py "주제" --no-video      # 숏폼 영상 건너뛰기
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

## 트렌드 자동 수집 (큐 자동 충전)

큐를 손으로 안 채워도 트렌딩 주제를 끌어와 `topics.txt` 에 추가한다(키 불필요).

```bash
python fill_queue.py --source trends --geo KR --limit 5   # Google Trends 일일 인기검색
python fill_queue.py --source hn --limit 5                 # Hacker News 인기글
```

이미 큐에 있는 주제는 자동으로 건너뛴다. 매일 워크플로우가 생성 직전에 한 번 실행한다.

## 중복 방지 (벡터DB)

`--dedupe` 를 켜면 생성 전 주제를 **무료 임베딩 API**로 벡터화해, 기존 글과의 의미 유사도가
`DEDUPE_THRESHOLD`(기본 0.88)를 넘으면 생성을 건너뛴다. 저장소는 **Chroma**(설치 시) →
없으면 의존성 없는 **JSON 폴백**을 자동 선택한다. 임베딩 호출이 실패하면 중복검사를 생략하고
생성은 막지 않는다(graceful).

```bash
pip install chromadb          # 선택: Chroma 사용 시. 안 깔면 JSON 폴백
python main.py --from-queue topics.txt --out content --dedupe
```

## 숏폼 영상화

썸네일과 내레이션이 모두 있으면 ffmpeg 로 **9:16 세로 영상(`short.mp4`)**을 합성한다.
영상이 있으면 글 페이지·갤러리에서 ▶ 배지와 함께 영상이 우선 노출된다.
ffmpeg 가 없으면 자동으로 건너뛴다(GitHub 러너엔 기본 설치).

## 다음 확장 (로드맵)

- **자동 업로드**: `short.mp4` → 유튜브 Shorts / 인스타 릴스 API 자동 게시
- **드로우텍스트 자막**: 내레이션 타임코드 기반 자막 번인
- **A/B 썸네일**: 여러 이미지 프롬프트 생성 후 클릭률로 자동 선택
