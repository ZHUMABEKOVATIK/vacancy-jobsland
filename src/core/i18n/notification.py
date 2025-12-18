from html import escape

# eng, rus, kaa, uzb, kaz, kgz, tjk, aze, tkm

def normalize_lang(code: str | None) -> str:
    if not code:
        return "eng"
    c = code.lower()
    return c

LABELS = {
    "eng": {
        'title': 'Application',
        'content': 'Your announcement has been submitted! We will publish it within 12 hours.',
        'approve': "✅ Your request number {id} has been sent to our channel @{channel}.",
        'reject': "❌ Your request number {id} has been rejected. Reason: {reason}",
    },
    "rus": {
        'title': "Заявка",
        'content': 'Ваше объявление отправлено! Мы опубликуем его в течение 12 часов.',
        'approve': "✅ Ваш запрос номер {id} был отправлен на наш канал @{channel}.",
        'reject': "❌ Ваш запрос номер {id} был отклонён. Причина: {reason}",
    },
    "kaa": {
        'title': "Soraw",
        'content': 'Sorawıńız jiberildi, Biz onı 12 saat ishinde daǵaza etemiz!',
        'approve': "✅ {id} sanlı sorawıńız @{channel} kanalımızǵa qoyıldi.",
        'reject': "❌ {id} sanlı sorawıńız biykar etildi. Sebebi: {reason}",
    },
    "uzb": {
        'title': "Ariza",
        'content': 'Eʼloningiz yuborildi! Biz uni 12 soat ichida eʼlon qilamiz.',
        'approve': "✅ Soʻrovingiz raqami {id} bizning @{channel} kanalimizga yuborildi.",
        'reject': "❌ So‘rovingiz raqami {id} rad etildi. Sabab: {reason}",
    },
    "kaz": {
        'title': "Өтініш",
        'content': 'Хабарламаңыз жіберілді! Біз оны 12 сағат ішінде жариялаймыз.',
        'approve': "✅ Сұранысыңыздың нөмірі {id} біздің @{channel} арнамызға жіберілді.",
        'reject': "❌ Сұранысыңыздың нөмірі {id} қабылданбады. Себебі: {reason}",
    },
    "kgz": {
        'title': "Өтүнүч",
        'content': 'Жарнамаңыз жөнөтүлдү! Биз аны 12 сааттын ичинде жарыялайбыз.',
        'approve': "✅ Суранышыңыздын номери {id} биздин @{channel} каналыбызга жөнөтүлдү.",
        'reject': "❌ Суранышыңыз №{id} четке кагылды. Себеби: {reason}",
    },
    "tjk": {
        'title': "Дархост",
        'content': 'Эълони шумо фиристода шуд! Мо онро дар давоми 12 соат нашр мекунем.',
        'approve': "✅ Дархости шумо бо рақами {id} ба канали мо @{channel} фиристода шуд.",
        'reject': "❌ Дархости шумо бо рақами {id} рад карда шуд. Сабаб: {reason}",
    },
    "aze": {
        'title': "Müraciət",
        'content': 'Elanınız göndərildi! Biz onu 12 saat ərzində dərc edəcəyik.',
        'approve': "✅ Sorğunuzun nömrəsi {id} bizim @{channel} kanalımıza göndərildi.",
        'reject': "❌ Sorğunuzun nömrəsi {id} rədd edildi. Səbəb: {reason}",
    },
    "tkm": {
        'title': "Arza",
        'content': 'Bildirişiňiz ugradyldy! Biz ony 12 sagadyň içinde çap ederis.',
        'approve': "✅ Sorgyňyz №{id} biziň @{channel} kanalymyza iberildi.",
        'reject': "❌ Sorgyňyz №{id} ret edildi. Sebäp: {reason}",
    },
}

def get_notification_format(request_id: int, lang_code: str):
    data = LABELS.get(lang_code, LABELS["eng"])
    text = (
        f"⏳ {data.get('title')} ID: {request_id}\n"
        f"{data.get('content')}"
    )
    return text

def get_approve_format(request_id: int, lang_code: str, channel_username: str):
    data = LABELS.get(f"{lang_code}")
    text = data.get('approve').format(id = request_id, channel = channel_username)
    return text

def get_reject_format(request_id: int, lang_code: str, reason: str):
    data = LABELS.get(f"{lang_code}")
    text = data.get('reject').format(id = request_id, reason = reason)
    return text