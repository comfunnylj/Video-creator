# Daily Quote Maker v1.0 — 운영 상태 (2026-10-25 KST)

## 검증 완료
- 정식 GitHub 프로젝트 스킬: `.claude/skills/daily-quote-maker/SKILL.md`
- 이미지 제작기: `daily-quote-maker/render_quote_card.py` (4:5, 9:16; 원본 고해상도 확인)
- 게시 payload 검증기: `daily-quote-maker/build_publisher_payloads.py` (인스타그램/Threads 구분, 체크섬, 중복 키)
- 원본 사진 품질 기준: `daily-quote-maker/QUALITY_POLICY.md`; 타임랩스/하이퍼랩스/저화질 업스케일 금지
- 실사 사진을 사용한 GitHub Actions 테스트 성공: https://github.com/comfunnylj/Video-creator/actions/runs/40115310525
- Google Sheets: https://docs.google.com/spreadsheets/d/1be-g64yNrQ6d3bAT-lopUpjZmDRBnhfe_1YAP674BjE/edit
  - 문구DB: 65개 문장 (권리 판단은 사용자)
  - 사진DB: 서울 사진 6개 (P001 사용 검수 완료, P002~P006 원본 검수 대기)
  - 게시이력 탭은 실제 게시 URL 확인 후에만 갱신
- Google Drive 결과물: https://drive.google.com/drive/folders/1dtgJ6i001xNdCklwWc8u9SJh6OUnFiYA
- Google Drive Skill & Manual: https://drive.google.com/drive/folders/1bnoleQJiWi9Lz7jjbQnOfKUrC5U-1D_6
- Threads quote 전용 입력 큐: `comfunnylj/telegram-market-feed/social-publisher/automation/quote.json`
- Threads `quote` 태스크 2026-10-25에 enabled=true로 변경; 실제 Oracle bridge 응답에 quote.enabled=true / account genie_carrot / task error=null 확인.
  - 실서버 read-only probe: https://github.com/comfunnylj/Video-creator/actions/runs/40142750048
- ChatGPT recurring automation `Daily Quote Maker` 한국시간 매일 09:00 활성화 (아직 첫 실행 전).

## 아직 완료되지 않은 범위
- Instagram 및 Threads에 Daily Quote Maker 명언을 **실제로 게시했다는 URL은 확인되지 않았습니다**.
- 문구DB '게시 승인' 상태는 현재 초기 미승인 상태여서, 예약 작업은 승인 전 이미지/글 생성과 보관까지 진행하는 안전모드입니다.
- 원본 사진 추가 5개는 검색 메타데이터 확인만 끝나고 실제 결과물 육안 검수 전입니다.
- 기존 Google Docs 운영 문서 자체는 별도 존재하나, 사진DB 및 수신 활성화 변경사항의 문서 내 동기화는 추가 점검 필요.

## 유지보수
1. 문구 추가/수정: Google Sheets 문구DB, 사진 추가/검증: 사진DB
2. 이미지 품질/타이포: `render_quote_card.py` + `QUALITY_POLICY.md`
3. 운영 절차: `SKILL.md` 및 Google Drive 매뉴얼
4. 자동 게시: 문구/이미지의 실제 게시 승인, 서버/계정 건강 상태, 중복 키, SNS 결과 permalink 모두 충족
5. 코드 변경 뒤 GitHub Actions QA 실행 → 실제 제작본 확인 → Google Drive 보관 → 버전 번호 갱신
