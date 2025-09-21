"""
📋 ملف الإعدادات - GitHub Profile Generator
قم بتعديل المعلومات هنا
"""

# معلوماتك الشخصية (⚠️ مهم: غير هذه المعلومات)
GITHUB_USERNAME = "Ammar-nasr13"  # ضع اسم المستخدم الخاص بك هنا
GITHUB_TOKEN = None  # سيتم أخذه من متغير البيئة

# إعدادات الرسوم البيانية
CHART_SETTINGS = {
    "figure_size": (16, 8),
    "dpi": 150,
    "style": "seaborn-v0_8",
    "language_limit": 10,  # عدد اللغات المعروضة
}

# إعدادات التحديث
UPDATE_SETTINGS = {
    "include_forks": False,  # تضمين المستودعات المنسوخة
    "recent_activity_days": 30,  # النشاط الحديث (أيام)
    "max_repos_to_process": 100,  # حد أقصى للمستودعات
}

# رسائل مخصصة للملف الشخصي
PROFILE_MESSAGES = {
    "welcome_message": "مرحباً بك في ملفي الشخصي",
    "current_work": "أعمل حالياً على مشاريع متنوعة",
    "learning": "أتعلم تقنيات جديدة باستمرار",
    "collaboration": "أبحث عن التعاون في مشاريع مفتوحة المصدر",
    "fun_fact": "أحب حل المشاكل البرمجية المعقدة!"
}