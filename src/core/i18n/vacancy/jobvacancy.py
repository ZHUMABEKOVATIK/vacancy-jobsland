# eng, rus, kaa, uzb, kaz, kgz, tjk, aze, tkm
from src.models.vacancy import JobVacancy
from src.core.i18n.vacancy.vacancy_types import TgPost

LABELS = {
    "eng": {
        'title': "Application",
        'location': {
            'country': 'Country',
            'region': 'Region',
        },
        'hashtag': "#vacancy",
        "position_title": "Position",
        "organization_name": "Company",
        "address": "Location",
        "requirements": "Requirements",
        "duties": "Responsibilities",
        "work_schedule": "Working hours",
        "salary": "Salary",
        "contact": "Contact",
        "additional_info": "Additional Info",
    },
    "rus": {
        'title': "Заявка",
        'location': {
            'country': 'Страна',
            'region': 'Область',
        },
        'hashtag': "#Вакансия",
        "position_title": "Должность",
        "organization_name": "Компания",
        "address": "Локация",
        "requirements": "Требования",
        "duties": "Обязанности",
        "work_schedule": "График работы",
        "salary": "Зарплата",
        "contact": "Контакты",
        "additional_info": "Дополнительно",
    },
    "kaa": {
        'title': "Soraw",
        'location': {
            'country': 'Mámleket',
            'region': 'Aymaq',
        },
        'hashtag': "#vacancy",
        "position_title": "Lawazım",
        "organization_name": "Mekeme",
        "address": "Mánzil",
        "requirements": "Talaplar",
        "duties": "Wazıypalar",
        "work_schedule": "Jumıs waqıtı",
        "salary": "Aylıq",
        "contact": "Baylanıs",
        "additional_info": "Qosımsha",
    },
    "uzb": {
        'title': "Ariza",
        'location': {
            'country': 'Davlat',
            'region': 'Viloyat',
        },
        'hashtag': "#vacancy",
        "position_title": "Lavozim",
        "organization_name": "Tashkilot",
        "address": "Manzil",
        "requirements": "Talablar",
        "duties": "Vazifalar",
        "work_schedule": "Ish vaqti",
        "salary": "Oylik",
        "contact": "Aloqa",
        "additional_info": "Qo‘shimcha",
    },
    "kaz": {
        'title': "Өтініш",
        'location': {
            'country': 'Мемлекет',
            'region': 'Аймақ',
        },
        'hashtag': "#vacancy",
        "position_title": "Лауазым",
        "organization_name": "Компания",
        "address": "Мекенжай",
        "requirements": "Талаптар",
        "duties": "Міндеттер",
        "work_schedule": "Жұмыс уақыты",
        "salary": "Жалақы",
        "contact": "Байланыс",
        "additional_info": "Қосымша",
    },
    "kgz": {
        'title': "Өтүнүч",
        'location': {
            'country': 'Өлкө',
            'region': 'Область',
        },
        'hashtag': "#vacancy",
        "position_title": "Кызмат орду",
        "organization_name": "Мекеме",
        "address": "Жайгашкан жери",
        "requirements": "Талаптар",
        "duties": "Милдеттер",
        "work_schedule": "Иштөө тартиби",
        "salary": "Айлык акы",
        "contact": "Байланыш",
        "additional_info": "Кошумча",
    },
    "tjk": {
        'title': "Дархост",
        'location': {
            'country': 'Кишвар',
            'region': 'Минтақа',
        },
        'hashtag': "#vacancy",
        "position_title": "Мансаб",
        "organization_name": "Ширкат",
        "address": "Ҷойгиршавӣ",
        "requirements": "Талабот",
        "duties": "Вазифа",
        "work_schedule": "Реҷаи корӣ",
        "salary": "Маош",
        "contact": "Тамос",
        "additional_info": "Маълумоти иловагӣ",
    },
    "aze": {
        'title': "Müraciət",
        'location': {
            'country': 'Ölkə',
            'region': 'Region',
        },
        'hashtag': "#vacancy",
        "position_title": "Уҳдадориҳо",
        "organization_name": "Şirkət",
        "address": "Yerləşdiyi yer",
        "requirements": "Tələblər",
        "duties": "Tapşırıqlar",
        "work_schedule": "İş qrafiki",
        "salary": "Maaş",
        "contact": "Əlaqə",
        "additional_info": "Əlavə",
    },
    "tkm": {
        'title': "Arza",
        'location': {
            'country': 'Ýurt',
            'region': 'Sebit',
        },
        'hashtag': "#vacancy",
        "position_title": "Wezipesi",
        "organization_name": "Kompaniýa",
        "address": "Ýerleşýän ýeri",
        "requirements": "Talaplar",
        "duties": "Borçlary",
        "work_schedule": "Iş tertibi",
        "salary": "Aýlyk",
        "contact": "Aragatnaşyk",
        "additional_info": "Goşmaça",
    },
}
# kaa, uzb, rus, kaz, eng, kgz, tjk, tkm, aze

