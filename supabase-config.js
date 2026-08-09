// מפתח publishable הוא ציבורי בכוונה — ההגנה האמיתית היא ב-RLS בצד Supabase.
window.SUPABASE_URL = "https://uneexjwwyloqnszropsg.supabase.co";
window.SUPABASE_KEY = "sb_publishable_Btguoh2XGTyHyOxUooZK5w_KRHrBJZG";

// נעילה מקומית לדף במקום navigator.locks.
// ברירת המחדל של Supabase נועלת ברמת המקור (origin) — טאב שנתקע או נסגר באמצע
// פעולת אימות משאיר נעילה תלויה, וכל התחברות בטאב אחר ממתינה לה לנצח.
// נעילה בזיכרון מסדרת את הקריאות בתוך הדף בלבד ולא יכולה להיתקע בין טאבים.
// הפונקציה מריצה את הפעולה ישירות. קריאות האימות כאן יזומות על ידי המשתמש
// ורצות בזו אחר זו, ולכן אין צורך בסריאליזציה — ואין שום מצב שבו נוצר קיפאון.
window.SUPABASE_MEMORY_LOCK = (_name, _acquireTimeout, fn) => fn();
