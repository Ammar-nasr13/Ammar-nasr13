"""
#!/usr/bin/env python3

import os
import subprocess
import sys

def quick_setup():
    print("🚀 GitHub Profile Generator - بداية سريعة")
    print("=" * 50)
    
    # التحقق من Python
    try:
        import sys
        print(f"✅ Python {sys.version.split()[0]} متوفر")
    except:
        print("❌ خطأ في Python")
        return
    
    # طلب معلومات المستخدم
    username = input("🔹 أدخل اسم مستخدم GitHub: ").strip()
    if not username:
        print("❌ اسم المستخدم مطلوب")
        return
    
    token = input("🔹 أدخل GitHub Token (اختياري): ").strip()
    
    # تحديث الكود
    try:
        with open('github_profile_generator.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # استبدال اسم المستخدم
        content = content.replace(
            'USERNAME = "Ammar-nasr13"',
            f'USERNAME = "{username}"'
        )
        
        with open('github_profile_generator.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ تم تحديث اسم المستخدم إلى: {username}")
        
    except FileNotFoundError:
        print("❌ ملف github_profile_generator.py غير موجود")
        return
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return
    
    # تعيين متغير البيئة
    if token:
        os.environ['GITHUB_TOKEN'] = token
        print("✅ تم تعيين GitHub Token")
    else:
        print("⚠️ لم يتم تعيين GitHub Token - سيتم استخدام API محدود")
    
    # تثبيت المتطلبات
    print("📥 تثبيت المتطلبات...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            'requests', 'matplotlib', 'seaborn', 'numpy', 'python-dateutil'
        ])
        print("✅ تم تثبيت جميع المتطلبات")
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المتطلبات")
        return
    
    # تشغيل المولد
    try:
        print("🔄 تشغيل مولد الملف الشخصي...")
        subprocess.check_call([sys.executable, 'github_profile_generator.py'])
        print("🎉 تم إنشاء الملف الشخصي بنجاح!")
        
        # عرض الملفات المُنشأة
        files = ['README.md', 'github_stats.json', '*.svg', '*.png']
        print("\n📁 الملفات المُنشأة:")
        for pattern in files:
            import glob
            matches = glob.glob(pattern)
            for match in matches:
                print(f"   ✅ {match}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ فشل في تشغيل المولد: {e}")
        return
    except FileNotFoundError:
        print("❌ ملف github_profile_generator.py غير موجود")
        return

if __name__ == "__main__":
    quick_setup()
"""