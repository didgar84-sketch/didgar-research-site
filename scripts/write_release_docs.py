"""Write factual release documentation after the packaged checks are complete."""
from pathlib import Path
import json
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'content/site-content.json').read_text())
routes=json.loads((ROOT/'content/routes.json').read_text())
stats=json.loads((ROOT/'reference/qa/content-check.json').read_text())
offline=json.loads((ROOT/'reference/qa/standalone-check.json').read_text())
http=json.loads((ROOT/'reference/qa/http-check.json').read_text())
assert stats['passed'] and offline['passed'] and http['passed']
original=json.loads((ROOT/'reference/previous/package-before-2026-10-06/content/site-content.json').read_text())
def words(articles): return sum(len(html.fragment_fromstring(a['body'],create_parent='div').text_content().split()) for a in articles)

readme=r'''# بستهٔ اصلاح‌شدۀ سایت دکتر دیدگر — نسخه 3.0.0

ویرایش: ۶ اکتبر ۲۰۲۶. بسته شامل سایت چندصفحه‌ای آماده برای Vercel و یک فایل
HTML مستقل برای مرور آفلاین است. تغییرها بر فایل ضمیمه و پیشنهادهای ضمیمه اعمال
شده‌اند. سایت در حساب میزبانی شما منتشر نشده است.

## محتوای این نسخه

- ۱۸۳ صفحۀ canonical: ۶۱ صفحه برای هر زبان، شامل ۴۵ راهنمای پژوهش در هر زبان.
- فارسی، انگلیسی و عربی با URL، جهت، عنوان و پیوند تغییر زبان مستقل.
- ۱۷ راهنمای جدید و تمرین‌های اختصاصی برای ۲۸ راهنمای پیشین.
- ۸ مسیر یادگیری و ۴۰ مدخل واژه‌نامه در هر زبان؛ ۶۱ منبع در هر فهرست منابع.
- ۱۳۵ کاربرگ راهنما و ۱۸ الگوی پایه با مثال و پرسش تکمیل؛ فایل‌های Markdown.
- بستۀ کد و ۱۲ رکورد کاملاً ساختگی، شش مسیر OLS توصیفی و مثال مستقل TOST.
- فونت‌ها، عکس‌ها، کد، کاربرگ‌ها و ZIP آموزشی در HTML مستقل نیز جاسازی شده‌اند.

## مشاهده و انتشار

**راهنمای استقرار GitHub/Vercel:** [README.md](README.md) را بخوانید.
ZIP را ابتدا استخراج و فایل‌های پروژه را در مخزن ثبت کنید. در بستهٔ جدید
`didgar-github-vercel-ready.zip` فایل‌های پروژه در ریشه‌اند و Root Directory
ریشهٔ مخزن (`./`) است. اگر از بستهٔ قبلی با پوشهٔ `didgar-site` استفاده می‌کنید،
Root Directory همان `didgar-site` است. Build Command در هر دو حالت
`npm run build` و Output Directory برابر `dist` است.

فایل مستقل `didgar-preview.html` تحویل قبلی را با مرورگر باز کنید. جابه‌جایی میان
صفحات و ابزارهای تعاملی به JavaScript نیاز دارد؛ تصاویر و صفحۀ اول بدون شبکه
قابل نمایش‌اند. منابع خارجی و تماس با سرویس‌های بیرونی به اینترنت نیاز دارند.
این فایل `noindex` است و نسخۀ مناسب انتشار سئو، سایت چندصفحه‌ای پوشۀ `didgar-site` است.

از پوشه‌ای که `package.json` دارد (در بستهٔ قبلی، پوشهٔ `didgar-site`):

```sh
npm run build
npm run dev
```

پیش‌نمایش محلی به صورت پیش‌فرض در `http://127.0.0.1:3000` اجرا می‌شود.
برای Vercel ریشۀ پروژه همین پوشه، Build Command برابر `npm run build` و
Output Directory برابر `dist` است. ساخت تولیدی به Python یا پکیج npm اضافی
نیاز ندارد؛ HTMLهای تولیدشده در بسته موجودند. `api/consultation.mjs` نیز برای
درخواست مشاوره آماده است و فقط پیوند پیام واتساپ می‌سازد؛ پیام را ارسال یا ذخیره نمی‌کند.

مبدأ پیش‌فرض حفظ‌شده از بستهٔ ضمیمه `https://dr17.vercel.app` است. پیش از انتشار
روی دامنه دیگر، `SITE_URL` را به مبدأ HTTPS واقعی بدون مسیر تنظیم کنید:

```sh
SITE_URL=https://your-domain.example npm run build
```

Vercel می‌تواند از `VERCEL_PROJECT_PRODUCTION_URL` استفاده کند؛ `SITE_URL`
اولویت دارد. URL موقتی پیش‌نمایش به canonical تبدیل نمی‌شود. محیط preview با
`noindex` ساخته می‌شود. توکن واقعی Search Console، در صورت داشتن، از متغیر
`GOOGLE_SITE_VERIFICATION` خوانده می‌شود؛ توکن آزمایشی در فایل تحویلی نیست.

## ویرایش و نگهداری

محتوا در `content/site-content.json` و قالب تولید در `scripts/generate_content.py`
است. تاریخ ویرایش را تنها هنگام تغییر واقعی محتوا به‌روز کنید. راهنمای جدید باید
ترجمه، منابع، مثال، کاربرگ، پیوندهای مرتبط و مسیر یادگیری داشته باشد.

برای تولید مجدد، Python 3.10+ و نیازهای `requirements-maintenance.txt` لازم‌اند:

```sh
python3 -m pip install -r requirements-maintenance.txt
npm run generate
npm run build
npm run standalone
```

`generate` ابتدا بستۀ مثال‌ها را بازاجرا و آزمون می‌کند، سپس صفحات، کاربرگ‌ها،
نقشۀ سایت و aliasها را تولید می‌کند. `standalone` خروجی را در
`../deliverables/didgar-preview.html` می‌نویسد. اسکریپت `upgrade_content.py`
ثبت تغییر محتوایی این انتشار است؛ آن را پس از ویرایش دستی بدون بررسی دوباره اجرا نکنید.

## بررسی‌ها

```sh
npm test
npm run test:seo
python3 scripts/seo-check.py dist
npm run test:content
npm run test:examples
npm run test:interactions
npm run test:build
npm run test:http
npm run test:standalone
npm run test:release
```

نتایج و حدود بررسی در `reference/qa` و `SEO-AUDIT-FA.md` آمده‌اند. خطای تداخل
شناسه واژه‌نامه که در بررسی پیدا شد اصلاح شده است. آزمون واقعی مرورگر در محیط
تهیهٔ بسته به علت نبود Chromium اجرا نشد؛ تأیید تصویری موبایل/دسکتاپ، Lighthouse،
Core Web Vitals و Rich Results زنده ادعا نشده‌اند. برای اجرای اختیاری Playwright:

```sh
npm install --no-save --package-lock=false playwright
npx playwright install chromium
PORT=3017 npm run dev
```

در ترمینال دیگر، پس از `npm run standalone`، دستور `npm run test:browser` را اجرا
کنید. بررسی Quarto و خروجی Word/PDF نیز جداست؛ CLI آن در محیط تهیه موجود نبود.

## حدود علمی و عملی

رتبۀ اول همۀ جست‌وجوهای جهان قابل تضمین نیست. این سایت اکنون آموزش روش پژوهش
و مسیرهای اجرایی ارائه می‌کند؛ دانشنامۀ تمام رشته‌ها و جایگزین منابع اصلی نیست.
برای مرجعیت پایدار، بازبینی تخصصی نام‌دار، اصلاح مستمر، محتوای اختصاصی رشته‌ها
و شواهد واقعی استفاده لازم است. استفاده از AI در تهیه/ترجمه/کد/تصاویر اعلام شده
و ادعای داوری تخصصی مستقل نداریم.

نمونه‌ها ساختگی‌اند. راهنمای سلامت مجوز اجرای پژوهش یا درمان نیست؛ حقوق نشر به
شرایط واقعی مؤسسه، حامی و قرارداد بستگی دارد. فهرست منابع به معنی همکاری یا تأیید
سازمان‌های نام‌برده نیست. لینک عمومی ایتا از نسخۀ قبلی حفظ و به عنوان وب‌سایت رسمی
ایتا برچسب خورده است؛ حساب اختصاصی تأییدشده‌ای ساخته نشده است.

منابع و تفکیک پیشنهادها در `SOURCES.md` و `SEO-AUDIT-FA.md` ثبت‌اند. نسخۀ قبل،
گزارش‌های تاریخی و مولد منسوخ در `reference/previous/package-before-2026-10-06`
برای مقایسه نگه‌داری شده‌اند و در `dist` منتشر نمی‌شوند.
'''
(ROOT/'README-FA.md').write_text(readme,encoding='utf-8')

