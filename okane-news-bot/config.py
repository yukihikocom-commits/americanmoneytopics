PROJECT_NAME = "在米日本人向け お金ネタ収集ボット"

CLAUDE_MODEL = "claude-sonnet-4-5"
MAX_CANDIDATES = 10

RSS_FEEDS = [
    "https://feeds.content.dowjones.io/public/rss/RSSPersonalFinance",
    "https://search.cnbc.com/rs/search/combinedcsvfeed.aspx?keyword=personal+finance&type=news",
    "https://feeds.marketwatch.com/marketwatch/personal-finance/",
    "https://www.kiplinger.com/feeds/rss/magazine.rss",
    "https://feeds.feedburner.com/nerdwallet/CsEp",
]

OFFICIAL_URLS = [
    "https://www.irs.gov/newsroom/irs-news",
    "https://studentaid.gov/announcements-events/news",
    "https://www.ssa.gov/news/press/releases/",
    "https://comptroller.texas.gov/taxes/",
]

TARGET_CATEGORIES = [
    "確定申告・税金（IRS、州税、自営業、控除）",
    "退職口座（401k、IRA、Roth、SEP-IRA）",
    "子どもの大学費用（529プラン、FAFSA、奨学金）",
    "米国不動産（住宅ローン、固定資産税、HOA）",
]

READER_PERSONA = "在米日本人（駐在員・移住者・永住者）、30〜50代、子育て世代"
