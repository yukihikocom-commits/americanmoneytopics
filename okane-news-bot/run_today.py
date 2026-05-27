import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

import config
from claude_client import filter_and_rank, generate_x_posts
from main import build_markdown

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

articles = [
    {
        "title": "IRS releases tax inflation adjustments for tax year 2026, including amendments from the One, Big, Beautiful Bill",
        "url": "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill",
        "summary": "Standard deduction increases to $32,200 for married couples filing jointly, $16,100 for single. New deductions for seniors up to $6,000/$12,000. Child tax credit max $2,200 per child.",
        "published": "2026-05-22",
        "source": "IRS.gov",
        "type": "official",
    },
    {
        "title": "8 IRS changes that could impact your taxes in 2026",
        "url": "https://www.empower.com/the-currency/money/8-irs-changes-could-impact-your-taxes-2026-news",
        "summary": "Older adults, tipped workers, and some car buyers gain access to new deductions. Standard deduction, tax brackets, and retirement contribution limits all adjusted upward for inflation.",
        "published": "2026-05-20",
        "source": "Empower",
        "type": "rss",
    },
    {
        "title": "2026 tax brackets and IRS changes: Reference guide",
        "url": "https://www.firstcitizens.com/wealth/insights/intel/2026-tax-brackets",
        "summary": "Comprehensive guide to 2026 federal income tax brackets and key IRS changes including standard deduction increases and new provisions from One Big Beautiful Bill.",
        "published": "2026-05-18",
        "source": "First Citizens Bank",
        "type": "rss",
    },
    {
        "title": "401(k) limit increases to $24,500 for 2026, IRA limit increases to $7,500",
        "url": "https://www.irs.gov/newsroom/401k-limit-increases-to-24500-for-2026-ira-limit-increases-to-7500",
        "summary": "401(k) standard contribution limit rises to $24,500. IRA limit increases to $7,500. Catch-up contribution for 401(k) increased to $8,000. IRA catch-up increased to $1,100. Super catch-up for age 60-63 remains $11,250.",
        "published": "2026-05-15",
        "source": "IRS.gov",
        "type": "official",
    },
    {
        "title": "6 Changes to IRAs, 401(k)s and HSAs in 2026",
        "url": "https://www.kiplinger.com/retirement/retirement-planning/changes-to-iras-401ks-hsas-in-2026",
        "summary": "Key changes include higher contribution limits, new Roth catch-up rules for high earners ($150K+), updated income phase-out ranges for IRA deductions, and SIMPLE plan limit increase to $17,000.",
        "published": "2026-05-12",
        "source": "Kiplinger",
        "type": "rss",
    },
    {
        "title": "Top 3 retirement planning changes in 2026",
        "url": "https://komonews.com/news/nation-world/top-3-retirement-planning-changes-in-2026-roth-ira-401k-secure-big-beautiful-bill-salt-deduction-seniors-filing-ira",
        "summary": "Roth IRA phase-out range rises to $153K-$168K for singles, $242K-$252K for married. High earners ($150K+) must make catch-up contributions as Roth. SECURE Act provisions continue.",
        "published": "2026-05-10",
        "source": "KOMO News",
        "type": "rss",
    },
    {
        "title": "The Latest 529 Plan Rule Changes: What's New for 2026",
        "url": "https://www.savingforcollege.com/article/529-plan-new-rules-changes",
        "summary": "K-12 withdrawal limit doubles from $10,000 to $20,000 per student. Expanded eligible expenses include tutoring, test fees, dual-enrollment, educational therapies. Roth IRA rollover option with $7,500 annual limit.",
        "published": "2026-05-14",
        "source": "Saving for College",
        "type": "rss",
    },
    {
        "title": "Grandparent 529 Plans: Now Invisible to the FAFSA Formula",
        "url": "https://www.collegehelpguide.com/blog/grandparent-529-fafsa-advantage-2026/",
        "summary": "As of 2026-27 aid cycle, grandparent 529 distributions are not reported as student income. Previously distributions counted as untaxed income and could reduce aid by up to 50%. Contribution limit $19,000/$38,000 per beneficiary.",
        "published": "2026-05-08",
        "source": "CollegeHelpGuide",
        "type": "rss",
    },
    {
        "title": "SALT deduction cap rises to $40,400 in 2026 under One Big Beautiful Bill",
        "url": "https://www.hrblock.com/tax-center/irs/tax-law-and-policy/one-big-beautiful-bill-salt-deduction/",
        "summary": "SALT deduction cap rises from $10,000 to $40,400 in 2026, climbing 1% annually through 2029. PMI premiums now deductible as mortgage interest. Residential energy credits expired end of 2025.",
        "published": "2026-05-20",
        "source": "H&R Block",
        "type": "rss",
    },
    {
        "title": "9 Major Real Estate Tax Changes Effective 2026",
        "url": "https://www.noradarealestate.com/blog/9-major-real-estate-tax-changes-effective-2026/",
        "summary": "QBI deduction made permanent at 23%. Property taxes surged 30% nationwide 2019-2024. Median home price record $417,700. Residential Clean Energy Credit expired. SALT cap increase significant for high-tax states.",
        "published": "2026-05-16",
        "source": "Norada Real Estate",
        "type": "rss",
    },
    {
        "title": "May 2026 Real Estate Market Update: Inventory up, prices at record highs",
        "url": "https://www.churchillmortgage.com/articles/may-2026-real-estate-market-update",
        "summary": "Inventory up 4.2% YoY with 1.23M active listings. Existing home sales rose 0.2% in April. Median prices hit record $417,700. Inflation jumped to 3.8% in April, highest in 3 years.",
        "published": "2026-05-22",
        "source": "Churchill Mortgage",
        "type": "rss",
    },
    {
        "title": "IRS announces time-limited settlement for conservation easement disputes",
        "url": "https://www.irs.gov/newsroom/news-releases-for-current-month",
        "summary": "On May 13, 2026, the IRS announced a time-limited settlement opportunity for eligible taxpayers involved in conservation easement or historic preservation easement disputes.",
        "published": "2026-05-13",
        "source": "IRS.gov",
        "type": "official",
    },
    {
        "title": "What 2026's Tax Shifts Mean for Homeowners",
        "url": "https://www.floridarealtors.org/news-media/news-articles/2026/02/what-2026s-tax-shifts-mean-homeowners",
        "summary": "Analysis of how 2026 tax law changes affect homeowners including SALT deduction increase, PMI deductibility, expired energy credits, and higher standard deduction impacts on mortgage interest deduction benefits.",
        "published": "2026-05-19",
        "source": "Florida Realtors",
        "type": "rss",
    },
    {
        "title": "IRS 2026 tax changes: what they mean for homeownership",
        "url": "https://www.mpamag.com/us/mortgage-industry/industry-trends/irs-2026-tax-changes-what-they-mean-for-homeownership/552545",
        "summary": "PMI premiums officially treated as deductible mortgage interest in 2026. SALT cap increase benefits homeowners in high-tax states. Standard deduction increase may reduce itemizing incentive for some.",
        "published": "2026-05-21",
        "source": "Mortgage Professional America",
        "type": "rss",
    },
]

logger.info("=== ネタ収集開始（WebSearch代替データ） ===")
logger.info(f"合計収集件数: {len(articles)}件")

candidates = filter_and_rank(articles)
if not candidates:
    logger.error("ネタ候補を生成できませんでした")
    sys.exit(1)

candidates = generate_x_posts(candidates)

date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
markdown = build_markdown(candidates, date_str)

output_path = f"output/{date_str}_candidates.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(markdown)
logger.info(f"保存完了: {output_path}")

print("\n" + "=" * 60)
print(markdown)
print("=" * 60)

logger.info("=== ネタ収集完了 ===")
