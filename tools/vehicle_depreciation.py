#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업무용승용차 비용처리 시뮬레이터 (개인사업자 · 복식부기의무자 기준)

근거: 소득세법 제33조의2, 같은 법 시행령 제78조의3
 - 5년 정액법 강제상각
 - 감가상각비 필요경비 한도: 차량 1대당 연 800만원(과세기간 월수 안분), 초과분 이월
 - 관련비용 1,500만원(월수 안분) 이하이면 운행기록부 없이 업무사용비율 100%
 - 업무전용자동차보험 미가입분은 업무사용비율에 인정률(50% 또는 0%)을 곱함

사용 예)
  python3 tools/vehicle_depreciation.py --cost 60000000 --start 2026-03
  python3 tools/vehicle_depreciation.py --cost 85000000 --start 2026-03 \
      --other-cost 6000000 --logbook --business-ratio 0.85

⚠️ 참고용 계산입니다. 최종 신고 수치는 세무대리인 확인을 거치십시오.
"""

import argparse
from dataclasses import dataclass

DEP_LIMIT_PER_YEAR = 8_000_000      # 감가상각비 필요경비 한도
LOGBOOK_THRESHOLD = 15_000_000      # 운행기록부 면제 기준금액
USEFUL_LIFE_MONTHS = 60             # 내용연수 5년 (강제상각)


@dataclass
class YearRow:
    year: int
    months: int          # 해당 과세기간 보유(사용) 월수
    dep_months: int      # 해당 과세기간 감가상각 대상 월수
    book_dep: int        # 회계상 감가상각비
    other_cost: int      # 감가상각비 외 관련비용
    related_cost: int    # 관련비용 합계
    threshold: int       # 1,500만원 기준금액(월할)
    ratio: float         # 업무사용비율(보험 인정률 반영 후)
    dep_business: int    # 감가상각비 중 업무사용분
    limit: int           # 800만원 한도(월할)
    dep_deducted: int    # 당기 필요경비 산입 감가상각비(이월분 포함)
    other_deducted: int  # 당기 필요경비 산입 기타 관련비용
    disallowed: int      # 당기 필요경비 불산입액
    carryover: int       # 기말 이월 잔액


def simulate(cost, start_year, start_month, annual_other_cost,
             business_ratio, has_logbook, recognition_rate, max_years):
    rows = []
    carryover = 0
    remaining_dep_months = USEFUL_LIFE_MONTHS
    monthly_dep = cost / USEFUL_LIFE_MONTHS

    year = start_year
    for i in range(max_years):
        months = (13 - start_month) if i == 0 else 12
        dep_months = min(months, remaining_dep_months)
        remaining_dep_months -= dep_months

        book_dep = round(monthly_dep * dep_months)
        other_cost = round(annual_other_cost * months / 12)
        related = book_dep + other_cost

        # 업무사용비율 결정
        threshold = round(LOGBOOK_THRESHOLD * months / 12)
        if has_logbook:
            ratio = business_ratio
        elif related <= threshold:
            ratio = 1.0
        else:
            ratio = threshold / related
        ratio *= recognition_rate  # 업무전용자동차보험 미가입 시 50% 또는 0%

        # 감가상각비 한도 적용
        dep_business = round(book_dep * ratio)
        limit = round(DEP_LIMIT_PER_YEAR * months / 12)

        if dep_business > limit:
            dep_deducted = limit
            carryover += dep_business - limit
        else:
            room = limit - dep_business
            recovered = min(room, carryover)
            carryover -= recovered
            dep_deducted = dep_business + recovered

        other_deducted = round(other_cost * ratio)
        disallowed = related - round(related * ratio) + max(0, dep_business - limit)

        rows.append(YearRow(
            year=year, months=months, dep_months=dep_months,
            book_dep=book_dep, other_cost=other_cost, related_cost=related,
            threshold=threshold, ratio=ratio, dep_business=dep_business,
            limit=limit, dep_deducted=dep_deducted, other_deducted=other_deducted,
            disallowed=disallowed, carryover=carryover,
        ))

        year += 1
        if remaining_dep_months == 0 and carryover == 0:
            break

    return rows


def won(n):
    return f"{n:,.0f}"


def render(rows, args):
    print()
    print("=" * 104)
    print("  업무용승용차 비용처리 시뮬레이션 (개인사업자 · 복식부기의무자)")
    print("=" * 104)
    print(f"  취득가액        : {won(args.cost)}원  (취득세·불공제 부가세 등 부대비용 포함 금액으로 입력)")
    print(f"  사업 사용 개시  : {args.start}")
    print(f"  연간 기타 관련비용: {won(args.other_cost)}원  (유류비·보험료·자동차세·수선비·통행료 등)")
    if args.logbook:
        print(f"  운행기록부      : 작성  → 업무사용비율 {args.business_ratio:.0%}")
    else:
        print(f"  운행기록부      : 미작성 → 관련비용 1,500만원 기준으로 자동 산정")
    if args.recognition_rate < 1.0:
        label = "미가입(전액 부인)" if args.recognition_rate == 0 else f"미가입({args.recognition_rate:.0%} 인정)"
        print(f"  업무전용자동차보험: {label}")
    print("-" * 104)

    header = (f"{'연도':>6}{'월수':>5}{'감가상각비':>14}{'관련비용계':>14}"
              f"{'업무사용율':>11}{'한도':>13}{'당기 필요경비':>15}{'불산입':>13}{'이월잔액':>13}")
    print(header)
    print("-" * 104)

    total_deducted = 0
    for r in rows:
        deducted = r.dep_deducted + r.other_deducted
        total_deducted += deducted
        print(f"{r.year:>6}{r.months:>5}{won(r.book_dep):>14}{won(r.related_cost):>14}"
              f"{r.ratio:>10.1%}{won(r.limit):>13}{won(deducted):>15}"
              f"{won(r.disallowed):>13}{won(r.carryover):>13}")

    print("-" * 104)
    total_dep_deducted = sum(r.dep_deducted for r in rows)
    total_related = sum(r.related_cost for r in rows)
    print(f"  감가상각비 회수 총액 : {won(total_dep_deducted)}원 / 취득가액 {won(args.cost)}원")
    print(f"  관련비용 총액        : {won(total_related)}원")
    print(f"  필요경비 산입 총액   : {won(total_deducted)}원")
    permanently_lost = total_related - total_deducted
    if permanently_lost > 0:
        print(f"  영구 불산입액(업무 미사용분) : {won(permanently_lost)}원")
    print(f"  이월액 소진 시점     : {rows[-1].year}년 "
          f"({len(rows)}개 과세기간, {rows[0].year}~{rows[-1].year})")
    print("=" * 104)

    warn = []
    if any(r.ratio < 1.0 and not args.logbook for r in rows):
        worst = min(r.ratio for r in rows)
        warn.append(f"관련비용이 1,500만원을 초과하여 업무사용비율이 최저 {worst:.1%}까지 축소됩니다. "
                    f"→ 운행기록부를 작성하면 실제 업무사용비율(통상 90% 이상)을 적용받을 수 있습니다.")
    if len(rows) > 5:
        warn.append(f"연 800만원 한도 때문에 5년이 아니라 {len(rows)}년에 걸쳐 비용이 회수됩니다. "
                    f"현금흐름·누진세율 측면을 감안해 취득 시기를 검토하십시오.")
    if args.recognition_rate < 1.0:
        warn.append("업무전용자동차보험 미가입 상태입니다. 2026 귀속분부터 미가입 차량(1대 초과분 또는 "
                    "성실신고확인대상자·전문직의 전 차량)은 관련비용이 전액 부인됩니다.")
    if warn:
        print("\n  [검토 포인트]")
        for w in warn:
            print(f"   • {w}")
        print()


def main():
    p = argparse.ArgumentParser(
        description="업무용승용차 비용처리 시뮬레이터 (개인사업자 · 복식부기의무자)")
    p.add_argument("--cost", type=int, required=True,
                   help="취득가액(원). 차량가 + 취득세 + 공채할인차손 + 불공제 부가세 포함")
    p.add_argument("--start", required=True,
                   help="사업 사용 개시 연월 (예: 2026-03)")
    p.add_argument("--other-cost", type=int, default=0,
                   help="연간 기타 관련비용(원): 유류비·보험료·자동차세·수선비·통행료·할부이자 등")
    p.add_argument("--logbook", action="store_true",
                   help="운행기록부를 작성하는 경우 지정")
    p.add_argument("--business-ratio", type=float, default=1.0,
                   help="운행기록부상 업무사용비율 (예: 0.85). --logbook과 함께 사용")
    p.add_argument("--insurance", choices=["ok", "none-50", "none-0"], default="ok",
                   help="업무전용자동차보험: ok=가입(또는 1대 예외), none-50=미가입 50%% 인정(2024~2025), "
                        "none-0=미가입 전액 부인(2026~)")
    p.add_argument("--max-years", type=int, default=15, help="시뮬레이션 최대 과세기간 수")
    args = p.parse_args()

    try:
        y, m = args.start.split("-")
        start_year, start_month = int(y), int(m)
        assert 1 <= start_month <= 12
    except Exception:
        p.error("--start 는 YYYY-MM 형식이어야 합니다 (예: 2026-03)")

    if args.business_ratio != 1.0 and not args.logbook:
        p.error("--business-ratio 는 --logbook 과 함께 사용해야 합니다. "
                "운행기록부 미작성 시 업무사용비율은 1,500만원 기준으로 법정 산정됩니다.")
    if not (0 < args.business_ratio <= 1):
        p.error("--business-ratio 는 0 초과 1 이하의 소수여야 합니다 (예: 0.85)")

    rate = {"ok": 1.0, "none-50": 0.5, "none-0": 0.0}[args.insurance]
    args.recognition_rate = rate

    rows = simulate(
        cost=args.cost, start_year=start_year, start_month=start_month,
        annual_other_cost=args.other_cost, business_ratio=args.business_ratio,
        has_logbook=args.logbook, recognition_rate=rate, max_years=args.max_years,
    )
    render(rows, args)


if __name__ == "__main__":
    main()
