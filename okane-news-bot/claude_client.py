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
