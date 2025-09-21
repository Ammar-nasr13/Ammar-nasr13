#!/usr/bin/env python3
"""
main.py
Entry point to generate GitHub profile assets (charts, README, json).
"""

import os
from utils.github_stats import GitHubProfileGenerator

def main():
    # يمكنك تغيير اسم المستخدم هنا أو استخدام المتغير البيئي GITHUB_USERNAME
    USERNAME = os.environ.get("GITHUB_USERNAME", "Ammar-nasr13")
    TOKEN = os.environ.get("GITHUB_TOKEN")  # من الأفضل ضبطه محليًا أو الاعتماد على GitHub Actions

    if not TOKEN:
        print("⚠️ لم يتم العثور على GITHUB_TOKEN في متغيرات البيئة. سيتم العمل بدون توكن (قد تواجه حدًا للـ API).")
        # نستمر لكن ننبه المستخدم

    generator = GitHubProfileGenerator(USERNAME, TOKEN)
    generator.generate_profile()

if __name__ == "__main__":
    main()
