import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging
import warnings
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Ignore matplotlib warnings for cleaner logs
warnings.filterwarnings("ignore")

# Output folder (سيتم حفظ كل المخرجات هنا)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure logging (يكتب لملف output/github_stats.log)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, "github_stats.log")),
        logging.StreamHandler()
    ]
)


class GitHubProfileGenerator:
    """
    GitHub profile generator:
    - fetch user & repos (pagination)
    - aggregate language bytes (from /languages endpoint)
    - compute stats
    - create charts (bar + pie + dashboard)
    - generate README.md (profile) and save assets to output/
    """

    def __init__(self, username: str, token: Optional[str] = None):
        self.username = username
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": f"GitHubStatsGenerator-{username}"
            })
        # palette / known colors (تطابق ألوان لغات معروفة)
        self.language_colors = {
            "Python": "#3776AB", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
            "Java": "#ED8B00", "C++": "#00599C", "C": "#A8B9CC", "C#": "#239120",
            "Go": "#00ADD8", "Rust": "#DEA584", "PHP": "#777BB4", "Ruby": "#CC342D",
            "Swift": "#FA7343", "Kotlin": "#7F52FF", "Dart": "#0175C2",
            "HTML": "#E34C26", "CSS": "#1572B6", "SCSS": "#CF649A",
            "Vue": "#4FC08D", "React": "#61DAFB", "Angular": "#DD0031",
            "Shell": "#89E051", "Other": "#A0A0A0"
        }

        # Arabic-friendly fonts fallback
        plt.rcParams["font.family"] = ["DejaVu Sans", "Arial Unicode MS", "Tahoma"]

        logging.info(f"Initialized GitHubProfileGenerator for: {username}")

    def fetch_user_data(self) -> Dict:
        url = f"{self.base_url}/users/{self.username}"
        try:
            r = self.session.get(url)
            r.raise_for_status()
            logging.info("Fetched user data")
            return r.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching user data: {e}")
            return {}

    def fetch_repositories(self) -> List[Dict]:
        repos = []
        page = 1
        per_page = 100
        logging.info("Fetching repositories (with pagination)...")
        while True:
            try:
                r = self.session.get(f"{self.base_url}/users/{self.username}/repos",
                                     params={"page": page, "per_page": per_page, "sort": "updated"})
                r.raise_for_status()
                page_repos = r.json()
                if not page_repos:
                    break
                repos.extend(page_repos)
                logging.info(f"Fetched page {page} ({len(page_repos)} repos)")
                page += 1
                if len(page_repos) < per_page:
                    break
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching repositories: {e}")
                break
        logging.info(f"Total repos fetched: {len(repos)}")
        return repos

    def fetch_language_stats(self, repos: List[Dict]) -> Dict[str, int]:
        """
        For each (non-fork) repo call /repos/{owner}/{repo}/languages
        sum bytes per language — returns dict lang -> bytes
        """
        language_bytes: Dict[str, int] = {}
        logging.info("Fetching languages per repository...")
        for idx, repo in enumerate(repos, start=1):
            if repo.get("fork", False):
                continue
            repo_name = repo.get("name")
            try:
                r = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}/languages")
                if r.status_code == 200:
                    langs = r.json()
                    for lang, b in langs.items():
                        language_bytes[lang] = language_bytes.get(lang, 0) + b
                else:
                    logging.debug(f"Languages fetch for {repo_name} returned {r.status_code}")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Failed to fetch languages for {repo_name}: {e}")
            if idx % 20 == 0:
                logging.info(f"Processed {idx} repositories for language stats...")
        logging.info(f"Collected language bytes for {len(language_bytes)} languages")
        return language_bytes

    def calculate_stats(self, repos: List[Dict], user_data: Dict) -> Dict:
        """
        Calculate totals and simple analytics.
        Returns a stats dict that used by dashboard + README
        """
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        total_size = sum(r.get("size", 0) for r in repos)  # size in KB as returned by API

        public_repos = len([r for r in repos if not r.get("private", False)])
        original_repos = len([r for r in repos if not r.get("fork", False)])
        forked_repos = len([r for r in repos if r.get("fork", False)])

        repo_languages = [r.get("language") for r in repos if r.get("language")]
        language_counts = Counter(repo_languages)

        # recent activity: repos updated in last 30 days
        now = datetime.utcnow()
        recent_repos = 0
        for r in repos:
            updated_at = r.get("updated_at")
            if updated_at:
                try:
                    dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    if (now - dt).days <= 30:
                        recent_repos += 1
                except Exception:
                    continue

        return {
            "user_data": user_data,
            "total_repos": len(repos),
            "public_repos": public_repos,
            "original_repos": original_repos,
            "forked_repos": forked_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_size_kb": total_size,
            "language_counts": language_counts,
            "recent_activity": recent_repos,
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "account_age_days": self._calculate_account_age(user_data.get("created_at", "")),
            "last_active": self._get_last_activity(repos)
        }

    def _calculate_account_age(self, created_at: str) -> int:
        try:
            if not created_at:
                return 0
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            return (datetime.utcnow() - created).days
        except Exception:
            return 0

    def _get_last_activity(self, repos: List[Dict]) -> str:
        try:
            if not repos:
                return "N/A"
            latest = max(repos, key=lambda x: x.get("updated_at", ""))
            date = datetime.fromisoformat(latest["updated_at"].replace("Z", "+00:00"))
            return date.strftime("%Y-%m-%d")
        except Exception:
            return "N/A"

    def _get_color(self, lang: str, idx: int) -> str:
        """Return pref color or fallback to seaborn palette"""
        if lang in self.language_colors:
            return self.language_colors[lang]
        palette = sns.color_palette("tab20", 20)
        return palette[idx % len(palette)].as_hex()

    def create_language_chart(self, language_bytes: Dict[str, int]) -> None:
        """Generate bar + pie for top languages (by bytes) and save png/svg"""
        if not language_bytes:
            logging.warning("No language bytes to plot")
            return

        total = sum(language_bytes.values())
        percentages = {l: (b / total) * 100 for l, b in language_bytes.items()}
        sorted_langs = sorted(percentages.items(), key=lambda x: x[1], reverse=True)[:10]
        langs = [l for l, _ in sorted_langs]
        pcts = [p for _, p in sorted_langs]
        colors = [self._get_color(l, i) for i, l in enumerate(langs)]

        plt.style.use("seaborn-v0_8")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=150)

        # Bar chart
        bars = ax1.bar(langs, pcts, color=colors, edgecolor="white", linewidth=1)
        for bar, pct in zip(bars, pcts):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     f"{pct:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax1.set_title("توزيع لغات البرمجة (Top 10)", fontsize=14, fontweight="bold")
        ax1.set_ylabel("النسبة المئوية (%)", fontsize=11)
        ax1.tick_params(axis="x", rotation=45)

        # Pie chart
        ax2.pie(pcts, labels=langs, colors=colors, autopct="%1.1f%%", startangle=90,
                textprops={"fontsize": 9, "fontweight": "bold"})
        ax2.set_title("التوزيع الدائري للغات", fontsize=14, fontweight="bold")

        plt.tight_layout()
        png_path = os.path.join(OUTPUT_DIR, "language_distribution.png")
        svg_path = os.path.join(OUTPUT_DIR, "language_distribution.svg")
        plt.savefig(svg_path, format="svg", dpi=300, bbox_inches="tight")
        plt.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        logging.info(f"Saved language charts: {svg_path}, {png_path}")

    def create_activity_dashboard(self, stats: Dict) -> None:
        """Create a 2x2 dashboard: repo types, social, engagement, account info"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), dpi=150)

            # repo stats
            repo_data = [stats["original_repos"], stats["forked_repos"]]
            repo_labels = ["مستودعات أصلية", "مستودعات منسوخة"]
            colors1 = ["#2E8B57", "#FF6347"]
            bars1 = ax1.bar(repo_labels, repo_data, color=colors1, edgecolor="white")
            for bar, val in zip(bars1, repo_data):
                ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         str(val), ha="center", va="bottom", fontweight="bold")
            ax1.set_title("إحصائيات المستودعات", fontsize=13, fontweight="bold")

            # social
            social_data = [stats["followers"], stats["following"]]
            social_labels = ["متابعون", "يتابع"]
            colors2 = ["#4169E1", "#32CD32"]
            bars2 = ax2.bar(social_labels, social_data, color=colors2, edgecolor="white")
            for bar, val in zip(bars2, social_data):
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         str(val), ha="center", va="bottom", fontweight="bold")
            ax2.set_title("الإحصائيات الاجتماعية", fontsize=13, fontweight="bold")

            # engagement
            engagement_data = [stats["total_stars"], stats["total_forks"]]
            engagement_labels = ["نجوم", "تفرعات"]
            colors3 = ["#FFD700", "#FF69B4"]
            bars3 = ax3.bar(engagement_labels, engagement_data, color=colors3, edgecolor="white")
            for bar, val in zip(bars3, engagement_data):
                ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         str(val), ha="center", va="bottom", fontweight="bold")
            ax3.set_title("إحصائيات التفاعل", fontsize=13, fontweight="bold")

            # account info box
            ax4.axis("off")
            info_text = f"""👤 {self.username}
