#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업무용승용차 운행기록부 검증 · 집계 도구

운행기록부 CSV를 읽어 기재 정합성을 검증하고 업무사용비율을 산출합니다.
관련비용을 함께 입력하면 운행기록부 작성 여부에 따른 필요경비 차이를 비교합니다.

근거: 「업무용승용차 운행기록 방법에 관한 고시」(국세청),
      소득세법 제33조의2, 같은 법 시행령 제78조의3

사용 예)
  python3 tools/mileage_log.py templates/운행기록부_양식.csv
  python3 tools/mileage_log.py 2026_운행기록부.csv --related-cost 25000000

⚠️ 참고용 계산입니다. 최종 신고 수치는 세무대리인 확인을 거치십시오.
"""

import argparse
import csv
import io
import sys

LOGBOOK_THRESHOLD = 15_000_000  # 운행기록부 면제 기준금액
COLUMNS = ["사용일자", "사용자", "주행전계기판", "주행후계기판",
           "주행거리", "출퇴근용", "일반업무용", "비업무용"]


def load(path):
    with io.open(path, encoding="utf-8-sig") as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#") and ln.strip()]
    if not lines:
        sys.exit(f"오류: {path} 에 데이터 행이 없습니다.")
    reader = csv.DictReader(lines)
    missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        sys.exit(f"오류: 필수 열이 없습니다 → {', '.join(missing)}\n"
                 f"      templates/운행기록부_양식.csv 의 열 이름을 사용하십시오.")
    return list(reader)


def to_int(row, col, lineno, errors):
    raw = (row.get(col) or "").strip().replace(",", "")
    if raw == "":
        return 0
    try:
        return int(float(raw))
    except ValueError:
        errors.append((lineno, f"'{col}' 값을 숫자로 읽을 수 없습니다: {raw!r}"))
        return 0


def verify(rows):
    """행별 정합성과 계기판 연속성을 검증한다. (errors, warnings, parsed) 반환"""
    errors, warnings, parsed = [], [], []
    prev_end = prev_date = None

    for i, row in enumerate(rows):
        lineno = i + 2  # 헤더 다음 행부터
        date = (row.get("사용일자") or "").strip()
        start = to_int(row, "주행전계기판", lineno, errors)
        end = to_int(row, "주행후계기판", lineno, errors)
        dist = to_int(row, "주행거리", lineno, errors)
        commute = to_int(row, "출퇴근용", lineno, errors)
        work = to_int(row, "일반업무용", lineno, errors)
        private = to_int(row, "비업무용", lineno, errors)

        if end - start != dist:
            errors.append((lineno, f"주행후({end:,}) - 주행전({start:,}) = {end - start:,} "
                                   f"이지만 주행거리는 {dist:,} 입니다."))
        if commute + work + private != dist:
            errors.append((lineno, f"출퇴근({commute:,}) + 일반업무({work:,}) + 비업무({private:,}) "
                                   f"= {commute + work + private:,} 이지만 주행거리는 {dist:,} 입니다."))
        if end < start:
            errors.append((lineno, f"주행후계기판({end:,})이 주행전계기판({start:,})보다 작습니다."))
        elif dist < 0:
            errors.append((lineno, "주행거리가 음수입니다."))

        if prev_end is not None:
            if start < prev_end:
                errors.append((lineno, f"계기판이 역행합니다: 직전 주행후 {prev_end:,} → 이번 주행전 {start:,}"))
            elif start > prev_end:
                warnings.append((lineno, f"계기판 공백 {start - prev_end:,}km "
                                         f"(직전 주행후 {prev_end:,} → 이번 주행전 {start:,}) "
                                         f"— 미기록 구간은 비업무용으로 추정될 수 있습니다."))
        if prev_date and date and date < prev_date:
            warnings.append((lineno, f"사용일자가 역순입니다 ({prev_date} → {date}). 날짜순 정렬을 권장합니다."))

        prev_end, prev_date = end, (date or prev_date)
        parsed.append({"date": date, "dist": dist, "commute": commute,
                       "work": work, "private": private})

    return errors, warnings, parsed


def report(parsed, errors, warnings, related_cost):
    total = sum(r["dist"] for r in parsed)
    commute = sum(r["commute"] for r in parsed)
    work = sum(r["work"] for r in parsed)
    private = sum(r["private"] for r in parsed)
    business = commute + work
    ratio = business / total if total else 0.0

    print()
    print("=" * 78)
    print("  업무용승용차 운행기록부 검증 · 집계")
    print("=" * 78)
    print(f"  기록 건수      : {len(parsed):,}건"
          + (f"  ({parsed[0]['date']} ~ {parsed[-1]['date']})" if parsed and parsed[0]['date'] else ""))
    print(f"  총 주행거리    : {total:,} km")
    print(f"    · 출퇴근용   : {commute:,} km")
    print(f"    · 일반업무용 : {work:,} km")
    print(f"    · 비업무용   : {private:,} km")
    print("-" * 78)
    print(f"  업무용 사용거리: {business:,} km   (출퇴근 + 일반업무)")
    print(f"  업무사용비율   : {ratio:.2%}")
    if errors:
        print("   ※ 기재 오류가 있어 위 집계는 신뢰할 수 없습니다. 오류를 먼저 수정하십시오.")
    elif ratio > 1.0:
        print("   ※ 업무사용비율이 100%를 넘습니다. 기재 내용을 확인하십시오.")
    print("=" * 78)

    if errors:
        print(f"\n  [오류 {len(errors)}건] — 아래를 수정해야 유효한 운행기록부가 됩니다.")
        for lineno, msg in errors:
            print(f"   ✗ {lineno}행: {msg}")
    if warnings:
        print(f"\n  [경고 {len(warnings)}건]")
        for lineno, msg in warnings:
            print(f"   ! {lineno}행: {msg}")
    if not errors and not warnings:
        print("\n  ✓ 기재 정합성과 계기판 연속성에 문제가 없습니다.")

    if related_cost and errors:
        print("\n  관련비용 비교는 기재 오류를 수정한 뒤 다시 실행하십시오.")
    elif related_cost:
        print("\n" + "-" * 78)
        print("  [운행기록부 작성 효과]")
        no_log_ratio = 1.0 if related_cost <= LOGBOOK_THRESHOLD else LOGBOOK_THRESHOLD / related_cost
        with_log = round(related_cost * ratio)
        without_log = round(related_cost * no_log_ratio)
        print(f"   관련비용            : {related_cost:,}원")
        print(f"   미작성 시 업무사용비율: {no_log_ratio:.2%}  → 업무사용금액 {without_log:,}원")
        print(f"   작성 시 업무사용비율  : {ratio:.2%}  → 업무사용금액 {with_log:,}원")
        diff = with_log - without_log
        if related_cost <= LOGBOOK_THRESHOLD:
            print(f"   → 관련비용이 1,500만원 이하이므로 운행기록부 없이도 100% 인정됩니다.")
            if diff < 0:
                print(f"      (기록상 비율 {ratio:.2%}를 적용하면 오히려 {-diff:,}원 불리합니다)")
        elif diff > 0:
            print(f"   → 작성 시 업무사용금액이 {diff:,}원 늘어납니다.")
            print(f"      ※ 감가상각비는 별도로 연 800만원 한도가 적용되므로 "
                  f"실제 필요경비 증가액은 이보다 작을 수 있습니다.")
        elif diff == 0:
            print(f"   → 작성 여부에 따른 차이가 없습니다.")
        else:
            print(f"   → 이 기록으로는 작성이 오히려 {-diff:,}원 불리합니다.")
        print("-" * 78)

    print()
    return 1 if errors else 0


def main():
    p = argparse.ArgumentParser(description="업무용승용차 운행기록부 검증 · 집계 도구")
    p.add_argument("csv_path", help="운행기록부 CSV 경로 (templates/운행기록부_양식.csv 형식)")
    p.add_argument("--related-cost", type=int, default=0,
                   help="해당 과세기간 업무용승용차 관련비용 합계(원). "
                        "입력하면 운행기록부 작성 여부에 따른 차이를 비교합니다.")
    args = p.parse_args()

    rows = load(args.csv_path)
    errors, warnings, parsed = verify(rows)
    sys.exit(report(parsed, errors, warnings, args.related_cost))


if __name__ == "__main__":
    main()
