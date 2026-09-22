const { Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle, PageBreak, convertInchesToTwip } = require('docx');
const fs = require('fs');
const FONT = "맑은 고딕";
const R = (t,o={}) => new TextRun({ text:t, font:FONT, size:o.size??20, bold:o.bold, italics:o.italics });
const P = (runs,o={}) => new Paragraph({ children:Array.isArray(runs)?runs:[runs],
  spacing:{ before:o.before??0, after:o.after??140, line:o.line??288 }, alignment:o.align });
const H = (t) => new Paragraph({ children:[R(t,{bold:true,size:24})], spacing:{before:0,after:160},
  border:{ bottom:{ style:BorderStyle.SINGLE, size:6, color:"000000", space:3 } } });

const doc = new Document({ sections:[{
  properties:{ page:{ margin:{ top:1100, bottom:1100, left:1100, right:1100 } } },
  children:[

H("커버레터 — [쿠팡] 내부조사 선임 담당자 (Global Investigations), Principal"),
P([R("이영한 (Young-Han LEE)  ·  younghanlee040@gmail.com  ·  010-7315-6400", {size:18})], {after:220}),

P([R("저는 "), R("수사와 기소로 법조 경력을 시작해, 증거개시와 형사·규제 대응을 거쳐, 현재 5개국 그룹의 법무·거버넌스를 총괄하고 있는 17년차 변호사", {bold:true}),
   R("입니다. 한국과 워싱턴 D.C. 양쪽에 변호사로 등록되어 있고, 미국 통일 CPA 시험에 합격했습니다.")]),

P([R("사실을 규명하는 일로 커리어를 시작했습니다.", {bold:true}),
   R(" 육군 법무관으로 재직하며 군 형사사건을 직접 수사하고 기소했습니다. 진술과 증거가 어긋날 때 무엇을 먼저 확보해야 하는지, 신문 순서를 어떻게 정해야 하는지, 결론을 뒷받침할 증거가 부족할 때 어떻게 써야 하는지를 그때 배웠습니다.")]),

P([R("증거를 다루는 일은 이후에도 이어졌습니다.", {bold:true}),
   R(" Dentons(워싱턴 D.C. 및 서울)에서 미국 국제무역위원회(ITC)의 영업비밀 침해 조사를 대리하며 "),
   R("증거개시 절차 전반을 총괄", {bold:true}),
   R("했습니다. 증인신문을 직접 수행하고 방어했으며, 상대방의 증거개시 위반에 대한 "),
   R("제재 신청을 주도해 인용받았고, 그에 따른 궐석판결을 위원회 단계에서 유지", {bold:true}),
   R("시켰습니다. 대규모 문서 검토, 은폐 정황의 입증, 그리고 그것을 판단권자가 받아들이는 형태로 서면화하는 작업이 그 사건의 전부였습니다.")]),

P([R("법무법인 태평양과 덴톤스에서는 조사받는 쪽을 대리했습니다.", {bold:true}),
   R(" 메릴린치 전 한국대표의 형사 사건을 포함해 기업과 임원의 형사·규제 절차를 다수 대리했습니다. 수사기관이 무엇을 보고 어떻게 판단하는지, 회사가 만든 기록이 나중에 어떻게 쓰이는지를 반대편에서 지켜본 경험은 조사를 설계할 때 그대로 쓰입니다.")]),

P([R("현재는 ㈜디스트릭트코리아에서 CSO 겸 CLO로", {bold:true}),
   R(" 한국·미국·일본·대만·중국 5개국의 그룹 법무를 총괄합니다. 규제기관 조사와 형사 절차를 직접 관장하고, 해외 자회사·합작법인의 거버넌스와 준법 관리를 담당하며, Big4 자문사와 함께 "),
   R("미국 상장 준비", {bold:true}),
   R("를 이끌고 있습니다 — 지주구조, 특수관계자 거래 정리, 공시 대응력과 내부회계관리 요건까지. USD 스테이블코인 발행·상환 거래의 "),
   R("외환·AML/CFT 규제 검토", {bold:true}), R("도 제가 맡고 있습니다.")]),

P([R("귀사에 지원하는 이유는 두 가지입니다.", {bold:true})], {before:80}),

P([R("첫째, 쿠팡은 "), R("미국 상장 법인이면서 한국 법제 아래에서 조사를 수행해야 하는", {bold:true}),
   R(" 회사입니다. 이 교차점은 까다롭습니다. 미국식 거버넌스(감사위원회 제보 접수 체계, 상장사 내부고발자 보호)와 한국 특유의 제약 — 직장 내 괴롭힘 조사의 법정 의무와 시한, 사내변호사 작성 문서의 제한적 보호, 직원 데이터 열람 근거의 사전 설계 필요성 — 은 서로 다른 설계를 요구합니다. 저는 양쪽 법역에서 자격을 갖고 실무를 해 왔고, 지금 미국 상장 준비를 직접 이끌면서 그 간극을 매일 다루고 있습니다.")]),

P([R("둘째, 이 포지션은 Fraud·Compliance 사건과 HR 사건을 "), R("한 사람이 모두", {bold:true}),
   R(" 다루도록 설계되어 있고, 조사 결론에서 멈추지 않고 권고와 개선까지 요구합니다. 대부분의 조사 전문가는 사실규명에서 끝납니다. 저는 그 사실이 형법상 횡령·배임에 해당하는지, 징계로 갔을 때 노동위원회에서 버티는지, 공시 의무를 발생시키는지를 "),
   R("조사 단계에서 함께 판단", {bold:true}), R("할 수 있습니다.")]),

P([R("한 가지를 먼저 말씀드리는 편이 나을 것 같습니다. 현재 C-level 직책에 있는 제가 Principal 포지션에 지원하는 것은 "),
   R("의도적인 선택", {bold:true}),
   R("입니다. 법무 총괄은 넓지만 얕습니다. 제가 가장 잘하고 가장 하고 싶은 일은 사안 하나를 끝까지 파고들어 사실을 확정하는 일이고, 그 감각은 수사·기소로 시작한 커리어에서 온 것입니다. 관리 범위를 넓히기보다, 법률 판단과 조사 실무가 모두 필요한 난도의 사건을 맡는 자리를 찾고 있습니다. 조사관은 조사 대상에 대한 인사권 없이 협조를 끌어내야 하는 직무이고, 귀사의 리더십 원칙 중 "),
   R("Influence without Authority", {bold:true}),
   R("가 제가 군에서도, 로펌에서도, 지금 자리에서도 해 온 일입니다.")]),

P([R("감사합니다.")], {before:120, after:60}),
P([R("이영한 드림")]),

new Paragraph({ children:[new PageBreak()] }),

H("Cover Letter — Principal, Global Investigations"),
P([R("Young-Han LEE  ·  younghanlee040@gmail.com  ·  +82 10-7315-6400", {size:18})], {after:220}),

P([R("I began my legal career "), R("investigating and prosecuting", {bold:true}),
   R(", moved through "), R("evidence discovery and criminal and regulatory defence", {bold:true}),
   R(", and now run the legal and governance function of a five-country group. I am admitted in "),
   R("Korea and Washington, D.C.", {bold:true}), R(", passed the "),
   R("Uniform CPA Examination", {bold:true}), R(", and have seventeen years of practice.")]),

P([R("Establishing facts is where I started.", {bold:true}),
   R(" As a Judge Advocate in the Republic of Korea Army, I investigated and prosecuted criminal matters. That is where I learned what to secure first when testimony and evidence diverge, how to sequence interviews, and how to write a finding when the evidence will not carry the conclusion you expected.")]),

P([R("Handling evidence stayed with me.", {bold:true}),
   R(" At Dentons in Washington, D.C. and Seoul, I "), R("led discovery and motions practice", {bold:true}),
   R(" in a U.S. International Trade Commission investigation involving trade-secret misappropriation. I took and defended depositions, drafted and won a "),
   R("motion for sanctions", {bold:true}),
   R(" against the opposing party for discovery misconduct, and "),
   R("sustained the resulting default judgment before the Commission", {bold:true}),
   R(". Large-scale document review, proving concealment, and writing it up so a decision-maker would adopt it — that case was all three.")]),

P([R("At Bae, Kim & Lee and Dentons I acted for the people being investigated.", {bold:true}),
   R(" I represented companies and their executives in Korean criminal and regulatory proceedings, including the former Head of Korea of Merrill Lynch. Watching from that side — what investigators look at, how a company’s own records are later used — is directly useful when designing an investigation.")]),

P([R("Today, as Chief Strategy Officer and Chief Legal Officer of d’strict Korea,", {bold:true}),
   R(" I run the group legal function across Korea, the United States, Japan, Taiwan and China. I oversee regulatory and criminal proceedings, govern overseas subsidiaries and joint ventures, and direct "),
   R("U.S. listing preparation", {bold:true}),
   R(" with a Big Four advisor — holding structure, related-party clean-up, disclosure readiness and internal accounting control. I also handle the "),
   R("foreign-exchange and AML/CFT", {bold:true}), R(" analysis for USD-stablecoin mint and redemption operations.")]),

P([R("Two things drew me to this role.", {bold:true})], {before:80}),

P([R("First, Coupang is a "), R("US-listed issuer that must investigate under Korean law", {bold:true}),
   R(". That intersection is genuinely difficult: US-style governance — audit-committee intake of complaints, issuer whistleblower protection — sits alongside Korea-specific constraints, including the statutory duty and timing for workplace harassment investigations, the limited protection afforded to documents prepared by in-house counsel, and the need to establish the basis for reviewing employee data in advance. I hold qualifications on "),
   R("both sides of that line", {bold:true}), R(" and work the gap daily in listing preparation.")]),

P([R("Second, the posting asks "), R("one person", {bold:true}),
   R(" to carry both fraud and HR matters, and to go past the finding to recommendations and remediation. Most investigators stop at the facts. I can assess, at the investigation stage, whether those facts amount to embezzlement or breach of trust under the Criminal Act, whether the resulting discipline survives the Labor Relations Commission, and whether a disclosure obligation is triggered.")]),

P([R("One thing is better said up front. Applying to a Principal role from a C-level seat is deliberate. A general counsel’s remit is wide but shallow. What I do best, and want to keep doing, is taking a single matter apart until the facts are settled — an instinct that goes back to prosecuting. I am looking for a seat where the hard matters land, not a wider span. An investigator has no line authority over anyone they investigate, which is why "),
   R("Influence without Authority", {bold:true}),
   R(" describes what I have been doing in uniform, in private practice, and in my current seat.")]),

P([R("Thank you for your consideration.")], {before:120, after:60}),
P([R("Young-Han LEE")]),

  ],
}]});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log("written:", b.length, "bytes"); });
