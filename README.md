# Storage

개인 업무·세무 관련 문서와 도구 저장소.

## 구성

| 경로 | 설명 |
|---|---|
| `docs/tax/업무용승용차-비용처리-가이드.md` | 개인사업자 차량 구매 후 감가상각·비용처리 전체 가이드 |
| `docs/tax/차량-비용처리-필요서류.md` | 취득·운행·신고 단계별 증빙서류 체크리스트 |
| `docs/tax/운행기록부-작성요령.md` | 운행기록부 작성 판단·기재·소명 요령 |
| `tools/vehicle_depreciation.py` | 업무용승용차 연도별 필요경비 시뮬레이터 |
| `tools/mileage_log.py` | 운행기록부 정합성 검증 · 업무사용비율 집계 |
| `templates/운행기록부_양식.csv` | 업무용승용차 운행기록부 양식 |
| `.claude/commands/morning-briefing.md` | 오전 브리핑 슬래시 커맨드 |

## 업무용승용차 시뮬레이터 사용법

```bash
# 취득가액 6,000만원, 2026년 3월 사업 사용 개시
python3 tools/vehicle_depreciation.py --cost 60000000 --start 2026-03

# 기타 관련비용(유류비·보험료·자동차세 등) 연 600만원 포함, 운행기록부 작성(업무사용비율 90%)
python3 tools/vehicle_depreciation.py --cost 85000000 --start 2026-03 \
    --other-cost 6000000 --logbook --business-ratio 0.9

# 1대를 초과하는 차량이 업무전용자동차보험 미가입인 경우(2026 귀속 — 전액 부인)
# ※ 사업자별 1대는 모든 유형에서 가입 의무가 제외되므로 1대 보유 시에는 기본값(ok) 사용
python3 tools/vehicle_depreciation.py --cost 60000000 --start 2026-03 --insurance none-0
```

| 옵션 | 설명 |
|---|---|
| `--cost` | 취득가액(원). 차량가 + 취득세 + 공채할인차손 + 불공제 부가세 |
| `--start` | 사업 사용 개시 연월 (`YYYY-MM`) |
| `--other-cost` | 연간 기타 관련비용(유류비·보험료·자동차세·수선비·통행료·할부이자) |
| `--logbook` / `--business-ratio` | 운행기록부 작성 시 실제 업무사용비율 적용 |
| `--insurance` | `ok`(가입 또는 사업자별 1대 제외) / `none-50` / `none-0` — 1대 초과 차량 미가입 시에만 사용 |

## 운행기록부 검증 도구 사용법

```bash
# 정합성 검증 + 업무사용비율 산출
python3 tools/mileage_log.py 2026_운행기록부.csv

# 관련비용과 함께 — 작성 여부에 따른 효과 비교
python3 tools/mileage_log.py 2026_운행기록부.csv --related-cost 25000000
```

계기판 연속성, 주행거리 합계 일치, 업무/비업무 구분 합계를 검사하고 업무사용비율을 산출합니다.
오류가 있으면 종료 코드 1을 반환합니다.

> ⚠️ 참고용 계산입니다. 최종 신고 수치는 세무대리인 확인을 거치십시오.
