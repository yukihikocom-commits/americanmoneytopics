import anthropic
import json
import logging
from config import CLAUDE_MODEL, TARGET_CATEGORIES, READER_PERSONA, MAX_CANDIDATES

logger = logging.getLogger(__name__)
client = anthropic.Anthropic()


def filter_and_rank(articles):
    if not articles:
        logger.warning("記事が0件のためフィルタリングをスキップします")
        return []

    article_list_text = "\n".join(
        f"{i+1}. [{a['source']}] {a['title']} ({a['url']})"
        for i, a in enumerate(articles)
    )
    target_categories_text = "\n".join(f"- {c}" for c in TARGET_CATEGORIES)

    prompt = f"""あなたは在米日本人向けお金情報メディアのコンテンツ担当です。

読者像: {READER_PERSONA}

対象カテゴリ:
{target_categories_text}

以下の記事リストの中から、上記カテゴリに関連し、在米日本人にとって
実際に役立つ情報を最大{MAX_CANDIDATES}件選んでください。

選定基準:
- 確定申告・税金・退職口座・大学費用・不動産に直接関係する
- 法改正・上限額変更・申請期限など、具体的な数字や変化がある
- 在米日本人特有の論点に触れていればなお良い
- 半導体・テック・個別株・仮想通貨の話題は除外する

出力はJSON形式のみで返してください。それ以外のテキストは不要です。

フォーマット:
[
  {{
    "rank": 1,
    "title": "記事タイトル",
    "url": "記事URL",
    "source": "メディア名",
    "category": "確定申告 / 退職口座 / 大学費用 / 不動産",
    "reason": "選んだ理由（日本語30字以内）",
    "article_type_suggestion": "A（ルール解説型）またはB（実体験深掘り型）"
  }}
]

記事リスト:
{article_list_text}
"""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        candidates = json.loads(raw)
        logger.info(f"フィルタリング完了: {len(candidates)}件選出")
        return candidates
    except json.JSONDecodeError as e:
        logger.error(f"JSONパースエラー: {e}")
        return []
    except Exception as e:
        logger.error(f"Claude API エラー: {e}")
        return []


def generate_x_posts(candidates):
    if not candidates:
        return candidates

    articles_text = "\n".join(
        f"{i+1}. [{c.get('category', '')}] {c['title']} — {c.get('reason', '')}\nURL: {c['url']}"
        for i, c in enumerate(candidates)
    )

    prompt = f"""あなたは在米日本人向けお金情報メディアのSNS担当です。

読者像: {READER_PERSONA}

以下の各記事について、X（旧Twitter）への投稿文を日本語で作成してください。

条件:
- 全角・半角を合わせて140文字以内（URLの23文字を除いた本文のみ）
- 在米日本人に刺さる切り口・言葉遣い
- 数字・期限・金額など具体的な情報を優先して入れる
- ハッシュタグは最後に1〜2個（例: #在米生活 #確定申告）
- 絵文字は冒頭に1つだけ使う

出力はJSON形式のみで返してください。それ以外のテキストは不要です。

フォーマット:
[
  {{
    "rank": 1,
    "x_post": "投稿本文（URLは含めない）"
  }}
]

記事リスト:
{articles_text}
"""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        posts = json.loads(raw)
        post_map = {p["rank"]: p["x_post"] for p in posts}
        for c in candidates:
            c["x_post"] = post_map.get(c["rank"], "")
        logger.info(f"Xポスト生成完了: {len(posts)}件")
    except Exception as e:
        logger.error(f"Xポスト生成エラー: {e}")

    return candidates
