# Security Policy

## Supported version
Security fixes target the latest release on `main`.

## Reporting
Please report suspected vulnerabilities privately through GitHub's security reporting features when available. Do not publish credentials, private URLs, tokens, or exploit details in a public issue.

## Security model
Link Health Monitor performs outbound HTTP(S) requests to user-supplied targets. Run it only against URLs you are authorized to access. URLs with embedded credentials are rejected. The tool does not store response bodies, cookies, credentials, or telemetry. Redirects are followed by Python's standard HTTP client, so operators running this in sensitive networks should treat target lists as trusted input and apply normal egress controls.

# سياسة الأمان
يُرجى الإبلاغ عن الثغرات بصورة خاصة وعدم نشر أسرار أو روابط داخلية حساسة في Issues العامة. الأداة ترسل طلبات HTTP/HTTPS إلى العناوين التي يحددها المستخدم، لذلك استخدمها فقط مع عناوين مخول لك فحصها وطبّق قيود الخروج الشبكي المناسبة في البيئات الحساسة.
