from src.models.vacancy import OneTimeTask
from src.core.i18n.vacancy.vacancy_types import TgPost
from src.core.i18n.vacancy.converter import read_json_file

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_channel_format(lang_code: str, post: OneTimeTask) -> TgPost:
    LABELS_JSON = await read_json_file("./i18n_jsons/one_time_task.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["eng"])
    lines = [
        f"{d['hashtag']}\n",
        f"👨‍💼 <b>{d['who_needed']}</b>: {esc(post.who_needed)}",
        f"🏛 <b>{d['task_description']}</b>: {esc(post.task_description)}",
        f"💰 <b>{d['salary']}</b>: {esc(post.salary)}",
    ]
    if post.deadline:
        lines.append(f"⚙️ <b>{d['deadline']}</b>: {esc(post.deadline)}")
    lines += [
        f"☎️ <b>{d['contact']}</b>: {esc(post.contact)}",
    ]
    if post.address:
        lines.append(f"⚙️ <b>{d['address']}</b>: {esc(post.address)}")
    if post.additional_info:
        lines.append(f"📎 <b>{d['additional_info']}</b>: {esc(post.additional_info)}")
    result = "\n".join(lines)
    return TgPost(text=result)

async def get_vacancy_group_format(post: OneTimeTask, lang_code: str = "kaa") -> str:
    LABELS_JSON = await read_json_file("./i18n_jsons/one_time_task.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["eng"])
    header = f"# {d['title']} ID: {post.id}\n\n"

    # Локация
    loc = f"🌎 {esc(post.country.name) if post.country else ''}"
    if post.region_id and post.region:
        loc += f" | {esc(post.region.name)}"
    loc += "\n\n"
    group_version = await get_vacancy_channel_format(lang_code=lang_code, post=post)
    return header + loc + group_version.text