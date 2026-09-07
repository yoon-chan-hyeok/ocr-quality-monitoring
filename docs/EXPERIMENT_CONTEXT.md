# OCR 실험 설정과 공개 구현의 범위

[프로젝트 소개](../README.md) · [결과 근거](../results/README.md)

## 어떤 환경을 가정했는가

고정된 OCR 엔진에서 나온 text와 confidence, 승인된 정상 로그를 사용해 새 문서의 검수 우선순위를 정하는 상황이다. 엔진의 가중치나 문자별 logit에 접근하지 않는다. 새 문서의 정답 전사본은 점수를 낼 때 사용할 수 없다고 가정한다.

임베딩은 text가 정상 출력 분포에서 얼마나 벗어났는지 측정한다. 이 거리가 실제 OCR 오류를 의미하는지는 별도 평가가 필요하다. 영문자 불일치, 문서 전체의 문자 오류율 증가, 중요한 금액의 누락·치환을 나눈 이유다.

## 데이터와 평가 단위

| 데이터 | 학습/reference 문서 | Test 문서 | 조건 | 전체 문서·조건 조합 |
|---|---:|---:|---:|---:|
| FUNSD | 149 | 50 | 9 | 1,791 |
| CORD v2 | 100 | 100 | 6 | 1,200 |

RapidOCR 설정을 고정하고 clean, blur, JPEG compression, downsampling과 contrast 조건을 만들었다. Text encoder는 `BAAI/bge-m3`, clean-reference novelty의 주 비교는 정규화한 embedding의 cosine kNN `k=5`다.

전체 건수에는 학습/reference 문서가 포함된다. FUNSD held-out 문서 평가의 test는 50 × 9 = 450건, CORD test는 100 × 6 = 600건이다. Component-level 비교에서는 OCR 문자열을 나누므로 행 수가 더 많다.

오류 정의도 구분했다.

- Local mismatch: 정답과 정렬한 OCR component의 문자 불일치.
- Document harm: 같은 문서의 clean OCR보다 CER가 0.03 이상 증가한 경우.
- Critical-field harm: clean image에서 맞았던 `total` 또는 `subtotal` 가격이 열화 뒤 새로 누락되거나 다른 값으로 바뀐 경우.

## Label-free의 범위

Runtime label-free는 새 문서의 정답 없이 점수를 계산한다는 뜻이다. 원 실험에는 다음 두 종류의 점수가 있다.

| 설정 | 과거 오류 label 사용 | 새 test 정답 사용 | 용도 |
|---|---|---|---|
| Clean-reference ECDF 보정 | 사용하지 않음 | 사후 평가에만 사용 | 정상 로그 기준으로 위험 순위를 계산 |
| Logistic regression 비교 | 학습 문서의 오류 label 사용 | 사후 평가에만 사용 | Confidence에 embedding 특징을 더했을 때의 보완 정보 확인 |

README의 FUNSD `0.8295 → 0.8454`와 CORD 영문자 `0.5907 → 0.6904`는 logistic regression 비교다. 학습까지 label-free인 detector의 결과로 제시하지 않는다. 원 코드의 `analyze_paired_gain.py`와 `analyze_cord_replication.py`에서 학습/test 문서를 분리하고 label을 사용하는 경로를 확인했다.

## 무엇을 확인했는가

Confidence는 문서 단위에서 강한 기준선이었다. FUNSD에 embedding direction을 더한 AUPRC 차이는 `+0.0159`, paired 95% CI는 `[-0.0062, +0.0388]`로 일반적인 개선을 확정하지 못했다. 학습에서 제외한 downsampling 조건에서는 `0.9291 → 0.9035`로 낮아졌다.

CORD의 영문자 component 불일치에서는 confidence에 clean-reference kNN을 추가한 AUPRC가 `0.5907 → 0.6904`였다. 이 결과는 일부 문자 오류의 보완 신호를 지지하며, 문서 단위 harm 전체의 개선을 뜻하지 않는다.

주 지표는 오류 비율을 고려해 AUPRC로 두고 AUROC와 Recall@5% FPR을 함께 확인했다. 신뢰구간은 동일 문서의 여러 조건을 묶는 document-cluster bootstrap으로 계산했다.

## Critical-field 보조 진단

`decomposed risk`는 정상 분포로 보정한 confidence, coverage와 numeric-output 점수를 평균한다. Coverage는 OCR box와 이미지의 잉크 영역을 비교하므로 엄격한 text-log-only 설정의 보조 진단이다. Embedding 결합 모델과 같은 방법으로 읽으면 안 된다.

CORD test 100개 문서 × 6개 조건에서 전체 critical harm의 AUPRC는 `0.5952 → 0.6268`이었다. Bootstrap 평균 차이의 95% CI가 0을 포함해 전체 개선을 확정하지 않았다. 누락에서는 `0.5638 → 0.6679`, bootstrap 평균 차이 `+0.1132`, 95% CI `[+0.0127, +0.2211]`이었다. 표의 점 추정치 차이와 bootstrap 평균 차이는 서로 다른 집계다. 치환에서는 결합 점수가 confidence를 개선하지 못했고 Recall@5% FPR도 0이었다.

정상 인식한 98개 중요 값을 바꾼 text counterfactual에서는 value-only embedding AUROC가 정상 범위 밖 치환에서 `0.9716`, 정상 범위 안의 값 교환에서 `0.4151`이었다. 이 비교는 거리 신호가 정답 여부를 직접 보장하지 않는다는 한계를 살핀 실험이며, 실제 오류 benchmark로 간주하지 않는다.

원 실험에서 보존한 상세 집계와 신뢰구간은 [results/source](../results/source/)에 있다. 원 corpus, OCR 출력과 case-level prediction은 포함하지 않는다.

## 공개 CLI는 무엇을 실행하는가

[`src/ocr_embedding_monitor`](../src/ocr_embedding_monitor/)는 승인 baseline과 새 candidate JSONL의 text를 embedding으로 변환한다. 최근접 정상 record와의 거리를 기준 분포로 보정해 문서별 점수를 만들고, centroid distance·MMD·평균 이웃 거리 비율을 batch 통계로 남긴다. 출력은 `scored_records.jsonl`, `summary.json`, `report.md`다.

이 CLI에는 confidence fusion, OCR 추론, 이미지 열화 생성이나 critical-field 평가를 구현하지 않았다. Confidence 필드를 입력해도 추가 정보로 보존할 뿐 점수에는 넣지 않는다. 원 실험의 kNN `k=5`와 달리 CLI의 record score는 최근접 이웃 하나의 거리를 사용한다.

Hash backend는 문자 n-gram을 사용한 고정 실행 예제다. Sentence-transformers backend를 선택하면 의미 embedding으로 같은 경로를 실행한다. 어느 쪽도 README의 benchmark 수치를 재현하는 runner는 아니다.
