import re
import os
from bs4 import BeautifulSoup

source_path = "موقع_مكتب_أبابطين.html"
target_path = "موقع_مكتب_أبابطين_v4.html"

print(f"Reading {source_path}...")
with open(source_path, "r", encoding="utf-8") as f:
    source_html = f.read()

soup = BeautifulSoup(source_html, "html.parser")

# 1. Extract @font-face rules
font_rules = re.findall(r'@font-face\s*\{[^}]+\}', source_html)
font_css = "\n".join(font_rules)

# 2. Extract LD-JSON scripts
ld_jsons = soup.find_all("script", type="application/ld+json")
ld_json_str = "\n".join(str(s) for s in ld_jsons)

# 3. Extract all head meta and link tags
meta_tags = [str(m) for m in soup.head.find_all("meta")]
meta_str = "\n".join(meta_tags)

link_tags = [str(l) for l in soup.head.find_all("link")]
link_str = "\n".join(link_tags)

# 4. Clean original style 0 (excluding font-face)
orig_style0 = soup.head.find_all("style")[0].string if soup.head.find_all("style") else ""
orig_style1 = soup.head.find_all("style")[1].string if len(soup.head.find_all("style")) > 1 else ""
clean_orig_style0 = re.sub(r'@font-face\s*\{[^}]+\}', '', orig_style0)

# 5. Extract all 33 sections
sections = soup.find_all("section", class_="page")
assert len(sections) == 33, f"Expected 33 sections, got {len(sections)}"
sec_dict = {s.get("id"): s for s in sections}

# Enhance pg-home: add dual CTA buttons to home-intro if not present
home_sec = sec_dict["pg-home"]
intro_div = home_sec.find("div", class_="home-intro")
if intro_div and not intro_div.find("div", class_="hero-actions"):
    actions_div = soup.new_tag("div", attrs={"class": "hero-actions reveal d3"})
    
    btn1 = soup.new_tag("a", attrs={"class": "btn-gold design-btn", "href": "#works", "data-page": "works"})
    btn1.string = "اكتشف أعمالنا "
    span1 = soup.new_tag("span", attrs={"aria-hidden": "true"})
    span1.string = "↙"
    btn1.append(span1)
    
    btn2 = soup.new_tag("a", attrs={"class": "btn-glass design-link", "href": "#contact", "data-page": "contact"})
    btn2.string = "لنبدأ مشروعك "
    span2 = soup.new_tag("span", attrs={"aria-hidden": "true"})
    span2.string = "←"
    btn2.append(span2)
    
    actions_div.append(btn1)
    actions_div.append(btn2)
    
    scroll_cue = intro_div.find("div", class_="scroll-cue")
    if scroll_cue:
        scroll_cue.insert_before(actions_div)
    else:
        intro_div.append(actions_div)

# In pg-calculator, add the in-page quick estimator widget right before calc-cta
calc_sec = sec_dict["pg-calculator"]
if calc_sec and not calc_sec.find("div", id="quickCalculatorWidget"):
    calc_cta = calc_sec.find("div", class_="calc-cta")
    widget_html = """
    <div id="quickCalculatorWidget" class="quick-calc-card reveal">
      <div class="qcalc-header">
        <span class="qcalc-badge">حاسبة تقديرية فورية</span>
        <h3>احسب التكلفة الأولية لمشروعك الآن</h3>
        <p>حدّد مسطحات البناء المتوقعة ومستوى التشطيب للحصول على تقدير استرشادي فوري</p>
      </div>
      <div class="qcalc-grid">
        <div class="qcalc-field">
          <label for="qcArea">مسطح البناء الإجمالي (م²): <b id="qcAreaVal">450 م²</b></label>
          <input type="range" id="qcArea" min="150" max="2500" step="25" value="450">
          <div class="qcalc-range-marks"><span>150 م²</span><span>1,000 م²</span><span>2,500 م²</span></div>
        </div>
        <div class="qcalc-field">
          <label for="qcType">نوع المشروع</label>
          <select id="qcType">
            <option value="villa" selected>فيلا سكنية خاصة</option>
            <option value="duplex">دوبلكس سكني</option>
            <option value="building">عمارة سكنية / تجارية</option>
            <option value="commercial">معارض ومحلات تجارية</option>
          </select>
        </div>
        <div class="qcalc-field">
          <label for="qcFinish">مستوى التشطيب المرغوب</label>
          <select id="qcFinish">
            <option value="bone">عظم فقط (بدون تشطيب)</option>
            <option value="standard">تشطيب تجاري / قياسي</option>
            <option value="lux" selected>تشطيب ديلوكس (عالي الجودة)</option>
            <option value="super">تشطيب سوبر ديلوكس فاخر</option>
          </select>
        </div>
      </div>
      <div class="qcalc-results">
        <div class="qres-item">
          <span>التكلفة التقديرية للبناء</span>
          <b id="qcTotalCost">810,000 ر.س</b>
          <small id="qcCostPerM">بمتوسط 1,800 ر.س / م²</small>
        </div>
        <div class="qres-breakdown">
          <div><span>الهيكل العظم (45%):</span> <strong id="qcBoneCost">364,500 ر.س</strong></div>
          <div><span>التشطيبات (35%):</span> <strong id="qcFinishCost">283,500 ر.س</strong></div>
          <div><span>الكهروميكانيك (12%):</span> <strong id="qcMechCost">97,200 ر.س</strong></div>
          <div><span>الموقع العام (8%):</span> <strong id="qcSiteCost">64,800 ر.س</strong></div>
        </div>
      </div>
      <div class="qcalc-actions">
        <button type="button" id="qcShareWa" class="btn-gold">
          <span>طلب تسعيرة دقيقة عبر واتساب</span>
          <svg viewBox="0 0 24 24" width="18" height="18"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2z" fill="currentColor"/></svg>
        </button>
      </div>
    </div>
    """
    w_soup = BeautifulSoup(widget_html, "html.parser")
    if calc_cta:
        calc_cta.insert_before(w_soup)
    else:
        calc_sec.append(w_soup)

# Header
header_el = soup.header
if header_el:
    nav_div = header_el.find("div", class_="nav")
    if nav_div and not nav_div.find("a", class_="nav-consult-btn"):
        cbtn = soup.new_tag("a", attrs={"href": "#contact", "data-page": "contact", "class": "nav-consult-btn"})
        cbtn.string = "احجز استشارة"
        tt = nav_div.find(id="themeToggle")
        if tt:
            tt.insert_before(cbtn)
        else:
            nav_div.append(cbtn)
    header_str = str(header_el)
else:
    header_str = ""

