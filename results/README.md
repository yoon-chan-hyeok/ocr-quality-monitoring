# 결과 자료 안내

[프로젝트 소개](../README.md) · [평가 설정](../docs/EXPERIMENT_CONTEXT.md)

`benchmark_summary.csv`와 `critical_field_summary.csv`는 README에 사용한 반올림 집계다. `source/`에는 원 실험에서 보존한 상세 집계 CSV를 파일 내용 그대로 두었다. 원 데이터나 개별 문서의 OCR text는 포함하지 않는다.

| 자료 | 확인할 내용 |
|---|---|
| [benchmark_summary.csv](benchmark_summary.csv) | FUNSD 문서 단위와 CORD 영문자 component의 대표 AUPRC |
| [critical_field_summary.csv](critical_field_summary.csv) | 중요 값의 누락·치환, 숫자 counterfactual 요약 |
| [funsd_paired_model_differences.csv](source/funsd_paired_model_differences.csv) | Confidence + direction 점 추정치와 paired CI, unseen downsampling 결과 |
| [cord_replication_metrics.csv](source/cord_replication_metrics.csv) | CORD component/document별 비교와 test 규모 |
| [cord_critical_document_metrics.csv](source/cord_critical_document_metrics.csv) | Critical harm의 confidence·coverage·numeric-output·결합 점수 |
| [cord_critical_document_bootstrap.csv](source/cord_critical_document_bootstrap.csv) | Critical harm의 bootstrap 평균 차이와 CI |
| [cord_numeric_counterfactual_metrics.csv](source/cord_numeric_counterfactual_metrics.csv) | 정상 범위 밖 값과 정상 범위 안 값 교환 비교 |

`source/` 표와 [FUNSD 그림](../assets/confidence-embedding-experiment.png)은 원 실험 보존본 `3d6b493fd03bda2ee556b50303a969c00ee68762`에서 가져왔다. 각 파일의 원래 이름은 FUNSD 표의 `funsd_` 접두사를 제외하면 동일하다.

## 수치를 읽을 때

FUNSD direction과 CORD confidence+kNN은 과거 오류 label로 학습한 logistic regression 비교다. Runtime에는 새 정답을 입력하지 않지만 학습까지 label-free인 방법은 아니다. 반면 critical-field `risk_mean`은 clean-reference ECDF로 보정한 confidence·coverage·numeric-output 점수의 평균이다. Coverage는 이미지 정보를 사용하므로 text-only 설정의 보조 진단이다.

Critical omission의 반올림 AUPRC 차이는 `0.668 - 0.564 = 0.104`이고, `gain=0.113`은 bootstrap 반복에서 계산한 차이의 평균이다. 둘을 같은 수치로 표기하지 않는다.

숫자 counterfactual은 정상 인식한 값 98개를 text에서 바꾼 기전 분석이다. 실제 OCR 오류 전체에 대한 성능을 뜻하지 않는다. 평가 단위와 label이 다른 행들을 하나의 순위표처럼 비교하지 않는다.

공개 CLI는 text embedding으로 검수 우선순위를 계산하는 실행 예제이며, 이 실험 표를 재생성하지 않는다.
