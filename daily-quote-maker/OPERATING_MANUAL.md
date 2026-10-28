# Daily Quote Maker v1.1.0 설치·운영·유지보수 매뉴얼

업데이트: 2026-10-29 (Asia/Seoul). 버전은 1.1.0을 유지합니다. 기본 산출물은 사진 위 문학 문구 4:5 JPEG 한 장입니다. 이번 버전은 개인적·비상업적 디자인 검수용이며 자동 제작·게시 중단 상태입니다.

## 1. 파일과 연결
- 저장소: https://github.com/comfunnylj/Video-creator , 브랜치 `claude/eloquent-hamilton-wvxqej`.
- `.claude/skills/daily-quote-maker/SKILL.md`: 에이전트 작업 지침 1.1.0.
- `daily-quote-maker/render_quote_card.py`: 사진·문구 렌더링. `requirements.txt`: Python 패키지.
- `QUALITY_POLICY.md`: 사진 선정과 육안 검수 규칙. `examples/`: 실제 3종 시안과 설정 예제.
- `tests/test_render.py`: 네트워크 없는 회귀 테스트. `CHANGELOG.md`: 변경과 복구 기준.
- `build_publisher_payloads.py`: 기존 게시용 JSON 생성기. 로컬 파일만 만들며 외부 큐에 제출하지 않습니다.
- DB: https://docs.google.com/spreadsheets/d/1be-g64yNrQ6d3bAT-lopUpjZmDRBnhfe_1YAP674BjE/edit . 문구DB 65개와 사진DB·게시이력을 보존합니다. 샘플 제작으로 승인/최근 게시일/성공 이력을 바꾸지 않습니다.
- 프로젝트: https://drive.google.com/drive/folders/1dtgJ6i001xNdCklwWc8u9SJh6OUnFiYA . 완성물은 하위 Output (ID `1hYu1BjrmtG3jBmDrOrRCr7aJpPgYOUPM`)에 보관합니다.
- 스킬·매뉴얼: https://drive.google.com/drive/folders/1bnoleQJiWi9Lz7jjbQnOfKUrC5U-1D_6 . 기존 두 Google Docs의 ID를 유지해 갱신합니다.

## 2. 설치 및 첫 실행
Python 3.11 이상, Pillow 10.4~13, fonttools 4.50 이상/5 미만을 사용합니다. Ubuntu에서는 `fonts-noto-cjk`를 설치하면 Noto Serif CJK 자동 검색이 됩니다. Windows/macOS에서는 한글을 포함한 명조 TTF/TTC의 실제 경로를 JSON의 `font_path` 또는 환경변수 `QUOTE_FONT_PATH`로 지정합니다. 폰트 라이선스는 배포 방식에 맞게 확인합니다. 이번 샘플은 Google Fonts의 Nanum Myeongjo Regular를 사용했습니다.

```bash
python -m pip install -r daily-quote-maker/requirements.txt
python -m unittest discover -s daily-quote-maker/tests -v
python daily-quote-maker/render_quote_card.py --job daily-quote-maker/examples/A_warm_lake.json --output output/A
```

기본 결과: `Q0025_daily_quote_IG_4x5.jpg`, `Q0025_daily_quote_provenance.json`, 원본 증거 `original_photo`. 폴더는 작업별로 분리합니다. 파일명에 날짜/시안명을 붙여 Drive에 저장해도 제작기록과 대응 관계를 함께 기록합니다.

9:16을 추가하려면 아래처럼 명시합니다.

```bash
python daily-quote-maker/render_quote_card.py --job daily-quote-maker/examples/B_star_mountain.json --output output/B --formats 4:5 9:16
python daily-quote-maker/render_quote_card.py --job job.json --config daily-quote-maker/examples/design_config.json --output output/custom
```

GitHub Actions `Daily Quote Maker v1.1 - Quality Test`는 코드 push/PR 때 오프라인 테스트만 수행합니다. 테스트용 단색 이미지는 제품 샘플로 사용하지 않습니다. 실제 사진 시안은 workflow_dispatch에서 render_samples=true를 명시한 경우만 생성합니다. 예약 실행·SNS 게시 단계는 없습니다. 기존 영상용 수동 도구는 이전 기능으로 보존되며 이번 정지사진 제작 경로에 사용하지 않습니다.