footer_str = str(soup.footer) if soup.footer else ""
lightbox_str = str(soup.find("div", id="lightbox")) if soup.find("div", id="lightbox") else ""
toast_str = str(soup.find("div", id="pv-toast")) if soup.find("div", id="pv-toast") else '<div id="pv-toast"></div>'
wafloat_str = str(soup.find("a", id="waFloat")) if soup.find("a", id="waFloat") else ""
totop_str = str(soup.find("button", id="toTop")) if soup.find("button", id="toTop") else ""

all_sections_str = "\n".join(str(sec_dict[sid]) for sid in [s.get("id") for s in sections])

v4_custom_css = """
/* ══════════════════════════════════════════════════════════════
   V4 LUXURY ARCHITECTURAL DESIGN SYSTEM
   مكتب معاذ بن عبدالله أبابطين للاستشارات الهندسية
   ══════════════════════════════════════════════════════════════ */

:root {
  --ink: #d4af37;
  --navy: #f8fafc;
  --bg: #0b0e11;
  --alt: #12161b;
  --line: rgba(255, 255, 255, 0.08);
  --line-gold: rgba(212, 175, 55, 0.35);
  --muted: #94a3b8;
  --faint: #64748b;
  --text: #cbd5e1;
  --card: #161c22;
  --brand: #d4af37;
  --accent: #d4af37;
  --gold: #d4af37;
  --gold-light: #e5c66b;
  --gold-glow: rgba(212, 175, 55, 0.18);
  --gold-bg: rgba(212, 175, 55, 0.08);
  --surface-glass: rgba(18, 22, 27, 0.78);
  --header-bg: rgba(11, 14, 17, 0.88);
  --card-hover: #1c242c;
  --font-ar: 'IBM Plex Sans Arabic', 'CenturyGothic', 'Fatimah', system-ui, sans-serif;
  color-scheme: dark;
}

html[data-theme="light"] {
  --ink: #9e7d3b;
  --navy: #14181c;
  --bg: #fcfbf9;
  --alt: #f4f0e8;
  --line: #e4dfd5;
  --line-gold: rgba(158, 125, 59, 0.35);
  --muted: #4b5563;
  --faint: #6b7280;
  --text: #242c33;
  --card: #ffffff;
  --brand: #9e7d3b;
  --accent: #9e7d3b;
  --gold: #9e7d3b;
  --gold-light: #b3914a;
  --gold-glow: rgba(158, 125, 59, 0.15);
  --gold-bg: rgba(158, 125, 59, 0.06);
  --surface-glass: rgba(255, 255, 255, 0.85);
  --header-bg: rgba(252, 251, 249, 0.92);
  --card-hover: #f9f7f2;
  color-scheme: light;
}

html {
  font-family: var(--font-ar);
  background: var(--bg);
  color: var(--text);
  line-height: 1.85;
  font-size: 16px;
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
}

body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  overflow-x: hidden;
  transition: background-color 0.35s ease, color 0.35s ease;
}

::selection {
  background: var(--gold);
  color: #0b0e11;
}

.skip-link {
  position: fixed;
  top: -100px;
  right: 20px;
  background: var(--gold);
  color: #0b0e11;
  padding: 12px 24px;
  border-radius: 8px;
  z-index: 10000;
  font-weight: 600;
  transition: top 0.25s ease;
  text-decoration: none;
}
.skip-link:focus {
  top: 20px;
}

#readProgress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--gold-light));
  z-index: 9999;
  width: 0%;
  transition: width 0.1s linear;
  box-shadow: 0 0 10px var(--gold-glow);
}

header {
  position: sticky;
  top: 0;
  width: 100%;
  background: var(--header-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--line);
  z-index: 1000;
  transition: background-color 0.35s ease, border-color 0.35s ease;
}

.nav {
  height: 84px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  text-decoration: none;
  flex-shrink: 0;
}

.brand img {
  height: 48px;
  width: auto;
  object-fit: contain;
  transition: transform 0.25s;
}

.brand:hover img {
  transform: translateY(-1px);
}

html[data-theme="light"] .brand img {
  filter: brightness(0.95);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: var(--text);
  text-decoration: none;
  font-size: 14.5px;
  font-weight: 500;
  padding: 8px 14px;
  border-radius: 8px;
  transition: color 0.25s, background-color 0.25s;
  white-space: nowrap;
  position: relative;
}

.nav-links a:hover {
  color: var(--navy);
  background: var(--gold-bg);
}

.nav-links a.active {
  color: var(--gold);
  background: var(--gold-bg);
  font-weight: 600;
}

.nav-links a.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 14px;
  right: 14px;
  height: 2px;
  background: var(--gold);
  border-radius: 2px;
  box-shadow: 0 0 8px var(--gold-glow);
}

.nav-consult-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #FFFFFF !important;
  background: #09507A !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  border-radius: 30px;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(9, 80, 122, 0.35);
  transition: transform 0.25s, box-shadow 0.25s, background-color 0.25s;
}

html[data-theme="light"] .nav-consult-btn {
  color: #FFFFFF !important;
  background: #09507A !important;
}

.nav-consult-btn:hover {
  transform: translateY(-2px);
  background: #0E679E !important;
  box-shadow: 0 6px 22px rgba(14, 103, 158, 0.55);
  color: #FFFFFF !important;
}


#themeToggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--navy);
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.25s;
  flex-shrink: 0;
}

#themeToggle:hover {
  border-color: var(--gold);
  transform: rotate(25deg);
}

#themeToggle svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

#themeToggle .ic-sun { display: block; }
#themeToggle .ic-moon { display: none; }
html[data-theme="light"] #themeToggle .ic-sun { display: none; }
html[data-theme="light"] #themeToggle .ic-moon { display: block; }

.burger {
  display: none;
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
  padding: 8px;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
  flex-shrink: 0;
}

.burger span {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--navy);
  border-radius: 2px;
  transition: transform 0.3s, opacity 0.3s;
}

@media (max-width: 1100px) {
  .nav {
    height: 72px;
  }
  .burger {
    display: flex;
  }
  .nav-consult-btn {
    display: none;
  }
  .nav-links {
    position: fixed;
    top: 72px;
    right: 0;
    left: 0;
    bottom: 0;
    background: var(--bg);
    flex-direction: column;
    align-items: stretch;
    padding: 24px;
    gap: 8px;
    overflow-y: auto;
    transform: translateY(-100%);
    opacity: 0;
    pointer-events: none;
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
    border-bottom: 1px solid var(--line);
    z-index: 999;
  }
  body.menu-open .nav-links {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
  }
  body.menu-open .burger span:nth-child(1) {
    transform: translateY(6px) rotate(45deg);
  }
  body.menu-open .burger span:nth-child(2) {
    opacity: 0;
  }
  body.menu-open .burger span:nth-child(3) {
    transform: translateY(-6px) rotate(-45deg);
  }
  .nav-links a {
    font-size: 16.5px;
    padding: 14px 18px;
    border-radius: 10px;
    background: var(--card);
    border: 1px solid var(--line);
  }
}

.page {
  display: none;
}

.page.current {
  display: block;
  animation: v4FadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes v4FadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-head {
  padding: clamp(48px, 8vh, 80px) 0 clamp(32px, 5vh, 56px);
  text-align: center;
  position: relative;
  border-bottom: 1px solid var(--line);
  margin-bottom: clamp(36px, 6vh, 64px);
  background: radial-gradient(circle at 50% 0%, var(--gold-bg) 0%, transparent 70%);
}

.page-head .kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--gold);
  letter-spacing: 0.04em;
  margin-bottom: 16px;
}

.page-head .kicker::before,
.page-head .kicker::after {
  content: '';
  width: 24px;
  height: 1px;
  background: var(--gold);
  opacity: 0.6;
}

.page-head .statement {
  font-size: clamp(32px, 5vw, 56px);
  font-weight: 600;
  line-height: 1.3;
  color: var(--navy);
  margin: 0 0 20px;
  max-width: 900px;
  margin-inline: auto;
}

.page-head .lede {
  font-size: clamp(15px, 1.8vw, 18px);
  line-height: 1.9;
  color: var(--muted);
  max-width: 720px;
  margin: 0 auto;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--gold);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 20px;
  padding: 6px 14px;
  border-radius: 20px;
  background: var(--gold-bg);
  border: 1px solid var(--line);
  transition: transform 0.25s, background-color 0.25s;
}

.back-link:hover {
  transform: translateX(4px);
  background: var(--line);
}

.back-link svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

#pg-home {
  padding-top: 0;
}

.home-brand {
  text-align: center;
  padding: 30px 0 10px;
}

.home-brand img {
  max-height: 70px;
  width: auto;
  opacity: 0.9;
}

.home-intro {
  text-align: center;
  padding: clamp(20px, 4vh, 40px) 0 clamp(24px, 4vh, 36px);
  max-width: 960px;
  margin-inline: auto;
}

.home-intro .kicker {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--gold);
  padding: 6px 18px;
  background: var(--gold-bg);
  border: 1px solid var(--line);
  border-radius: 30px;
  margin-bottom: 22px;
}

.home-intro .statement {
  font-size: clamp(38px, 6vw, 76px);
  font-weight: 600;
  line-height: 1.25;
  color: var(--navy);
  margin: 0 0 24px;
  letter-spacing: -0.01em;
}

.home-intro .statement em {
  font-style: normal;
  color: var(--gold);
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.home-intro .lede {
  font-size: clamp(16px, 2vw, 20px);
  line-height: 2;
  color: var(--muted);
  max-width: 760px;
  margin: 0 auto 36px;
}

.hero-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  flex-wrap: wrap;
  margin-bottom: 28px;
}

/* Primary Buttons — Signature Ababtain Blue (#09507A) from original موقع_مكتب_أبابطين.html */
.btn-gold, .btn-primary, .design-btn, #qcShareWa, .qbtn.blue, .nav-consult-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 14px 32px;
  background: #09507A !important;
  color: #FFFFFF !important;
  font-size: 16px;
  font-weight: 600;
  border-radius: 40px;
  text-decoration: none;
  box-shadow: 0 6px 24px rgba(9, 80, 122, 0.4);
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.25s, background-color 0.25s;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.btn-gold:hover, .btn-primary:hover, .design-btn:hover, #qcShareWa:hover, .qbtn.blue:hover, .nav-consult-btn:hover {
  transform: translateY(-3px) scale(1.02);
  background: #0E679E !important;
  box-shadow: 0 10px 30px rgba(14, 103, 158, 0.55);
  color: #FFFFFF !important;
}

/* Secondary Buttons */
.btn-glass, .design-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 14px 30px;
  background: var(--surface-glass);
  color: var(--navy) !important;
  font-size: 16px;
  font-weight: 500;
  border-radius: 40px;
  text-decoration: none;
  border: 1.5px solid var(--line);
  backdrop-filter: blur(12px);
  transition: transform 0.25s, background-color 0.25s, border-color 0.25s, color 0.25s;
}

.btn-glass:hover, .design-link:hover {
  transform: translateY(-2px);
  border-color: #09507A;
  color: #09507A !important;
  background: rgba(9, 80, 122, 0.08);
}

html[data-theme="dark"] .btn-glass:hover, html:not([data-theme="light"]) .btn-glass:hover {
  color: #8CCBF2 !important;
  border-color: #8CCBF2;
}

.home-hero {
  position: relative;
  margin: 0 auto clamp(40px, 6vh, 70px);
  max-width: 1280px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  border: 1px solid var(--line);
}

.home-hero .slides {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  min-height: 420px;
  max-height: 680px;
  background: #000;
  overflow: hidden;
}

.home-hero .slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 1s cubic-bezier(0.4, 0, 0.2, 1), visibility 1s ease;
}

.home-hero .slide.on {
  opacity: 1;
  visibility: visible;
}

.home-hero .slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1);
  transition: transform 7s ease-out;
}

.home-hero .slide.on img {
  transform: scale(1.06);
}

.home-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(0deg, rgba(11,14,17,0.85) 0%, rgba(11,14,17,0.2) 40%, transparent 100%);
  pointer-events: none;
}

.slide-cap {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  z-index: 5;
}

#slideCap {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0,0,0,0.6);
  background: rgba(11, 14, 17, 0.6);
  backdrop-filter: blur(12px);
  padding: 8px 18px;
  border-radius: 30px;
  border: 1px solid rgba(255,255,255,0.12);
}

.slide-dots {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slide-dots button {
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background: rgba(255,255,255,0.35);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.slide-dots button.on {
  width: 28px;
  background: var(--gold);
  box-shadow: 0 0 10px var(--gold-glow);
}

.numbers-sec {
  background: var(--alt);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: clamp(50px, 7vh, 80px) 0;
  position: relative;
  overflow: hidden;
}

.numbers {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 20px;
  text-align: center;
}

.numbers > div {
  padding: 16px;
  border-inline-end: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.numbers > div:last-child {
  border-inline-end: none;
}

.numbers b {
  font-size: clamp(34px, 4.5vw, 56px);
  font-weight: 700;
  font-family: 'CenturyGothic', 'IBM Plex Sans Arabic', sans-serif;
  color: var(--gold);
  line-height: 1.1;
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.numbers span {
  font-size: 13.5px;
  color: var(--muted);
  font-weight: 500;
  line-height: 1.6;
}

@media (max-width: 900px) {
  .numbers {
    grid-template-columns: repeat(3, 1fr);
    row-gap: 32px;
  }
  .numbers > div:nth-child(3) {
    border-inline-end: none;
  }
}

@media (max-width: 540px) {
  .numbers {
    grid-template-columns: repeat(2, 1fr);
  }
  .numbers > div {
    border-inline-end: none;
    border-bottom: 1px solid var(--line);
    padding-bottom: 20px;
  }
}

.sec {
  padding: clamp(60px, 9vh, 100px) 0;
}

.sec-alt {
  background: var(--alt);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.sec-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: clamp(32px, 5vh, 48px);
  flex-wrap: wrap;
}

.sec-head h2 {
  font-size: clamp(28px, 4vw, 40px);
  font-weight: 600;
  color: var(--navy);
  margin: 0;
  position: relative;
  padding-inline-start: 18px;
}

.sec-head h2::before {
  content: '';
  position: absolute;
  inset-inline-start: 0;
  top: 10%;
  bottom: 10%;
  width: 4px;
  background: var(--gold);
  border-radius: 4px;
  box-shadow: 0 0 10px var(--gold-glow);
}

.more-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--gold);
  font-size: 14.5px;
  font-weight: 600;
  text-decoration: none;
  padding: 8px 18px;
  border-radius: 20px;
  background: var(--gold-bg);
  border: 1px solid var(--line);
  transition: transform 0.25s, background-color 0.25s, border-color 0.25s;
}

.more-link:hover {
  transform: translateX(-4px);
  background: var(--line);
  border-color: var(--gold);
}

.more-link svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.works-strip {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  padding-bottom: 24px;
  scrollbar-width: thin;
  scrollbar-color: var(--gold) var(--line);
}

.works-strip::-webkit-scrollbar {
  height: 6px;
}
.works-strip::-webkit-scrollbar-thumb {
  background: var(--gold);
  border-radius: 3px;
}

.works-strip .fig {
  flex: 0 0 clamp(280px, 30vw, 360px);
  margin: 0;
}

.fig {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  overflow: hidden;
  background: var(--card);
  border: 1px solid var(--line);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s, box-shadow 0.3s;
}

.fig:hover {
  transform: translateY(-5px);
  border-color: var(--gold);
  box-shadow: 0 14px 36px rgba(0,0,0,0.35);
}

.fig .im {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: var(--alt);
}

.fig .im img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.fig:hover .im img {
  transform: scale(1.06);
}

.fig figcaption {
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.fig figcaption b {
  font-size: 12px;
  color: var(--gold);
  letter-spacing: 0.05em;
  font-weight: 600;
}

.fig figcaption h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--navy);
  margin: 0;
}

.fig figcaption p {
  font-size: 13.5px;
  color: var(--muted);
  margin: 0;
  line-height: 1.6;
}

.works-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 28px;
}

.journey {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  position: relative;
  margin-top: 20px;
}

.jstep {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 28px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
  position: relative;
}

.jstep:hover {
  transform: translateY(-6px);
  border-color: var(--gold);
  box-shadow: 0 12px 30px rgba(0,0,0,0.3);
}

.jdot {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: var(--gold-bg);
  border: 1px solid var(--gold);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
  color: var(--gold);
  box-shadow: 0 0 15px var(--gold-glow);
}

.jdot svg {
  width: 24px;
  height: 24px;
  stroke: var(--gold);
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.jstep b {
  font-size: 17px;
  font-weight: 600;
  color: var(--navy);
  margin-bottom: 8px;
}

.jstep p {
  font-size: 13.5px;
  color: var(--muted);
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 990px) {
  .journey {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .journey {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .jstep {
    flex-direction: row;
    text-align: right;
    gap: 16px;
    padding: 18px;
  }
  .jdot {
    margin-bottom: 0;
    flex-shrink: 0;
  }
}

.quote-band {
  background: radial-gradient(circle at center, #1b242a 0%, #0d1216 100%);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: clamp(70px, 10vh, 110px) 0;
  text-align: center;
  position: relative;
  overflow: hidden;
}

html[data-theme="light"] .quote-band {
  background: radial-gradient(circle at center, #f5efe6 0%, #ebe2d3 100%);
}

.qmark {
  display: block;
  width: 64px;
  height: auto;
  margin: 0 auto 24px;
  opacity: 0.85;
}

.qmark svg path {
  fill: var(--gold);
}

.quote-band .ar {
  font-size: clamp(20px, 2.5vw, 30px);
  font-weight: 500;
  line-height: 1.8;
  color: var(--navy);
  max-width: 980px;
  margin: 0 auto 24px;
}

.quote-band .en {
  font-size: clamp(15px, 1.6vw, 18px);
  font-weight: 400;
  line-height: 1.8;
  color: var(--muted);
  max-width: 880px;
  margin: 0 auto;
  font-family: 'CenturyGothic', sans-serif;
  letter-spacing: 0.02em;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.g-item {
  border: none;
  background: var(--card);
  border-radius: 12px;
  overflow: hidden;
  padding: 0;
  cursor: pointer;
  aspect-ratio: 4/3;
  position: relative;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s;
}

.g-item.wide {
  grid-column: span 2;
  aspect-ratio: 16/9;
}

@media (max-width: 768px) {
  .g-item.wide {
    grid-column: span 1;
    aspect-ratio: 4/3;
  }
}

.g-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.g-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.35);
}

.g-item:hover img {
  transform: scale(1.05);
}

#lightbox {
  position: fixed;
  inset: 0;
  background: rgba(8, 10, 12, 0.95);
  backdrop-filter: blur(20px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  padding: 30px;
}

#lightbox.open {
  opacity: 1;
  pointer-events: auto;
}

#lightbox img {
  max-width: 90vw;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.8);
  border: 1px solid var(--line);
}

.lb-close {
  position: absolute;
  top: 24px;
  left: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 24px;
  transition: background-color 0.2s, transform 0.2s;
}

.lb-close:hover {
  background: var(--gold);
  color: #0b0e11;
  transform: scale(1.08);
}

.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.lb-prev { right: 24px; }
.lb-next { left: 24px; }

.lb-nav:hover {
  background: var(--gold);
  color: #0b0e11;
  transform: translateY(-50%) scale(1.08);
}

.quick-calc-card {
  background: var(--card);
  border: 1px solid var(--line-gold);
  border-radius: 20px;
  padding: clamp(28px, 5vw, 44px);
  margin: 0 auto clamp(40px, 6vh, 60px);
  max-width: 860px;
  box-shadow: 0 16px 40px rgba(0,0,0,0.3), 0 0 25px var(--gold-glow);
  position: relative;
  overflow: hidden;
}

.qcalc-header {
  text-align: center;
  margin-bottom: 32px;
}

.qcalc-badge {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: var(--gold);
  background: var(--gold-bg);
  padding: 4px 16px;
  border-radius: 20px;
  margin-bottom: 12px;
  border: 1px solid var(--line);
}

.qcalc-header h3 {
  font-size: clamp(22px, 3vw, 32px);
  font-weight: 600;
  color: var(--navy);
  margin: 0 0 10px;
}

.qcalc-header p {
  font-size: 15px;
  color: var(--muted);
  margin: 0;
}

.qcalc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.qcalc-field:first-child {
  grid-column: span 2;
}

.qcalc-field label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14.5px;
  font-weight: 600;
  color: var(--navy);
  margin-bottom: 10px;
}

.qcalc-field label b {
  color: var(--gold);
  font-size: 16px;
}

.qcalc-field input[type="range"] {
  width: 100%;
  accent-color: var(--gold);
  cursor: pointer;
}

.qcalc-range-marks {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--faint);
  margin-top: 4px;
}

.qcalc-field select {
  width: 100%;
  padding: 12px 16px;
  background: var(--alt);
  color: var(--navy);
  border: 1px solid var(--line);
  border-radius: 10px;
  font-size: 15px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
  transition: border-color 0.25s;
}

.qcalc-field select:focus {
  border-color: var(--gold);
}

.qcalc-results {
  background: var(--alt);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 24px;
  align-items: center;
  margin-bottom: 28px;
}

.qres-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.qres-item span {
  font-size: 13.5px;
  color: var(--muted);
}

.qres-item b {
  font-size: clamp(26px, 3.5vw, 36px);
  color: var(--gold);
  font-family: 'CenturyGothic', 'IBM Plex Sans Arabic', sans-serif;
  line-height: 1.1;
}

.qres-item small {
  font-size: 12.5px;
  color: var(--faint);
}

.qres-breakdown {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  font-size: 13.5px;
  border-inline-start: 1px solid var(--line);
  padding-inline-start: 24px;
}

.qres-breakdown strong {
  display: block;
  color: var(--navy);
  font-size: 14px;
}

.qcalc-actions {
  text-align: center;
}

@media (max-width: 680px) {
  .qcalc-grid {
    grid-template-columns: 1fr;
  }
  .qcalc-field:first-child {
    grid-column: span 1;
  }
  .qcalc-results {
    grid-template-columns: 1fr;
  }
  .qres-breakdown {
    border-inline-start: none;
    border-top: 1px solid var(--line);
    padding-inline-start: 0;
    padding-top: 16px;
  }
}

.faq-item {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.faq-item[open] {
  border-color: var(--gold);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.faq-item summary {
  padding: 18px 24px;
  font-size: 16.5px;
  font-weight: 600;
  color: var(--navy);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  list-style: none;
  gap: 16px;
  user-select: none;
}

.faq-item summary::-webkit-details-marker {
  display: none;
}

.faq-item summary svg {
  width: 18px;
  height: 18px;
  stroke: var(--gold);
  fill: none;
  stroke-width: 2.2;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.faq-item[open] summary svg {
  transform: rotate(180deg);
}

.faq-item p {
  padding: 0 24px 20px;
  margin: 0;
  font-size: 15px;
  line-height: 1.8;
  color: var(--muted);
}

.svcs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.svc-tile {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 30px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.svc-tile:hover {
  transform: translateY(-5px);
  border-color: var(--gold);
  box-shadow: 0 12px 30px rgba(0,0,0,0.25);
}

.svc-ic {
  width: 44px;
  height: 44px;
  color: var(--gold);
  stroke: var(--gold);
  fill: none;
  stroke-width: 1.6;
  margin-bottom: 6px;
}

.svc-tile h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--navy);
  margin: 0;
}

.svc-tile span {
  font-size: 13px;
  color: var(--muted);
  font-family: 'CenturyGothic', sans-serif;
  letter-spacing: 0.03em;
}

.terms-wrap {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 80px;
}

.terms-block {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 28px;
  margin-bottom: 24px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
  transition: transform 0.25s, border-color 0.25s;
}

.terms-block:hover {
  border-color: var(--gold);
  transform: translateY(-2px);
}

.tb-logo {
  max-width: 160px;
  height: auto;
  border-radius: 8px;
  background: #ffffff;
  padding: 8px;
  flex-shrink: 0;
}

.partners-mini, .partners-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 20px;
  align-items: center;
}

.partners-mini img, .partner-card img {
  width: 100%;
  height: 80px;
  object-fit: contain;
  background: #ffffff;
  border-radius: 10px;
  padding: 12px;
  border: 1px solid var(--line);
  transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
}

.partners-mini img:hover, .partner-card img:hover {
  transform: translateY(-3px);
  border-color: var(--gold);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.cta-band {
  background: radial-gradient(circle at center, #1b232a 0%, #0c1013 100%);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: clamp(60px, 9vh, 90px) 0;
  text-align: center;
}

html[data-theme="light"] .cta-band {
  background: radial-gradient(circle at center, #f5f0e6 0%, #eae2d3 100%);
}

.cta-band .kicker {
  font-size: 14px;
  font-weight: 600;
  color: var(--gold);
  display: block;
  margin-bottom: 14px;
}

.cta-band .big {
  font-size: clamp(26px, 3.5vw, 42px);
  font-weight: 600;
  color: var(--navy);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 16px;
  transition: color 0.25s, transform 0.25s;
}

.cta-band .big:hover {
  color: var(--gold);
  transform: translateX(-4px);
}

footer {
  background: #080a0c;
  color: #94a3b8;
  padding: clamp(50px, 8vh, 80px) 0 30px;
  border-top: 1px solid var(--line);
}

html[data-theme="light"] footer {
  background: #14181c;
  color: #a0aec0;
}

.f-grid {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
}

.f-grid img {
  max-height: 55px;
  width: auto;
  object-fit: contain;
  margin-bottom: 0;
  filter: brightness(0) invert(0.85);
  transition: filter 0.3s;
}

html[data-theme="light"] .f-grid img {
  filter: none;
}

.f-links {
  border-top: 1px solid var(--line);
  padding: 24px 0 20px;
  display: flex !important;
  flex-direction: row !important;
  justify-content: center !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 12px 14px !important;
  list-style: none;
  margin: 0 auto 16px;
  max-width: 960px;
}

.f-links a {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  font-size: 14px !important;
  font-weight: 500;
  color: #D2D1D6 !important;
  background: #09507A !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 25px !important;
  padding: 8px 22px !important;
  text-decoration: none !important;
  white-space: nowrap !important;
  width: auto !important;
  box-shadow: 0 4px 14px rgba(9, 80, 122, 0.25);
  transition: transform 0.25s, background-color 0.25s, border-color 0.25s, color 0.25s, box-shadow 0.25s !important;
}

.f-links a:hover {
  transform: translateY(-2px) !important;
  background: #0E679E !important;
  border-color: #7CC5EF !important;
  color: #FFFFFF !important;
  box-shadow: 0 6px 20px rgba(14, 103, 158, 0.45) !important;
}

.f-bottom {
  border-top: 1px solid rgba(255,255,255,0.08);
  padding-top: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13.5px;
}

.f-copy {
  text-align: center;
  font-size: 13px;
  color: var(--faint);
  padding-top: 8px;
}

#waFloat {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #25d366;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(37, 211, 102, 0.4);
  z-index: 9990;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s;
}

#waFloat:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(37, 211, 102, 0.6);
}

#waFloat svg {
  width: 32px;
  height: 32px;
  fill: currentColor;
}

#toTop {
  position: fixed;
  bottom: 28px;
  left: 28px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: var(--card);
  border: 1px solid var(--line);
  color: var(--navy);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  transform: translateY(16px);
  transition: opacity 0.3s, transform 0.3s, border-color 0.25s;
  z-index: 9990;
}

#toTop.show {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}

#toTop:hover {
  border-color: var(--gold);
  color: var(--gold);
}

#toTop svg {
  width: 20px;
  height: 20px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2.2;
}

#pv-toast {
  position: fixed;
  inset-inline: 0;
  bottom: 30px;
  margin: 0 auto;
  width: max-content;
  max-width: 88vw;
  background: var(--card);
  color: var(--navy);
  border: 1px solid var(--gold);
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 14.5px;
  line-height: 1.6;
  box-shadow: 0 12px 34px rgba(0,0,0,0.5);
  opacity: 0;
  transform: translateY(16px);
  pointer-events: none;
  transition: opacity 0.3s, transform 0.3s;
  z-index: 10001;
}

#pv-toast.on {
  opacity: 1;
  transform: translateY(0);
}
"""

