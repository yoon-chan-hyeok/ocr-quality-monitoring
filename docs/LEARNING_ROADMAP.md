# Learning & Engineering Roadmap

이 저장소는 현재 다섯 프로젝트 중 학습을 통해 가장 크게 확장할 프로젝트입니다.

## 1. 데이터 파이프라인

- Pydantic 기반 OCR event schema
- idempotent batch ingestion과 실패 레코드 격리
- PostgreSQL에 문서·실행·feature·검수 결과 저장
- 시간창 집계 SQL과 데이터 품질 테스트

**완료 증거:** 손상·중복·지연 이벤트를 포함한 통합 테스트

## 2. 통계적 모니터링

- PSI, KS, Jensen-Shannon divergence의 가정과 한계 학습
- 계절성·문서 유형을 고려한 baseline window
- alert precision, Precision@k, Risk Lift, calibration 평가
- 다중 신호 가중치와 threshold를 validation set에서만 결정

**완료 증거:** 합성 drift 주입 실험과 false alert 분석

## 3. 백엔드·운영

- FastAPI ingestion/query API
- background worker와 retry/dead-letter 처리
- metrics·structured logging·alert runbook
- Docker Compose와 CI 회귀 테스트

**완료 증거:** 입력 분포 변화 주입 → 경보 → 검수 → 재보정 end-to-end demo