## 3. 문구와 사진 준비
사용자 자작 문구는 `user_original=true`로 구분합니다. 제공하지 않은 작가·작품명은 빈 문자열로 유지하며 만들어 넣지 않습니다. 사용자가 지정한 저자·작품명을 표기하려면 `attribution_approved=true`를 명시합니다. 이 예외는 기존 문구DB 65개를 변경하지 않습니다. 전달받은 실제 문구를 대조한 뒤에만 `source_verified=true`를 설정합니다.

DB를 실시간 읽어 quote_id, quote, author, work, quote_reference를 확인합니다. `source_verified=true`는 출처 대조가 완료됐을 때만 씁니다. 원문 보존, 현대어 표기, 자체 번역을 구분해 기록합니다. 카드 줄바꿈은 조정할 수 있지만 문장을 임의로 바꾸지 않습니다. 캡션은 2–4문장으로 작품 맥락을 조용히 설명하고, 확인되지 않은 집필 이유·시기를 만들지 않습니다.

사진 검색은 Unsplash → Pexels → Pixabay → Wikimedia Commons → 공개 아카이브 순으로 진행합니다. `photo.source_url`, `photographer`, `license_url`, `download_url`을 채웁니다. 이미 확보한 실제 원본은 `photo.local_path`로 입력할 수 있지만 출처 필드는 여전히 필수입니다. 실제 디코딩 픽셀 긴 변 3000 이상, 크롭 후 출력보다 큰 원본을 요구합니다. 화면 캡처/작은 미리보기를 확대하지 않습니다.

사진의 정서·여백·최종 크롭을 먼저 봅니다. 사진이 화려해도 글을 놓을 공간이 없으면 탈락입니다. 모든 사진을 어둡게 하거나 채도를 낮추지 않습니다. 영상·타임랩스·하이퍼랩스 및 금지된 Pexels 37522118을 사용하지 않습니다. 카메라 정보와 작가 페이지는 실사 판단의 근거이며 진위를 절대 보장하는 것은 아닙니다.

## 4. JSON 디자인 설정 — 코드 수정 없이 변경
기존 문구 JSON은 호환됩니다. `design.style`을 공통 설정으로, `design.formats['9:16']`을 해당 비율만의 덮어쓰기로 사용합니다. 별도 `--config` 파일이 인라인 design보다 우선하고, CLI --formats가 output_formats보다 우선합니다.

