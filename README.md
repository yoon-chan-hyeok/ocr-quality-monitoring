![Label-Free OCR Quality Monitor project hero](assets/project-hero.svg)

<div align="center">

**Gold label이 늦게 도착하는 OCR pipeline에서 embedding-space local/global drift를 측정하고, record-level review queue와 batch risk signal을 생성하는 label-free monitor**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tests](https://github.com/yoon-chan-hyeok/ocr-quality-monitoring/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-0F766E)
![Scope](https://img.shields.io/badge/Scope-Risk%20Signal%2C%20Not%20Accuracy-D97706)

[문제와 판단](#문제와-판단) · [동작 구조](#monitoring-flow) · [빠른 실행](#quick-start) · [운영 확장](docs/LEARNING_ROADMAP.md)

</div>

---

## 프로젝트 개요

| 구분 | 내용 |
|---|---|
| **Input** | accepted baseline JSONL과 새 candidate JSONL |
| **Local signal** | baseline leave-one-out nearest-neighbor distance를 median/MAD로 calibration해 record anomaly score를 계산 |
| **Global signal** | centroid cosine distance와 RBF-MMD로 candidate batch 전체의 분포 이동을 측정 |
| **Output** | review JSONL, batch summary JSON, Markdown report, reproducible run hash |
| **Verification** | synthetic fixture, deterministic hash backend, unit test, GitHub Actions |

출력값은 OCR accuracy나 CER/WER의 대체값이 아닙니다. 라벨이 도착하기 전 검토 예산을 어디에 먼저 쓸지 정하는 risk signal입니다.

## 문제와 판단

운영 환경에서는 새 문서가 들어온 순간 정답 transcription이 존재하지 않는 경우가 많습니다. 그렇다고 라벨이 쌓일 때까지 아무것도 보지 않으면 새로운 양식·언어·손상 패턴을 늦게 발견합니다.

그래서 두 수준의 신호를 분리했습니다.

| 수준 | 질문 | 신호 |
|---|---|---|
| **Record level** | 어떤 OCR 결과가 baseline에서 멀리 떨어졌는가? | nearest-neighbor distance + robust z-score |
| **Batch level** | 전체 candidate 분포가 이동했는가? | centroid cosine distance + RBF-MMD |

최종 출력은 pass/fail 정답이 아니라 검수자가 사용할 **review queue**입니다.

## Monitoring flow

```mermaid
flowchart LR
    A["Accepted baseline<br/>OCR JSONL"] --> V["Schema validation"]
    B["New candidate<br/>OCR JSONL"] --> V
    V --> E["Hash or semantic<br/>embedding"]
    E --> N["Nearest-neighbor<br/>record distance"]
    E --> G["Centroid shift<br/>+ RBF-MMD"]
    N --> Z["Median / MAD<br/>robust score"]
    G --> R["Risk aggregation"]
    Z --> R
    R --> Q["Human review queue"]
    R --> P["JSON · JSONL · MD<br/>reports"]
```

## 구현 범위

- JSONL schema validation과 stable record ID
- deterministic hashing backend와 sentence-transformers backend
- baseline leave-one-out nearest-neighbor calibration
- median/MAD 기반 robust anomaly score
- centroid cosine distance와 RBF Maximum Mean Discrepancy
- record별 review recommendation과 reproducible run hash
- installable CLI, synthetic examples, tests, GitHub Actions
- 결과를 “accuracy”로 오해하지 않도록 명시한 interpretation boundary

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

ocr-embedding-monitor \
  --baseline examples/baseline.jsonl \
  --candidate examples/candidate_corrupted.jsonl \
  --output-dir outputs/demo \
  --backend hash

pytest
```

`hash` backend는 외부 모델·API 없이 전체 흐름을 재현합니다. 의미 기반 비교에는 `sentence-transformers` 추가 의존성과 BGE 계열 임베딩을 사용할 수 있습니다.

## Output contract

| 산출물 | 용도 |
|---|---|
| Summary JSON | 자동화·dashboard 연동용 batch signal |
| Review JSONL | 사람이 확인할 record 우선순위 |
| Markdown report | 실행 결과를 빠르게 검토·공유 |
| Run hash | 동일 입력·설정 실행의 추적성 |

## Repository map

```text
src/ocr_embedding_monitor/   detector, embedding, metrics, CLI
examples/                    synthetic baseline and candidate batches
tests/                       detector, I/O, end-to-end tests
.github/workflows/           automated test workflow
docs/LEARNING_ROADMAP.md     data and production expansion plan
assets/                      portfolio hero artwork
```

## Decision boundary

- signal은 OCR error rate나 accuracy가 아닙니다.
- domain shift가 반드시 품질 저하를 의미하지는 않습니다.
- 실제 alert threshold는 샘플 검수와 업무 비용을 반영해 보정해야 합니다.
- 새 문서 유형이 정상 변화라면 baseline 승인·갱신 절차가 필요합니다.
- embedding distance만으로 개인정보·안전 관련 판정을 자동화해서는 안 됩니다.

## 기여 범위

문제 정의, label-free signal의 해석 범위, local/global signal 조합과 출력 계약을 설계했습니다. 공개 코드는 synthetic example, deterministic backend, 테스트와 CI로 실행 경로를 검증할 수 있게 구성했습니다.

[운영 수준 확장 로드맵](docs/LEARNING_ROADMAP.md)

