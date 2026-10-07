# راهنمای انتشار سایت دیدگر در GitHub و Vercel

اصلاح بسته‌بندی برای استقرار: ۷ اکتبر ۲۰۲۶.

در `didgar-github-vercel-ready.zip` فایل‌های پروژه مستقیماً در ریشهٔ ZIP هستند.
این بسته شامل همان سایت سه‌زبانه با ۱۸۳ صفحه و ۴۵ راهنما در هر زبان است.
تغییر این انتشار، ساختار بسته‌بندی و توضیحات استقرار است.

## ۱. فایل‌های سایت را در GitHub قرار دهید

ابتدا ZIP را روی رایانه استخراج کنید. **محتویات استخراج‌شده را در ریشهٔ مخزن
GitHub قرار دهید.** اگر برنامهٔ استخراج یک پوشه با نام ZIP ساخته است، وارد آن
شوید و محتویاتش را منتقل کنید. در صفحهٔ اصلی مخزن باید این فایل‌ها و پوشه‌ها
را ببینید:

| مسیر در ریشهٔ مخزن | نقش |
| --- | --- |
| `package.json` | دستور ساخت پروژه |
| `vercel.json` | تنظیمات Vercel و مسیرها |
| `index.html` | صفحهٔ اصلی |
| `scripts/build.mjs` | ساخت خروجی انتشار |
| `content/routes.json` | فهرست صفحات |
| `fa/`، `en/`، `ar/` | صفحات سه زبان |
| `assets/` | عکس‌ها، فونت‌ها و فایل‌های دانلود |
| `api/consultation.mjs` | آماده‌سازی پیوند درخواست مشاوره |

آپلود یک فایل `.zip` در GitHub، محتوای آن را به فایل‌های مخزن تبدیل نمی‌کند.
پروژهٔ حاضر هم دستور استخراج ZIP در زمان استقرار ندارد؛ Vercel باید به فایل‌های
استخراج‌شده دسترسی داشته باشد.

GitHub در رابط وب، در هر بار آپلود حداکثر ۱۰۰ فایل می‌پذیرد. این بسته فایل‌های
بیشتری دارد. برای انتقال کامل از Git یا GitHub Desktop استفاده کنید؛ در روش
وب، فایل‌ها را در چند نوبت و با حفظ مسیر پوشه‌ها اضافه کنید.

روش Git برای یک مخزن موجود: مخزن را clone کنید، تمام محتویات استخراج‌شده را
در پوشهٔ clone شده کپی کنید، سپس در همان پوشه تغییرات را مرور و ثبت کنید:

```sh
git status
git add .
git commit -m "Add Didgar website with Vercel files at repository root"
git push
```

## ۲. تنظیمات Vercel

در پروژهٔ Vercel، به `Settings → Build and Deployment` بروید:

| تنظیم | مقدار برای بستهٔ جدید |
| --- | --- |
| Root Directory | ریشهٔ مخزن؛ پیش‌فرض `./`، بدون انتخاب زیرپوشه |
| Framework Preset | `Other` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | پیش‌فرض npm |

`vercel.json` موجود، `framework: null`، دستور ساخت و پوشهٔ خروجی را مشخص می‌کند.
این سایت HTML/CSS/JavaScript چندصفحه‌ای است و preset مناسبش `Other` است.
خروجی `dist` در زمان ساخت دوباره از فایل‌های منبع ایجاد می‌شود.
ساخت انتشار به Python، Quarto یا پکیج npm اضافه نیاز ندارد.

اگر از ZIP قبلی استفاده می‌کنید و فایل‌ها را در پوشهٔ `didgar-site` مخزن
استخراج کرده‌اید، Root Directory را **`didgar-site`** قرار دهید و سه تنظیم دیگر
را مانند جدول نگه دارید. اگر مخزن فقط فایل ZIP دارد، ابتدا فایل‌ها را استخراج
و در مخزن ثبت کنید؛ تغییر Root Directory به تنهایی کافی نیست.

در قسمت Git نیز اطمینان حاصل کنید شاخهٔ انتخاب‌شده برای Production همان شاخه‌ای
است که فایل‌های سایت را در آن ثبت کرده‌اید.

اگر دامنهٔ نهایی شما با `https://dr17.vercel.app` متفاوت است، متغیر محیطی
`SITE_URL` را به مبدأ HTTPS واقعی سایت، بدون مسیر صفحه، تنظیم کنید. نمونه:
`https://your-domain.example`. این متغیر برای canonical و sitemap است.

## ۳. دوباره منتشر کنید و خروجی را بررسی کنید

تنظیمات را ذخیره و جدیدترین commit را Deploy کنید. برای بازسازی پس از تغییر
تنظیمات، در `Deployments` از `Redeploy` استفاده کنید و گزینهٔ استفاده از Build
Cache را خاموش کنید. از `Visit` در صفحهٔ همان deployment تازه، سایت را باز کنید.

در Build Logs باید پیام `Built 183 canonical pages` دیده شود. در خروجی ساخت،
`index.html`، `en/index.html` و `ar/index.html` باید وجود داشته باشند. مسیرهای
زیر را روی نشانی جدید `.vercel.app` بررسی کنید:

- `/`
- `/en/`
- `/ar/`
- `/fa/guides/research-proposal/`
- `/sitemap.xml`

اگر نشانی `.vercel.app` کار می‌کند اما دامنهٔ اختصاصی ۴۰۴ می‌دهد، تنظیم دامنه
را بررسی کنید. اگر هر دو ۴۰۴ می‌دهند، آدرس مخزن، آدرس deployment تازه، Root
Directory و Build Logs برای تشخیص لازم‌اند. شناسه‌ای مانند `fra1::...` به تنهایی
نشان نمی‌دهد کدام فایل یا تنظیم علت خطاست.

## بررسی محلی و جزئیات محتوا

از همان پوشه‌ای که `package.json` دارد:

```sh
npm run build
npm run dev
```

جزئیات سایت در [README-FA.md](README-FA.md)، گزارش سئو در
[SEO-AUDIT-FA.md](SEO-AUDIT-FA.md) و منابع علمی در [SOURCES.md](SOURCES.md) است.
HTML مستقل قبلاً جداگانه تحویل شده است. برای ساخت دوبارهٔ آن، `npm run standalone`
را اجرا کنید؛ خروجی در `../deliverables/didgar-preview.html` ایجاد می‌شود.

## منابع رسمی تنظیمات

- [Vercel: تنظیم ساخت، Root Directory و Output Directory](https://vercel.com/docs/builds/configure-a-build)
- [Vercel: معنی خطای NOT_FOUND](https://vercel.com/docs/errors/not_found)
- [GitHub: افزودن فایل و محدودیت آپلود مرورگر](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

این بسته با ساخت و سرویس HTTP محلی بررسی می‌شود. حساب Vercel، مخزن GitHub و
نشانی استقرار فعلی شما در این بررسی در دسترس نبوده‌اند؛ برطرف شدن خطای همان
استقرار، پس از اعمال تنظیمات و انتشار جدید باید بررسی شود.