عمر الحساب: {stats['account_age_days']} يوم
إجمالي المستودعات: {stats['total_repos']}
حجم الكود (تقريبي): {stats['total_size_kb'] / 1024:.1f} MB
نشاط خلال 30 يوم: {stats['recent_activity']} مستودع
آخر نشاط: {stats['last_active']}
"""
            ax4.text(0.05, 0.95, info_text, fontsize=12, verticalalignment="top",
                     bbox=dict(boxstyle="round,pad=0.6", facecolor="#e6f2ff", alpha=0.9))

            plt.suptitle(f"لوحة GitHub - {self.username}", fontsize=16, fontweight="bold")
            plt.tight_layout()
            svg_path = os.path.join(OUTPUT_DIR, "github_dashboard.svg")
            png_path = os.path.join(OUTPUT_DIR, "github_dashboard.png")
            plt.savefig(svg_path, format="svg", dpi=300, bbox_inches="tight")
            plt.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
            plt.close()
            logging.info(f"Saved dashboard: {svg_path}, {png_path}")
        except Exception as e:
            logging.error(f"Error creating dashboard: {e}")

    def create_readme_content(self, stats: Dict) -> str:
        """
        Generate a README.md string that can be written to repo root.
        It references the generated images (output/*.png or svg)
        """
        user = stats.get("user_data", {})
        top_langs = stats["language_counts"].most_common(5)
        top_langs_list = ", ".join([l for l, _ in top_langs[:3]]) or "—"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        readme = f"""# مرحباً 👋 أنا {user.get('name', self.username)}

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=36BCF7&center=true&vCenter=true&width=600&lines=مرحباً+بكم+في+ملفي+الشخصي;مطور+شغوف;{top_langs_list}" alt="Typing"/>
</div>

## 📊 إحصائياتي على GitHub

<div align="center">
  <!-- صور التوزيع والداشبورد -->
  <img src="./{OUTPUT_DIR}/language_distribution.svg" alt="Languages" width="700"/>
  <br/>
  <img src="./{OUTPUT_DIR}/github_dashboard.svg" alt="Dashboard" width="700"/>
</div>

### 🚀 لمحة سريعة
- 🔭 أعمل على مشاريع: {top_langs_list}
- 🌱 أتعلم باستمرار تقنيات جديدة
- 👯 أحب التعاون في Open Source

### 📈 إحصائيات رئيسية
- ⭐ إجمالي النجوم: {stats['total_stars']}
- 🍴 إجمالي التفرعات: {stats['total_forks']}
- 👥 المتابعون: {stats['followers']}
- 📅 آخر نشاط: {stats['last_active']}

---

⏱ آخر تحديث: {now}
"""
        return readme
