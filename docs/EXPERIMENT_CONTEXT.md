# 원 연구와 공개 구현의 범위

## 연구 질문

실제 OCR pipeline에서는 새 문서의 gold transcription을 즉시 만들기 어렵다. 원 연구에서는 OCR confidence와 sentence embedding novelty가 정답 없이 실패 위험을 정렬하는 데 어느 정도 도움이 되는지 비교했다. Gold transcription은 detector 입력에 넣지 않고 사후 평가에만 사용했다.

## 데이터와 조건

| Dataset | Documents | Conditions | Evaluation records |
|---|---:|---:|---:|
| FUNSD | 199 | 9 | 1,791 |
| CORD v2 | 200 | 6 | 1,200 |

Blur, compression, downsampling과 contrast 변화처럼 문서 전체에 영향을 주는 조건을 포함했다. 별도로 숫자나 일부 문자만 바뀌는 local error가 document-level signal에서 어떻게 보이는지도 확인했다.

## 대표 결과

| Condition | Confidence AUPRC | Compared combination | Combination AUPRC |
|---|---:|---|---:|
| FUNSD 전체 degradation | 0.8295 | confidence + direction | 0.8454 |
| CORD alphabetic mismatch | 0.5907 | confidence + kNN5 | 0.6904 |

Confidence는 예상보다 강한 baseline이었다. Embedding signal은 일부 failure type을 보완했지만 모든 조건에서 성능을 높이지 않았다. 따라서 embedding이 confidence를 대체한다고 결론내리지 않았다.

대표 결과의 machine-readable 집계는 [benchmark_summary.csv](../results/benchmark_summary.csv)에 저장했다.

### Critical field 분석

CORD의 `total`과 `subtotal`을 critical field로 두고 omission과 substitution을 분리했다.

| 조건 | 지표 | Confidence | 결합 또는 embedding 신호 | 해석 |
|---|---|---:|---:|---|
| Critical harm 전체 | AUPRC | 0.595 | 0.627 | 평균 gain의 95% CI가 0을 포함했다. |
| Critical omission | AUPRC | 0.564 | 0.668 | Gain `+0.113`, 95% CI `[+0.013, +0.221]` |
| Critical substitution | AUPRC | 0.136 | 0.110 | Recall@5% FPR도 0이었다. |
| OOD 숫자 치환 | AUROC | 해당 없음 | 0.972 | Value-only embedding으로 정상 범위 밖 값을 구분했다. |
| 정상 분포 안의 값 교환 | AUROC | 해당 없음 | 0.415 | 그럴듯한 값끼리 바뀌면 구분하지 못했다. |

세부 집계는 [critical_field_summary.csv](../results/critical_field_summary.csv)에 저장했다. 이 수치는 raw prediction을 대신하는 재현 결과가 아니라, 완료된 실험에서 남긴 검증 집계다.

문서 전체가 훼손된 경우에는 confidence나 embedding novelty가 움직일 수 있다. 반면 금액, 비율, 금리, 날짜처럼 일부 field만 잘못 인식되면 문서 전체 의미는 거의 유지될 수 있다. 이런 local critical error에는 field extraction, rule check와 별도 검증이 필요하다.

## 공개 저장소와의 차이

현재 저장소에는 원 corpus, OCR inference output과 전체 실험 harness를 포함하지 않는다. 검증된 대표 결과와 해석 범위는 README와 `results/`의 aggregate CSV에 정리했다.

`src/ocr_embedding_monitor/`는 승인 baseline과 새 candidate를 받아 record anomaly와 batch drift를 계산하고 review queue를 만드는 CLI다. Synthetic fixture와 deterministic backend는 운영형 실행 경로를 빠르게 검증하기 위한 것이며, 연구 AUPRC를 재현하는 benchmark runner는 아니다.

## 작업 범위

문제 정의, confidence baseline, embedding novelty 가설, detector 비교와 결과 해석을 설계했다. OCR inference와 corruption 실험, feature extraction, 평가 집계, 재시작 가능한 실행과 테스트를 반복하며 결과를 검증했다.
