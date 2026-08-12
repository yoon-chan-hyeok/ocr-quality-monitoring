# 미구현 운영 확장 계획

현재 저장소는 JSONL batch를 처리하는 CLI와 synthetic fixture를 제공합니다. 아래 항목은 아직 구현하지 않은 학습·확장 후보입니다.

## 데이터와 모니터링

- OCR event schema, idempotent ingestion과 실패 record 격리
- PostgreSQL에 document, run, feature와 review 결과 저장
- 문서 유형과 계절성을 반영한 baseline window
- drift 주입 평가, alert Precision@k, Risk Lift와 false alert 분석

## 서비스

- FastAPI ingestion/query API와 background worker
- retry와 dead-letter 처리
- metrics, structured logging, dashboard와 alert runbook
- Docker Compose와 CI regression test

완료 기준은 공개 synthetic event로 `ingestion → alert → review → recalibration`을 재현하는 end-to-end demo입니다.
