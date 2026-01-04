# it-burns-when-ip
# 📡 פרויקט גמר: רשתות תקשורת מחשבים (Computer Networks Final Project)

## תוכן העניינים
- [מבוא](#מבוא)
- [חלק 1: אריזה ולכידת מנות](#-חלק-1-אריזה-ולכידת-מנות-packet-analysis)
- [חלק 2: מערכת צ'אט](#-חלק-2-מערכת-צאט-tcpip-chat-system)
- [ריכוז קבצי הפרויקט](#-ריכוז-קבצי-הפרויקט-inventory)

---

## מבוא

פרויקט זה עוסק בניתוח מעמיק של פרוטוקולי תקשורת, סימולציית אריזת נתונים (Encapsulation) ופיתוח מערכת צ'אט מלאה ב‑TCP/IP.

הפרויקט מחולק לשני חלקים עיקריים:

1. **חלק 1:** אריזה ולכידת מנות (Packet Analysis & Wireshark)  
2. **חלק 2:** פיתוח מערכת צ'אט (Client‑Server Chat System)

---

## 📦 חלק 1: אריזה ולכידת מנות (Packet Analysis)

בחלק זה ביצענו סימולציה של תעבורת רשת משכבת היישום ועד לשכבה הפיזית, כולל לכידה וניתוח ב‑Wireshark.

### 📂 קבצים מצורפים לחלק 1

- `group212252217_http_input.csv` – קובץ קלט עם הודעות מדומות בשכבת היישום.
- `raw_tcp_ip_notebook_fallback_annotated-v1.ipynb` – מחברת Jupyter המדמה תהליך Encapsulation.
- `capture.pcap` – קובץ לכידה מ‑Wireshark.

### ⚙️ תהליך העבודה (Workflow)

1. **יצירת נתונים** – יצירת קובץ CSV עם תרחישי HTTP/SMTP.  
2. **עיבוד במחברת Jupyter**
   - טעינת הנתונים.
   - הוספת כותרות TCP/IP/Ethernet.
   - שידור מנות בלולאה מקומית (Loopback).
3. **לכידה וניתוח**
   - לכידה באמצעות Wireshark.
   - אימות הופעת תוכן ההודעות ב‑Payload.

---

## 💬 חלק 2: מערכת צ'אט (TCP/IP Chat System)

מערכת צ'אט מרובת משתמשים המבוססת על **Sockets** ו‑**Threading**.  
המערכת תומכת בלפחות 5 לקוחות במקביל, ניתוב הודעות פרטיות וממשק משתמש מתקדם.

### ✨ תכונות מרכזיות

- ארכיטקטורת שרת‑לקוח.
- Multi‑threading לטיפול במספר לקוחות.
- פרוטוקול הודעות: `TargetName:Message`.
- ממשק GUI ו‑CLI.
- טיפול בניתוקים וחסימת הודעות ריקות.

### 🛠 הוראות התקנה והרצה

#### דרישות קדם
- Python 3.6+
- התקנת ספריות (ל‑GUI):

```bash
pip install -r requirements.txt
```

#### 🎨 הרצה עם GUI (מומלץ)

**שרת**
```bash
python server_gui.py
```

הזן הגדרות, או השתמש בדיפולטיות, ולחץ **START SERVER**.

**לקוח**
```bash
python client_gui.py
```

הזן Nickname והתחבר.

#### 💻 הרצה ב‑CLI

- שרת: `python server.py`
- לקוח: `python client.py`

---

## 📂 ריכוז קבצי הפרויקט (Inventory)

| קובץ | חלק | תיאור |
|-----|-----|------|
| group212252217_http_input.csv | חלק 1 | קובץ נתונים אפליקטיביים |
| raw_tcp_ip_notebook_fallback_annotated-v1.ipynb | חלק 1 | סימולציית Encapsulation |
| csv_communications_capture.pcap | חלק 1 | לכידת Wireshark |
| server.py | חלק 2 | שרת CLI |
| server_gui.py | חלק 2 | שרת GUI |
| client.py | חלק 2 | לקוח CLI |
| client_gui.py | חלק 2 | לקוח GUI |
| requirements.txt | כללי | ספריות נדרשות |
| Project_Report.docx | כללי | דוח מסכם |

---

**מגישים:** שי כהן, שחר סידון, איסבל דייצ׳ב
