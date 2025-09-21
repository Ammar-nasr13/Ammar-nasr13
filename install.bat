"""
@echo off
echo 🚀 GitHub Profile Generator - سكريبت الإعداد
echo ==============================================

REM التحقق من وجود Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python غير مثبت. يرجى تثبيته أولاً.
    pause
    exit /b 1
)

echo ✅ Python متوفر

REM التحقق من وجود pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip غير مثبت. يرجى تثبيته أولاً.
    pause
    exit /b 1
)

echo ✅ pip متوفر

REM سؤال حول virtual environment
set /p venv="هل تريد إنشاء virtual environment؟ (y/n): "
if /i "%venv%"=="y" (
    echo 📦 إنشاء virtual environment...
    python -m venv github_profile_env
    call github_profile_env\Scripts\activate.bat
    echo ✅ تم تفعيل virtual environment
)

REM تثبيت المتطلبات
echo 📥 تثبيت المتطلبات...
pip install -r requirements.txt

REM التحقق من متغير البيئة
if "%GITHUB_TOKEN%"=="" (
    echo ⚠️ تحذير: متغير GITHUB_TOKEN غير محدد
    set /p token="أدخل GitHub Token الخاص بك: "
    setx GITHUB_TOKEN "%token%"
    set GITHUB_TOKEN=%token%
    echo ✅ تم حفظ GitHub Token
) else (
    echo ✅ GitHub Token محدد
)

REM طلب اسم المستخدم
set /p username="أدخل اسم مستخدم GitHub الخاص بك: "

REM إنشاء ملف config
(
echo # إعدادات GitHub Profile Generator
echo GITHUB_USERNAME = "%username%"
echo GITHUB_TOKEN = "%GITHUB_TOKEN%"
) > config.py

echo ✅ تم إنشاء ملف الإعدادات

echo 🎉 انتهى الإعداد بنجاح!
echo لتشغيل المولد، استخدم: python github_profile_generator.py
pause
"""
