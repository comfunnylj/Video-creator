# Daily Quote Maker v1.1.0 — 운영 상태 (2026-10-25 KST)

## 2026-10-29 재검증 보완
- 아래 본문은 10월 25일 배포 기록이다. 최신 재검증은 REVALIDATION_20261029.md를 따른다.
- 과거 fontTools 누락은 기존 c85a850에서 수정됐고 후속 자작시 렌더 40195857726 및 회귀 40195843730 성공을 직접 확인했다. 10월 27–28일 조회된 quote issue 실행은 skipped로, 실패 렌더가 아니었다.
- 현재 보완본에서 회귀 테스트 19개 통과 및 A/B/C 4:5·9:16 총 6장 재렌더를 확인했다. C story 위치를 조정하고 실제 육안 검수를 다시 수행했다. 자작시 워크플로 의존성을 공통 requirements로 통일했다.
- 기존 Drive 문서와 샘플 파일은 ID를 유지해 갱신한다. 이번 저장 확인은 Output의 storage_verification.json에 기록한다. DB·SNS 큐에 새 쓰기 요청은 하지 않는다. 자동 제작·게시는 중단 유지한다.

## 현재 상태: 디자인 검수 완료 / 자동 제작·게시 중단
- 구현 커밋: https://github.com/comfunnylj/Video-creator/commit/1d1d6981e3a3db9ec5b2772b522b60a8c99d5e2a
- GitHub Actions 회귀 테스트 성공: https://github.com/comfunnylj/Video-creator/actions/runs/40194080421
- 로컬 회귀 테스트 16개 통과. 원본 사진 3종으로 4:5 3장과 선택 9:16 3장을 렌더하고 참고 비교·360px 미리보기·100% 디테일을 실제 확인했습니다.
- 사진별 중앙/상단/측면 배치, 명조 서식과 JSON 설정, 독립 크롭, EXIF/ICC, 네이티브 픽셀/글리프/가독성/피사체 보호/출력 검사와 실패 복구를 구현했습니다.
- 기본 출력은 1080×1350 sRGB JPEG 한 장이며 1080×1920은 명시한 경우만 추가합니다.

## 자동화 및 SNS
- Daily Quote Maker 자동화 ID 6adce8c3eea08191be7dab5261338783: is_enabled=false 상태 확인, 재활성화하지 않음.
- telegram-market-feed의 Threads quote 수신 작업만 enabled=false로 변경했습니다.
- quote.json의 jobs=[] 확인. 서버 상태 조회에도 quote 작업이 없었습니다.
- 기존 아침/저녁/에너지/쇼핑/기타/부동산 작업 설정은 변경 전과 동일함을 대조했습니다.
- Instagram outbox는 수정하지 않았습니다. 이번 작업에서 Instagram/Threads 게시 또는 새 예약 작업을 생성하지 않았습니다.
- 사용자가 완성 이미지 검수 후 재개를 지시하기 전에는 자동 제작·게시를 재개하지 않습니다.

## 데이터와 저장 검증
- 기존 문구DB 65개, 사진DB 6행, 게시이력은 읽기만 했으며 수정하지 않았습니다.
- 기존 Google Docs 스킬 원본·운영매뉴얼은 같은 ID로 v1.1 내용으로 갱신한 뒤 본문 버전·중단 규칙·구현 커밋을 재조회했습니다.
- 스킬/정책/변경이력 원본 Markdown도 지정 Skill & Manual 폴더에 저장하고 메타데이터를 재조회했습니다.
- 프로젝트 Output에 시안 JPEG 6장, 원본 사진 3장, 제작 JSON·캡션·비교판·원본 디테일·검수/테스트/릴리스 기록 등을 저장했습니다.
- 최초 20개 결과 파일의 ID·크기·부모 폴더를 모두 재조회해 로컬 크기와 대조했고, 별도 storage_verification.json도 저장·재조회했습니다. 원격 체크섬 필드는 연결 도구가 노출하지 않으므로 원격 해시 검증을 주장하지 않습니다.
- Output: https://drive.google.com/drive/folders/1hYu1BjrmtG3jBmDrOrRCr7aJpPgYOUPM
- 매뉴얼: https://docs.google.com/document/d/1NI1Cc2Ovr3WC1ZBQ7eKC6QJvZLfCUJi2jjvAGpwox9w
- 스킬 원본 문서: https://docs.google.com/document/d/1HFH5SGb0CpJsSI-XnpEjKLt4K_hkkRbYwujmSmHSA0I

## 유지보수상 제한
- 자동 배치 추천은 대비·질감·명시된 보호영역 기반 휴리스틱입니다. 피사체 의미나 감성 품질을 자동으로 보장하지 않습니다.
- 같은 작업 폴더의 동시 렌더는 지원하지 않습니다. 작업별 출력 폴더를 분리하고 한 번에 한 실행을 사용합니다.
- 출처 검증/시안 제작/사용자의 권리 판단/실제 SNS 게시는 별도 단계입니다. 모든 이번 시안은 NOT_PUBLISHED입니다.
