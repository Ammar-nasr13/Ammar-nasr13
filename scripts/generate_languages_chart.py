#!/usr/bin/env python3
"""
سكريبت لإنشاء مخطط النسب المئوية للغات البرمجة بدون Token
"""

import matplotlib.pyplot as plt
import requests
import os
import collections
import time

# إعداد الألوان الاحترافية
PRO_COLORS = [
    '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B',
    '#6A0572', '#5C80BC', '#4FB477', '#E4572E', '#29335C',
    '#F3A712', '#A41623', '#0B132B', '#5D7599', '#AB83A1'
]

def get_languages_data_no_token(username):
    """
    جلب بيانات اللغات بدون استخدام Token (باستخدام GitHub REST API)
    """
    languages_data = collections.Counter()
    page = 1
    per_page = 100
    
    try:
        while True:
            # جلب صفحة من المستودعات
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"❌ خطأ في جلب البيانات: {response.status_code}")
                break
                
            repos = response.json()
            if not repos:
                break
                
            # معالجة كل مستودع
            for repo in repos:
                if not repo.get('fork', False):  # تجاهل المستودعات المقولة
                    if repo.get('languages_url'):
                        lang_response = requests.get(repo['languages_url'])
                        if lang_response.status_code == 200:
                            repo_langs = lang_response.json()
                            for lang, bytes_count in repo_langs.items():
                                languages_data[lang] += bytes_count
                        # انتظر قليلاً بين الطلبات لتجنب الحدود
                        time.sleep(0.1)
            
            page += 1
            if len(repos) < per_page:
                break
                
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return {}
    
    # تحويل إلى نسب مئوية
    total_bytes = sum(languages_data.values())
    if total_bytes == 0:
        return {}
        
    languages_percent = {lang: (bytes_count / total_bytes) * 100 
                        for lang, bytes_count in languages_data.items()}
    
    return dict(sorted(languages_percent.items(), key=lambda x: x[1], reverse=True))

def create_languages_chart(username, output_path="charts/languages_chart.png"):
    """
    إنشاء مخطط النسب المئوية للغات البرمجة
    """
    # جلب بيانات اللغات بدون Token
    print("📥 جلب بيانات اللغات من GitHub...")
    languages_data = get_languages_data_no_token(username)
    
    if not languages_data:
        print("⚠️  استخدام بيانات تجريبية لأن جلب البيانات فشل")
        # بيانات تجريبية للعرض
        languages_data = {
            'Python': 45, 
            'JavaScript': 25, 
            'HTML': 15, 
            'CSS': 8, 
            'Java': 7
        }
    
    # تجميع اللغات الصغيرة في فئة "Other"
    main_languages = {}
    other_percent = 0
    
    for lang, percent in languages_data.items():
        if percent >= 2.0:  # اللغات التي تمثل أكثر من 2%
            main_languages[lang] = percent
        else:
            other_percent += percent
    
    if other_percent > 0:
        main_languages['Other'] = other_percent
    
    # إعداد البيانات للمخطط
    labels = list(main_languages.keys())
    sizes = list(main_languages.values())
    colors = PRO_COLORS[:len(labels)]
    
    # إنشاء الشكل مع خلفية داكنة
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0D1B2A')
    ax.set_facecolor('#0D1B2A')
    
    # إنشاء مخطط دائري
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, shadow=True, explode=[0.05] * len(labels),
                                      textprops={'color': 'white', 'fontsize': 11})
    
    # تحسين النصوص
    for text in texts:
        text.set_color('white')
        text.set_fontsize(12)
        text.set_fontweight('bold')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    
    # إضافة عنوان
    ax.set_title('نسب لغات البرمجة المستخدمة', color='white', 
                 fontsize=18, fontweight='bold', pad=20)
    
    # إضافة ثقب في المنتصف لجعله مخطط دائري مجوف
    centre_circle = plt.Circle((0,0), 0.70, fc='#0D1B2A')
    fig.gca().add_artist(centre_circle)
    
    # ضمان أن المخطط دائري مثالي
    ax.axis('equal')
    
    # إضافة وسيلة إيضاح
    ax.legend(wedges, [f'{l}: {s:.1f}%' for l, s in main_languages.items()],
              title="اللغات", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
              facecolor='#1B263B', edgecolor='#415A77', labelcolor='white')
    
    # حفظ المخطط
    plt.savefig(output_path, bbox_inches='tight', facecolor='#0D1B2A', dpi=150)
    plt.close()
    
    print("✅ تم إنشاء المخطط بنجاح!")
    print("📊 النسب المئوية للغات:")
    for lang, percent in main_languages.items():
        print(f"   {lang}: {percent:.2f}%")
    
    return True

if __name__ == "__main__":
    # الحصول على اسم المستخدم من المتغيرات البيئية أو استخدام افتراضي
    username = os.environ.get("GITHUB_USERNAME", "Ammar-nasr13")
    
    # إنشاء مجلد charts إذا لم يكن موجوداً
    os.makedirs("charts", exist_ok=True)
    
    # إنشاء المخطط
    success = create_languages_chart(username)
    
    if not success:
        exit(1)