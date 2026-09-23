# Link Health Monitor

A small, dependency-free Python HTTP/HTTPS link checker for local use, CI pipelines, scheduled jobs, and documentation/site maintenance.

It checks whether links respond successfully, follows redirects, measures latency, supports batch target files, emits JSON for automation, and uses meaningful exit codes. It does **not** crawl websites, store response bodies, or depend on a hosted monitoring service.

## Why it exists

Broken links and unexpected redirects are easy to miss. Link Health Monitor provides a reproducible command-line check that can run on a laptop or in CI without API keys or third-party accounts.

## Features

- HTTP and HTTPS validation with safe input checks.
- `HEAD` by default; optional `GET` for servers that do not support HEAD correctly.
- Redirect detection and final URL reporting.
- HTTP status and request latency measurement.
- Optional maximum-latency threshold.
- One URL, many URLs, or UTF-8 target files with comments.
- Duplicate target removal in the CLI.
- Human-readable and structured JSON reports.
- Optional report file output.
- `--fail-on-redirect` for stricter CI policies.
- Exit codes designed for automation: `0` healthy, `1` unhealthy/policy failure, `2` invalid input/configuration.
- Python API plus `link-health` and `python -m link_health_monitor` entry points.
- No runtime dependencies, telemetry, accounts, or API keys.

## Preview

```text
$ link-health https://example.com
[OK] 200 | 142.31 ms | https://example.com

Total: 1 | Healthy: 1 | Unhealthy: 0 | Redirected: 0
```

Actual status and latency depend on the network and target. For screenshots, capture the terminal output from your own environment; no static screenshot is required to use the project.

## Requirements & installation

- Python 3.10+
- Network access to the targets you intend to check

```bash
git clone https://github.com/rad03i2/link-health-monitor.git
cd link-health-monitor
python -m pip install -e .
```

For development/testing:

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
link-health https://example.com https://www.iana.org/domains/reserved
link-health --file examples/targets.txt
link-health https://example.com --method GET --timeout 5
link-health --file examples/targets.txt --max-latency 1000 --json
link-health --file examples/targets.txt --json --output report.json
link-health https://example.com --fail-on-redirect
link-health --version
```

Target files contain one URL per line. Empty lines and lines beginning with `#` are ignored.

### Python API

```python
from link_health_monitor import check_link, check_links, summarize

one = check_link("https://example.com", timeout=5)
print(one.status, one.healthy, one.latency_ms)

results = check_links(["https://example.com", "https://www.iana.org"])
print(summarize(results))
```

## Configuration

There is intentionally no configuration file or `.env`: all behavior is explicit through CLI flags or Python function arguments. `HEAD` is the default method, timeout is 10 seconds, and any HTTP status from 200 through 399 is considered healthy after redirects are followed. A latency threshold, when supplied, can mark an otherwise successful response unhealthy.

## Project structure

```text
src/link_health_monitor/
  __init__.py       Public API and version
  __main__.py       python -m entry point
  core.py           URL validation, HTTP checks, summaries, JSON
  cli.py            CLI parsing, reports, exit codes
tests/
  test_core.py      Validation/reporting/file tests
  test_http.py      Real local HTTP end-to-end tests
  test_cli.py       CLI behavior tests
examples/targets.txt
.github/workflows/ci.yml
```

## Testing

```bash
python -m compileall -q src tests
python -m pytest
```

CI runs these checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13. HTTP integration tests use a temporary local test server and do not depend on public internet availability.

## Security & privacy

The application does not collect telemetry or persist response bodies, cookies, or credentials. URLs containing embedded usernames/passwords are rejected. Because targets cause outbound network requests and redirects are followed, treat target lists as trusted input in sensitive networks and apply appropriate egress controls. See [SECURITY.md](SECURITY.md).

## Limitations

- This is a point-in-time checker, not a hosted uptime service or scheduler.
- It does not crawl HTML pages to discover links automatically.
- It does not retain historical measurements or send alerts.
- Some servers reject `HEAD`; use `--method GET` for those targets.
- A successful HTTP status does not prove that page content is semantically correct.
- Redirect chains are followed by Python's standard HTTP client; the report exposes only the original and final URLs, not every intermediate hop.

## Optional roadmap

Potential future additions include bounded HTML link discovery, historical SQLite reports, and optional notification adapters. These are not required for the current core checker.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes focused, tested, and free of secrets.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية — مراقب صحة الروابط

أداة Python خفيفة وبدون اعتماديات تشغيل خارجية لفحص روابط HTTP/HTTPS محليًا، ومناسبة لسطر الأوامر وCI والمهام المجدولة وصيانة روابط المواقع والتوثيق.

تفحص الأداة استجابة الرابط، وتتبع إعادة التوجيه، وتقيس زمن الاستجابة، وتتعامل مع ملفات أهداف متعددة، وتوفر JSON للأتمتة ورموز خروج واضحة. وهي **لا** تزحف داخل المواقع ولا تخزن محتوى الصفحات ولا تحتاج خدمة مراقبة سحابية.

## لماذا هذا المشروع؟

