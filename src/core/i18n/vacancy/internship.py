# eng, rus, kaa, uzb, kaz, kgz, tjk, aze, tkm
from src.models.vacancy import Internship
from src.core.i18n.vacancy.vacancy_types import TgPost
from src.core.i18n.vacancy.converter import read_json_file

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_channel_format(lang_code: str, post: Internship) -> TgPost:
    LABELS_JSON = await read_json_file("./i18n_jsons/internship.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["eng"])
    lines = [
        f"{d['hashtag']}\n",
        f"👨‍💼 <b>{d['position_title']}</b>: {esc(post.position_title)}",
    ]
    if post.organization_name:
        lines.append(f"🏛 <b>{d['organization_name']}</b>: {esc(post.organization_name)}")
    lines += [
        f"📌 <b>{d['requirements']}</b>: {esc(post.requirements)}",
        f"⚙️ <b>{d['duties']}</b>: {esc(post.duties)}"
    ]
    if post.conditions:
        lines.append(f"⚖️ <b>{d['conditions']}</b>: {esc(post.conditions)}")
    lines += [
        f"📍 <b>{d['address']}</b>: {esc(post.address)}",
        f"💰 <b>{d['salary']}</b>: {esc(post.salary)}",
        f"☎️ <b>{d['contact']}</b>: {esc(post.contact)}",
    ]
    if post.additional_info:
        lines.append(f"📎 <b>{d['additional_info']}</b>: {esc(post.additional_info)}")
    result = "\n".join(lines)
    return TgPost(text=result)

async def get_vacancy_group_format(post: Internship, lang_code: str = "kaa") -> str:
    LABELS_JSON = await read_json_file("internship.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["kaa"])
    header = f"# {d['title']} ID: {post.id}\n\n"

    # Локация
    loc = f"🌎 {esc(post.country.name) if post.country else ''}"
    if post.region_id and post.region:
        loc += f" | {esc(post.region.name)}"
    loc += "\n\n"
    group_version = await get_vacancy_channel_format(lang_code=lang_code, post=post)
    return header + loc + group_version.text