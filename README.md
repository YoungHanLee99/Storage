# Storage

개인 업무·세무 관련 문서와 도구 저장소.

## 구성

| 경로 | 설명 |
|---|---|
| `docs/tax/업무용승용차-비용처리-가이드.md` | 개인사업자 차량 구매 후 감가상각·비용처리 전체 가이드 |
| `tools/vehicle_depreciation.py` | 업무용승용차 연도별 필요경비 시뮬레이터 |
| `templates/운행기록부_양식.csv` | 업무용승용차 운행기록부 양식 |
| `.claude/commands/morning-briefing.md` | 오전 브리핑 슬래시 커맨드 |

## 업무용승용차 시뮬레이터 사용법

```bash
# 취득가액 6,000만원, 2026년 3월 사업 사용 개시
python3 tools/vehicle_depreciation.py --cost 60000000 --start 2026-03

# 기타 관련비용(유류비·보험료·자동차세 등) 연 600만원 포함, 운행기록부 작성(업무사용비율 90%)
python3 tools/vehicle_depreciation.py --cost 85000000 --start 2026-03 \
    --other-cost 6000000 --logbook --business-ratio 0.9

# 업무전용자동차보험 미가입(2026 귀속분 — 전액 부인)
python3 tools/vehicle_depreciation.py --cost 60000000 --start 2026-03 --insurance none-0
```

| 옵션 | 설명 |
|---|---|
| `--cost` | 취득가액(원). 차량가 + 취득세 + 공채할인차손 + 불공제 부가세 |
| `--start` | 사업 사용 개시 연월 (`YYYY-MM`) |
| `--other-cost` | 연간 기타 관련비용(유류비·보험료·자동차세·수선비·통행료·할부이자) |
| `--logbook` / `--business-ratio` | 운행기록부 작성 시 실제 업무사용비율 적용 |
| `--insurance` | `ok` / `none-50`(2024~2025) / `none-0`(2026~) |

> ⚠️ 참고용 계산입니다. 최종 신고 수치는 세무대리인 확인을 거치십시오.