v4_custom_js = """
// ─── نظام الصفحات المتكامل V4 SPA Router ───
const pages = [
  'home','about','works','initiatives','contact','residential',
  'residential-classic','residential-coast','residential-abha','towers',
  'sculptures','municipal','decor','mosques','interior','landscape',
  'industrial','services','ajyal','residential-modern','calculator',
  'article-bim','commercial','other','special','terms','thamudic',
  'partners','credentials','faq','en','ajyal-guide','review'
];

let observers = [];
const pageDescs = {
  "home": "مكتب استشارات هندسية معتمد في الخبر — تصميم معماري وإنشائي وإشراف هندسي، +520 مشروعاً في المملكة.",
  "about": "تعرف على مكتب معاذ أبابطين — مسيرة نمو، معايير مهنية، ومساهمات في صياغة العمارة السعودية.",
  "services": "17 خدمة هندسية متكاملة: تصميم معماري وداخلي، إنشائي، كهروميكانيكي، تراخيص وإشراف.",
  "works": "أعمالنا الهندسية: فلل وقصور، أبراج وفنادق، مساجد، ومشاريع بالعمارة السعودية الأصيلة.",
  "ajyal": "خدمات مخطط أجيال أرامكو: نماذج معتمدة، تصاميم خاصة، وإشراف هندسي متكامل حتى رخصة البناء.",
  "calculator": "قدّر تكلفة بناء مشروعك في دقائق عبر حاسبة البناء الاسترشادية المتطورة.",
  "contact": "تواصل مع مكتب معاذ أبابطين — برج أبابطين، طريق خادم الحرمين الشريفين، الخبر.",
  "faq": "إجابات واضحة عن أكثر أسئلة العملاء حول التصميم والرخص والإشراف والتكاليف.",
  "credentials": "التراخيص والاعتمادات الرسمية للمكتب من الهيئات والوزارات السعودية وأرامكو.",
  "partners": "شركاء نجاح المكتب من الجهات الحكومية وأرامكو والشركات الكبرى.",
  "initiatives": "مبادرات المكتب في خدمة العمارة السعودية: إصدارات ومنصات رقمية تثقيفية.",
  "ajyal-guide": "دليل شامل لتصميم وبناء منزلك في حي أجيال أرامكو بالظهران.",
  "review": "مبادرة مجتمعية لمراجعة مخططاتك المعمارية مجاناً مع مهندسينا قبل التنفيذ.",
  "thamudic": "منصة محوّل الخطوط العربية القديمة الثمودية والدادانية."
};

function show(page) {
  if (page === 'why') page = 'about';
  if (!pages.includes(page)) page = 'home';
  
  document.querySelectorAll('.page').forEach(p => p.classList.remove('current'));
  const target = document.getElementById('pg-' + page);
  if (target) target.classList.add('current');
  
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.classList.toggle('active', a.dataset.page === page);
  });
  
  const titles = {
    'residential-abha': 'عمارة مرتفعات أبها وعسير',
    'sculptures': 'المجسمات والأشكال الجمالية والميادين',
    'municipal': 'مشاريع البلديات والمرافق العامة',
    'decor': 'التصميم الداخلي والديكور والتأثيث',
    'residential-coast': 'العمارة الساحلية بالخبر',
    'residential-classic': 'الطراز الكلاسيكي',
    'residential-modern': 'الطراز الحديث',
    'towers': 'الأبراج والفنادق',
    'mosques': 'عمارة المساجد',
    'interior': 'التصميم الداخلي',
    'industrial': 'المشاريع الصناعية',
    'commercial': 'المشاريع التجارية والمجمعات',
    'landscape': 'تنسيق الحدائق واللاندسكيب',
    'other': 'مشاريع هندسية أخرى',
    'special': 'مشاريع معمارية خاصة',
    'terms': 'الشروط وسياسة الاستخدام',
    'thamudic': 'منصة محوّل الخطوط العربية القديمة',
    'partners': 'شركاء النجاح',
    'credentials': 'التراخيص والاعتمادات الرسمية',
    'faq': 'الأسئلة الشائعة',
    'en': 'English Version',
    'ajyal-guide': 'دليل البناء في أجيال أرامكو',
    'review': 'مراجعة المخططات مجاناً'
  };
  
  document.title = (titles[page] ? titles[page] + ' — ' : '') + 'مكتب معاذ بن عبدالله أبابطين للاستشارات الهندسية';
  
  const md = document.querySelector('meta[name="description"]');
  if (md && pageDescs[page]) md.setAttribute('content', pageDescs[page]);
  
  window.scrollTo({ top: 0, behavior: 'instant' });
  bindReveals();
  bindCounters();
}

function route() {
  const hash = (location.hash || '#home').replace('#', '');
  show(hash);
}

addEventListener('hashchange', route);

document.addEventListener('click', e => {
  const a = e.target.closest('a[data-page]');
  if (a) {
    e.preventDefault();
    location.hash = a.dataset.page;
    document.body.classList.remove('menu-open');
  }
});

function bindReveals() {
  observers.forEach(o => o.disconnect());
  observers = [];
  const cur = document.querySelector('.page.current');
  if (!cur) return;
  
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    cur.querySelectorAll('.reveal').forEach(el => {
      io.observe(el);
      observers.push(io);
    });
  } else {
    cur.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
  }
}

function bindCounters() {
  const cur = document.querySelector('.page.current');
  if (!cur) return;
  const cio = new IntersectionObserver((entries, obs) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target;
      const t = +el.dataset.count;
      if (!t) return;
      const suf = el.textContent.startsWith('+') ? '+' : '';
      const start = performance.now();
      const dur = 1400;
      function step(now) {
        const p = Math.min((now - start) / dur, 1);
        el.textContent = suf + Math.round(t * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      cio.unobserve(el);
    });
  }, { threshold: 0.5 });
  cur.querySelectorAll('[data-count]').forEach(c => cio.observe(c));
}

(function() {
  const caps = [
    'من أعمالنا — قصر خاص · كورنيش الخبر',
    'من أعمالنا — فيلا خاصة · حي أجيال أرامكو، الظهران',
    'من أعمالنا — فيلا خاصة · حي أجيال، الظهران',
    'من أعمالنا — فيلا خاصة · حي الفيصلية، الدمام',
    'من أعمالنا — فندق · مكة المكرمة',
    'من أعمالنا — فيلا خاصة · مدينة الظهران'
  ];
  const wrap = document.getElementById('heroSlides');
  if (!wrap) return;
  const slides = [...wrap.querySelectorAll('.slide')];
  const dots = document.getElementById('slideDots');
  const cap = document.getElementById('slideCap');
  
  if (dots) {
    dots.innerHTML = '';
    slides.forEach((_, i) => {
      const b = document.createElement('button');
      b.setAttribute('aria-label', 'شريحة ' + (i + 1));
      if (i === 0) b.classList.add('on');
      b.onclick = () => go(i, true);
      dots.appendChild(b);
    });
  }
  
  let cur = 0, timer;
  function go(i, manual) {
    slides[cur].classList.remove('on');
    if (dots && dots.children[cur]) dots.children[cur].classList.remove('on');
    cur = (i + slides.length) % slides.length;
    slides[cur].classList.add('on');
    if (dots && dots.children[cur]) dots.children[cur].classList.add('on');
    if (cap && caps[cur]) cap.textContent = caps[cur];
    if (manual) {
      clearInterval(timer);
      start();
    }
  }
  
  function start() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    timer = setInterval(() => go(cur + 1), 5500);
  }
  start();
})();

(function() {
  const strip = document.getElementById('homeWorksStrip');
  if (!strip) return;
  strip.innerHTML = '';
  document.querySelectorAll('#pg-works .works-list a.fig').forEach(c => {
    const n = c.cloneNode(true);
    n.classList.remove('reveal', 'd1', 'd2', 'd3', 'wide7');
    strip.appendChild(n);
  });
})();

let lbImgs = [], lbAlts = [], lbIdx = 0;

document.addEventListener('click', e => {
  const it = e.target.closest('.g-item');
  if (it) {
    const items = [...it.closest('.gallery').querySelectorAll('.g-item img')];
    lbImgs = items.map(i => i.src);
    lbAlts = items.map(i => i.alt || '');
    lbIdx = +it.dataset.lb || 0;
    openLb();
    return;
  }
  
  const c = e.target.closest('.cover');
  if (c) {
    const al = document.getElementById('al-' + c.dataset.album);
    if (!al) return;
    lbImgs = [...al.querySelectorAll('img')].map(i => i.src);
    lbAlts = [...al.querySelectorAll('img')].map(i => i.alt || '');
    lbIdx = 0;
    openLb();
  }
});

function openLb() {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lbImg');
  if (!lb || !img || !lbImgs.length) return;
  img.src = lbImgs[lbIdx];
  img.alt = lbAlts[lbIdx] || '';
  lb.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function lbClose() {
  const lb = document.getElementById('lightbox');
  if (lb) lb.classList.remove('open');
  document.body.style.overflow = '';
}

function lbNav(d) {
  if (!lbImgs.length) return;
  lbIdx = (lbIdx + d + lbImgs.length) % lbImgs.length;
  const im = document.getElementById('lbImg');
  if (im) {
    im.src = lbImgs[lbIdx];
    im.alt = lbAlts[lbIdx] || '';
  }
}

document.addEventListener('click', e => {
  if (e.target.id === 'lightbox' || e.target.closest('.lb-close')) {
    lbClose();
  }
  if (e.target.closest('.lb-next')) lbNav(1);
  if (e.target.closest('.lb-prev')) lbNav(-1);
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.body.classList.remove('menu-open');
    lbClose();
  }
  const lb = document.getElementById('lightbox');
  if (lb && lb.classList.contains('open')) {
    if (e.key === 'ArrowLeft') lbNav(1);
    if (e.key === 'ArrowRight') lbNav(-1);
  }
});

document.addEventListener('click', e => {
  const b = e.target.closest('.ajtabs button');
  if (!b) return;
  b.parentElement.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
  document.querySelectorAll('.ajpanel').forEach(p => p.classList.toggle('on', p.id === 'aj-' + b.dataset.aj));
  bindReveals();
});

(function() {
  const boxes = document.querySelectorAll('.cbox');
  boxes.forEach(b => b.addEventListener('click', () => {
    const p = document.getElementById(b.dataset.target);
    if (!p) return;
    const willOpen = p.hidden;
    document.querySelectorAll('.cpanel').forEach(x => x.hidden = true);
    boxes.forEach(x => x.classList.remove('active'));
    if (willOpen) {
      p.hidden = false;
      b.classList.add('active');
      p.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }));
})();

(function() {
  const f = document.getElementById('quoteForm');
  if (!f) return;
  let via = 'wa';
  f.querySelectorAll('.qbtn').forEach(b => b.addEventListener('click', () => { via = b.dataset.via; }));
  
  const qV = document.getElementById('qVilla'), qO = document.getElementById('qOther');
  f.querySelectorAll('#qType input').forEach(r => r.addEventListener('change', () => {
    const checked = f.querySelector('#qType input:checked');
    const villa = checked && checked.value === 'فيلا';
    if (qV) qV.hidden = !villa;
    if (qO) qO.hidden = villa;
  }));
  
  f.addEventListener('submit', e => {
    e.preventDefault();
    const L = [];
    const checkedType = f.querySelector('#qType input:checked');
    const qtype = checkedType ? checkedType.value : 'مشروع معماري';
    L.push('طلب تسعيرة تصميم — من موقع مكتب معاذ أبابطين V4');
    L.push('نوع المشروع: ' + qtype);
    
    f.querySelectorAll('.qgrid input, .qgrid select').forEach(i => {
      if (i.value && !i.closest('[hidden]')) L.push(i.name + ': ' + i.value);
    });
    
    f.querySelectorAll('.qgroup').forEach(g => {
      if (g.closest('[hidden]')) return;
      const bEl = g.querySelector('b');
      const t = bEl ? bEl.textContent : 'خدمات مطلوبة';
      const c = [...g.querySelectorAll('.qchecks input:checked')].map(i => i.value);
      if (c.length && !g.querySelector('#qType')) L.push(t + ': ' + c.join('، '));
    });
    
    f.querySelectorAll('textarea').forEach(ta => {
      const v = ta.value.trim();
      if (v && !ta.closest('[hidden]')) L.push(ta.name + ': ' + v);
    });
    
    const msg = L.join('\\n');
    if (via === 'mail') {
      location.href = 'mailto:info@ababtain-eng.com?subject=' + encodeURIComponent('طلب تسعيرة تصميم') + '&body=' + encodeURIComponent(msg);
    } else {
      window.open('https://wa.me/966505611000?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    }
  });
})();

(function() {
  const qcArea = document.getElementById('qcArea');
  const qcAreaVal = document.getElementById('qcAreaVal');
  const qcType = document.getElementById('qcType');
  const qcFinish = document.getElementById('qcFinish');
  
  const qcTotal = document.getElementById('qcTotalCost');
  const qcCostPerM = document.getElementById('qcCostPerM');
  const qcBone = document.getElementById('qcBoneCost');
  const qcFinishCost = document.getElementById('qcFinishCost');
  const qcMech = document.getElementById('qcMechCost');
  const qcSite = document.getElementById('qcSiteCost');
  const qcShareWa = document.getElementById('qcShareWa');
  
  if (!qcArea) return;
  
  const finishRates = {
    bone: 950,
    standard: 1400,
    lux: 1800,
    super: 2400
  };
  
  const typeMultipliers = {
    villa: 1.0,
    duplex: 0.95,
    building: 0.9,
    commercial: 1.15
  };
  
  function updateCalc() {
    const area = +qcArea.value;
    qcAreaVal.textContent = area.toLocaleString('ar-SA') + ' م²';
    
    const baseRate = finishRates[qcFinish.value] || 1800;
    const mult = typeMultipliers[qcType.value] || 1.0;
    const ratePerM = Math.round(baseRate * mult);
    
    const total = area * ratePerM;
    const bone = Math.round(total * 0.45);
    const finishing = Math.round(total * 0.35);
    const mech = Math.round(total * 0.12);
    const site = Math.round(total * 0.08);
    
    qcTotal.textContent = total.toLocaleString('ar-SA') + ' ر.س';
    qcCostPerM.textContent = 'بمتوسط ' + ratePerM.toLocaleString('ar-SA') + ' ر.س / م²';
    qcBone.textContent = bone.toLocaleString('ar-SA') + ' ر.س';
    qcFinishCost.textContent = finishing.toLocaleString('ar-SA') + ' ر.س';
    qcMech.textContent = mech.toLocaleString('ar-SA') + ' ر.س';
    qcSite.textContent = site.toLocaleString('ar-SA') + ' ر.س';
  }
  
  qcArea.addEventListener('input', updateCalc);
  qcType.addEventListener('change', updateCalc);
  qcFinish.addEventListener('change', updateCalc);
  updateCalc();
  
  if (qcShareWa) {
    qcShareWa.addEventListener('click', () => {
      const area = qcArea.value;
      const typeText = qcType.options[qcType.selectedIndex].text;
      const finishText = qcFinish.options[qcFinish.selectedIndex].text;
      const totalText = qcTotal.textContent;
      
      const msg = [
        'السلام عليكم ورحمة الله وبركاته،',
        'أرغب في الحصول على استشارة هندسية وتسعيرة دقيقة لبناء مشروعي وفق معطيات حاسبة البناء:',
        '• نوع المشروع: ' + typeText,
        '• مسطح البناء الإجمالي: ' + area + ' م²',
        '• مستوى التشطيب: ' + finishText,
        '• التكلفة التقديرية بالحاسبة: ' + totalText,
        'نأمل التواصل معي لبدء الخطوة التالية.'
      ].join('\\n');
      
      window.open('https://wa.me/966505611000?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    });
  }
})();

(function() {
  const bar = document.getElementById('readProgress');
  const tt = document.getElementById('toTop');
  
  addEventListener('scroll', () => {
    const h = document.documentElement;
    const p = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
    if (bar) bar.style.width = (p * 100) + '%';
    if (tt) tt.classList.toggle('show', scrollY > 500);
  }, { passive: true });
  
  if (tt) {
    tt.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();

(function() {
  const btn = document.getElementById('themeToggle');
  if (!btn) return;
  let saved = null;
  try { saved = localStorage.getItem('ababtain_v4_theme'); } catch(e) {}
  if (saved === 'light') document.documentElement.setAttribute('data-theme', 'light');
  
  btn.addEventListener('click', () => {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    if (isLight) {
      document.documentElement.removeAttribute('data-theme');
      try { localStorage.setItem('ababtain_v4_theme', 'dark'); } catch(e) {}
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
      try { localStorage.setItem('ababtain_v4_theme', 'light'); } catch(e) {}
    }
  });
})();

document.addEventListener('click', function(e) {
  const a = e.target.closest('[data-nopdf]');
  if (!a) return;
  e.preventDefault();
  const t = document.getElementById('pv-toast');
  if (!t) return;
  t.textContent = 'ملف الـPDF غير مرفق في نسخة المعاينة — متاح في الملف الأصلي الكامل.';
  t.classList.add('on');
  clearTimeout(window.__pvt);
  window.__pvt = setTimeout(() => { t.classList.remove('on'); }, 3200);
}, true);

route();
"""

v4_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
{meta_str}
<title>مكتب معاذ بن عبدالله أبابطين للاستشارات الهندسية | مكتب هندسي في الخبر</title>
{link_str}
{ld_json_str}
<style id="ababtain-fonts">
{font_css}
</style>
<style id="ababtain-original-base">
{clean_orig_style0}
{orig_style1}
</style>
<style id="ababtain-v4-luxury">
{v4_custom_css}
</style>
</head>
<body>
<a class="skip-link" href="#main-content">تجاوز إلى المحتوى</a>
<div id="readProgress" aria-hidden="true"></div>
{wafloat_str}
{header_str}

<main id="main-content" tabindex="-1">
{all_sections_str}
</main>

{footer_str}
{totop_str}
{lightbox_str}
{toast_str}

<script>
{v4_custom_js}
</script>
</body>
</html>
"""

print(f"Writing {target_path}...")
with open(target_path, "w", encoding="utf-8") as f:
    f.write(v4_html)

print("Build complete!")