mapping=[
 ('registered-reports','Registered Reports','تفکیک مرحلۀ ۱، شروط IPA، انحراف و مرحلۀ ۲؛ کاربرگ و تمرین پروتکل/پاسخ'),
 ('secondary-data-preregistration','پیش‌ثبت داده ثانویه','دفتر دسترسی قبلی، تعریف نمونه/پیامد و زمان تصمیم'),
 ('qualitative-preregistration','پیش‌ثبت کیفی','رویکرد، بازاندیشی و تغییر انعطاف‌پذیرِ تاریخ‌دار'),
 ('top-2025-transparency','TOP 2025','تفکیک نسخۀ جدید، افشا/اشتراک/گواهی و شاهد واقعی'),
 ('multiverse-analysis','Multiverse / specification curve','جدول تصمیم و وابستگی، شش مسیر توصیفی؛ بدون ادعای آزمون رسمی منحنی'),
 ('computational-thesis-quarto','رسالۀ محاسباتی Quarto','کد و دادۀ اجرایی، inline result، QMD و محدودیت ساخت Word/PDF'),
 ('thesis-by-publication','رسالۀ مقاله‌محور','استدلال مرکزی، معماری، فصل اتصال، سهم و حقوق؛ بدون شمار مقاله جهانی'),
 ('open-peer-review','PCI / eLife','تمایز توصیه، Reviewed Preprint، انتخاب سردبیری و وضعیت انتشار'),
 ('data-papers','مقالۀ داده','فرهنگ، کنترل کیفیت، دسترسی، مثال بازاستفاده و طرح Data Descriptor'),
 ('research-software-papers','مقالۀ نرم‌افزار / JOSS','سابقۀ عمومی و مدارک بلوغ، آزمون و سیاست AI؛ مثال کوچک واجد شرایط معرفی نشده'),
 ('rights-retention','Rights Retention / Jisc','نسخه، حامی، قرارداد و حل تعارض؛ بدون اجازۀ حقوقی جهانی'),
 ('equivalence-testing','SESOI / TOST','حدود پیشینی، SE، CI90 و کد با جواب معلوم؛ p بزرگ اثبات نبود اثر نیست'),
 ('constraints-on-generality','COG','جمعیت، محیط، محرک و زمان با بیانیۀ تکمیل‌شده'),
 ('living-systematic-reviews','PRISMA-LSR 2024','پایش، محرک انتشار، نسخه و توقف؛ نه صرف افزودن مقاله'),
 ('chatbot-health-studies','CHART 2025','دامنۀ سلامت، نسخه/پرسش، تکرار، ارزیابی انسانی و خطا'),
 ('consort-spirit-2025','CONSORT / SPIRIT 2025','۳۰ مورد گزارش و ۳۴ مورد پروتکل، ماتریس شاهد و جریان سازگار'),
 ('reporting-standard-verification','اعتبارسنجی استاندارد / PRISMA-trAIce','نامۀ ۱۸ اوت ۲۰۲۶ و فهرست رسمی؛ پیشنهاد به عنوان افزونۀ تأییدشده معرفی نشده'),
]
comparison='| زبان | شمار راهنما قبل | شمار اکنون | کلمات تقریبی متن راهنما قبل | اکنون |\n| --- | ---: | ---: | ---: | ---: |\n'
for lang,label in [('fa','فارسی'),('en','انگلیسی'),('ar','عربی')]:
    comparison+=f'| {label} | {len(original["articles"][lang])} | {len(D["articles"][lang])} | {words(original["articles"][lang]):,} | {words(D["articles"][lang]):,} |\n'