قد تبقى الروابط المعطلة أو التحويلات غير المقصودة دون ملاحظة. يوفر المشروع فحصًا قابلًا للتكرار يمكن تشغيله على الحاسوب أو داخل CI دون مفاتيح API أو حسابات خارجية.

## الميزات

- التحقق من روابط HTTP وHTTPS ومدخلاتها.
- استخدام `HEAD` افتراضيًا مع دعم `GET` عند الحاجة.
- اكتشاف إعادة التوجيه وإظهار الرابط النهائي.
- عرض حالة HTTP وزمن الاستجابة.
- حد اختياري لأقصى زمن استجابة مقبول.
- فحص رابط واحد أو عدة روابط أو ملف UTF-8.
- إزالة الأهداف المكررة في CLI.
- تقارير نصية أو JSON.
- حفظ التقرير في ملف.
- خيار `--fail-on-redirect` لسياسات CI الصارمة.
- رموز خروج: `0` نجاح، `1` رابط غير سليم/مخالفة سياسة، `2` إدخال أو إعداد غير صالح.
- Python API وتشغيل عبر `link-health` أو `python -m link_health_monitor`.
- لا telemetry ولا API keys ولا حسابات ولا اعتماديات تشغيل خارجية.

## معاينة

```text
link-health https://example.com
[OK] 200 | 142.31 ms | https://example.com
```

القيمة الفعلية للزمن والحالة تعتمد على الشبكة والخادم. يمكن أخذ لقطة شاشة من الطرفية عند الحاجة لعرض المشروع.

## المتطلبات والتثبيت

يتطلب Python 3.10 أو أحدث واتصالًا شبكيًا بالأهداف المراد فحصها.

```bash
git clone https://github.com/rad03i2/link-health-monitor.git
cd link-health-monitor
python -m pip install -e .
```

للتطوير والاختبارات:

```bash
python -m pip install -e ".[dev]"
```

## الاستخدام

```bash
link-health https://example.com
link-health --file examples/targets.txt
link-health https://example.com --method GET --timeout 5
link-health --file examples/targets.txt --max-latency 1000 --json
link-health --file examples/targets.txt --json --output report.json
```

ملف الأهداف يحتوي رابطًا واحدًا في كل سطر، ويتم تجاهل الأسطر الفارغة والأسطر التي تبدأ بـ`#`.

### Python API

```python
from link_health_monitor import check_link

result = check_link("https://example.com", timeout=5)
print(result.status, result.healthy, result.latency_ms)
```

## الإعداد

لا يحتاج المشروع ملف إعداد أو `.env`. كل الخيارات صريحة عبر CLI أو Python API. المهلة الافتراضية 10 ثوانٍ والطريقة الافتراضية `HEAD`، وتعد حالات HTTP من 200 إلى 399 سليمة بعد اتباع التحويلات. ويمكن لحد زمن الاستجابة أن يجعل الاستجابة الناجحة غير سليمة إذا كانت أبطأ من الحد المطلوب.

## بنية المشروع

الكود موجود في `src/link_health_monitor`، والاختبارات في `tests`، ومثال الأهداف في `examples/targets.txt`، وCI في `.github/workflows/ci.yml`.

## الاختبارات

```bash
python -m compileall -q src tests
python -m pytest
```

تغطي الاختبارات التحقق من الروابط، JSON، الملخصات، ملفات الأهداف، CLI، ورموز الخروج، إضافة إلى اختبارات HTTP متكاملة تستخدم خادمًا محليًا مؤقتًا. ويشغّل CI الاختبارات على Linux وWindows وmacOS مع عدة إصدارات Python.

## الأمان والخصوصية

لا تجمع الأداة telemetry ولا تخزن محتوى الاستجابات أو cookies أو بيانات الاعتماد، وترفض الروابط التي تتضمن اسم مستخدم أو كلمة مرور. بما أن الفحص ينشئ اتصالات شبكة ويتبع التحويلات، يجب استخدام قوائم أهداف موثوقة وتطبيق قيود خروج مناسبة في الشبكات الحساسة. راجع [SECURITY.md](SECURITY.md).

## القيود

- ليست خدمة uptime مستضافة ولا scheduler.
- لا تستخرج الروابط تلقائيًا من HTML.
- لا تحتفظ بسجل تاريخي ولا ترسل تنبيهات.
- بعض الخوادم ترفض `HEAD`؛ استخدم `--method GET` معها.
- نجاح HTTP لا يضمن صحة محتوى الصفحة وظيفيًا.
- يعرض التقرير الرابط الأصلي والنهائي ولا يسجل كل خطوة وسيطة في سلسلة التحويل.

## تطوير اختياري مستقبلًا

يمكن مستقبلًا إضافة اكتشاف محدود للروابط داخل HTML، وسجل SQLite تاريخي، ومحولات تنبيه اختيارية. هذه إضافات اختيارية وليست ميزات مدعاة في الإصدار الحالي.

## المساهمة

راجع [CONTRIBUTING.md](CONTRIBUTING.md)، وأبقِ التغييرات مركزة ومختبرة وخالية من الأسرار.

## الترخيص

MIT — راجع [LICENSE](LICENSE).

## المؤلف

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
