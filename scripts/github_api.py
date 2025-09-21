#!/usr/bin/env python3
"""
سكريبت لجلب بيانات اللغات من مستودعات GitHub
"""

from github import Github
import os
import collections

def get_languages_data(username, token=None):
    """
    جلب بيانات اللغات من جميع المستودعات العامة للمستخدم
    """
    if token:
        g = Github(token)
    else:
        g = Github()
    
    try:
        user = g.get_user(username)
        repos = user.get_repos()
        
        # جمع إحصائيات اللغات من جميع المستودعات
        language_bytes = collections.Counter()
        
        for repo in repos:
            if not repo.fork:  # تجاهل المستودعات المقولة
                try:
                    repo_languages = repo.get_languages()
                    for lang, bytes_count in repo_languages.items():
                        language_bytes[lang] += bytes_count
                except Exception as e:
                    print(f"خطأ في جلب لغات المستودع {repo.name}: {e}")
                    continue
        
        # تحويل البايتات إلى نسب مئوية
        total_bytes = sum(language_bytes.values())
        languages_percent = {lang: (bytes_count / total_bytes) * 100 
                            for lang, bytes_count in language_bytes.items()}
        
        # ترتيب اللغات حسب النسبة المئوية (من الأعلى إلى الأقل)
        sorted_languages = dict(sorted(languages_percent.items(), 
                                      key=lambda item: item[1], 
                                      reverse=True))
        
        return sorted_languages
        
    except Exception as e:
        print(f"خطأ في جلب البيانات: {e}")
        return {}