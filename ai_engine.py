from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# =====================================================
# 08:00 — PUL TOPISH PROMPTI
# =====================================================
def prompt_money(topic: str) -> str:
    return f"""
Sof o‘zbek tilida yoz.

Mavzu: {topic}

Bu post pul topish haqida bo‘lsin.
Umumiy gaplar qat’iyan bo‘lmasin.

Majburiy tarkib:
1. Aniq pul topish yo‘li (real bo‘lsin)
2. Bu yo‘l KIMLAR uchun mos
3. Qanday xizmat yoki ish bajariladi
4. Qancha daromad qilish mumkin (oyiga oraliq bilan)
5. Boshlash uchun 1-VA-ENG MUHIM qadam

Talablar:
- Motivatsion shiorlar yo‘q
- Amaliy va aniq yoz
- 6–8 jumla
- Oxirida savol: “Siz shu yo‘lni sinab ko‘rganmisiz?”
"""

# =====================================================
# 15:00 — KASB + YO‘L XARITASI + O‘ZBEKCHA YOUTUBE
# =====================================================
def prompt_skill(topic: str) -> str:
    return f"""
Sof o‘zbek tilida yoz.

Mavzu: {topic}

Bu post BITTA real kasb haqida bo‘lsin.

Majburiy tarkib:
1. Kasb nomi
2. Kimlar uchun mos
3. 0 dan boshlash uchun 3 bosqich (1 → 2 → 3)
4. O‘rganilishi kerak bo‘lgan ENG MUHIM ko‘nikma
5. O‘rganish uchun YOUTUBE’dagi O‘ZBEK TILIDAGI darslar:
   - 1–2 ta o‘zbekcha YouTube kanal yoki dars mavzusi
   - Kanal yoki video nomi aniq yozilsin
6. Qo‘shimcha o‘rganish uchun:
   - 1 ta kitob YOKI bepul resurs
7. 3–6 oyda qanday natijaga chiqish mumkin

Talablar:
- Umumiy gaplar yo‘q
- Juda amaliy yoz
- Reklama ohangi bo‘lmasin
- Oxirida savol: “Siz shu kasbni o‘rganishni bugun boshlaysizmi?”
"""

# =====================================================
# 20:00 — MOTIVATSIYA (REAL SHAXS)
# =====================================================
def prompt_motivation(topic: str) -> str:
    return f"""
Sof o‘zbek tilida yoz.

Mavzu: {topic}

Bu post REAL inson misolida motivatsiya bo‘lsin.

Majburiy tarkib:
1. Inson kim bo‘lgan (oldin)
2. Qanday qiyinchilik bo‘lgan
3. Qaysi BITTA qaror burilish yasagan
4. Hozirgi holati (natija)
5. O‘quvchi uchun xulosa

Talablar:
- Hikoya tarzida yoz
- Juda realistik bo‘lsin
- Sun’iy motivatsiya yo‘q
- Oxirida savol: “Siz qaysi qarorni kechiktiryapsiz?”
"""

# =====================================================
# ASOSIY GENERATOR — VAQTGA QARAB TANLAYDI
# =====================================================
def generate_post(topic: str, post_type: str) -> str:
    if post_type == "money":
        prompt = prompt_money(topic)
    elif post_type == "skill":
        prompt = prompt_skill(topic)
    elif post_type == "motivation":
        prompt = prompt_motivation(topic)
    else:
        raise ValueError("Noto‘g‘ri post_type")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()