def _lbl(labels: dict, code: str, key: str) -> str:
    return labels.get(code, labels["eng"]).get(key, key)

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_group_format(post: JobVacancy, lang_code: str = "kaa") -> str:
    d = LABELS.get(lang_code, LABELS["eng"])

    header = f"# {d['title']} ID: {post.id}\n\n"

    # Локация
    loc = f"🌎 {esc(post.country.name) if post.country else ''}"
    if post.region_id and post.region:
        loc += f" | {esc(post.region.name)}"
    loc += "\n\n"

    lines = []
    lines.append(f"{d['hashtag']}\n")
    lines.append(f"👨‍💼 <b>{d['position_title']}</b>: {esc(post.position_title)}")
    if post.organization_name:
        lines.append(f"🏛 <b>{d['organization_name']}</b>: {esc(post.organization_name)}")
    lines.append(f"📍 <b>{d['address']}</b>: {esc(post.address)}")
    lines.append(f"📌 <b>{d['requirements']}</b>: {esc(post.requirements)}")
    if post.duties:
        lines.append(f"📑 <b>{d['duties']}</b>: {esc(post.duties)}")
    lines.append(f"⏰ <b>{d['work_schedule']}</b>: {esc(post.work_schedule)}")
    lines.append(f"💰 <b>{d['salary']}</b>: {esc(post.salary)}")
    lines.append(f"☎️ <b>{d['contact']}</b>: {esc(post.contact)}")
    if post.additional_info:
        lines.append(f"📎 <b>{d['additional_info']}</b>: {esc(post.additional_info)}")

    return header + loc + "\n".join(lines)

async def get_vacancy_channel_format(lang_code: str, post: JobVacancy) -> TgPost:
    d = LABELS.get(lang_code, LABELS["eng"])
    lines = [
        f"{d['hashtag']}\n",
        f"👨‍💼 <b>{d['position_title']}</b>: {esc(post.position_title)}",
    ]
    if post.organization_name:
        lines.append(f"🏛 <b>{d['organization_name']}</b>: {esc(post.organization_name)}")
    lines.append(f"📍 <b>{d['address']}</b>: {esc(post.address)}")
    lines.append(f"📌 <b>{d['requirements']}</b>: {esc(post.requirements)}")
    if post.duties:
        lines.append(f"📑 <b>{d['duties']}</b>: {esc(post.duties)}")
    lines.append(f"⏰ <b>{d['work_schedule']}</b>: {esc(post.work_schedule)}")
    lines.append(f"💰 <b>{d['salary']}</b>: {esc(post.salary)}")
    lines.append(f"☎️ <b>{d['contact']}</b>: {esc(post.contact)}")
    if post.additional_info:
        lines.append(f"📎 <b>{d['additional_info']}</b>: {esc(post.additional_info)}")
    result = "\n".join(lines)
    return TgPost(text=result)