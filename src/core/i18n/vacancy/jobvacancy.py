# eng, rus, kaa, uzb, kaz, kgz, tjk, aze, tkm
from src.models.vacancy import JobVacancy
from src.core.i18n.vacancy.vacancy_types import TgPost
from src.core.i18n.vacancy.converter import read_json_file

def _lbl(labels: dict, code: str, key: str) -> str:
    return labels.get(code, labels["eng"]).get(key, key)

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_group_format(post: JobVacancy, lang_code: str = "kaa") -> str:
    LABELS_JSON = await read_json_file("./i18n_jsons/jobvacancy.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["eng"])

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
    LABELS_JSON = await read_json_file("./i18n_jsons/jobvacancy.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["eng"])
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