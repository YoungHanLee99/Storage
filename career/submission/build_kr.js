const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
        BorderStyle, LevelFormat, convertInchesToTwip } = require('docx');
const fs = require('fs');

const FONT = "맑은 고딕";
const R = (text, o={}) => new TextRun({ text, font: FONT, size: o.size ?? 19, bold: o.bold, italics: o.italics, color: o.color });

const P = (runs, o={}) => new Paragraph({
  children: Array.isArray(runs) ? runs : [runs],
  spacing: { before: o.before ?? 0, after: o.after ?? 60, line: o.line ?? 264 },
  alignment: o.align,
  indent: o.indent,
  border: o.border,
});

// 섹션 제목 (아래 테두리)
const H = (t) => new Paragraph({
  children: [R(t, { bold: true, size: 22 })],
  spacing: { before: 240, after: 100 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "000000", space: 2 } },
});

// 소제목
const H2 = (t) => P([R(t, { bold: true, size: 20 })], { before: 140, after: 50 });

// 회사 / 직위 줄
const ORG = (org, period) => new Paragraph({
  children: [R(org, { bold: true, size: 20 }), R("\t" + period, { size: 18 })],
  tabStops: [{ type: "right", position: convertInchesToTwip(6.9) }],
  spacing: { before: 160, after: 20 },
});
const ROLE = (t) => P([R(t, { italics: true, size: 18 })], { after: 50 });

// 불릿
const B = (t, bold) => new Paragraph({
  numbering: { reference: "bul", level: 0 },
  children: typeof t === "string" ? [R(t)] : t,
  spacing: { after: 40, line: 264 },
});

