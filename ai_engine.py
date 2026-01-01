import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# =====================================================
# 1️⃣ ASOSIY POST GENERATOR
# =====================================================
def generate_post(topic: str) -> str:
    prompt = f"""
Sof o‘zbek tilida yoz.
Mavzu: {topic}

Bu oddiy motivatsion post bo‘lmasin.

Majburiy talablar:
1) Real pul topish yo‘li yoki real kasb haqida yoz
2) Kimlar uchun mosligini ayt
3) Qanday bosqichlarda o‘rganilishini yoz
4) Shu yo‘lda muvaffaqiyatga erishgan REAL shaxs yoki kasb egasi misolini keltir
5) 1–2 ta kitob yoki manba tavsiya qil
6) Oxirida aniq savol yoki topshiriq ber

Tuzilishi:
- Sarlavha (aniq kasb yoki yo‘l bilan)
- Muammo
- Bosqichma-bosqich yo‘l
- Real misol
- Kitob/manba
- Savol yoki harakat

Umumiy gaplar, hammaga ma’lum nasihatlar bo‘lmasin.

"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


# =====================================================
# 2️⃣ RASM UCHUN QISQA MATN (AI)
# =====================================================
def generate_image_text(full_post: str) -> dict:
    """
    To‘liq postdan rasm uchun mos, qisqa variant chiqaradi.
    """
    prompt = f"""
Quyidagi postdan RASM uchun mos, juda qisqa va lo‘nda variant tayyorla.

Qoidalar:
- Sof o‘zbek tilida
- Sarlavha: 1 qisqa gap
- Asosiy fikr: 2–3 qisqa gap
- Savol: 1 gap
- Ortiqcha gap bo‘lmasin

Post:
{full_post}

Natijani aynan shu formatda ber:
Sarlavha:
Asosiy:
Savol:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    raw_text = response.choices[0].message.content.strip()

    result = {"title": "", "body": "", "question": ""}

    for line in raw_text.splitlines():
        line = line.strip()
        if line.lower().startswith("sarlavha"):
            result["title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("asosiy"):
            result["body"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("savol"):
            result["question"] = line.split(":", 1)[1].strip()

    return result


# =====================================================
# 3️⃣ RASMGA SIG‘DIRISH UCHUN MAJBURIY QISQARTIRISH
# =====================================================
def fit_text_for_image(text: dict) -> dict:
    """
    Matn juda uzun bo‘lsa, rasm formatiga majburan moslaydi.
    """
    MAX_TITLE = 90
    MAX_BODY = 220
    MAX_QUESTION = 90

    def cut(t: str, limit: int) -> str:
        if not t:
            return ""
        return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "…"

    return {
        "title": cut(text.get("title", ""), MAX_TITLE),
        "body": cut(text.get("body", ""), MAX_BODY),
        "question": cut(text.get("question", ""), MAX_QUESTION),
    }
