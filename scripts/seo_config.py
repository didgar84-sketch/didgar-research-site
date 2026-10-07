"""Editorial metadata and topic relationships. Edit here, then regenerate HTML.

UPDATED is a content revision date, not a build date. Change it only when
the published content or its SEO annotations have actually been revised.
"""

UPDATED = '2026-10-04'
LANGUAGES = ('fa', 'en', 'ar')
SHORT_BRAND = {'fa': 'دکتر دیدگر', 'en': 'Dr. Didgar', 'ar': 'الدكتور ديدگر'}
LOCALES = {'fa': 'fa_IR', 'en': 'en_US', 'ar': 'ar_AR'}
FONT_FAMILIES = {'fa': 'Vazirmatn', 'en': 'Inter', 'ar': 'Cairo'}
FONT_ASSETS = {
    'fa': '/assets/fonts/Vazirmatn-Variable.woff2',
    'ar': '/assets/fonts/Cairo-Variable.woff2',
}

# Each entry is a complete, page-specific title and an independently written
# description. Character counts are editorial guidance, not ranking rules.
META = {
    'fa': {
        '': ('مشاوره پایان‌نامه و مقاله، تحلیل آماری و پروپوزال', 'مشاوره پایان‌نامه و رساله، تدوین پروپوزال، تحلیل آماری، برنامه‌نویسی و ویرایش مقاله؛ با خروجی مستند و پشتیبانی پژوهشی در فارسی، انگلیسی و عربی.'),
        'guides': ('دانشنامه پژوهش؛ راهنمای پایان‌نامه، مقاله و تحلیل داده', '۱۲ راهنمای پژوهشی درباره پروپوزال، پایان‌نامه، تحلیل داده، ارجاع‌دهی، گزارش مشابهت و انتشار مقاله؛ همراه با چک‌لیست‌ها و منابع معتبر.'),
        'planner': ('برنامه‌ریز زمان پژوهش و پایان‌نامه', 'زمان پژوهش را میان طراحی، مرور منابع، گردآوری داده، تحلیل و بازبینی تقسیم کنید؛ برنامه‌ای اولیه برای بررسی با استاد راهنما بسازید.'),
        'privacy': ('حریم خصوصی و اطلاعات درخواست مشاوره', 'نحوه استفاده از اطلاعات فرم مشاوره، آماده‌سازی پیام واتساپ، سرویس‌های بیرونی، حفاظت از داده حساس و راه تماس برای پرسش‌های حریم خصوصی.'),
        'terms': ('شرایط همکاری و مسئولیت علمی پژوهش', 'دامنه خدمات پژوهشی، توافق بر خروجی و زمان، شرایط اصلاحات و پشتیبانی، محرمانگی و مسئولیت علمی پژوهشگر را پیش از شروع همکاری بخوانید.'),
        'services/proposal': ('مشاوره و تدوین پروپوزال پژوهشی', 'از تعریف مسئله و شکاف پژوهش تا اهداف، روش‌شناسی و زمان‌بندی پروپوزال؛ مشاوره با دامنه مشخص و چک‌لیست مدارک و خروجی‌های قابل تحویل.'),
        'services/data-analysis': ('تحلیل آماری و مدل‌سازی با SPSS، R و Python', 'تحلیل داده و مدل‌سازی با SPSS، R، Python، Stata و MATLAB؛ همراه با کد، بررسی فرض‌ها و تفسیر علمی متناسب با طراحی پژوهش.'),
        'services/programming': ('برنامه‌نویسی علمی و شبیه‌سازی پژوهشی', 'پیاده‌سازی الگوریتم و شبیه‌سازی با Python، R و MATLAB؛ همراه با کد، محیط اجرای مستند، اعتبارسنجی و راهنمای بازتولید نتایج.'),
        'services/scientific-writing': ('مشاوره نگارش علمی پایان‌نامه و مقاله', 'پشتیبانی نگارش علمی، ساختاردهی پایان‌نامه و مقاله، مرور ادبیات و گزارش نتایج؛ با حفظ نقش نویسنده و رعایت سیاست دانشگاه و نشریه.'),
        'services/editing': ('ویرایش مقاله و قالب‌بندی پایان‌نامه', 'ویرایش زبانی و ساختاری، تنظیم منابع در APA، IEEE و Harvard و قالب‌بندی پایان‌نامه یا مقاله مطابق شیوه‌نامه دانشگاه و نشریه.'),
        'services/originality': ('بررسی مشابهت و کیفیت پژوهش', 'بررسی گزارش مشابهت متن و صحت ارجاع‌ها، شناسایی بخش‌های نیازمند اصلاح و تهیه گزارش قابل بررسی؛ ابزار و دامنه خدمت در توافق تعیین می‌شوند.'),
        'guides/research-proposal': ('راهنمای نوشتن پروپوزال؛ ساختار و روش پژوهش', 'ساختار پروپوزال، بیان مسئله، شکاف پژوهش، اهداف و فرضیه‌ها، روش‌شناسی، طرح تحلیل و زمان‌بندی را با یک چک‌لیست عملی مرور کنید.'),
        'guides/thesis-dissertation': ('ساختار پایان‌نامه و رساله؛ نگارش و آمادگی دفاع', 'راهنمای فصل‌های پایان‌نامه و رساله، پیوند پرسش با روش و نتایج، مدیریت اصلاحات و آمادگی دفاع با رعایت شیوه‌نامه دانشگاه.'),
        'guides/statistical-software': ('مقایسه نرم‌افزارهای آماری؛ SPSS، R و Python', 'کاربرد و تفاوت SPSS، R، Python، Stata، MATLAB و NVivo؛ همراه با نمونه کد آموزشی و نکات انتخاب ابزار و گزارش تحلیل پژوهشی.'),
        'guides/research-programming': ('برنامه‌نویسی پژوهشی؛ کد و شبیه‌سازی بازتولیدپذیر', 'انتخاب زبان برنامه‌نویسی، ساختار پروژه علمی، ثبت وابستگی‌ها، کنترل نسخه و اعتبارسنجی شبیه‌سازی را برای بازتولید نتایج بشناسید.'),
        'guides/citation-styles': ('راهنمای ارجاع‌دهی APA، IEEE و Harvard', 'قالب‌های آموزشی APA، IEEE و Harvard، تطبیق استنادهای متن با فهرست منابع و کنترل DOI؛ سبک نهایی را با شیوه‌نامه مؤسسه هماهنگ کنید.'),
        'guides/similarity-check': ('تفسیر مشابهت متن در Turnitin و iThenticate', 'گزارش مشابهت را در بافت نقل‌قول، ارجاع و تنظیمات ابزار تفسیر کنید؛ با محدودیت‌های Turnitin و iThenticate و اصلاح علمی متن آشنا شوید.'),
        'guides/similarity-report': ('گزارش مشابهت؛ اجزا و چک‌لیست اصلاح متن', 'اجزای گزارش مشابهت، ثبت نسخه و تنظیمات ابزار و الگوی جدول اقدامات اصلاحی؛ چرا یک درصد به‌تنهایی برای داوری درباره اصالت کافی نیست.'),
        'guides/research-articles': ('انواع مقاله علمی و انتخاب نشریه مناسب', 'تفاوت مقاله پژوهشی، مروری و سایر قالب‌ها، ساختار مقاله و چک‌لیست ارسال؛ جایگاه نمایه‌های نشریه را از نوع مقاله تفکیک کنید.'),
        'guides/systematic-review': ('مرور نظام‌مند و PRISMA؛ از پروتکل تا گزارش', 'سؤال و پروتکل مرور نظام‌مند، جست‌وجوی بازتولیدپذیر، غربال‌گری، استخراج شواهد و گزارش بر اساس PRISMA را مرحله‌به‌مرحله مرور کنید.'),
        'guides/research-data': ('مدیریت داده پژوهشی و بازتولید نتایج', 'فرهنگ داده، پاک‌سازی، ثبت تغییرات، حفظ حریم خصوصی و مستندسازی کد و محیط تحلیل؛ راهنمای مدیریت داده برای پژوهشی قابل بررسی.'),
        'guides/journal-submission': ('ارسال مقاله و پاسخ به داوران؛ چک‌لیست عملی', 'انتخاب نشریه، آماده‌سازی فایل‌ها و بیانیه‌ها، پاسخ بندبه‌بند به داوران و بررسی نسخه نهایی مقاله را با چک‌لیستی عملی انجام دهید.'),
        'guides/ai-research-ethics': ('هوش مصنوعی در پژوهش؛ مسئولیت، منابع و افشا', 'کاربرد مسئولانه هوش مصنوعی در پژوهش، تأیید مستقل منابع و محاسبات، حفاظت از داده محرمانه و افشای استفاده مطابق سیاست مؤسسه و نشریه.'),
    },
    'en': {
        '': ('Thesis support, research proposals and data analysis', 'Research consultation for theses, dissertations and articles: proposal design, statistical analysis, scientific programming and manuscript editing.'),
        'guides': ('Research guides: theses, articles and data analysis', 'Explore 12 practical research guides covering proposals, theses, statistics, citations, similarity reports and journal submission, with checklists and sources.'),
        'planner': ('Research and thesis timeline planner', 'Allocate research time across design, literature, data collection, analysis and revision. Create a starting schedule to discuss with your supervisor.'),
        'privacy': ('Privacy and consultation information', 'Learn how consultation details prepare a WhatsApp message, how external services are used, and how to handle sensitive data or contact the institute.'),
        'terms': ('Research engagement terms and responsibilities', 'Review research support scope, written agreements, deliverables, timelines, revision terms, confidentiality and researcher responsibilities before engaging.'),
        'services/proposal': ('Research proposal consultation and development', 'Define your research problem, gap, objectives, methods and timeline. Review proposal consultation scope, required materials and expected deliverables.'),
        'services/data-analysis': ('Statistical analysis with SPSS, R and Python', 'Research data analysis and modeling with SPSS, R, Python, Stata and MATLAB, including documented code, assumptions and interpretation of results.'),
        'services/programming': ('Scientific programming and research simulation', 'Algorithm implementation and simulation with Python, R and MATLAB, supported by documented code, reproducible environments and model validation.'),
        'services/scientific-writing': ('Thesis and article writing consultation', 'Support for thesis structure, literature synthesis and scientific reporting, with clear deliverables and respect for authorship and institutional policies.'),
        'services/editing': ('Manuscript editing and thesis formatting', 'Language and structural editing, reference checking and APA, IEEE or Harvard formatting aligned with your institution or journal requirements.'),
        'services/originality': ('Similarity checking and research quality', 'Review textual matches, citations and passages needing revision. Receive a contextual similarity report under an agreed scope and tool-access arrangement.'),
        'guides/research-proposal': ('How to write a research proposal: structure and methods', 'Plan a research proposal with a clear problem, literature gap, objectives, methods, analysis and timeline. Use a practical review checklist.'),
        'guides/thesis-dissertation': ('Thesis and dissertation structure and defense preparation', 'Review thesis chapters, align questions with methods and findings, track revisions and prepare a defense under your institution’s requirements.'),
        'guides/statistical-software': ('Statistical software compared: SPSS, R and Python', 'Compare SPSS, R, Python, Stata, MATLAB and NVivo for research, with educational code examples and guidance on tool selection and analytical reporting.'),
        'guides/research-programming': ('Reproducible scientific code and simulation', 'Choose research programming tools, organize projects, record dependencies, use version control and validate simulations for reproducible results.'),
        'guides/citation-styles': ('APA, IEEE and Harvard citation guide', 'Review educational citation templates, reconcile in-text citations and reference lists, check DOI records and follow your institution’s style guidance.'),
        'guides/similarity-check': ('Interpreting Turnitin and iThenticate similarity', 'Understand textual matches, quotations, citations and report settings. Learn the limits of similarity scores and a responsible approach to revision.'),
        'guides/similarity-report': ('Similarity reports: components and revision checklist', 'Review report components, document versions and tool settings, and use a revision-action table. A similarity percentage alone cannot determine plagiarism.'),
        'guides/research-articles': ('Scientific article types and journal selection', 'Understand original research, review articles and other formats, plan a manuscript and prepare submission. Distinguish journal indexing from article type.'),
        'guides/systematic-review': ('Systematic reviews and PRISMA: a practical workflow', 'Plan a review protocol, reproducible search, screening, evidence extraction and PRISMA reporting. Keep reporting quality distinct from study validity.'),
        'guides/research-data': ('Research data management and reproducibility', 'Build a data dictionary, document cleaning and changes, protect confidential information and preserve code and analysis environments for review.'),
        'guides/journal-submission': ('Journal submission and reviewer-response checklist', 'Check journal fit, prepare submission files and declarations, respond to each reviewer comment and inspect the final article proof.'),
        'guides/ai-research-ethics': ('AI in research: verification, responsibility and disclosure', 'Use AI responsibly in research: verify sources and calculations, protect confidential information and disclose use under institution and journal policies.'),
    },
    'ar': {
        '': ('استشارات الأطروحات والمقالات والتحليل الإحصائي', 'استشارات الرسائل والأطروحات والمقالات، إعداد مقترح البحث، التحليل الإحصائي والبرمجة العلمية والتحرير؛ بدعم موثق بالعربية والفارسية والإنجليزية.'),
        'guides': ('أدلة البحث؛ الأطروحات والمقالات وتحليل البيانات', '١٢ دليلاً عملياً للمقترحات والأطروحات والإحصاء والمراجع وتقارير التشابه والنشر العلمي؛ مع قوائم مراجعة ومصادر موثوقة.'),
        'planner': ('مخطط وقت البحث والأطروحة', 'وزّع وقت البحث بين التصميم والأدبيات وجمع البيانات والتحليل والمراجعة؛ وأنشئ جدولاً أولياً لمناقشته مع المشرف.'),
        'privacy': ('الخصوصية ومعلومات طلب الاستشارة', 'كيفية استخدام معلومات الاستشارة لإعداد رسالة واتساب، والخدمات الخارجية وحماية البيانات الحساسة وطرق التواصل بشأن الخصوصية.'),
        'terms': ('شروط التعاون والمسؤولية العلمية', 'راجع نطاق الدعم البحثي والاتفاق المكتوب والمخرجات والوقت وشروط المراجعات والسرية ومسؤولية الباحث قبل بدء التعاون.'),
        'services/proposal': ('استشارات إعداد مقترح البحث', 'من تحديد المشكلة والفجوة والأهداف إلى المنهجية والجدول الزمني؛ تعرّف على نطاق استشارة المقترح والوثائق المطلوبة والمخرجات المتوقعة.'),
        'services/data-analysis': ('التحليل الإحصائي باستخدام SPSS وR وPython', 'تحليل البيانات والنمذجة باستخدام SPSS وR وPython وStata وMATLAB؛ مع شفرات موثقة وفحص الافتراضات والتفسير الملائم لتصميم الدراسة.'),
        'services/programming': ('البرمجة العلمية والمحاكاة البحثية', 'تنفيذ الخوارزميات والمحاكاة باستخدام Python وR وMATLAB؛ مع الشفرة وبيئة تشغيل موثقة والتحقق من النموذج وإعادة إنتاج النتائج.'),
        'services/scientific-writing': ('استشارات الكتابة العلمية للأطروحات والمقالات', 'دعم هيكلة الأطروحة والمقال ومراجعة الأدبيات وكتابة النتائج؛ مع تحديد المخرجات والحفاظ على مسؤولية المؤلف وسياسات الجامعة والمجلة.'),
        'services/editing': ('تحرير المقالات وتنسيق الأطروحات', 'تحرير لغوي وهيكلي ومراجعة المراجع وتنسيق APA وIEEE وHarvard وفق تعليمات الجامعة أو المجلة ومتطلبات التسليم.'),
        'services/originality': ('فحص التشابه وجودة البحث', 'مراجعة تطابق النصوص والمراجع وتحديد مواضع التصحيح وإعداد تقرير تشابه قابل للمراجعة؛ تُحدد الأداة ونطاق الخدمة في الاتفاق.'),
        'guides/research-proposal': ('كتابة مقترح البحث؛ الهيكل والمنهجية', 'راجع مشكلة البحث والفجوة والأهداف والفرضيات والمنهجية وخطة التحليل والجدول الزمني؛ مع قائمة عملية لتقييم اتساق المقترح.'),
        'guides/thesis-dissertation': ('هيكل الأطروحة وكتابتها والاستعداد للمناقشة', 'دليل لفصول الأطروحة وربط الأسئلة بالمنهج والنتائج وإدارة التعديلات والاستعداد للمناقشة وفق تعليمات الجامعة.'),
        'guides/statistical-software': ('مقارنة البرامج الإحصائية؛ SPSS وR وPython', 'استخدامات SPSS وR وPython وStata وMATLAB وNVivo؛ مع أمثلة شفرة تعليمية وإرشادات اختيار الأداة وتوثيق التحليل البحثي.'),
        'guides/research-programming': ('البرمجة البحثية والمحاكاة القابلة لإعادة الإنتاج', 'اختيار لغة البرمجة وهيكل المشروع العلمي وتوثيق الاعتماديات والتحكم بالإصدارات والتحقق من المحاكاة لإعادة إنتاج النتائج.'),
        'guides/citation-styles': ('دليل الاستشهاد وفق APA وIEEE وHarvard', 'قوالب تعليمية للمراجع ومطابقة الاستشهادات مع قائمة المصادر والتحقق من DOI؛ اتبع النسخة المعتمدة لدى الجامعة أو المجلة.'),
        'guides/similarity-check': ('تفسير التشابه في Turnitin وiThenticate', 'افهم تطابق النصوص والاقتباسات والمراجع وإعدادات التقارير؛ وتعرّف على حدود نسبة التشابه والتصحيح العلمي المسؤول.'),
        'guides/similarity-report': ('تقرير التشابه؛ المكونات وقائمة التصحيح', 'مكونات التقرير وتوثيق نسخة النص وإعدادات الأداة ونموذج جدول إجراءات التصحيح؛ لماذا لا تكفي نسبة التشابه وحدها للحكم على الانتحال.'),
        'guides/research-articles': ('أنواع المقالات العلمية واختيار المجلة', 'تعرّف على المقال الأصلي والمراجعة والقوالب الأخرى وهيكل المخطوطة ومتطلبات الإرسال؛ وميّز فهرسة المجلة عن نوع المقال.'),
        'guides/systematic-review': ('المراجعة المنهجية وPRISMA؛ من البروتوكول للتقرير', 'سؤال المراجعة والبروتوكول والبحث القابل لإعادة الإنتاج والفرز واستخراج الأدلة والتقرير وفق PRISMA؛ بخطوات عملية موثقة.'),
        'guides/research-data': ('إدارة بيانات البحث وإعادة إنتاج النتائج', 'قاموس البيانات والتنظيف وتوثيق التغييرات وحماية الخصوصية وحفظ الشفرة وبيئة التحليل؛ دليل لإدارة بيانات قابلة للمراجعة.'),
        'guides/journal-submission': ('إرسال المقال والرد على المراجعين؛ قائمة عملية', 'اختيار المجلة وتجهيز الملفات والتصريحات والرد على كل ملاحظة للمراجعين وفحص النسخة النهائية للمقال قبل النشر.'),
        'guides/ai-research-ethics': ('الذكاء الاصطناعي في البحث؛ التحقق والمسؤولية والإفصاح', 'استخدام مسؤول للذكاء الاصطناعي: تحقق مستقل من المصادر والحسابات، وحماية البيانات السرية والإفصاح وفق سياسات الجامعة والمجلة.'),
    },
}

