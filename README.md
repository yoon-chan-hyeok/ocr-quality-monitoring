![OCR Failure Risk Monitoring](assets/project-hero.svg)

<div align="center">

**정답 transcription이 도착하기 전에 위험 문서와 batch를 먼저 검수하도록 우선순위를 만듭니다.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tests](https://github.com/yoon-chan-hyeok/ocr-quality-monitoring/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-0F766E)
![Scope](https://img.shields.io/badge/Scope-Risk%20Triage-D97706)

[실험 결과](#실험-결과) · [공개 도구](#공개-도구) · [실행](#실행) · [상세 문서](#상세-문서)

</div>

## 문제

OCR 품질은 CER이나 WER로 평가할 수 있지만 두 지표에는 정답 transcription이 필요합니다. 새 문서가 들어온 직후에는 정답지가 없는 경우가 많고 모든 문서를 사람이 먼저 확인하기도 어렵습니다.

이 프로젝트는 OCR confidence와 text embedding 기반 novelty를 비교해, scoring 시점에 정답 없이도 먼저 확인할 문서와 batch를 정할 수 있는지 검토했습니다. Gold transcription은 detector 입력에 쓰지 않았고 연구 단계의 성능 평가에만 사용했습니다.

## 연구 실험과 공개 도구

이 저장소에는 성격이 다른 두 artifact가 있습니다.

| 구분 | 목적 | 공개 범위 |
|---|---|---|
| 연구 실험 | Confidence와 embedding signal의 failure detection 성능 비교 | Dataset, corruption 조건과 aggregate AUPRC 문서 |
| 공개 CLI | 승인 baseline과 새 candidate 사이의 record, batch drift 계산 | 실행 코드, JSONL 예제, 테스트, report 생성 |

README의 AUPRC 표는 원 연구 실험의 결과입니다. 현재 공개 CLI는 OCR inference와 corruption을 포함한 benchmark 재현 도구가 아닙니다. 공개 코드는 embedding drift와 review queue 생성 경로를 재현합니다.

## 무엇을 비교했나

| Signal | 보는 대상 | 해석할 때 주의한 점 |
|---|---|---|
| OCR confidence | OCR model이 인식 결과를 얼마나 확신하는지 | Model별 calibration이 다를 수 있음 |
| Embedding novelty | 결과 text가 정상 문서 의미 공간에서 얼마나 벗어났는지 | 정상 domain shift도 크게 반응할 수 있음 |
| Record score | 개별 문서의 이상 정도 | 숫자 한 글자 오류에는 둔감할 수 있음 |
| Batch shift | 입력 묶음 전체의 변화 | 오류가 아니라 새 양식일 수 있음 |

처음에는 embedding이 confidence가 놓치는 오류를 전반적으로 보완할 것으로 예상했습니다. 실제로는 confidence가 강한 baseline이었고 embedding의 이득은 오류 유형에 따라 달랐습니다.

## 실험 결과

FUNSD 199개 문서에 9개 조건을 적용한 1,791건과 CORD v2 200개 문서에 6개 조건을 적용한 1,200건을 평가했습니다.

| 대표 조건 | Confidence AUPRC | 결합한 signal | 결합 AUPRC |
|---|---:|---|---:|
| FUNSD 전체 degradation | 0.8295 | confidence + direction | 0.8454 |
| CORD alphabetic mismatch | 0.5907 | confidence + kNN5 | 0.6904 |

Embedding 결합은 모든 조건에서 좋아지지 않았습니다. 문서 전체가 훼손된 경우에는 confidence가 잘 작동했지만, 금액, 금리, 날짜처럼 한 글자만 틀려도 중요한 local error는 confidence와 document-level embedding이 모두 놓칠 수 있었습니다.

결론은 "embedding이 더 좋은 detector"가 아닙니다. Confidence를 기본 signal로 두고 특정 failure type에서 embedding novelty를 보조적으로 쓰는 편이 결과와 맞았습니다.

Dataset, corruption 조건과 결과 범위는 [Experiment context](docs/EXPERIMENT_CONTEXT.md)에 정리했습니다.

## 공개 도구

```mermaid
flowchart LR
    A["Accepted baseline<br/>JSONL"] --> V["Schema validation"]
    B["New candidate<br/>JSONL"] --> V
    V --> E["Hash or semantic<br/>embedding"]
    E --> R["Record novelty"]
    E --> G["Batch shift"]
    R --> Q["Review queue"]
    G --> Q
    Q --> O["JSONL + JSON<br/>Markdown report"]
```

낮은 위험 문서는 기존 처리 흐름으로 보내고 높은 위험 문서는 재인식, fallback 또는 사람 검수 후보로 올리는 용도입니다. Batch signal은 입력 양식이나 공급처가 한꺼번에 바뀌었는지 확인하는 경보로 사용할 수 있습니다.

Threshold는 하루에 사람이 확인할 수 있는 문서 수, false alarm 비용과 오류를 놓쳤을 때의 업무 비용으로 보정해야 합니다.

## 실행

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
ocr-embedding-monitor --baseline examples/baseline.jsonl --candidate examples/candidate_corrupted.jsonl --output-dir outputs/demo --backend hash
pytest
```

Hash backend는 외부 model 없이 동일한 입력에 동일한 결과를 내는 demo입니다. 의미 기반 비교에는 sentence-transformers backend를 사용할 수 있습니다.

## 저장소 구성

```text
src/ocr_embedding_monitor/   CLI, embedding, detector, I/O, runner
examples/                    baseline과 candidate JSONL
tests/                       detector, I/O, runner test
docs/                        원 실험 범위와 후속 검증 계획
.github/workflows/           package test CI
```

공개 package는 Python 3.10+, NumPy와 scikit-learn을 사용합니다. Semantic backend는 Sentence Transformers와 PyTorch를 선택 dependency로 둡니다.

## 상세 문서

- [Experiment context](docs/EXPERIMENT_CONTEXT.md): dataset, corruption 조건, 원 연구 결과
- [Learning roadmap](docs/LEARNING_ROADMAP.md): field-level detector와 운영 확장 항목
- [Examples](examples/): baseline과 candidate JSONL
- [Tests](tests/): detector, I/O, runner 검증

Domain shift가 곧 OCR 오류라는 뜻은 아닙니다. 공개 CLI만으로 README의 AUPRC 표를 다시 만들 수 없으며, 실제 threshold는 검수 결과와 업무 비용으로 calibration해야 합니다. 숫자나 핵심 단어 하나가 틀린 local error에는 field-level 검사가 추가로 필요합니다.