table='| پیشنهاد | تغییر انجام‌شده | راهنمای فارسی |\n| --- | --- | --- |\n'+''.join(f'| {title} | {action} | [مطالعه](fa/guides/{slug}/index.html) |\n' for slug,title,action in mapping)
audit='''# گزارش بازبینی و اصلاح — ۶ اکتبر ۲۰۲۶

## نتیجۀ قابل اتکا

سایت از ۱۲۶ به ۱۸۳ صفحۀ canonical و از ۲۸ به ۴۵ راهنما در هر زبان توسعه یافته
است. آموزش در صفحۀ اصلی جلو آمده، راهنماها تمرین و خروجی مشخص دارند، مسیرهای
مطالعه و واژه‌نامه به آن‌ها متصل‌اند و دانلودها در نسخۀ مستقل نیز موجودند.
این تغییر ظرفیت آموزشی و کیفیت ساختار فنی را بالا می‌برد؛ نتیجهٔ رتبه‌بندی زنده
یا مرجعیت جهانی هنوز اندازه‌گیری نشده است.

Google تصریح می‌کند روشی وجود ندارد که خودکار رتبه اول را تضمین کند و حتی
نمایه‌شدن سایت تضمین عمومی ندارد. هدف قابل دفاع، محتوای مفید و قابل بررسی،
دسترسی خزنده، URL روشن و رشد اعتبار واقعی است، نه ادعای برتری جهانی:
[راهنمای رسمی SEO](https://developers.google.com/search/docs/fundamentals/seo-starter-guide).

## دامنهٔ بررسی

منبع محتوا، ترجمه‌ها، ۶ خدمت، صفحات حقوقی، فرم، API، ابزار DOI و برنامه‌ریز،
CSS/JS، فونت/دارایی‌ها، تولیدکنندۀ صفحات، robots/sitemap، aliasها، تنظیم Vercel،
ساخت تولیدی/پیش‌نمایش، HTML مستقل و اسکریپت‌های بررسی بازبینی شدند. فایل پیشنهاد
ضمیمه مبنای تطبیق موضوعات بود. ادعای آن متن درباره «۱۴۷ جست‌وجو» یا نبود محتوای
فارسی در تمام وب، در این انتشار بازتولید یا تأیید نشده است. منابع اصلی و رسمی
برای تصمیم‌های نسخه‌حساس بررسی شدند؛ منبع بنیادی قدیمی صرفاً به علت سن حذف نشده است.
بایگانی تاریخی برای ردگیری نگه‌داری شده و بخشی از خروجی عمومی نیست.

## مشکل‌های محتوایی و پاسخ اجراشده

بسیاری از راهنماهای قبلی کوتاه و بیشتر معرفی ابزار بودند. جمله‌های تکراری نامرتبط
درباره طول چکیده/دفاع/کد نیز در چند صفحه وجود داشت. برای تمام ۲۸ موضوع پیشین
پروندۀ آموزشی اختصاصی، جدول تصمیم/کنترل، خروجی تمرین و کاربرگ نوشته شد و
تکرار نامرتبط حذف شد. مثال‌ها صریحاً فرضی‌اند و نتیجه واقعی یا پذیرش علمی نمی‌سازند.

عنوان مشاهده‌ای از قالب پیش‌فرض «تأثیر» جدا شد؛ چکیدۀ پروپوزال به مشارکت
برنامه‌ریزی‌شده اشاره دارد نه نتیجۀ آینده ساختگی. محدودۀ فرمول نمونه، تعبیر آلفا،
فرضیه متناسب با هدف، زبان چکیدۀ دانشگاه و تفاوت SE/SD روشن‌تر شد. منبع استنباط
علّی به کتاب اصلی نویسندگان پیوند خورد. ادعای منسوخ Google Fonts از محتوای پایه
حذف شد؛ فونت‌ها محلی‌اند.

'''+comparison+'''
این شمارش تقریبی با جداسازی فاصله در متن HTML انجام شده است؛ تعداد کلمه معیار
کیفیت علمی یا امتیاز سئو نیست. نسخه عربی در برخی بخش‌ها موجزتر است و همۀ زبان‌ها
هنوز به بازبینی تخصصی و ویرایش انسانی مستقل نیاز دارند.

## بازبینی پیشنهادهای ضمیمه

دو موضوع مرکب (پیش‌ثبت و مقاله داده/نرم‌افزار) تفکیک شدند؛ حاصل ۱۷ راهنمای جدید
در هر زبان است. هر راهنما منابع، مثال، جدول و کاربرگ دارد. چک‌لیست رسمی دیگران
کپی نشده و مثال نوشتاری و عددی از نو برای آموزش ساخته شده است.

'''+table+'''
TOP 2025 با چارچوب قبلی یکی نیست. سیاست JOSS به سابقۀ واقعی توسعه عمومی و
استفاده پژوهشی توجه دارد؛ یک اسکریپت کوچک به عنوان نرم‌افزار پذیرفتنی معرفی نشده.
CHART دامنه خاص سلامت دارد. نام شبیه PRISMA به معنی تأیید رسمی نیست؛ نامۀ ۲۰۲۶
درباره trAIce همراه فهرست اصلی بررسی شده و نوع سند «نامه/اظهارنظر» است، نه
آزمون تجربی اثربخشی. قوانین حفظ حقوق نیز تنها در پروندۀ واقعی قابل تطبیق‌اند.

## معماری دانش و دسترسی

۸ مسیر یادگیری با ترتیب پیشنهادی و خروجی ساخته شد؛ همۀ ۴۵ موضوع حداقل در یک
مسیر حضور دارند. روش پیشرفته به خواندن طراحی و مفاهیم پایه متصل است. ترتیب
یادگیری با زمان واقعی پیش‌ثبت اشتباه گرفته نمی‌شود. واژه‌نامه ۴۰ اصطلاح و
مخفف را به راهنمای کاربردی پیوند می‌دهد. فهرست ۶۱ منبع شامل کشف آموزش، اقتصاد،
کتاب و پیش‌چاپ نیز هست؛ دسترسی کامل، حقوق استفاده و وابستگی نهادی از هم تفکیک‌اند.

صفحه اصلی آموزش را جلو می‌آورد و خدمات، روند کار، پرسش‌ها و تماس را حفظ می‌کند.
هویت، فونت‌های Vazirmatn/Cairo و پنج کانال تماس موجود حفظ شدند؛ حذف‌های نمایشی
نسخۀ ضمیمه دوباره افزوده نشده‌اند. هیچ حساب ایتای اختصاصی حدس زده نشده است.

جست‌وجو تفاوت ک/ك، ی/ي، اَلف‌های عربی، حرکت، نیم‌فاصله، واژۀ متصل و ارقام
فارسی/عربی/لاتین را پوشش می‌دهد. مخفف انگلیسی در محتوای جست‌وجوی محلی راهنماها
و واژه‌نامه قابل استفاده است. تقاطع جست‌وجو و دسته و حالت بدون نتیجه آزموده شد.

## الگوگیری از منابع مرجع

این جدول برداشت طراحی و آموزشی این انتشار است؛ مقایسۀ رتبه یا ادعای هم‌سطح‌بودن
سایت با نهادهای مرجع نیست. روش‌های مناسب با اندازۀ پروژه تطبیق داده شده‌اند.

| منبع/الگو | اصل قابل استفاده | پیاده‌سازی این سایت |
| --- | --- | --- |
| Google Search Central | دسترسی خزنده، محتوای مفید و URL مشخص | HTML کامل، canonical و پیوندهای توصیفی با بررسی گراف |
| OSF و COS | تصمیم زمان‌دار و شفافیتِ متناسب با نوع پژوهش | دفتر شناخت قبلی، تغییر و شاهد؛ تفکیک ثبت، IPA و گواهی |
| EQUATOR و PRISMA | انتخاب راهنما بر اساس طرح و نسخه | ماتریس طرح/نسخه/شاهد و کنترل منشأ استاندارد تازه |
| ANU | استدلال مشترک بین مقاله‌های رساله | معماری فصل، فقرة اتصال و بحث تلفیقی، با قواعد محلی |
| Quarto | اتصال محاسبه و متن | عدد درون‌متنی، کد و نمودار از ورودی؛ نیازهای ساخت جدا |
| Scientific Data | منشأ، کیفیت و امکان استفادۀ مجدد | فرهنگ داده، کنترل ورودی، گزارش اعتبارسنجی و محدودیت |
| JOSS | نرم‌افزار، مستند و شواهد بلوغ پیش از مقالۀ کوتاه | جدول آمادگی و آزمون با جواب معلوم؛ بدون ادعای پذیرش |

## اصلاح‌ها و کنترل‌های فنی سئو

- محتوا در HTML کامل است؛ خواندن مقاله به اجرای JS وابسته نیست.
- canonical، hreflang متقابل سه زبان و x-default، عنوان/توضیح، Breadcrumb، Article
  و ItemList با محتوای دیده‌شده و منابع هم‌خوان‌اند؛ نویسنده ساختگی اضافه نشده.
- تاریخ ویرایش واقعی است. برای راهنمای تازه dateCreated داریم؛ تاریخ انتشار
  عمومی که هنوز مشخص نیست به عنوان datePublished ساخته نشده است.
- همۀ ۱۸۳ URL از پیوندهای داخلی قابل رسیدن‌اند. تصاویر ابعاد و نسخۀ واکنش‌گرا
  دارند؛ تصویر اصلی eager/high و تصاویر کارت‌ها lazy هستند.
- سایت‌مپ تصویر/زبان و robots با مبدأ تولیدی هماهنگ‌اند. aliasهای index و HTML
  به URL اصلی می‌روند؛ ۷۳۴ alias با حفظ query و مقصد ۲۰۰ بررسی شدند.
- دامنه سفارشی، عنوان canonical، robots و حتی لینک در کاربرگ Markdown را تغییر
  می‌دهد. مبدأ preview برای canonical به کار نمی‌رود؛ preview قابل خواندن برای
  دیدن noindex است. فایل‌های دانلود noindex دارند و صفحات آموزشی قابل نمایه‌اند.
- خروجی عمومی فقط فایل‌های لازم سایت را دارد؛ منبع محتوا، بایگانی و اسکریپت‌ها
  عمومی نشده‌اند. CSP، nosniff، referrer policy و cache دارایی‌ها حفظ شدند.
- API محدودۀ ورودی، consent، honeypot، نوع JSON و تاریخ نامعتبر را کنترل می‌کند؛
  فقط پیام قابل بازبینی آماده می‌شود و هیچ پیام یا داده‌ای ارسال/ذخیره نشده است.

## مثال اجرایی و نسخۀ مستقل

بستۀ Python از کتابخانۀ استاندارد استفاده می‌کند. شش آزمون با خط/صفحۀ رگرسیون
با ضرایب معلوم، دم نرمال مستقل، ورودی نامعتبر و تطبیق فایل خروجی موفق شدند.
میانگین ۸۰۸÷۱۲ و شمار مسیرهای ۱۲/۱۲،۱۰/۱۰،۸/۸ بازاجرا شدند. شش مسیر صرفاً توصیفی
هستند و آزمون رسمی specification curve، CI یا نتیجۀ علّی ندارند.

TOST آموزشی با مدل نرمال، برآورد ۰٫۲۰، SE=۰٫۱۵ و حدود ±۰٫۵ بازاجرا شد؛ CI90
حدود [−۰٫۰۴۶۷۲۸،۰٫۴۴۶۷۲۸] و p≈۰٫۰۲۲۷۵۰ است. این مثال مستقل از CSV است؛ حدود
و روش طرح واقعی را تعیین نمی‌کند. با SE=۱ هم‌ارزی پشتیبانی نمی‌شود.

HTML مستقل ۱۸۳ صفحه، دو فونت، عکس‌ها، JS/CSS و تمام لینک‌های دانلود را همراه
دارد. ۳۱۲ لینک جاسازی‌شده با فایل اصلی، بایت‌به‌بایت تطبیق داده شد؛ از جمله ZIP
آموزشی با CRC سالم. ۵۵۲ عنصر تصویر حفظ و لینک‌های مسیر/بخش بررسی شدند. فایل
مستقل برای مرور آفلاین noindex است و جای URL مستقل صفحات تولیدی را نمی‌گیرد.

## نتیجهٔ بررسی و حدود آن

بررسی پایه، سئو منبع/ساخت، محتوا و کاربرگ، شش آزمون محاسبه، رفتار JS با شبیه‌ساز
DOM، ساخت مبدأ/preview، HTTP/API، فایل مستقل و شرایط انتشار موفق بودند. جزئیات
در `reference/qa` است. شبیه‌ساز DOM مرورگر واقعی نیست. Chromium در محیط موجود
نبود؛ بررسی تصویری موبایل/دسکتاپ و Lighthouse اجرا نشد. Quarto نیز موجود نبود؛
سند QMD و دستورها آماده‌اند ولی خروجی HTML/Word/PDF آن ادعای آزمون ندارد.

Rich Results Test، URL Inspection، Search Console، پوشش نمایه، رتبه، CWV و رفتار
کاربر سایت زنده بررسی نشده‌اند. داده، ابزار، تصویر یا محتوای AI به عنوان تأیید
متخصص معرفی نشده. هیچ درصد بهبود رتبه، امتیاز ۱۰۰ سئو یا تضمین مرجعیت ساخته نشده است.

## کار لازم برای مرجعیت بلندمدت

۱. دامنه تولیدی واقعی و مالکیت آن را تثبیت و Search Console/sitemap را در همان
حساب مالک بررسی کنید. بعد از انتشار، پاسخ URL، canonical انتخاب‌شده، کشف و
نمایه را از داده واقعی بسنجید. توکن و حساب لازم در ضمیمه موجود نبود.

۲. برای هر خوشۀ تخصصی، نویسنده و بازبین واجد صلاحیت با شرح نقش و سابقۀ قابل
تأیید تعیین کنید؛ متن فارسی/عربی/انگلیسی و مثال‌ها را مستقل ویرایش کنید. تاریخ
بررسی باید نشان‌دهندۀ کار واقعی باشد. راهنمای سلامت و آمار پیچیده اولویت بالاتر دارند.

۳. پوشش فعلی بیشتر روش عمومی پژوهش است. برای تبدیل به مرجع رشته‌ای، محتوای
مبتنی بر نیاز و شواهد در مهندسی، علوم پایه، علوم انسانی و آموزش بسازید؛ با سؤال
دقیق، مثال معتبر، داده/کد مجاز و معیار پایان کار. انبوه‌سازی متن مشابه ارزش مرجع
ایجاد نمی‌کند. هیچ سایت کوچک تمام نیاز همه رشته‌ها و همه زبان‌ها را برطرف نمی‌کند.

۴. بازخورد و خطا را با منبع اصلاح ثبت کنید، شکست بازاجرا و تغییر سیاست را پیگیری
کنید و پیوندهای بیرونی/نسخه استانداردها را دوباره بررسی کنید. فایل حقوقی یا راهنمای
یک دانشگاه را قانون همۀ جهان ننامید. DOI وجود مقاله را باید در رکورد اصلی کنترل کرد.

۵. اعتبار را از کار باکیفیت، استفاده واقعی و ارجاع علمی مرتبط بسازید؛ رتبه و
CTR و مشکلات فنی را پس از انتشار پایش کنید. خرید لینک یا وعده رتبه تضمینی جای
کیفیت و اعتماد نیست. تغییر کوچک یا تعداد کلمه به تنهایی امتیاز علمی ایجاد نمی‌کند.

## مدارک همراه

`README-FA.md`: اجرا و نگهداری؛ `SOURCES.md`: منابع و حدود انتساب؛
`content/site-content.json`: محتوای قابل ویرایش؛ `examples/research-demo`:
کد و مثال‌ها؛ `reference/qa`: بررسی جاری؛ `reference/previous`: سوابق حفظ‌شده.
'''
(ROOT/'SEO-AUDIT-FA.md').write_text(audit,encoding='utf-8')