- `preset`: center / upper / side. 중앙/상단/측면의 기본 위치·폭·정렬을 제공합니다.
- `position`: [가로, 세로] 0~1. 글자 전체 블록 중심 위치입니다. 사진 중앙 [0.5,0.43], 상단 [0.5,0.25], 우측 아래 [0.69,0.64] 등을 사용합니다. position을 명시하면 preset 기본 위치보다 우선합니다.
- `max_width`: 화면 너비의 비율. 중앙 .78, 측면 .38~.46 등. 너무 넓거나 안전여백을 넘으면 실패합니다.
- `align`: left / center / right. 지정 폭 내부의 행 정렬입니다.
- `font_path`, `font_index`: TTF/TTC 실제 경로와 TTC 인덱스. 한글이 없는 글꼴은 대체 글리프로 출력하지 않고 실패합니다.
- `font_size`: 본문 픽셀 크기. 기본 38. `min_font_size`: 자동 줄수/공간 조정 시 최저값, 최소 28. 허용 최대 72.
- `line_spacing`: 본문 크기의 배수, 기본 1.65, 허용 1.1~2.2.
- `color`: auto 또는 #RRGGBB. auto는 흰색/아이보리/차콜/검정을 비교합니다. 투명색은 거부합니다.
- `author`, `work`: 각각 font_size/color/gap 별도 지정. gap은 앞 요소 이후 픽셀 간격입니다. 기본 저자 21px·작품 18px이며 본문 최소 크기보다 작아야 합니다.
- `safe_margin`: 가로·세로 가장자리 최소 비율. 기본 .075. 모바일 피드용 최소값이며 모든 앱 오버레이를 자동 보장하지 않습니다. Stories용은 상하 UI도 육안 확인합니다.
- `crop_center`: EXIF 회전 후 원본에서 넘치는 영역 중 어느 쪽을 보존할지 정하는 [가로,세로] 0~1 값입니다. .5는 중앙, 0은 왼쪽/위, 1은 오른쪽/아래 정렬입니다. 최종 feed 이미지를 story로 재사용하지 않습니다.
- `protected_regions`: EXIF 반영 원본 좌표계의 [left,top,right,bottom] 정규화 사각형 목록. 지정 피사체가 잘리거나 글자와 겹치면 실패합니다. 비율별로 별도 지정할 수 있습니다.
- `recommend`: true일 때 현재 위치와 중앙/상단/우측 후보를 로컬 대비·질감·보호영역으로 비교합니다. 피사체 의미를 인식하는 AI 기능이 아니므로 결과를 직접 확인해야 합니다.
- `shadow_opacity`: 기본 0, 최대 45/255. `shadow_offset`은 각 축 절댓값 2px 이하. 외곽선·배경박스·그라데이션 필터는 지원하지 않습니다.
- `contrast_min`: 기본 3.0. `contrast_coverage_min`: 기본 .88. 각 행의 실제 글자 내부에서 대비 조건을 만족하는 픽셀 비율을 검사합니다. 통과가 미적 완성도나 WCAG 인증을 뜻하지 않습니다.

## 5. 검수와 제작기록
원본은 EXIF 회전을 적용한 뒤 실제 픽셀과 프로파일을 확인합니다. ICC가 있으면 sRGB로 변환하고 없으면 sRGB 가정임을 기록합니다. 각 비율을 별도로 크롭하고 LANCZOS 다운샘플링합니다. 출력은 sRGB ICC가 포함된 RGB JPEG quality 96, 4:4:4입니다. 인위적 여백과 블랙바는 넣지 않습니다.

모든 요청 출력은 임시 폴더에서 렌더·검증한 뒤 교체합니다. 두 번째 비율이 실패해도 기존 완성본/제작기록을 유지합니다. 성공한 4:5 전용 재렌더는 같은 문구의 이전 story 파일을 제거합니다. 파일 설치 도중 오류도 이전 파일로 복구를 시도합니다. 여러 파일의 운영체제 차원 동시 원자성이나 동시 실행 잠금까지 보장하는 구조는 아니므로 한 작업 폴더에는 한 번에 한 실행만 사용합니다.

provenance는 원본·출력 SHA256, 실제 픽셀, 크롭 사각형, EXIF, sRGB 처리, 폰트·좌표·서식, 각 행 대비, 유효 설정, 캡션, 출처와 NOT_PUBLISHED 상태를 기록합니다. 자동 생성 시 visual_review는 REQUIRED입니다. 검수자는 별도 QA 기록에 실제로 본 시안·모바일 미리보기·100% 원본 부분·조정 내역을 적습니다. 파일을 열지 않고 완료로 적지 않습니다.

참고 이미지와 나란히 놓고 글자 크기·정서·답답함·주요 피사체·여백·줄바꿈을 봅니다. 360px 모바일 폭에서도 확인합니다. 원본과 최종 크롭의 세부 질감이 충분한지 점검합니다. 참고 스크린샷의 검은 주변은 디자인 요소로 따라 만들지 않습니다.

## 6. 현재 게시 중단 상태와 재개 조건
09:00 예약 ID 6adce8c3eea08191be7dab5261338783은 비활성 상태로 유지합니다. Threads tasks.json의 quote만 enabled=false로 변경했고 quote.json의 jobs=[]를 확인합니다. 다른 브리핑/쇼핑/부동산 수신 작업과 Instagram outbox는 수정하지 않습니다.

