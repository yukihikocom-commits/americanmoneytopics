PROJECT_NAME = "在米日本人向け アメリカ生活ネタ収集ボット"

CLAUDE_MODEL = "claude-sonnet-4-5"
MAX_CANDIDATES = 10

RSS_FEEDS = [
    "https://feeds.feedburner.com/TravelersToday",
    "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "https://feeds.washingtonpost.com/rss/national",
    "https://www.usatoday.com/rss/news/",
    "https://feeds.npr.org/1003/rss.xml",
    "https://rss.cnn.com/rss/cnn_us.rss",
]

OFFICIAL_URLS = [
    "https://www.uscis.gov/newsroom",
    "https://travel.state.gov/content/travel/en/News/visas-news.html",
    "https://www.dmv.org/news/",
    "https://www.usa.gov/news",
]

TARGET_CATEGORIES = [
    "ビザ・グリーンカード・移民手続き",
    "運転免許・車・交通",
    "医療・保険・病院",
    "子育て・学校・教育",
    "生活インフラ（電気・水道・ネット・携帯）",
    "治安・自然災害・緊急情報",
]

READER_PERSONA = "在米日本人（駐在員・移住者・永住者）、30〜50代、アメリカ生活の実務情報を求めている層"