sources='''# Sources and editorial provenance — 2026-10-06

Primary publications, author-hosted material, official tool documentation and
university guidance were preferred. Teaching prose, synthetic cases, matrices
and code were authored for this edition rather than copied checklists. Links do
not imply endorsement, partnership or affiliation. Read the original for a real
project and check the scope, version, corrections and outlet requirements.

The new version-sensitive topics were checked against their actual official or
primary sources. Older foundational references remain where relevant. The check
date records this editorial pass; it is not the source's publication date, a
perpetual freshness guarantee or proof that every external page is always reachable.
The PRISMA-trAIce source is a letter/commentary on endorsement, not an empirical
validation study. Discovery services contain varied record and full-text statuses.

AI tools assisted prose, translations, code and imagery. Source inspection and
the accompanying executable checks are documented; independent specialist peer
review of this site or its translations is not claimed. Site author attribution
remains organizational. Fictional examples are not observed research results.

## SEO primary guidance

- [Google SEO starter guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Google helpful content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Google localized pages](https://developers.google.com/search/docs/specialty/international/localized-versions)

## Research source registry

| Key | Source | Type | Editorial check |
| --- | --- | --- | --- |
'''
for key,source in D['source_registry'].items():
    sources+='| '+key+' | ['+source['name'].replace('|','\\|')+']('+source['url']+') | '+source.get('type','Original package reference / official or primary material')+' | '+source.get('checked','Inherited reference; consult original and current requirements')+' |\n'
sources+='''
## Source-to-guide mapping

Every guide includes its source IDs in `content/site-content.json`, corresponding
visible references and matching Article citations. Each workbook repeats the
applicable references. New topics and their local paths are listed below.

'''
for slug,title,action in mapping:
    a=next(a for a in D['articles']['en'] if a['slug']==slug)
    sources+='- ['+a['title']+'](en/guides/'+slug+'/index.html): '+', '.join(a['sources'])+'.\n'
sources+='''
## Assets and reuse

See `IMAGE-CREDITS.md` and `reference/image-prompts.json` for inherited images.
Service images are illustrative rather than verified employee portraits or study
findings. Self-hosted fonts retain their OFL licence files under `assets/fonts`.
The new teaching mini-project has its own MIT code licence and CC0 synthetic-data
notice. Those grants do not include third-party references or institute branding.
No official reporting checklist was reproduced as an endorsed local translation.
'''
(ROOT/'SOURCES.md').write_text(sources,encoding='utf-8')
print('Wrote README-FA.md, SEO-AUDIT-FA.md and SOURCES.md with current coverage and explicit validation limits.')
