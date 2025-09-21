#!/usr/bin/env python3
"""
🚀 GitHub Profile Stats Generator
Professional tool for generating dynamic GitHub profile statistics
Author: GitHub Profile Automation
Version: 2.0.0
"""

import requests
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import Counter
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_stats.log'),
        logging.StreamHandler()
    ]
)

class GitHubProfileGenerator:
    """Professional GitHub Profile Statistics Generator"""
    
    def __init__(self, username: str, token: Optional[str] = None):
        self.username = username
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        # Set up headers
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": f"GitHubStatsGenerator-{username}"
            })
        
        # Enhanced color palette
        self.language_colors = {
            "Python": "#3776AB", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
            "Java": "#ED8B00", "C++": "#00599C", "C": "#A8B9CC", "C#": "#239120",
            "Go": "#00ADD8", "Rust": "#DEA584", "PHP": "#777BB4", "Ruby": "#CC342D",
            "Swift": "#FA7343", "Kotlin": "#7F52FF", "Dart": "#0175C2",
            "HTML": "#E34C26", "CSS": "#1572B6", "SCSS": "#CF649A",
            "Vue": "#4FC08D", "React": "#61DAFB", "Angular": "#DD0031",
            "Shell": "#89E051", "PowerShell": "#5391FE", "Dockerfile": "#2496ED",
            "YAML": "#CB171E", "JSON": "#000000", "XML": "#FF6600",
            "Jupyter Notebook": "#DA5B0B", "R": "#276DC3", "MATLAB": "#E16737",
            "Other": "#A0A0A0"
        }
        
        # Arabic font support
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
        
        logging.info(f"🚀 GitHub Profile Generator initialized for user: {username}")

    def fetch_user_data(self) -> Dict:
        """Fetch comprehensive user data from GitHub API"""
        try:
            response = self.session.get(f"{self.base_url}/users/{self.username}")
            response.raise_for_status()
            user_data = response.json()
            logging.info(f"✅ User data fetched successfully")
            return user_data
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Error fetching user data: {e}")
            return {}

    def fetch_repositories(self) -> List[Dict]:
        """Fetch all repositories with pagination support"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/users/{self.username}/repos",
                    params={"page": page, "per_page": per_page, "sort": "updated"}
                )
                response.raise_for_status()
                page_repos = response.json()
                
                if not page_repos:
                    break
                    
                repos.extend(page_repos)
                page += 1
                
                # Rate limit protection
                if len(page_repos) < per_page:
                    break
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"❌ Error fetching repositories: {e}")
                break
        
        logging.info(f"✅ Fetched {len(repos)} repositories")
        return repos

    def fetch_language_stats(self, repos: List[Dict]) -> Dict[str, int]:
        """Fetch detailed language statistics from repositories"""
        language_bytes = {}
        
        for i, repo in enumerate(repos, 1):
            if repo.get('fork', False):
                continue  # Skip forked repositories
                
            try:
                response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo['name']}/languages")
                if response.status_code == 200:
                    langs = response.json()
                    for lang, bytes_count in langs.items():
                        language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
                
                # Progress indicator
                if i % 10 == 0:
                    logging.info(f"📊 Processing repositories... {i}/{len(repos)}")
                    
            except requests.exceptions.RequestException as e:
                logging.warning(f"⚠️ Error fetching languages for {repo['name']}: {e}")
                continue
        
        return language_bytes

    def calculate_stats(self, repos: List[Dict], user_data: Dict) -> Dict:
        """Calculate comprehensive GitHub statistics"""
        if not repos:
            return {}
        
        # Basic stats
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        total_size = sum(repo.get('size', 0) for repo in repos)
        
        # Repository analysis
        public_repos = len([repo for repo in repos if not repo.get('private', False)])
        original_repos = len([repo for repo in repos if not repo.get('fork', False)])
        forked_repos = len([repo for repo in repos if repo.get('fork', False)])
        
        # Language analysis
        repo_languages = [repo.get('language') for repo in repos if repo.get('language')]
        language_counts = Counter(repo_languages)
        
        # Activity analysis
        recent_repos = [
            repo for repo in repos 
            if datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00')) > 
               datetime.now().replace(tzinfo=None) - timedelta(days=30)
        ]
        
        return {
            'user_data': user_data,
            'total_repos': len(repos),
            'public_repos': public_repos,
            'original_repos': original_repos,
            'forked_repos': forked_repos,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_size_kb': total_size,
            'language_counts': language_counts,
            'recent_activity': len(recent_repos),
            'followers': user_data.get('followers', 0),
            'following': user_data.get('following', 0),
            'account_age': self._calculate_account_age(user_data.get('created_at', '')),
            'last_active': self._get_last_activity(repos)
        }

    def _calculate_account_age(self, created_at: str) -> int:
        """Calculate account age in days"""
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            return (datetime.now().replace(tzinfo=None) - created.replace(tzinfo=None)).days
        except:
            return 0

    def _get_last_activity(self, repos: List[Dict]) -> str:
        """Get last activity date"""
        try:
            if not repos:
                return "N/A"
            latest = max(repos, key=lambda x: x.get('updated_at', ''))
            date = datetime.fromisoformat(latest['updated_at'].replace('Z', '+00:00'))
            return date.strftime("%Y-%m-%d")
        except:
            return "N/A"

    def create_language_chart(self, language_bytes: Dict[str, int]) -> None:
        """Create professional language distribution chart"""
        if not language_bytes:
            logging.warning("⚠️ No language data available")
            return
        
        # Calculate percentages
        total_bytes = sum(language_bytes.values())
        language_percentages = {
            lang: (bytes_count / total_bytes) * 100 
            for lang, bytes_count in language_bytes.items()
        }
        
        # Filter and sort languages (show top 10)
        sorted_languages = sorted(
            language_percentages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        if not sorted_languages:
            return
        
        # Create the chart
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=150)
        
        # Bar chart
        languages = [lang for lang, _ in sorted_languages]
        percentages = [pct for _, pct in sorted_languages]
        colors = [self.language_colors.get(lang, self.language_colors["Other"]) for lang in languages]
        
        bars = ax1.bar(languages, percentages, color=colors, edgecolor='white', linewidth=1.5)
        
        # Add percentage labels
        for bar, pct in zip(bars, percentages):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + 0.5, 
                    f'{pct:.1f}%', ha='center', va='bottom', 
                    fontweight='bold', fontsize=10)
        
        ax1.set_title('📊 توزيع لغات البرمجة', fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('النسبة المئوية (%)', fontsize=12)
        ax1.set_xlabel('اللغات البرمجية', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3)
        
        # Pie chart
        wedges, texts, autotexts = ax2.pie(
            percentages, labels=languages, colors=colors,
            autopct='%1.1f%%', startangle=90, 
            textprops={'fontsize': 9, 'fontweight': 'bold'}
        )
        
        ax2.set_title('🥧 التوزيع الدائري للغات', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('language_distribution.svg', format='svg', dpi=300, bbox_inches='tight')
        plt.savefig('language_distribution.png', format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info("✅ Language distribution chart created successfully")

    def create_activity_dashboard(self, stats: Dict) -> None:
        """Create comprehensive activity dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), dpi=150)
        
        # Repository Stats
        repo_data = [stats['original_repos'], stats['forked_repos']]
        repo_labels = ['مستودعات أصلية', 'مستودعات منسوخة']
        colors1 = ['#2E8B57', '#FF6347']
        
        bars1 = ax1.bar(repo_labels, repo_data, color=colors1, edgecolor='white', linewidth=2)
        ax1.set_title('📁 إحصائيات المستودعات', fontsize=14, fontweight='bold')
        ax1.set_ylabel('عدد المستودعات', fontsize=12)
        
        for bar, count in zip(bars1, repo_data):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + 0.5, 
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # Social Stats
        social_data = [stats['followers'], stats['following']]
        social_labels = ['متابعون', 'يتابع']
        colors2 = ['#4169E1', '#32CD32']
        
        bars2 = ax2.bar(social_labels, social_data, color=colors2, edgecolor='white', linewidth=2)
        ax2.set_title('👥 الإحصائيات الاجتماعية', fontsize=14, fontweight='bold')
        ax2.set_ylabel('العدد', fontsize=12)
        
        for bar, count in zip(bars2, social_data):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.5, 
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # Engagement Stats
        engagement_data = [stats['total_stars'], stats['total_forks']]
        engagement_labels = ['نجوم', 'تفرعات']
        colors3 = ['#FFD700', '#FF69B4']
        
        bars3 = ax3.bar(engagement_labels, engagement_data, color=colors3, edgecolor='white', linewidth=2)
        ax3.set_title('⭐ إحصائيات التفاعل', fontsize=14, fontweight='bold')
        ax3.set_ylabel('العدد', fontsize=12)
        
        for bar, count in zip(bars3, engagement_data):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, height + 0.5, 
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        # Account Info
        ax4.axis('off')
        info_text = f"""
📊 معلومات الحساب
        
👤 اسم المستخدم: {self.username}
📅 عمر الحساب: {stats['account_age']} يوم
📂 إجمالي المستودعات: {stats['total_repos']}
💾 إجمالي الحجم: {stats['total_size_kb'] / 1024:.1f} MB
🔄 نشاط حديث: {stats['recent_activity']} مستودع
📈 آخر نشاط: {stats['last_active']}
        """
        
        ax4.text(0.1, 0.9, info_text, fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
        
        plt.suptitle(f'🚀 لوحة تحكم GitHub - {self.username}', fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig('github_dashboard.svg', format='svg', dpi=300, bbox_inches='tight')
        plt.savefig('github_dashboard.png', format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info("✅ Activity dashboard created successfully")

    def create_readme_content(self, stats: Dict) -> str:
        """Generate professional README content"""
        user_data = stats['user_data']
        
        # Calculate top languages
        top_languages = stats['language_counts'].most_common(5)
        total_lang_repos = sum(stats['language_counts'].values())
        
        readme_content = f"""
# 👋 مرحباً، أنا {user_data.get('name', self.username)}!

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=36BCF7&center=true&vCenter=true&width=435&lines=مرحباً+بك+في+ملفي+الشخصي;مطور+شغوف+بالتكنولوجيا;أحب+البرمجة+والتطوير" alt="Typing SVG" />
</div>

## 📊 إحصائياتي على GitHub

<div align="center">
  <img src="./github_dashboard.svg" alt="GitHub Dashboard" width="100%"/>
</div>

### 🚀 نظرة سريعة

- 🔭 أعمل حالياً على مشاريع متنوعة
- 🌱 أتعلم تقنيات جديدة باستمرار
- 👯 أبحث عن التعاون في مشاريع مفتوحة المصدر
- 💬 اسألني عن **{', '.join([lang for lang, _ in top_languages[:3]])}**
- ⚡ حقيقة ممتعة: أحب حل المشاكل البرمجية المعقدة!

### 💻 توزيع لغات البرمجة

<div align="center">
  <img src="./language_distribution.svg" alt="Language Distribution" width="100%"/>
</div>

### 📈 الإحصائيات التفصيلية

```text
📂 إجمالي المستودعات:     {stats['total_repos']}
🌟 إجمالي النجوم:          {stats['total_stars']}
🍴 إجمالي التفرعات:        {stats['total_forks']}
👥 المتابعون:              {stats['followers']}
💾 حجم الكود الإجمالي:      {stats['total_size_kb'] / 1024:.1f} MB
📅 عمر الحساب:            {stats['account_age']} يوم
```

### 🔥 أكثر اللغات استخداماً

"""

        # Add language bars
        for lang, count in top_languages:
            percentage = (count / total_lang_repos) * 100 if total_lang_repos > 0 else 0
            bar_length = int((percentage / 100) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            readme_content += f"{lang:<12} {bar} {percentage:.1f}% ({count} مستودع)\n"

        readme_content += f"""

### 🛠️ التقنيات والأدوات

<div align="center">
  
![GitHub Stats](https://github-readme-stats.vercel.app/api?username={self.username}&show_icons=true&theme=radical&count_private=true&hide_border=true&bg_color=0D1117&title_color=F85D7F&icon_color=F8D866&text_color=A7A7A7)

![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={self.username}&layout=compact&theme=radical&hide_border=true&bg_color=0D1117&title_color=F85D7F&text_color=A7A7A7)

</div>

### 🏆 GitHub Trophies

<div align="center">
  <img src="https://github-profile-trophy.vercel.app/?username={self.username}&theme=radical&no-frame=true&no-bg=true&column=7" alt="GitHub Trophies"/>
</div>

### 📊 أسبوع النشاط

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username={self.username}&bg_color=0D1117&color=79ff97&line=00E676&point=FFFFFF&hide_border=true" alt="Activity Graph"/>
</div>

### 🤝 دعني أتواصل معك

<div align="center">
  
[![GitHub followers](https://img.shields.io/github/followers/{self.username}?label=المتابعون&style=social)](https://github.com/{self.username})
[![GitHub User's stars](https://img.shields.io/github/stars/{self.username}?affiliations=OWNER%2CCOLLABORATOR&style=social)](https://github.com/{self.username})

</div>

---

<div align="center">
  <img src="https://komarev.com/ghpvc/?username={self.username}&label=زوار+الملف&color=0e75b6&style=flat" alt="Profile Views" />
</div>

<div align="center">
  <i>آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</i>
</div>
"""
        
        return readme_content

    def save_stats_json(self, stats: Dict) -> None:
        """Save statistics to JSON file for future use"""
        stats_for_json = {
            'username': self.username,
            'generated_at': datetime.now().isoformat(),
            'total_repos': stats['total_repos'],
            'total_stars': stats['total_stars'],
            'total_forks': stats['total_forks'],
            'followers': stats['followers'],
            'following': stats['following'],
            'language_counts': dict(stats['language_counts']),
            'account_age_days': stats['account_age']
        }
        
        with open('github_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats_for_json, f, ensure_ascii=False, indent=2)
        
        logging.info("✅ Statistics saved to github_stats.json")

    def generate_profile(self) -> None:
        """Main method to generate complete GitHub profile"""
        try:
            logging.info("🚀 Starting GitHub profile generation...")
            
            # Fetch data
            user_data = self.fetch_user_data()
            if not user_data:
                logging.error("❌ Failed to fetch user data")
                return
            
            repos = self.fetch_repositories()
            if not repos:
                logging.error("❌ No repositories found")
                return
            
            # Calculate statistics
            stats = self.calculate_stats(repos, user_data)
            
            # Generate language statistics
            language_bytes = self.fetch_language_stats(repos)
            
            # Create visualizations
            self.create_language_chart(language_bytes)
            self.create_activity_dashboard(stats)
            
            # Generate README content
            readme_content = self.create_readme_content(stats)
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Save statistics
            self.save_stats_json(stats)
            
            logging.info("🎉 GitHub profile generation completed successfully!")
            print(f"\n✅ ملفات تم إنشاؤها:")
            print(f"   📄 README.md")
            print(f"   📊 github_dashboard.svg/png")
            print(f"   📈 language_distribution.svg/png")
            print(f"   📋 github_stats.json")
            print(f"   📋 github_stats.log")
            
        except Exception as e:
            logging.error(f"❌ Error during profile generation: {e}")
            raise

def main():
    """Main function to run the profile generator"""
    
    # Configuration
    USERNAME = "Ammar-nasr13"  # اسم المستخدم
    TOKEN = os.environ.get("GITHUB_TOKEN")  # متغير بيئي للتوكن
    
    if not TOKEN:
        print("⚠️ تحذير: لم يتم العثور على GITHUB_TOKEN في متغيرات البيئة")
        print("   سيتم استخدام API بدون مصادقة (حد أقل من الطلبات)")
    
    # Create generator instance
    generator = GitHubProfileGenerator(USERNAME, TOKEN)
    
    # Generate profile
    generator.generate_profile()

if __name__ == "__main__":
    main()