현재 버전은 어떤 샘플도 SNS에 게시하지 않습니다. 사용자가 결과를 검수하고 별도로 재개를 지시하기 전에는 자동화 재활성화/예약 생성/큐 제출을 하지 않습니다. 기존 build_publisher_payloads.py는 호환성 검증용 로컬 어댑터로 보존했습니다. --approved-for-posting 없이 실패하며, 이 플래그를 사용해 로컬 JSON을 만들었다고 게시 승인/서버 접수/게시 성공이 되는 것은 아닙니다.

향후 재개 시: 실제 문구/완성 이미지/본문의 승인 → 채널별 계정·서버 상태 → SHA 고정 이미지·파일 해시 → 안정적 중복 키 → 기존 큐 프로토콜 → 실제 공개 URL 순으로 확인합니다. unknown 상태에는 새 중복 키로 반복 제출하지 않습니다. 게시이력은 실제 공개 URL이 확인됐을 때만 갱신합니다.

## 7. 저장·유지보수·복구
완성 JPEG 3종과 선택 story, 출처/제작 JSON, 캡션, QA 비교/미리보기/테스트 결과를 Output에 저장합니다. 원본 사진은 필요시 별도 source 파일로 기록하며 미리보기로 대신하지 않습니다. 저장 후 같은 파일 ID를 다시 조회해 이름·부모·크기/해상도·수정시각을 확인합니다.

설정 수정 → 오프라인 테스트 → 실제 샘플 → 이미지 육안 검수 → Git 커밋 → 기존 Drive 문서 갱신 순으로 진행합니다. 기존 문구DB·사진DB·게시이력은 유지합니다. 게시 재개 여부는 별도 사용자 지시로만 바꿉니다.

v1.0 원본은 기준 커밋 46d6966b646b365b90e89ba182ccceb575cae38b에 있습니다. 되돌릴 때는 그 커밋의 해당 스킬/렌더러/정책만 새 커밋으로 복원하고 관련 테스트를 수행합니다. 다른 프로젝트의 변경이나 DB를 되돌리지 않습니다. 전체 브랜치 강제 리셋은 피합니다. GitHub에 파일이 있다는 이유만으로 계정 전체 ChatGPT 스킬 설치를 완료했다고 표현하지 않습니다.

## 8. v1.1 시안과 출처
2026-10-29 재검증: 공통 requirements.txt를 모든 정지사진 렌더 워크플로에 적용하고 회귀 테스트를 19개로 확장했습니다. 과거 fontTools 누락 실패는 c85a850에서 이미 수정됐으며 후속 렌더 성공을 확인했습니다. 최신 코드와 보관 원본으로 6장을 재출력하고 육안 검수했습니다. C의 9:16 문구를 [0.72,0.63]에서 [0.72,0.50]으로 이동해 출처 주변 반사광을 줄였습니다. 상세 근거와 한계는 REVALIDATION_20261029.md를 확인합니다. 이미지 서버가 지연될 경우 검증된 보관 원본을 local_path로 지정하고 원래 출처·촬영자·라이선스를 유지합니다. 네트워크 장애를 화질 검사 통과로 처리하지 않습니다.

A: Q0025, 예이츠 / 이니스프리의 호수 섬, 기존 DB 자체 번역. Brandi Alexandra, Unsplash zn-fKdxc2R8, 실제 3024×4032. 따뜻한 호수 노을에 44px 검정 상단 배치.
B: Q0039, 윤동주 / 별 헤는 밤, 靑春을 청춘으로 표기. Elijah Grimm, Unsplash -YFE6ThVMjU, 실제 4000×5262. 별밤 설산에 36px 아이보리 상단 배치.
C: Q0036, 한용운 / 님의 침묵, DB 현대어 발췌. mathieu gauzy, Unsplash bCaEKOnl-uk, 실제 2000×3000. 반짝이는 바닷물에 36px 아이보리 우측 배치. 사진은 프랑스 Collioure이며 시 속 장소라고 주장하지 않습니다.
사진 3장 모두 작가 페이지·카메라 정보·Unsplash License를 확인했습니다. JPEG는 각각 1080×1350, 선택 story는 각각 1080×1920입니다. 폰트/크롭/최종 대비의 상세 수치는 함께 저장하는 provenance와 QA_REPORT를 봅니다.
