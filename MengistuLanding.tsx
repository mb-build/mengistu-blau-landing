/**
 * MengistuLanding — דף נחיתה ליועץ השקעות מנגיסטו בלאו
 *
 * להוסיף ל-src/index.css (בתוך @layer base):
 *   :root {
 *     --ink:        222 62% 10%;
 *     --ink-2:      226 57% 16%;
 *     --gold:       45 68% 47%;
 *     --gold-light: 44 73% 65%;
 *     --mint:       165 66% 50%;
 *     --cloud:      228 33% 97%;
 *   }
 * ול-tailwind.config.ts (theme.extend.colors):
 *   ink: "hsl(var(--ink))", "ink-2": "hsl(var(--ink-2))",
 *   gold: "hsl(var(--gold))", "gold-light": "hsl(var(--gold-light))",
 *   mint: "hsl(var(--mint))", cloud: "hsl(var(--cloud))"
 * ופונט Heebo ב-index.html + fontFamily.sans.
 */

import { useState, type FormEvent } from "react";
import {
  ArrowLeft,
  Building2,
  Check,
  CheckCircle2,
  LineChart,
  Plus,
  Rocket,
  Shield,
  Star,
  Wallet,
  Wind,
  Landmark,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type Lead = {
  name: string;
  email: string;
  phone: string;
  amount: string;
  message: string;
};

const AMOUNTS = [
  "עד ₪50,000",
  "₪50,000 – ₪250,000",
  "₪250,000 – ₪1,000,000",
  "מעל ₪1,000,000",
];

const TRACKS = [
  {
    icon: LineChart,
    title: "שוק ההון",
    body: "תיק מדדי רחב, חשיפה גלובלית ופיזור אמיתי. הליבה של רוב התוכניות — פשוט, זול ומשעמם במובן הטוב.",
    horizon: "אופק מומלץ: 5+ שנים",
  },
  {
    icon: Building2,
    title: "נדל״ן מניב",
    body: "מקרנות ריט ועד עסקאות משותפות בארץ ובחו״ל. תזרים חודשי לצד עליית ערך — עם בדיקת היתכנות לפני כל שקל.",
    horizon: "אופק מומלץ: 7+ שנים",
  },
  {
    icon: Shield,
    title: "אג״ח וסולידי",
    body: "הכרית שמאפשרת לך לא לברוח בירידות. אג״ח ממשלתי, קונצרני מדורג וקרנות כספיות — לכסף שצריך להישאר יציב.",
    horizon: "אופק מומלץ: 1–3 שנים",
  },
  {
    icon: Rocket,
    title: "אלטרנטיבי",
    body: "קרנות פרייבט אקוויטי, הלוואות חוץ־בנקאיות וסטארטאפים. נתח קטן ומחושב מהתיק — שם לוקחים סיכון מודע.",
    horizon: "אופק מומלץ: 5–10 שנים",
  },
];

const PAINS = [
  {
    icon: Landmark,
    title: "הכסף שוכב ולא עובד",
    body: "עו״ש ופיקדונות נשחקים מול האינפלציה. כל שנה שהכסף לא מושקע היא שנה שלא תחזור — ריבית דריבית לא סולחת על דחיינות.",
  },
  {
    icon: Wind,
    title: "יותר מדי דעות, אפס כיוון",
    body: "יוטיוב אומר קריפטו, הבנקאי אומר קרן, החבר אומר נדל״ן. בלי מסגרת שמתאימה דווקא לך, כל עצה היא רק עוד רעש.",
  },
  {
    icon: Wallet,
    title: "עמלות שאוכלות בשקט",
    body: "דמי ניהול של אחוז וחצי נשמעים זניחים — עד שמחשבים אותם על עשרים שנה. רוב המשקיעים לא יודעים כמה הם באמת משלמים.",
  },
];

const STEPS = [
  {
    n: "01",
    title: "שיחת אבחון (45 דק׳)",
    body: "מיפוי מלא: כמה יש, מאיפה זה מגיע, למה זה מיועד ומתי תצטרך אותו. בלי מכירה — רק הבנה.",
  },
  {
    n: "02",
    title: "תוכנית כתובה",
    body: "מסמך אחד, בעברית פשוטה: התמהיל המדויק, הסכומים, העמלות הצפויות ותרחישי הקיצון — כדי שתדע למה לצפות.",
  },
  {
    n: "03",
    title: "ביצוע וליווי",
    body: "עוברים יחד על ההוצאה לפועל, ואז נפגשים רבעונית לאיזון ועדכון. אתה לא נשאר לבד מול המסך.",
  },
];

const TESTIMONIALS = [
  {
    quote:
      "שנתיים הכסף שלנו ישב בבנק כי פחדנו לטעות. מנגיסטו פירק את זה לצעדים קטנים שהבנתי, והיום יש לנו תוכנית שאני לא מפחדת להסתכל עליה.",
    who: "שירה כ׳ · מנהלת מוצר, תל אביב",
  },
  {
    quote:
      "הדבר הראשון שהוא עשה זה להראות לי כמה אני משלם עמלות. רק התיקון הזה שינה לי את התמונה — ומשם בנינו תיק הגיוני.",
    who: "אבי ט׳ · בעל עסק, חיפה",
  },
  {
    quote:
      "בירידה הגדולה רציתי למכור הכל. שיחה אחת איתו הרגיעה אותי והחזירה אותי לתוכנית. זה השווה יותר מכל טיפ שקיבלתי אי פעם.",
    who: "רונן מ׳ · מהנדס, ראשל״צ",
  },
];

const FAQ = [
  {
    q: "כמה כסף צריך כדי להתחיל?",
    a: "אין רף מינימום. ההבדל בין ₪20,000 ל־₪2,000,000 הוא בתמהיל ובכלים, לא בשאלה אם כדאי להתחיל. ככל שמתחילים מוקדם — לזמן יש יותר עבודה לעשות.",
  },
  {
    q: "האם מובטחת לי תשואה?",
    a: "לא, ואף אחד לא יכול להבטיח. מה שכן מובטח: תדע בדיוק מה רמת הסיכון שלקחת, מה התרחיש הגרוע שאתה חשוף אליו, ולמה בחרנו בכל רכיב בתיק.",
  },
  {
    q: "שיחת האבחון באמת בחינם?",
    a: "כן, 45 דקות ללא עלות וללא התחייבות. גם אם לא נמשיך יחד — תצא עם מפה ברורה של המצב ושלוש נקודות שאפשר לשפר בעצמך.",
  },
  {
    q: "אני כבר מושקע דרך הבנק. יש טעם?",
    a: "דווקא אז. רוב הבדיקות מגלות כפילויות, פיזור מדומה ודמי ניהול גבוהים מהנדרש. לפעמים השיפור הגדול ביותר הוא בתיק שכבר קיים.",
  },
  {
    q: "מה קורה כשהשוק יורד?",
    a: "מתכוננים לזה מראש. בתוכנית כתוב מה עושים בכל תרחיש, וברגע האמת יש עם מי לדבר לפני שמקבלים החלטה רגשית שעולה כסף.",
  },
];

const HERO_BULLETS = [
  "מפה מלאה של הכסף שלך תוך 45 דקות",
  "התאמה מדויקת לרמת הסיכון שלך",
  "ליווי צמוד — לא מסמך שנשכח במגירה",
  "שקיפות מלאה בעמלות ובעלויות",
];

const STATS = [
  { value: "12+", label: "שנות ניסיון בשוק ההון" },
  { value: "1,400+", label: "משקיעים שקיבלו תוכנית" },
  { value: "₪380M", label: "היקף נכסים מלווה" },
];

const grain =
  "bg-[radial-gradient(rgba(255,255,255,.06)_1px,transparent_1px)] bg-[length:22px_22px]";

export default function MengistuLanding() {
  const [lead, setLead] = useState<Lead>({
    name: "",
    email: "",
    phone: "",
    amount: AMOUNTS[1],
    message: "",
  });
  const [sent, setSent] = useState(false);

  const set = (k: keyof Lead) => (e: { target: { value: string } }) =>
    setLead((prev) => ({ ...prev, [k]: e.target.value }));

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // TODO: לחבר ל-Supabase / Resend / webhook לשליחת הליד במייל
    console.log("lead", lead);
    setSent(true);
  };

  return (
    <div dir="rtl" className="min-h-[100dvh] w-full overflow-x-hidden bg-cloud font-sans text-ink antialiased">
      {/* NAV */}
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-ink/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-5 sm:h-20 sm:px-8">
          <a href="#top" className="flex shrink-0 items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-gold-light to-gold text-lg font-black text-ink">
              מב
            </span>
            <span className="leading-tight">
              <span className="block text-base font-bold text-white sm:text-lg">מנגיסטו בלאו</span>
              <span className="block text-[11px] tracking-wide text-gold-light/80 sm:text-xs">ייעוץ וליווי השקעות</span>
            </span>
          </a>
          <nav className="hidden items-center gap-8 text-sm text-white/70 lg:flex">
            <a href="#tracks" className="transition hover:text-gold-light">מסלולי השקעה</a>
            <a href="#process" className="transition hover:text-gold-light">איך זה עובד</a>
            <a href="#about" className="transition hover:text-gold-light">על מנגיסטו</a>
            <a href="#faq" className="transition hover:text-gold-light">שאלות נפוצות</a>
          </nav>
          <Button asChild className="shrink-0 rounded-full bg-gold px-4 font-bold text-ink hover:bg-gold-light sm:px-6">
            <a href="#lead">לשיחת אבחון חינם</a>
          </Button>
        </div>
      </header>

      {/* HERO */}
      <section id="top" className={`relative flex min-h-[100dvh] items-center overflow-hidden bg-ink pb-16 pt-28 ${grain}`}>
        <div className="pointer-events-none absolute -left-40 -top-40 h-[520px] w-[520px] rounded-full bg-gold/20 blur-[120px]" />
        <div className="pointer-events-none absolute -bottom-40 -right-32 h-[460px] w-[460px] rounded-full bg-mint/10 blur-[120px]" />

        <div className="relative mx-auto grid w-full max-w-7xl items-center gap-12 px-5 sm:px-8 lg:grid-cols-[1.15fr_.85fr] lg:gap-16">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-gold/40 bg-gold/10 px-4 py-1.5 text-xs font-medium text-gold-light sm:text-sm">
              <span className="h-2 w-2 animate-pulse rounded-full bg-mint" />
              נותרו 7 מקומות לשיחות אבחון החודש
            </div>

            <h1 className="mt-6 text-[clamp(2.25rem,6vw,4.25rem)] font-black leading-[1.08] text-white">
              הכסף שלך יושב בעו״ש
              <span className="block bg-gradient-to-l from-gold-light via-gold to-gold-light bg-clip-text text-transparent">
                ומאבד ערך בכל חודש.
              </span>
            </h1>

            <p className="mt-6 max-w-xl text-[clamp(1rem,2.2vw,1.25rem)] leading-relaxed text-white/70">
              מנגיסטו בלאו בונה איתך תוכנית השקעה אישית — מסלול ברור, מותאם לסכום, לגיל ולרמת הסיכון שלך.
              בלי ז׳רגון, בלי הבטחות באוויר. רק החלטות שאתה מבין ויכול לעמוד מאחוריהן.
            </p>

            <ul className="mt-8 grid max-w-xl gap-3 sm:grid-cols-2">
              {HERO_BULLETS.map((b) => (
                <li key={b} className="flex items-center gap-3 text-sm text-white/85 sm:text-base">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-mint/20 text-mint">
                    <Check className="h-3.5 w-3.5" />
                  </span>
                  {b}
                </li>
              ))}
            </ul>

            <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-4">
              {STATS.map((s, i) => (
                <div key={s.label} className="flex items-center gap-8">
                  <div>
                    <div className="text-3xl font-black text-gold-light">{s.value}</div>
                    <div className="text-xs text-white/50">{s.label}</div>
                  </div>
                  {i < STATS.length - 1 && <div className="hidden h-10 w-px bg-white/15 sm:block" />}
                </div>
              ))}
            </div>
          </div>

          {/* LEAD FORM */}
          <div id="lead" className="rounded-3xl bg-white p-6 shadow-[0_0_0_1px_hsl(var(--gold)/.25),0_30px_80px_-30px_hsl(var(--gold)/.45)] sm:p-8">
            {sent ? (
              <div className="rounded-2xl border border-mint/30 bg-mint/10 p-8 text-center">
                <CheckCircle2 className="mx-auto h-14 w-14 text-mint" />
                <h3 className="mt-4 text-lg font-black">הפרטים התקבלו</h3>
                <p className="mt-2 text-sm text-ink/65">
                  מנגיסטו יחזור אליך תוך יום עסקים אחד. בינתיים — שווה לרדת ולקרוא על מסלולי ההשקעה.
                </p>
              </div>
            ) : (
              <>
                <h2 className="text-xl font-black sm:text-2xl">שיחת אבחון — ללא עלות</h2>
                <p className="mt-2 text-sm leading-relaxed text-ink/60">
                  משאירים פרטים, מנגיסטו חוזר אישית תוך יום עסקים אחד עם שלוש נקודות שאפשר לשפר כבר עכשיו.
                </p>

                <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                  <div>
                    <Label htmlFor="name" className="mb-1.5 block text-sm font-semibold">שם מלא</Label>
                    <Input id="name" required value={lead.name} onChange={set("name")} placeholder="ישראל ישראלי"
                      className="rounded-xl border-ink/15 bg-cloud py-6 focus-visible:ring-gold/30" />
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <Label htmlFor="email" className="mb-1.5 block text-sm font-semibold">אימייל</Label>
                      <Input id="email" type="email" required dir="ltr" value={lead.email} onChange={set("email")}
                        placeholder="you@mail.com"
                        className="rounded-xl border-ink/15 bg-cloud py-6 text-right focus-visible:ring-gold/30" />
                    </div>
                    <div>
                      <Label htmlFor="phone" className="mb-1.5 block text-sm font-semibold">טלפון</Label>
                      <Input id="phone" type="tel" required dir="ltr" value={lead.phone} onChange={set("phone")}
                        placeholder="050-0000000"
                        className="rounded-xl border-ink/15 bg-cloud py-6 text-right focus-visible:ring-gold/30" />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="amount" className="mb-1.5 block text-sm font-semibold">סכום להשקעה</Label>
                    <select id="amount" value={lead.amount} onChange={set("amount")}
                      className="w-full rounded-xl border border-ink/15 bg-cloud px-4 py-3 text-sm outline-none transition focus:border-gold focus:ring-2 focus:ring-gold/30">
                      {AMOUNTS.map((a) => <option key={a}>{a}</option>)}
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="msg" className="mb-1.5 block text-sm font-semibold">
                      מה הכי מטריד אותך כרגע? <span className="font-normal text-ink/40">(אופציונלי)</span>
                    </Label>
                    <Textarea id="msg" rows={3} value={lead.message} onChange={set("message")}
                      placeholder="למשל: יש לי כסף שיושב בבנק ואני לא יודע מה לעשות איתו"
                      className="resize-none rounded-xl border-ink/15 bg-cloud focus-visible:ring-gold/30" />
                  </div>

                  <Button type="submit" className="w-full rounded-xl bg-ink py-6 text-base font-black text-white hover:bg-ink-2">
                    קבעו לי שיחת אבחון
                  </Button>
                  <p className="text-center text-xs text-ink/45">הפרטים נשמרים אצלנו בלבד. אפס ספאם, אפס טלמרקטינג.</p>
                </form>
              </>
            )}
          </div>
        </div>
      </section>

      {/* PAIN */}
      <section className="bg-white py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-5 sm:px-8">
          <div className="max-w-3xl">
            <span className="text-sm font-bold tracking-widest text-gold">הבעיה האמיתית</span>
            <h2 className="mt-3 text-[clamp(1.75rem,4.5vw,3rem)] font-black leading-tight">
              רוב האנשים לא מפסידים כסף בגלל השקעה גרועה.
              <br className="hidden sm:block" />
              <span className="text-ink/45">הם מפסידים בגלל חוסר החלטה.</span>
            </h2>
          </div>

          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {PAINS.map(({ icon: Icon, title, body }) => (
              <div key={title} className="rounded-3xl border border-ink/10 p-8 transition hover:border-gold/50 hover:shadow-xl">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gold/10 text-gold">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-5 text-xl font-black">{title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-ink/60">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TRACKS */}
      <section id="tracks" className={`relative overflow-hidden bg-ink py-20 sm:py-28 ${grain}`}>
        <div className="pointer-events-none absolute top-1/3 -right-40 h-[420px] w-[420px] rounded-full bg-gold/15 blur-[130px]" />
        <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
          <div className="max-w-3xl">
            <span className="text-sm font-bold tracking-widest text-gold-light">מסלולי השקעה</span>
            <h2 className="mt-3 text-[clamp(1.75rem,4.5vw,3rem)] font-black leading-tight text-white">
              מסלול אחד לא מתאים לכולם.
            </h2>
            <p className="mt-4 text-lg text-white/60">
              מנגיסטו מרכיב עבורך תמהיל מתוך ארבעה עולמות — לפי אופק הזמן, הנזילות שאתה צריך והסיכון שאתה באמת מסוגל לישון איתו בלילה.
            </p>
          </div>

          <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {TRACKS.map(({ icon: Icon, title, body, horizon }) => (
              <article key={title} className="rounded-3xl border border-white/10 bg-white/[.04] p-7 transition hover:border-gold/40 hover:bg-white/[.08]">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-gold/15 text-gold-light">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-5 text-lg font-black text-white">{title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-white/55">{body}</p>
                <div className="mt-5 border-t border-white/10 pt-5 text-xs text-gold-light">{horizon}</div>
              </article>
            ))}
          </div>

          <p className="mt-8 max-w-3xl text-xs leading-relaxed text-white/35">
            * האמור אינו מהווה ייעוץ השקעות אישי ואינו תחליף לייעוץ המתחשב בנתונים ובצרכים המיוחדים של כל אדם. אין באמור התחייבות לתשואה כלשהי. כל השקעה כרוכה בסיכון, לרבות אובדן חלק מהקרן.
          </p>
        </div>
      </section>

      {/* PROCESS */}
      <section id="process" className="bg-cloud py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-5 sm:px-8">
          <div className="max-w-3xl">
            <span className="text-sm font-bold tracking-widest text-gold">איך זה עובד</span>
            <h2 className="mt-3 text-[clamp(1.75rem,4.5vw,3rem)] font-black leading-tight">שלושה צעדים מבלבול לתוכנית</h2>
          </div>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.n} className="relative rounded-3xl bg-white p-8 shadow-sm">
                <span className="absolute -top-5 right-8 grid h-12 w-12 place-items-center rounded-2xl bg-ink text-lg font-black text-gold-light">
                  {s.n}
                </span>
                <h3 className="mt-6 text-xl font-black">{s.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-ink/60">{s.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ABOUT */}
      <section id="about" className="bg-white py-20 sm:py-28">
        <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 sm:px-8 lg:grid-cols-2">
          <div className="relative">
            <div className={`mx-auto grid aspect-[4/5] w-full max-w-md place-items-center overflow-hidden rounded-[2rem] bg-gradient-to-br from-ink to-ink-2 lg:mx-0 ${grain}`}>
              <span className="bg-gradient-to-l from-gold-light to-gold bg-clip-text text-[clamp(4rem,12vw,8rem)] font-black text-transparent">
                מב
              </span>
            </div>
            <div className="absolute -bottom-6 left-4 rounded-2xl bg-gold px-6 py-4 shadow-xl lg:left-auto lg:-right-6">
              <div className="text-2xl font-black text-ink">12+</div>
              <div className="text-xs font-medium text-ink/70">שנות ניסיון</div>
            </div>
          </div>
          <div>
            <span className="text-sm font-bold tracking-widest text-gold">על מנגיסטו</span>
            <h2 className="mt-3 text-[clamp(1.75rem,4.5vw,3rem)] font-black leading-tight">
              ״הכסף שלך לא צריך יועץ מרשים. הוא צריך תוכנית ברורה.״
            </h2>
            <div className="mt-6 space-y-4 leading-relaxed text-ink/65">
              <p>
                מנגיסטו בלאו מלווה משקיעים פרטיים, משפחות ובעלי עסקים בבניית תוכניות השקעה — מהשקל הראשון ועד תיקים בני מיליונים.
                הגישה שלו פשוטה: קודם מבינים את החיים שלך, רק אחר כך בוחרים מכשיר פיננסי.
              </p>
              <p>
                הוא לא מוכר מוצרים ולא מבטיח תשואות. הוא בונה מסגרת שאתה מבין לעומק, מסביר בדיוק מה הסיכון בכל צעד,
                ונשאר איתך גם כשהשוק יורד — כי שם נקבעות התוצאות האמיתיות.
              </p>
            </div>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-cloud p-5">
                <div className="font-black">ניסיון מוסדי</div>
                <div className="mt-1 text-sm text-ink/55">רקע בניהול תיקים ובשוק ההון הישראלי והגלובלי</div>
              </div>
              <div className="rounded-2xl bg-cloud p-5">
                <div className="font-black">שקיפות מלאה</div>
                <div className="mt-1 text-sm text-ink/55">כל עמלה, כל עלות וכל ניגוד עניינים — על השולחן</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="bg-ink-2 py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-5 sm:px-8">
          <h2 className="max-w-2xl text-[clamp(1.75rem,4.5vw,3rem)] font-black leading-tight text-white">
            מה אומרים אחרי השיחה הראשונה
          </h2>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {TESTIMONIALS.map((t) => (
              <figure key={t.who} className="rounded-3xl border border-white/10 bg-white/[.05] p-7">
                <div className="flex gap-1 text-gold-light">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-current" />
                  ))}
                </div>
                <blockquote className="mt-4 text-sm leading-relaxed text-white/80">״{t.quote}״</blockquote>
                <figcaption className="mt-5 text-xs text-white/45">{t.who}</figcaption>
              </figure>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="bg-white py-20 sm:py-28">
        <div className="mx-auto max-w-3xl px-5 sm:px-8">
          <h2 className="text-center text-[clamp(1.75rem,4.5vw,3rem)] font-black leading-tight">
            שאלות ששואלים לפני שמתחילים
          </h2>
          <div className="mt-12 divide-y divide-ink/10 border-y border-ink/10">
            {FAQ.map((f) => (
              <details key={f.q} className="group py-5">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-bold">
                  {f.q}
                  <Plus className="h-5 w-5 shrink-0 text-gold transition group-open:rotate-45" />
                </summary>
                <p className="mt-3 text-sm leading-relaxed text-ink/60">{f.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className={`relative overflow-hidden bg-ink py-20 sm:py-28 ${grain}`}>
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-l from-transparent via-gold to-transparent" />
        <div className="pointer-events-none absolute -bottom-40 left-1/2 h-[420px] w-[720px] -translate-x-1/2 rounded-full bg-gold/15 blur-[130px]" />
        <div className="relative mx-auto max-w-3xl px-5 text-center sm:px-8">
          <h2 className="text-[clamp(1.9rem,5vw,3.25rem)] font-black leading-tight text-white">
            בעוד שנה תרצה שהתחלת היום.
          </h2>
          <p className="mt-5 text-lg text-white/65">45 דקות. ללא עלות. בלי התחייבות. עם מפה ברורה ביד.</p>
          <Button asChild className="mt-9 rounded-full bg-gold px-9 py-6 text-base font-black text-ink hover:bg-gold-light">
            <a href="#lead">
              לקביעת שיחת אבחון
              <ArrowLeft className="mr-2 h-5 w-5" />
            </a>
          </Button>
          <p className="mt-5 text-xs text-white/35">נותרו 7 מקומות לחודש הקרוב</p>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/10 bg-ink-2 py-12">
        <div className="mx-auto grid max-w-7xl items-start gap-8 px-5 sm:px-8 md:grid-cols-3">
          <div>
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-gold-light to-gold font-black text-ink">
                מב
              </span>
              <span className="font-bold text-white">מנגיסטו בלאו</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-white/45">
              ייעוץ וליווי השקעות אישי — תוכנית שאתה מבין, ומלווה שנשאר גם כשקשה.
            </p>
          </div>
          <div className="text-sm">
            <div className="font-bold text-white">יצירת קשר</div>
            <ul className="mt-3 space-y-2 text-white/50">
              <li><a href="mailto:hello@mengistu-blau.co.il" dir="ltr" className="transition hover:text-gold-light">hello@mengistu-blau.co.il</a></li>
              <li><a href="tel:+972500000000" dir="ltr" className="transition hover:text-gold-light">050-000-0000</a></li>
              <li>א׳–ה׳ 09:00–18:00</li>
            </ul>
          </div>
          <div className="text-xs leading-relaxed text-white/35">
            האמור באתר זה הוא מידע שיווקי כללי בלבד ואינו מהווה ייעוץ השקעות, שיווק השקעות או ייעוץ מס, ואינו מתחשב בנתוניו ובצרכיו של כל אדם.
            אין באמור התחייבות לתשואה. כל השקעה כרוכה בסיכון, לרבות אובדן חלק מהקרן או כולה.
            <div className="mt-4">© {new Date().getFullYear()} מנגיסטו בלאו. כל הזכויות שמורות.</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