RELATED = {
    'research-proposal': ['thesis-dissertation', 'systematic-review', 'citation-styles', 'research-data'],
    'thesis-dissertation': ['research-proposal', 'citation-styles', 'statistical-software', 'journal-submission'],
    'statistical-software': ['research-data', 'research-programming', 'research-proposal', 'systematic-review'],
    'research-programming': ['research-data', 'statistical-software', 'ai-research-ethics', 'research-proposal'],
    'citation-styles': ['similarity-check', 'similarity-report', 'research-articles', 'journal-submission'],
    'similarity-check': ['similarity-report', 'citation-styles', 'ai-research-ethics', 'research-articles'],
    'similarity-report': ['similarity-check', 'citation-styles', 'research-articles', 'journal-submission'],
    'research-articles': ['journal-submission', 'systematic-review', 'citation-styles', 'ai-research-ethics'],
    'systematic-review': ['research-proposal', 'research-data', 'statistical-software', 'research-articles'],
    'research-data': ['statistical-software', 'research-programming', 'research-proposal', 'ai-research-ethics'],
    'journal-submission': ['research-articles', 'citation-styles', 'similarity-check', 'ai-research-ethics'],
    'ai-research-ethics': ['citation-styles', 'research-data', 'similarity-check', 'research-programming'],
}
SERVICE_GUIDES = {
    'proposal': ['research-proposal', 'systematic-review', 'thesis-dissertation'],
    'data-analysis': ['statistical-software', 'research-data', 'research-proposal'],
    'programming': ['research-programming', 'research-data', 'statistical-software'],
    'scientific-writing': ['thesis-dissertation', 'research-articles', 'journal-submission'],
    'editing': ['citation-styles', 'journal-submission', 'thesis-dissertation'],
    'originality': ['similarity-check', 'similarity-report', 'citation-styles'],
}
GUIDE_SERVICE = {
    'research-proposal': 'proposal', 'thesis-dissertation': 'scientific-writing',
    'statistical-software': 'data-analysis', 'research-programming': 'programming',
    'citation-styles': 'editing', 'similarity-check': 'originality',
    'similarity-report': 'originality', 'research-articles': 'scientific-writing',
    'systematic-review': 'proposal', 'research-data': 'data-analysis',
    'journal-submission': 'editing', 'ai-research-ethics': 'scientific-writing',
}

IMAGE_ALT = {
    'fa': {'library-hero': 'تصویر مفهومی کتابخانه و میز مطالعه پژوهشی', 'research-team': 'تصویر مفهومی همکاری گروهی در بررسی داده‌های پژوهشی', 'research-desk': 'تصویر مفهومی میز پژوهش، یادداشت‌ها و ابزار تحلیل'},
    'en': {'library-hero': 'Illustration of a research library and study desk', 'research-team': 'Illustration of researchers collaborating on data review', 'research-desk': 'Illustration of a research desk, notes and analysis tools'},
    'ar': {'library-hero': 'صورة توضيحية لمكتبة بحثية ومكتب دراسة', 'research-team': 'صورة توضيحية لتعاون الباحثين في مراجعة البيانات', 'research-desk': 'صورة توضيحية لمكتب بحث وملاحظات وأدوات تحليل'},
}
