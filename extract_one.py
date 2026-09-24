import json
import re
import html as html_module
from bs4 import BeautifulSoup

def extract_lab_page(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Title
    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].split("|")[0].strip()
    if not title:
        header = soup.find("div", class_="page-header") or soup.find("div", class_="page-main-banner")
        if header:
            h1 = header.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            else:
                title = header.get_text(" ", strip=True)
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

    # 2. Lab Code (Lab focus pages only)
    lab_code = ""
    step1_h2 = soup.find("h2", id="step1")
    if step1_h2:
        lab_code = step1_h2.get_text(strip=True)

    # 3. Description (Meta tag description)
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
    if meta_desc and meta_desc.get("content"):
        raw_desc = html_module.unescape(meta_desc["content"].strip())
        # Strip residual HTML tags if any
        description = re.sub(r'<[^>]+>', '', raw_desc).strip()

    # 4. Duration details
    duration_details = ""
    # Method A: Lab focus page (p.small-label)
    for p in soup.find_all("p", class_="small-label"):
        text = p.get_text(" ", strip=True)
        if "Duration:" in text:
            raw = text.replace("Duration:", "").strip()
            cleaned = re.sub(r'[^\x00-\x7F]+', ' / ', raw)
            duration_details = re.sub(r'\s+', ' ', cleaned).strip()

    # Method B: Course template page (div.course-details > span.course-detail)
    if not duration_details:
        course_details = soup.find("div", class_="course-details")
        if course_details:
            spans = course_details.find_all("span", class_="course-detail")
            for span in spans:
                stext = span.get_text(strip=True)
                if any(time_unit in stext.lower() for time_unit in ["minute", "hour", "day", "min", "hr"]):
                    duration_details = stext

    # 5. Level
    level = ""
    # Method A: Lab focus page
    for p in soup.find_all("p", class_="small-label"):
        text = p.get_text(" ", strip=True)
        if "Levels:" in text:
            level = text.replace("Levels:", "").strip()

    # Method B: Course template page
    if not level:
        course_details = soup.find("div", class_="course-details")
        if course_details:
            spans = course_details.find_all("span", class_="course-detail")
            for span in spans:
                stext = span.get_text(strip=True)
                if stext.lower() in ["introductory", "intermediate", "advanced", "fundamental", "all levels"]:
                    level = stext

    # 6. Permalink
    permalink = ""
    for p in soup.find_all("p", class_="small-label"):
        text = p.get_text(" ", strip=True)
        if "Permalink:" in text:
            permalink = text.replace("Permalink:", "").strip()
    if not permalink:
        og_url = soup.find("meta", property="og:url")
        if og_url and og_url.get("content"):
            permalink = og_url["content"].strip()

    # Helper function to extract section text content preserving code blocks & structure
    def extract_section_content(start_h2, stop_h_names=["h1", "h2"]):
        content_parts = []
        curr = start_h2.next_sibling
        while curr:
            name = getattr(curr, 'name', None)
            if name in stop_h_names:
                break
            if name:
                if name in ["ql-code-block", "pre", "code"] or curr.find(["ql-code-block", "pre"]):
                    code_text = curr.get_text().strip()
                    lang = curr.get("language", "")
                    content_parts.append(f"```{lang}\n{code_text}\n```")
                elif name == "ql-activity-tracking":
                    tracking_text = curr.get_text(" ", strip=True)
                    if tracking_text:
                        content_parts.append(f"[Activity Tracking: {tracking_text}]")
                else:
                    text = curr.get_text(" ", strip=True)
                    if text:
                        content_parts.append(text)
            curr = curr.next_sibling
        return "\n\n".join(content_parts)

    instructions = soup.find("div", class_="markdown-lab-instructions")
    
    # 7. Overview
    overview = ""
    if instructions:
        overview_h2 = instructions.find(lambda el: el.name == "h2" and el.get_text(strip=True).lower() == "overview")
        if overview_h2:
            overview = extract_section_content(overview_h2)

    if not overview:
        course_desc = soup.find("div", class_="course-description") or soup.find("div", class_="course-description-section")
        if course_desc:
            raw_text = course_desc.get_text(" ", strip=True)
            overview = re.sub(r'\s+', ' ', raw_text)

    # 8. Objectives
    objectives = ""
    if instructions:
        obj_h2 = instructions.find(lambda el: el.name == "h2" and el.get_text(strip=True).lower() == "objectives")
        if obj_h2:
            objectives = extract_section_content(obj_h2)

    # 9. Tasks / Activities
    tasks = []
    if instructions:
        task_h2s = instructions.find_all(lambda el: el.name == "h2" and el.get_text(strip=True).startswith("Task "))
        for th2 in task_h2s:
            task_title = th2.get_text(strip=True)
            task_content = extract_section_content(th2)
            tasks.append({
                "title": task_title,
                "content": task_content
            })

    # If course_templates page with ql-contents-menu modules attribute
    contents_menu = soup.find("ql-contents-menu")
    if contents_menu and contents_menu.get("modules"):
        try:
            modules_data = json.loads(contents_menu["modules"])
            for mod in modules_data:
                for step in mod.get("steps", []):
                    for act in step.get("activities", []):
                        act_title = act.get("title", "")
                        act_desc = act.get("description") or ""
                        act_type = act.get("type") or ""
                        if act_title:
                            tasks.append({
                                "title": f"[{act_type.upper()}] {act_title}",
                                "content": act_desc
                            })
        except Exception as e:
            pass

    # 10. Checkpoints
    checkpoints = []
    assessment_panel = soup.find("div", class_=lambda c: c and "lab-assessment__panel" in c)
    if assessment_panel:
        steps = assessment_panel.find_all("div", class_="lab-assessment__step")
        for step in steps:
            title_p = step.find("p", class_="lab-assessment__step__title")
            score_p = step.find("p", class_="lab-assessment__step__score")
            
            cp_title = title_p.get_text(strip=True) if title_p else ""
            cp_score = None
            if score_p:
                score_text = score_p.get_text(strip=True)
                match = re.search(r'/\s*(\d+)', score_text)
                if match:
                    cp_score = int(match.group(1))
            
            if cp_title:
                checkpoints.append({
                    "title": cp_title,
                    "score": cp_score
                })

    return {
        "title": title,
        "lab_code": lab_code,
        "description": description,
        "duration_details": duration_details,
        "level": level,
        "permalink": permalink,
        "overview": overview,
        "objectives": objectives,
        "tasks": tasks,
        "checkpoints": checkpoints
    }

if __name__ == "__main__":
    html_file = r"c:\Users\acer\Desktop\credBase\scratch_page_2.html"
    with open(html_file, "r", encoding="utf-8") as f:
        raw_html_str = f.read()
    
    data = extract_lab_page(raw_html_str)
    
    out_file = r"c:\Users\acer\Desktop\credBase\test_extracted_2.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("=== UPDATED EXTRACTED DATA FOR SECOND PAGE (test_extracted_2.json) ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
