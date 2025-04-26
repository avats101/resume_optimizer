import json
import copy
def extract_relevant_json(full_resume: dict):
    extracted = {
        "$schema": full_resume.get("$schema", ""),
        "basics": {
            "summary": full_resume.get("basics", {}).get("summary", "")
        },
        "work": [],
        "skills": [],
        "projects": []
    }

    # Extract work highlights
    for work_item in full_resume.get("work", []):
        highlights = work_item.get("highlights", [])
        if highlights:
            extracted["work"].append({
                "highlights": highlights
            })

    # Extract skills (name and keywords only)
    for skill_item in full_resume.get("skills", []):
        name = skill_item.get("name", "")
        keywords = skill_item.get("keywords", [])
        if name or keywords:
            extracted["skills"].append({
                "name": name,
                "keywords": keywords
            })

    # Extract projects (name and highlights only)
    for project_item in full_resume.get("projects", []):
        name = project_item.get("name", "")
        highlights = project_item.get("highlights", [])
        if name or highlights:
            extracted["projects"].append({
                "name": name,
                "highlights": highlights
            })
    with open('resume-prompt.json', 'w') as f:
        json.dump(extracted, f, indent=2) 
 
    


def update_relevant_json(prompt_path,resume_path):
    try:
        # Load both files
        with open(resume_path, 'r') as f:
            resume_data = json.load(f)

        with open(prompt_path, 'r') as f:
            prompt_data = json.load(f)

        updated_resume = copy.deepcopy(resume_data)  # Make a copy so original remains safe

        # Update basics.summary
        summary = prompt_data.get("basics", {}).get("summary")
        if summary:
            updated_resume.setdefault("basics", {})["summary"] = summary

        # Update work highlights
        work_prompts = prompt_data.get("work", [])
        for i, work_update in enumerate(work_prompts):
            if "highlights" in work_update and i < len(updated_resume.get("work", [])):
                updated_resume["work"][i]["highlights"] = work_update["highlights"]

        # Update skills
        updated_resume["skills"] = prompt_data.get("skills", updated_resume.get("skills", []))

        # Update projects
        project_prompts = prompt_data.get("projects", [])
        for i, project_update in enumerate(project_prompts):
            if i < len(updated_resume.get("projects", [])):
                updated_resume["projects"][i]["highlights"] = project_update.get("highlights", [])
                if "name" in project_update:
                    updated_resume["projects"][i]["name"] = project_update["name"]

        return updated_resume

    except Exception as e:
        print(f"Error updating JSON: {e}")
        return resume_data

if __name__ == '__main__':
    # Example usage
    resume_path = 'data/Richard Hendricks.json'
    prompt_path = 'data/optimized_resume.json'
    print("Updating resume...")
    updated_json=update_relevant_json(prompt_path, resume_path)
    print(json.dumps(updated_json, indent=2))
    print("Updated resume successfully.")