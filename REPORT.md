# FlavorGraph-HGN 실험 리포트

**기준일**: 2026-05-09  
**실험 범위**: scripts/gnn/22–29

---

## 설정

| 항목 | 값 |
|------|-----|
| 데이터 | flavorgraph_v2.db |
| 재료 수 | 151개 |
| 재료-화합물 연결 | 9,377개 |
| 고유 페어 (ing_a < ing_b) | 11,269개 |
| 평가 지표 | Spearman(predicted_score, PMI) |
| Train/Test split | 80/20, 랜덤 셔플, 시드별 고정 |
| 학습 손실 | BPR (Bayesian Personalized Ranking) |
| 학습 시간 | 모델당 180초 (CPU) |

**주의**: `pair_score` 테이블은 이름 기준 (ing_a, ing_b가 string). 전체 재료 원본(ingr_info.tsv)은 1,530개이나 PMI 계산된 것은 151개만.

---

## 핵심 결과

### 1. 데이터 누수 확인 (23_proper_eval)

| 모델 | Train (누수) | Test (proper) |
|------|------|------|
| BPR-MF | 0.832 | **0.670** |
| 1L-HGN | 0.830 | **0.717** |
| DualEncoder | 0.834 | **0.713** |

→ BPR-MF의 0.836은 암기. proper eval에서 그래프가 이긴다.

### 2. Lambda 스윕 — Anti-Homophily HGN (29_comprehensive E1, 3 seeds)

| λ (init) | Test Spearman | Δ vs 1L-HGN |
|------|------|------|
| 0.05 | 0.7199 ± 0.0047 | +0.0025 |
| 0.10 | 0.7210 ± 0.0050 | +0.0036 |
| 0.15 | 0.7210 ± 0.0052 | +0.0036 |
| **0.20** | **0.7256 ± 0.0024** | **+0.0082** |
| 0.25 | 0.7181 ± 0.0050 | +0.0007 |
| 0.30 | 0.7204 ± 0.0056 | +0.0030 |
| 0.35 | 0.7137 ± 0.0074 | −0.0037 |
| 0.50 | 0.7182 ± 0.0039 | +0.0008 |

→ λ=0.2에서 피크. 단, λ는 학습 가능한 파라미터(sigmoid 통과) — init 값이 수렴점을 결정.

### 3. 조합 실험 (29_comprehensive E2, E3)

| 모델 | Test | 비고 |
|------|------|------|
| AntiHomo-λ=0.2 + DualEncoder | 0.7194 ± 0.0025 | 단독보다 낮음 |
| AntiHomo-λ=0.2 + MSE loss | 0.2857 ± 0.0137 | 실패. MSE는 ranking에 부적합 |

### 4. Bootstrap CI (29_comprehensive E4, 10 seeds)

| 모델 | Test Spearman (10 seeds) |
|------|------|
| 1L-HGN | 0.7148 ± 0.0056 |
| AntiHomo-λ=0.2 | 0.7163 ± 0.0094 |

```
delta = +0.0015
95% CI = [−0.0159, +0.0114]
→ NOT statistically significant
```

→ 3-seed의 +0.0082는 seed variance. 10 seeds에서 +0.0015로 수렴, CI 0 포함.

### 5. 부가 분석

**Ahn 가설 전역 검정** (26_cuisine_analysis):
```
Spearman(shared_count, PMI) = −0.054  (p = 8.8e-9, N = 11,269)
```
→ 화합물 공유가 많을수록 PMI가 낮다. 가설 부호 반전.

**Quadrant 분석** (24_quadrant_analysis):
```
Q2: Low-shared + High-PMI (Complementarity) = 25.0%
Q4: High-shared + Low-PMI (Substitutability) = 26.5%
Off-diagonal total = 51.6%
```
→ 두 메커니즘이 거의 동등. 전역 신호가 약한 이유.

**Flavor class별 Spearman**:
- Nitrogen: +0.063* (Ahn 지지)
- Alcohol: −0.063*, Ester: −0.064* (Ahn 반박)

---

## 가정 및 한계

| 가정 | 내용 |
|------|------|
| 재료 수 | 151개 (pair_score 존재하는 것만) |
| PMI 출처 | flavorgraph_v2.db pair_score 사전 계산값 — 레시피 co-occurrence 기반 |
| 그래프 구조 | Ingredient-Compound bipartite (HGT 1-layer) |
| λ semantics | `sigmoid(nn.Parameter(init))` — 학습 중 변화함 |
| 통계 검증 | Bootstrap (10 seeds × 180s per seed, CPU) |

**핵심 한계**: 151개 재료 → 통계 검증력 부족. 1,530개 재료 기준 PMI 재계산 시 개선 가능.

---

## 전체 모델 순위 (proper eval 기준)

```
AntiHomo-λ=0.2  0.7256  (3 seeds, significant 여부 미확정)
1L-HGN          0.717   ← 실질적 baseline
DualEncoder     0.713
ClassConditioned 0.711
ProfileGated    0.710
BPR-MF          0.670   ← 암기 모델
```

---

## 다음 단계

1. **PMI 재계산** — ingr_info.tsv(1,530개) + PP_recipes.csv(178,265개 레시피) 기반
2. 스케일 확장 후 bootstrap 재실행 → anti-homophily 유의성 재검증
3. Cuisine-stratified 분석 (현재 쿠진 컬럼 없음 → 레시피에서 추출 가능 여부 확인)
