# git-stats-card

[English](README.md) | [한국어](readme_ko.md)

브라우저, Canvas 또는 무거운 렌더링 런타임 없이 네이티브 SVG로 생성되는
빠르고 서버리스 친화적인 GitHub 프로필 카드입니다.

```md
![GitHub 통계](https://your-deployment.vercel.app/api/card?username=octocat&theme=3d-card)
```

## 테마

| 테마 | 특징 |
| --- | --- |
| `3d-card` | 그라데이션 표면, 깊이 레이어, 플로팅 애니메이션 |
| `cyberpunk` | 네온 광원, 그리드, 스캔라인, 글리치 타이포그래피 |
| `retro-pixel` | 선명한 8비트 테두리, 아케이드 색상, 블록형 막대 |
| `minimal-dark` | 절제된 글라스 표면과 은은한 포인트 조명 |

테마 사용 예시:

```text
/api/card?username=octocat&theme=cyberpunk
/api/card?username=octocat&theme=retro-pixel&animation=false
/api/card?username=octocat&theme=minimal-dark&show_langs=false
/api/card?username=octocat&bg_color=101828&text_color=f8fafc&border_radius=8
```

## API

`GET /api/card` (`/api/badge` 별칭도 지원)

| 매개변수 | 필수 | 기본값 | 허용 값 |
| --- | --- | --- | --- |
| `username` | 예 | — | 유효한 GitHub 사용자 이름 |
| `theme` | 아니요 | `3d-card` | `3d-card`, `cyberpunk`, `retro-pixel`, `minimal-dark` |
| `show_langs` | 아니요 | `true` | 불리언 |
| `border_radius` | 아니요 | `14` | 0–20 사이의 정수 |
| `bg_color` | 아니요 | 테마 기본값 | `#` 포함 여부와 관계없는 3자리 또는 6자리 16진수 |
| `text_color` | 아니요 | 테마 기본값 | `#` 포함 여부와 관계없는 3자리 또는 6자리 16진수 |
| `animation` | 아니요 | `true` | 불리언 |

카드는 `image/svg+xml` 형식으로 반환되며 CDN 캐시는 4시간,
stale-while-revalidate 기간은 1일입니다. `GET /health`에서 서비스 상태를
확인할 수 있습니다.

## GitHub 데이터

최적화된 단일 GraphQL 요청으로 프로필 정보, 최근 1년 커밋, Pull Request,
이슈, 기여한 저장소 수, 저장소의 스타 및 언어별 바이트 수를 가져옵니다.
소유한 비포크 저장소가 100개를 초과하는 계정은 후속 페이지를 조회해 스타와
언어 통계의 전체 합계를 계산합니다. GitHub GraphQL API는 전체 기간의 커밋
합계를 제공하지 않으므로 카드에는 최근 1년 동안의 커밋 수가 표시됩니다.

`GITHUB_TOKEN`이 없거나 업스트림 요청이 실패하고 `MOCK_FALLBACK`이
활성화되어 있으면, 서비스는 결정적인 미리보기 데이터를 반환하고
`X-Git-Stats-Source: fallback` 헤더를 추가합니다. 존재하지 않는 GitHub
사용자는 폴백하지 않고 404 카드를 반환합니다.

## 로컬 개발

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn api.index:app --reload
```

브라우저에서 `http://localhost:8000/api/card?username=octocat`을 엽니다.

테스트 실행:

```bash
pytest
```

## Vercel 배포

1. Vercel에서 저장소를 가져옵니다.
2. `GITHUB_TOKEN`을 암호화된 환경 변수로 추가합니다.
3. 배포합니다. 포함된 `vercel.json`이 요청을 FastAPI 진입점으로 전달합니다.

공개 프로필 데이터를 조회할 때 토큰에 별도의 저장소 권한은 필요하지 않습니다.
토큰을 카드 URL에 넣거나 소스 코드에 커밋하지 마세요.

## 아키텍처

```text
api/index.py              FastAPI 라우트 및 응답 정책
src/github_client.py      GraphQL 요청, 응답 파싱, 폴백
src/cache.py              비동기 TTL 캐시 및 중복 요청 병합
src/renderers/            순수 SVG 테마 렌더러
src/utils/                이스케이프, 형식화, 색상 유틸리티
tests/                    API, 파서 및 렌더러 테스트
```

## 라이선스

MIT
