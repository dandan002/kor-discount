import re

bib_content = open("tex/citations.bib", "r", encoding="utf-8").read()

updates = {
    "kim_korea_discount_causes": {
        "author": "김현석 and 서정원 and 최서연",
        "title": "코리아 디스카운트의 잠재적 원인들에 대한 실증분석"
    },
    "lee_korea_discount_pbr": {
        "author": "이정환",
        "title": "기업의 자본배분관점에서 코리아 디스카운트 분석: PBR 변화의 결정요인을 중심으로"
    },
    "lee_value_up_effectiveness": {
        "author": "이진효",
        "title": "기업 밸류업 프로그램의 실효성에 관한 연구"
    },
    "joo_foreign_investors_value_up": {
        "author": "주병철",
        "title": "외국인 투자자의 비대칭적 규율과 기업 밸류업 — 코리아 디스카운트 기업의 성장 불일치 해소를 중심으로"
    },
    "park_cross_shareholdings_takeover": {
        "author": "박진재",
        "title": "상호주를 통한 경영권 방어 — 전략의 유효성, 코리아 디스카운트 해소 가능성을 중심으로"
    },
    "yang_korea_discount_growth_vs_governance": {
        "author": "양철원 and 왕수봉 and 최재원",
        "title": "무엇이 과연 코리아디스카운트와 PBR을 설명하는가? 성장동력, 주주환원, 기업지배 가설의 비교"
    },
    "kang_commercial_act_market_reactions": {
        "author": "강나라 and 김희주",
        "title": "상법 개정의 기대감과 한국 주식시장의 반응: “코리아 디스카운트” 완화 가능성"
    },
    "park_stewardship_code_earnings": {
        "author": "박성환 and 강평경 and 정태섭 and 박재형",
        "title": "기관투자자의 스튜어드십 코드 도입과 기업의 재무보고 품질: 이익의 질을 중심으로"
    },
    "suh_holding_company_discount": {
        "author": "박진 and 서정원 and 강신우",
        "title": "한국주식시장의 지주회사 디스카운트"
    }
}

for key, data in updates.items():
    pattern = r"(@article\{" + key + r",\s*author\s*=\s*\{).*?(?=\},\s*title)"
    bib_content = re.sub(pattern, r"\g<1>" + data["author"], bib_content, flags=re.DOTALL)
    
    title_pattern = r"(@article\{" + key + r",.*?title\s*=\s*\{).*?(?=\},\s*(?:note|journal|year))"
    bib_content = re.sub(title_pattern, r"\g<1>" + data["title"], bib_content, flags=re.DOTALL)

with open("tex/citations.bib", "w", encoding="utf-8") as f:
    f.write(bib_content)
