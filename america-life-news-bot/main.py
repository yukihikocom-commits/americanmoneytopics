import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

import config
from fetcher import fetch_all
from claude_client import filter_and_rank, generate_x_posts

load_dotenv()

Path("logs").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

log_filename = f"logs/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

CATEGORY_EMOJI = {
    "ビザ": "🛂",
    "運転免許": "🚗",
    "医療": "🏥",
    "子育て": "🎒",
    "生活インフラ": "💡",
    "治安": "🚨",
    "災害": "🌪️",
}


def build_markdown(candidates, date_str):
    lines = [
        f"# 今日のネタ候補 {date_str}",
        "",
        f"合計 {len(candidates)} 件",
        "",
        "---",
        "",
    ]
    for item in candidates:
        emoji = next(
            (v for k, v in CATEGORY_EMOJI.items() if k in item.get("category", "")),
            "📌",
        )
        lines += [
            f"## {item['rank']}. {emoji} {item['title']}",
            "",
            f"- カテゴリ: {item.get('category', '—')}",
            f"- タイプ提案: {item.get('article_type_suggestion', '—')}",
            f"- 理由: {item.get('reason', '—')}",
            f"- 出典: {item.get('source', '—')}",
            f"- URL: {item.get('url', '—')}",
            "",
            "【Xポスト案（3パターン）】",
        ]
        x_posts = item.get("x_posts") or []
        if x_posts:
            for i, p in enumerate(x_posts, 1):
                lines += [
                    f"({i}) [{p.get('angle', '—')}]",
                    p.get("text", "—"),
                    "",
                ]
        else:
            lines += ["—", ""]
        lines += ["---", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY が .env に設定されていません")
        sys.exit(1)

    logger.info("=== ネタ収集開始 ===")

    articles = fetch_all(config.RSS_FEEDS, config.OFFICIAL_URLS)
    if not articles:
        logger.error("記事を1件も取得できませんでした")
        sys.exit(1)

    candidates = filter_and_rank(articles)
    if not candidates:
        logger.error("ネタ候補を生成できませんでした")
        sys.exit(1)

    candidates = generate_x_posts(candidates)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    markdown = build_markdown(candidates, date_str)

    if args.dry_run:
        print("\n" + "=" * 60)
        print(markdown)
        print("=" * 60)
        logger.info("dry-runのためファイル保存をスキップしました")
    else:
        output_path = f"output/{date_str}_candidates.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        logger.info(f"保存完了: {output_path}")

    logger.info("=== ネタ収集完了 ===")


if __name__ == "__main__":
    main()
