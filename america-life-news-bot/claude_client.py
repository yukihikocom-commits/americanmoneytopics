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

    prompt = f"""あなたは在米日本人向けアメリカ生活情報メディアのコンテンツ担当です。

読者像: {READER_PERSONA}

対象カテゴリ:
{target_categories_text}

以下の記事リストの中から、上記カテゴリに関連し、在米日本人にとって
アメリカでの日常生活の実務に役立つ情報を最大{MAX_CANDIDATES}件選んでください。

選定基準:
- ビザ・移民、運転免許・車、医療・保険、子育て・教育、生活インフラ、治安・災害など、
  アメリカ生活の実務に直接関係する
- 制度変更・申請方法・期限・料金改定など、具体的な数字や変化がある
- 在米日本人特有の論点（言語の壁、文化差、駐在員ならではの事情等）に触れていればなお良い
- 金融・投資・株式市場・仮想通貨・個別企業の業績など、お金や資産運用に関する話題は除外する
- 政治家のゴシップ、芸能、スポーツなど生活実務と関係ない話題は除外する

出力はJSON形式のみで返してください。それ以外のテキストは不要です。

フォーマット:
[
  {{
    "rank": 1,
    "title": "記事タイトル",
    "url": "記事URL",
    "source": "メディア名",
    "category": "ビザ / 運転免許 / 医療 / 子育て / 生活インフラ / 治安・災害",
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

    prompt = f"""あなたは在米日本人向けアメリカ生活情報メディアのSNS担当である。

読者像: {READER_PERSONA}

以下の各記事について、X（旧Twitter）への投稿文を日本語で1記事につき3パターン作成せよ。
各パターンは違う観点・切り口で書き分けること（例: 結論直球、数字インパクト、実用Tips、読者への問いかけ、など）。

文体・構成ルール:
- 本文は120〜180字（URLの23字は除く）
- だ・である調（です・ます調は禁止）
- 結論先行（冒頭で要点をズバッと提示）
- 修飾語は削る。シンプルに、強い言葉で
- フックは強く、本文はシンプル
- 数字・金額・期限・制度名・ツール名（サービス名）など具体的情報を必ず入れる
- 実用Tips（読者が今すぐ行動できる要素）を1つ以上含める
- 在米日本人向けの言葉遣い
- ハッシュタグは使わない
- 絵文字は冒頭に1つだけ

出力はJSON形式のみで返せ。それ以外のテキストは不要。

フォーマット:
[
  {{
    "rank": 1,
    "x_posts": [
      {{"angle": "観点ラベル（例: 結論直球）", "text": "投稿本文（URLは含めない）"}},
      {{"angle": "観点ラベル（例: 数字インパクト）", "text": "投稿本文（URLは含めない）"}},
      {{"angle": "観点ラベル（例: 実用Tips）", "text": "投稿本文（URLは含めない）"}}
    ]
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
        post_map = {p["rank"]: p.get("x_posts", []) for p in posts}
        for c in candidates:
            c["x_posts"] = post_map.get(c["rank"], [])
        logger.info(f"Xポスト生成完了: {len(posts)}件 × 3パターン")
    except Exception as e:
        logger.error(f"Xポスト生成エラー: {e}")

    return candidates
