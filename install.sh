#!/bin/bash

echo "🚀 GitHub Profile Generator - سكريبت الإعداد"
echo "=============================================="

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت. يرجى تثبيته أولاً."
    exit 1
fi

echo "✅ Python 3 متوفر"

# التحقق من وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت. يرجى تثبيته أولاً."
    exit 1
fi

echo "✅ pip3 متوفر"

# إنشاء virtual environment (اختياري)
read -p "هل تريد إنشاء virtual environment؟ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 إنشاء virtual environment..."
    python3 -m venv github_profile_env
    source github_profile_env/bin/activate
    echo "✅ تم تفعيل virtual environment"
fi

# تثبيت المتطلبات
echo "📥 تثبيت المتطلبات..."
pip3 install -r requirements.txt

# التحقق من متغير البيئة
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️ تحذير: متغير GITHUB_TOKEN غير محدد"
    read -p "هل تريد إدخال GitHub Token الآن؟ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -sp "أدخل GitHub Token الخاص بك: " token
        echo
        export GITHUB_TOKEN="$token"
        echo "export GITHUB_TOKEN=\"$token\"" >> ~/.bashrc
        echo "✅ تم حفظ GitHub Token"
    fi
else
    echo "✅ GitHub Token محدد"
fi

# طلب اسم المستخدم
read -p "أدخل اسم مستخدم GitHub الخاص بك: " username

# إنشاء ملف config
cat > config.py << EOF
# إعدادات GitHub Profile Generator
GITHUB_USERNAME = "$username"
GITHUB_TOKEN = "$GITHUB_TOKEN"
EOF

echo "✅ تم إنشاء ملف الإعدادات"

# تشغيل تجريبي
echo "🧪 تشغيل تجريبي..."
python3 -c "
import sys
import os
sys.path.append(os.getcwd())

# تحديث اسم المستخدم في الكود
with open('github_profile_generator.py', 'r') as f:
    content = f.read()

content = content.replace('USERNAME = \"Ammar-nasr13\"', f'USERNAME = \"$username\"')

with open('github_profile_generator.py', 'w') as f:
    f.write(content)

print('✅ تم تحديث اسم المستخدم في الكود')
"

echo "🎉 انتهى الإعداد بنجاح!"
echo "لتشغيل المولد، استخدم: python3 github_profile_generator.py"