const doc = new Document({
  numbering: { config: [{ reference: "bul", levels: [{
    level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 340, hanging: 200 } } } }] }] },
  sections: [{
    properties: { page: { margin: { top: 900, bottom: 900, left: 1000, right: 1000 } } },
    children: [

P([R("경 력 기 술 서", { bold: true, size: 30 })], { align: AlignmentType.CENTER, after: 60 }),
P([R("지원 포지션 : [쿠팡] 내부조사 선임 담당자 (Global Investigations), Principal", { size: 18 })], { align: AlignmentType.CENTER, after: 40 }),
P([R("이영한 (Young-Han LEE)  ·  younghanlee040@gmail.com  ·  010-7315-6400", { size: 18 })], { align: AlignmentType.CENTER, after: 120 }),

H("1. 요약"),
P([R("수사와 기소로 법조 경력을 시작해, 증거개시와 기업 형사·규제 대응을 거쳐, 현재 5개국 그룹의 법무·거버넌스를 총괄하는 "),
   R("17년차 한·미 이중자격 변호사", { bold: true }), R("입니다.")]),
P([R("육군 법무관으로 "), R("군 형사사건을 직접 수사·기소", { bold: true }),
   R("했고, 미국 국제무역위원회(ITC) 영업비밀 침해 조사에서 "), R("증거개시 절차를 총괄", { bold: true }),
   R("하며 증인신문을 직접 수행·방어하고 상대방에 대한 제재 신청을 주도해 인용받았으며, 그에 따른 궐석판결을 위원회 단계에서 유지시켰습니다. 법무법인 태평양·덴톤스에서 기업과 임원의 형사·규제 사건을 대리했고, 현재 ㈜디스트릭트코리아 CSO 겸 CLO로서 한국·미국·일본·대만·중국 5개국 그룹 법무와 규제·형사 절차를 총괄하며 Big4 자문사와 함께 미국 상장 준비(특수관계자 정리·공시 대응력·내부회계관리)를 이끌고 있습니다.")]),
P([R("대한민국 변호사(2009) · Washington D.C. Bar(2014) · ", { bold: true }),
   R("미국 통일 CPA 시험 합격(AICPA, Maine, 2012)", { bold: true }),
   R(" · 한국어(원어민) / 영어(full professional) / 일본어(business level)")]),

H("2. 핵심 역량"),
B([R("형사 수사 및 기소", { bold: true }), R(" — 육군 법무관으로 군 형사사건 수사·기소 직접 수행")]),
B([R("증거개시(Discovery) 총괄", { bold: true }), R(" — 미 ITC 조사에서 문서개시·증인신문·제재 신청 주도")]),
B("증인신문(Deposition) 수행 및 방어, 신청서면 작성"),
B("사실관계·증거 분석에 기반한 결론 및 권고 도출"),
B("기업 및 임원의 형사·규제 절차 대응 (수사기관·국토부·산업부·과세당국)"),
B([R("AML/CFT 및 금융범죄 규제 자문", { bold: true }), R(" — USD 스테이블코인 발행·상환 거래의 외환·자금세탁방지 검토")]),
B([R("미국 상장 준비", { bold: true }), R(" — 지주구조, 특수관계자 거래 정리, 공시 대응력, 내부회계관리 요건")]),
B("그룹 거버넌스 — 이사회·주주총회 운영, 해외 법인·합작법인 설립 및 지속적 준법 관리"),
B("다국적 이해관계자 관리 — 5개국 그룹, 군 지휘부, 정부부처, 글로벌 투자자"),
B("국제중재 및 분쟁 해결 (USD 5,000만 규모 지체상금 중재 포함)"),

H("3. 경력 상세"),

ORG("㈜디스트릭트코리아", "2023. 8. ~ 현재"),
ROLE("CSO 겸 CLO (Chief Strategy Officer & Chief Legal Officer)"),
B("ARTE MUSEUM을 운영하는 d'strict 그룹의 전사 법무 기능 총괄 — 한국·미국·일본·대만·중국 5개국 사업장 및 프로젝트"),
B([R("규제·형사 절차 총괄", { bold: true }), R(" — 국내 규제기관 조사 및 형사 절차, 국제 합의·중재·소송, 관할을 넘는 분쟁 및 집행 대응")]),
B([R("AML/CFT 자문", { bold: true }), R(" — USD 스테이블코인 발행·상환 운영의 외환 및 자금세탁방지 규제 검토, 토큰 이코노미·바이백 구조 자문")]),
B([R("미국 상장 준비 주도", { bold: true }), R(" (Big4 자문사 공동) — 지주회사 구조, 기업 정비(corporate housekeeping), 특수관계자 거래 정리, 공시 대응력(disclosure readiness) 확보")]),
B("해외 자회사·합작법인 설립 및 거버넌스 — 법인 설립, 자본구조, 이사·임원 선임, 이사회·주주총회 운영, 지속적 준법 관리"),
B("그룹 조직 재편 설계·실행 — 계열사 감자 및 주주 엑시트"),
B("투자 유치 및 IR — 실사 대응, 텀시트 협상, 본계약 체결 (국내외 전략적·재무적 투자자)"),
B("라이선싱·유통·공급·용역·부동산 등 그룹 상시 계약 검토·협상 및 사업부서 법률 자문"),

ORG("법무법인(유) 덴톤스리 (Dentons Lee)", "2020. 8. ~ 2023. 7."),
ROLE("파트너"),
B([R("미국 ITC 조사 대리", { bold: true }), R(" (영업비밀 침해 및 특허침해) — 증거개시 절차 및 신청(motions practice) 총괄, 상대방에 대한 제재(sanctions) 인용 및 이에 따른 궐석판결을 위원회 단계에서 유지")]),
B("한국 및 다국적 기업 대상 국제 분쟁, cross-border M&A·PE, 기술·플랫폼 규제 자문"),
B("d'strict에 대한 IMM인베스트먼트 PE 투자 건 회사측 대리 (텀시트 ~ 2023. 1. 클로징)"),

ORG("Dentons US LLP", "2019. 8. ~ 2020. 8."),
ROLE("Associate (Washington, D.C.)"),
B("미국 ITC 영업비밀 침해 조사 참여 — 증거개시 지원, 증인신문(deposition) 수행 및 방어, 신청서면 작성"),
B("상대방에 대한 궐석 및 제재 신청서(motion for default and sanctions) 기초"),

ORG("법무법인(유) 태평양 (Bae, Kim & Lee)", "2014. 4. ~ 2019. 7."),
ROLE("Senior Associate — 입법·행정 그룹 / 환경 그룹"),
B("금융규제, 에너지, cross-border 거래, 방위사업, 기술법 자문"),
B("삼성전자, 현대모비스, 아시아나항공, 한국항공우주산업 등 주요 기업의 중요 사건 대리"),
B("투자계약·주식매매계약·조합계약 등 거래문서 협상 및 작성"),
B("자율주행차·전기차·드론·로보틱스 규제 자문"),

ORG("대한민국 육군 법무관 (JAG Corps)", "2009. 4. ~ 2014. 3."),
ROLE("법무참모 / 군검찰관"),
B([R("군 형사사건 수사 및 기소 직접 수행", { bold: true })]),
B("제12보병사단장에 대한 교전규칙 자문"),
B("대한민국 정부 관련 손해배상 민사소송 대리"),
B([R("(파견) 한미연합사령부 법무참모", { bold: true }), R(" (2013. 4. ~ 2014. 3.) — 연합사·유엔사·주한미군 사령관에 대한 교전규칙 및 SOFA 자문, 미군 법무관과의 정례 협의 주재")]),
B([R("(파견) 방위사업청 사업관리자", { bold: true }), R(" (2012. 4. ~ 2013. 3.) — 불량탄약 관련 USD 5,000만 규모 지체상금 국제중재 수행 (서면 ~ 합의)")]),

ORG("기타", "2017 ~ 2018"),
B("평창2018 동계올림픽·패럴림픽조직위원회 법률자문 (2017. 8. ~ 2018. 6.) — 계약·지식재산·조세 자문, 후원사·파트너 계약 작성"),
B("Olympic Broadcasting Services(OBS) 중재인 (2018. 1. ~ 3.) — 국가올림픽위원회 간 국제계약 분쟁 재정"),

H("4. 대표 사례"),

H2("조사 · 형사 · 규제"),
B("미국 ITC 영업비밀 침해·특허침해 조사 — 증거개시 및 신청 절차 총괄, 증인신문 수행·방어, 궐석 및 제재 신청서 작성, 제재 인용 및 궐석판결 유지"),
B("육군 법무관으로서 군 형사사건 수사 및 기소"),
B("메릴린치 전 한국대표 형사사건 변호 (수사 및 공판)"),
B("기업 및 임원의 형사·규제 절차 대리 — 조세, 인허가"),
B("아시아나항공 국토교통부 60일 운항정지 처분 취소 행정소송 대리"),
B("대한민국 정부 대리 — 불량 함포탄 관련 USD 5,000만 지체상금 국제중재"),

H2("거버넌스 · 컴플라이언스 · 상장 대응력"),
B("Big4 자문사와 미국 상장 준비 주도 — 지주구조 분석, 특수관계자 정리, 공시 대응력"),
B("미국 지주회사 기준 다국적 그룹 구조 설계 — 자본금, 주주권, 이사회 거버넌스"),
B("미국·일본 자회사 및 합작법인 설립 — 설립·출자부터 지분 이전, 임원 선임까지"),
B("정관상 Qualified IPO 정의(해외거래소 한정)와 실제 상장 트랙의 불일치를 식별하고, 그로 인한 자동전환·CB전환·리픽싱 조항의 작동 불능을 정관 및 투자계약 개정으로 정비"),
B("외국 발행인의 국내 시장 1차 상장 구조 설계 — 해외 지주회사 직상장 vs 국내 SPC, US-GAAP 인정, 정관 전면 개정, 3개 법역 법률의견서, 명의개서대리인·락업·내부회계관리제도 요건"),

H2("금융범죄 · 디지털자산 · 기술규제"),
B("블록체인 인프라 사업자 자문 — USD 스테이블코인 발행·상환의 외환 및 AML/CFT 규제 검토"),
B("게임·콘텐츠 발행사 자문 — 토큰 이코노미 및 토큰 바이백 구조"),
B("산업통상자원부 자문 — 전기차·자율주행차·로보틱스·드론에 대한 국내외 규제체계 비교 연구"),
B("Royal Dutch Shell 한국거래소 REC 시장 거래참여자 등록 및 REC 거래 대리"),

H("5. 학력 · 자격 · 어학"),
H2("자격"),
B([R("대한민국 변호사", { bold: true }), R(" (2009. 1.)  ·  "), R("Washington D.C. Bar", { bold: true }), R(" (2014. 9.)")]),
B([R("미국 통일 CPA 시험 합격", { bold: true }), R(" — AICPA, State of Maine (2012. 6.)")]),
B("한국금융투자협회 증권투자권유자문인력(2009. 9.) · 파생상품투자권유자문인력(2009. 11.) · 집합투자자산운용사(2009. 12.)"),
H2("학력"),
B("Georgetown University Law Center — LL.M. (Energy Law), 2019. 5."),
B("Northwestern Pritzker School of Law — LL.M. (Joint Degree Program in Seoul), 2014. 5. (우등졸업)"),
B("서울대학교 대학원 법학과 — 법학석사 (증권법·상법), 과정 수료"),
B("사법연수원 (대법원) 수료 — 2009. 1."),
B("서울대학교 법과대학 — 법학사, 2005. 2."),
H2("어학"),
B("한국어 (원어민) · 영어 (full professional) · 일본어 (business level)"),

    ],
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(process.argv[2], b);
  console.log("written:", process.argv[2], b.length, "bytes");
});
