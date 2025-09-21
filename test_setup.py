"""
#!/usr/bin/env python3

def test_setup():
    print("🧪 اختبار إعداد GitHub Profile Generator")
    print("=" * 45)
    
    # اختبار Python
    try:
        import sys
        print(f"✅ Python {sys.version.split()[0]}")
    except Exception as e:
        print(f"❌ Python: {e}")
        return False
    
    # اختبار المكتبات
    required_modules = [
        'requests', 'matplotlib', 'seaborn', 
        'numpy', 'json', 'os', 'logging'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} غير متوفر")
            print(f"   لتثبيته: pip install {module}")
    
    # اختبار متغير البيئة
    import os
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        print(f"✅ GITHUB_TOKEN محدد ({len(token)} حرف)")
    else:
        print("⚠️ GITHUB_TOKEN غير محدد (سيتم استخدام API محدود)")
    
    # اختبار وجود الملفات
    files_to_check = [
        'github_profile_generator.py',
        'requirements.txt'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} غير موجود")
    
    print("\n🎯 الإعداد جاهز للاستخدام!")
    return True

if __name__ == "__main__":
    test_setup()
"""