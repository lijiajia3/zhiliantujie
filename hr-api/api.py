from http.client import HTTPException
from fastapi import FastAPI, UploadFile, File, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from openai import OpenAI
import os
from datetime import datetime
import hashlib
import time
import random
import json
import re
from datetime import datetime
from fastapi import HTTPException as FastAPIHTTPException
import joblib  
import tempfile
import requests
import docx2txt
import pdfplumber
import pandas as pd
def get_employee_db():
    if not os.path.exists("employees.json"):
        with open("employees.json", "w", encoding="utf-8") as f:
            f.write("[]")
    with open("employees.json", "r", encoding="utf-8") as f:
        return json.load(f)
client = OpenAI(
    api_key="sk-991bf91a56e34be9b3aabd01d87ef748",
    base_url="https://api.deepseek.com"
)

import json, os
def get_recommend_db():
    if not os.path.exists("recommend.json"):
        with open("recommend.json", "w", encoding="utf-8") as f:
            f.write("[]")
    with open("recommend.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_recommend_db(data):
    with open("recommend.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_json_db(path: str):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_db(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_resume_id():
    now = datetime.now()
    prefix = now.strftime("%Y%m")
    db = get_json_db("talent_pool.json")
    count = sum(1 for item in db if item.get("resume_id", "").startswith(prefix))
    return f"{prefix}-{count + 1:02d}"
def generate_id():
    import uuid
    return str(uuid.uuid4())
app = FastAPI()
APP_KEY = "0dae68817e8cfd3bdd2d2cc900c1bee0"
APP_SECRET = "29d8935b8b6a"
NONCE = "123456"
sms_code_cache = {}

def send_sms_code(phone):
    code = str(random.randint(100000, 999999))
    cur_time = str(int(time.time()))
    checksum = hashlib.sha1((APP_SECRET + NONCE + cur_time).encode('utf-8')).hexdigest()

    headers = {
        "AppKey": APP_KEY,
        "Nonce": NONCE,
        "CurTime": cur_time,
        "CheckSum": checksum,
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    data = {
        "mobile": phone,
        "codeLen": "6"
    }

    response = requests.post(
        "https://api.netease.im/sms/sendcode.action",
        headers=headers,
        data=data
    )

    sms_code_cache[phone] = code
    return response.json(), code
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

MODEL_PATH = "model.pkl"
model = joblib.load(MODEL_PATH)
MODEL2_PATH = "model2.pkl"
model2 = joblib.load(MODEL2_PATH)

def append_to_history(record):
    history_path = "recommend_history.json"
    if not os.path.exists(history_path):
        with open(history_path, "w", encoding="utf-8") as f:
            f.write("[]")
    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)
    history.append(record)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
def extract_text(file: UploadFile) -> str:
    suffix = file.filename.lower()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    if suffix.endswith(".pdf"):
        with pdfplumber.open(tmp_path) as pdf:
            text = "\n".join([page.extract_text() or '' for page in pdf.pages])
    elif suffix.endswith(".docx"):
        text = docx2txt.process(tmp_path)
    else:
        raise ValueError("Unsupported file type")

    return text.strip()

def generate_resume_id(source_flag="0"):
    now = datetime.now()
    prefix = now.strftime("%Y%m%d")
    max_index = 0
 
    for db_file in ["recommend.json", "recommend_history.json", "batch_resume_summary.json", "batch_resume_features.json"]:
        if os.path.exists(db_file):
            try:
                with open(db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for d in data:
                        rid = d.get("resume_id", "")
                        if isinstance(rid, str) and rid.startswith(prefix):
                            parts = rid.split("-")
                            if len(parts) >= 2 and parts[1].isdigit():
                                max_index = max(max_index, int(parts[1]))
            except:
                continue
 
    return f"{prefix}-{max_index + 1:02d}-{source_flag}"

def extract_structured_features(resume_text: str) -> dict:
    features = {}
 
    
    if '博士' in resume_text:
        features['学历_x'] = 5
    elif '硕士' in resume_text:
        features['学历_x'] = 4
    elif '本科' in resume_text:
        features['学历_x'] = 3
    elif '大专' in resume_text or '专科' in resume_text:
        features['学历_x'] = 2
    else:
        features['学历_x'] = 1
 
    
    match = re.search(r'(\d{1,2})年.*?(经验|工作)', resume_text)
    features['经验_x'] = int(match.group(1)) if match else 0
 
    
    skill_keywords = ['Python', 'Excel', 'SQL', 'C++', 'Java', 'Linux', '数据', '分析', '开发']
    features['技能数_x'] = sum(1 for kw in skill_keywords if kw.lower() in resume_text.lower())
 
    
    cert_keywords = ['四级', '六级', '技工', '资格', '认证', '证书', '职称']
    features['证书数_x'] = sum(1 for kw in cert_keywords if kw in resume_text)
 
    return features
def get_employee_db():
    if not os.path.exists("employees.json"):
        with open("employees.json", "w", encoding="utf-8") as f:
            f.write("[]")
    with open("employees.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_employee_db(db):
    with open("employees.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user_db():
    if not os.path.exists("users.json"):
        default_users = {
            "users": [
                {
                    "id": 1,
                    "username": "hr_user",
                    "password": "password123",
                    "role": "hr",
                    "email": "hr@example.com"
                },
                {
                    "id": 2,
                    "username": "leader_user",
                    "password": "password123",
                    "role": "leader",
                    "email": "leader@example.com"
                },
                {
                    "id": 3,
                    "username": "admin_user",
                    "password": "password123",
                    "role": "admin",
                    "email": "admin@example.com"
                }
            ]
        }
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_db(data):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def ensure_all_features(features: dict) -> dict:
    all_fields = ['学历_x', '经验_x', '技能数_x', '证书数_x', '年龄_x', '项目经验_x', '自我评分_x']
    for field in all_fields:
        if field not in features:
            features[field] = 0
    return features


def generate_gpt_report(resume_text: str, score: int) -> str:
    prompt = f"""
请根据以下简历内容和模型评分撰写简要的分析报告，内容包括：优点、缺点、改进建议。

评分：{score}
简历内容如下：
{resume_text}
"""
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "你是一位人力资源分析师，请根据以下简历内容和模型评分撰写分析报告"},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content

def extract_recommended_position(text: str) -> str:
    pattern = r"(?:适合的?岗位(?:类型)?|岗位类型)[：:\s]*([^\n。；]*)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return "暂无明确岗位推荐"
@app.post("/api/recommend")
async def hr_recommend(data: dict):
    print("🟡 接收到推荐数据：", data)
    db = get_recommend_db()
    resume_id = data.get("resume_id")
    if not resume_id:
        resume_id = generate_resume_id()
    record = {
        "id": resume_id,
        "resume_id": resume_id,
        "recommend_reason": data.get("recommend_reason", ""),
        "status": data.get("status", "待审批"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    import shutil
    upload_dir = "uploads/talent_pool"
    os.makedirs(upload_dir, exist_ok=True)
    resume_file_path = os.path.join(upload_dir, f"{resume_id}.pdf")
    uploaded_path = data.get("file_path")

    if uploaded_path and os.path.exists(uploaded_path):
        shutil.copy(uploaded_path, resume_file_path)
        record["pdf_path"] = resume_file_path
    elif "pdf_base64" in data:
        import base64
        decoded = base64.b64decode(data["pdf_base64"])
        with open(resume_file_path, "wb") as f:
            f.write(decoded)
        record["pdf_path"] = resume_file_path
    else:
        record["pdf_path"] = "无"

    details = get_json_db("batch_resume_details.json")
    target = next((item for item in details if item.get("resume_id") == resume_id), None)

    if target:
        target["analysis"] = "待生成"
        save_json_db("batch_resume_details.json", details)
        record["name"] = target.get("name", "未知")
        record["score"] = target.get("score", 0)

    record["analysis"] = "待生成"
    pool = get_json_db("talent_pool.json")
    pool.append(record)
    save_json_db("talent_pool.json", pool)
    print("✅ 已保存推荐记录：", record)
    return {"message": "推荐成功", "data": record}

@app.patch("/api/recommend/{recommend_id}")
def update_recommend_status(recommend_id: str, payload: dict):
    db = get_recommend_db()
    item = next((i for i in db if i["id"] == recommend_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="推荐记录未找到")

    item["status"] = payload.get("status", item["status"])

    
    history = get_json_db("recommend_history.json")
    history.append(item)
    save_json_db("recommend_history.json", history)

    
    db = [i for i in db if i["id"] != recommend_id]
    save_recommend_db(db)

    
    if item["status"] == "已录用":
        employees = get_json_db("employees.json")
        employees.append(item)
        save_json_db("employees.json", employees)
    elif item["status"] == "不通过":
        pool = get_json_db("talent_pool.json")
        pool.append(item)
        save_json_db("talent_pool.json", pool)

    return {"message": "状态已更新", "status": item["status"]}
@app.get("/api/recommend")
async def get_recommend_list(status: str = "全部"):
    db = get_recommend_db()
    if status == "全部":
        return {"data": db}
    return {"data": [item for item in db if item.get("status") == status]}
@app.post("/api/recommend/approve")
async def leader_approve(data: dict):
    db = get_recommend_db()
    for item in db:
        if item["id"] == data["id"]:
            item["status"] = data["decision"]  
            break
    save_recommend_db(db)
    return {"message": "已处理"}

@app.post("/api/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        resume_text = extract_text(file)
        print("✅ 简历内容片段：", resume_text[:200])

        features = extract_structured_features(resume_text)
        print("✅ 提取的特征：", features)

        

        
        features = ensure_all_features(features)
        print("✅ 补全后的特征：", features)

        X_input = pd.DataFrame([{
            "学历_x": features["学历_x"],
            "经验_x": features["经验_x"],
            "技能数_x": features["技能数_x"],
            "证书数_x": features["证书数_x"],
            "年龄_x": features["年龄_x"],
            "项目经验_x": features["项目经验_x"],
            "自我评分_x": features["自我评分_x"]
        }])
        score_raw = model.predict(X_input)[0]
        score = float(score_raw)
        if score <= 1 and model.__class__.__name__ == "RandomForestRegressor":
            score = score * 100  
        elif score <= 5:
            score = score / 5 * 100 
        print("✅ 规范化百分制评分：", score)

        
        analysis = generate_gpt_report(resume_text, score)
        print("✅ LLM 分析报告：", analysis)

        recommended = extract_recommended_position(analysis)

        analysis = str(analysis)
        analysis = re.sub(r"[]+", "", analysis)
        resume_id = generate_resume_id()

        result = {
            "score": int(score),
            "recommended_position": recommended,
            "analysis": analysis,
            "score_breakdown": {
                "学历_x": features["学历_x"],
                "经验_x": features["经验_x"],
                "技能数_x": features["技能数_x"],
                "证书数_x": features["证书数_x"],
                "年龄_x": features["年龄_x"],
                "项目经验_x": features["项目经验_x"],
                "自我评分_x": features["自我评分_x"]
            },
            "resume_id": resume_id,
            "name": file.filename.replace(".pdf", "").replace(".docx", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        db = get_json_db("batch_resume_details.json")
        db.append(result)
        save_json_db("batch_resume_details.json", db)
        return result

    except Exception as e:
        print("❌ 出错了：", e)
        return {"error": str(e)}

@app.get("/api/employees")
async def get_employees():
    raw = get_employee_db()
    formatted = [
        {
            "id": item.get("工号") or item.get("id"),
            "name": item.get("姓名") or item.get("name"),
            "position": item.get("职位AL") or item.get("position"),
            "experience": item.get("工龄") or item.get("experience"),
            "status": item.get("状态") or item.get("status", "在职"),
            "note": item.get("个人简历O") or item.get("note", "")
        }
        for item in raw
    ]
    return {"data": formatted}

@app.get("/api/leader/employees")
async def get_leader_employees(request: Request):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    
    team_path = "leader_team_members.json"
    if os.path.exists(team_path):
        with open(team_path, "r", encoding="utf-8") as f:
            all_teams = json.load(f)
        return all_teams.get(username, [])
    return []

@app.post("/api/leader/add-by-id")
async def add_employee_by_id(data: dict, request: Request):
    employee_id = data.get("id")
    if not employee_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少工号")
    
    username = request.cookies.get("current_user")
    if not username:
         raise FastAPIHTTPException(status_code=401, detail="未登录")

    db = get_employee_db()
    matched = next((e for e in db if str(e.get("id") or e.get("工号")) == str(employee_id)), None)
    if not matched:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应员工")

    
    team_path = "leader_team_members.json"
    if os.path.exists(team_path):
        with open(team_path, "r", encoding="utf-8") as f:
            all_teams = json.load(f)
    else:
        all_teams = {}

    team = all_teams.get(username, [])

    
    if not any(str(e.get("id") or e.get("工号")) == str(employee_id) for e in team):
        team.append(matched)
        all_teams[username] = team
        with open(team_path, "w", encoding="utf-8") as f:
            json.dump(all_teams, f, ensure_ascii=False, indent=2)

    return matched

@app.post("/api/employees")
async def add_employees(request: Request, employees: list[dict] = Body(...)):
    print("🟡 接收到员工数据：", employees)
    username = request.cookies.get("current_user")
    if not username:
         raise FastAPIHTTPException(status_code=401, detail="未登录")

    if not isinstance(employees, list) or len(employees) == 0:
        raise FastAPIHTTPException(status_code=400, detail="员工数据为空或格式错误")

    
    for employee in employees:
        if not employee.get("name"):
            source_id = employee.get("source_resume_id")
            if source_id:
                details = get_json_db("batch_resume_details.json")
                rec = next((r for r in details if r.get("resume_id") == source_id), None)
                if rec and rec.get("name"):
                    employee["name"] = rec["name"]
            if not employee.get("name"):
                employee["name"] = f"员工{employee['id']}"
        if "leader" not in employee or not employee["leader"]:
            employee["leader"] = username

    for employee in employees:
        if not employee.get("id") or employee.get("id") == "null":
            raise FastAPIHTTPException(status_code=400, detail="某个员工缺少工号")
    db = get_employee_db()
    db.extend(employees)
    save_employee_db(db)
    print("✅ 已保存员工数据，共计：", len(employees))
    return {"message": "员工数据已保存", "count": len(employees)}

@app.post("/api/chart-data")
async def chart_data(file: UploadFile = File(...)):
    print("✅ 收到 chart-data 请求")
    try:
        resume_text = extract_text(file)
        
        
        llm_dimension_prompt = f"""
        请根据以下简历内容，从“学历背景”“工作经验”“技能匹配度”“证书资质”“岗位适配度”五个维度分别打分（1~10分）并返回 JSON 结果，例如：{"学历背景": 8, "工作经验": 7, "技能匹配度": 9, "证书资质": 6, "岗位适配度": 8}
        
        简历内容如下：
        {resume_text}
        """

        try:
            llm_score_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位经验丰富的企业人力资源助手"},
                    {"role": "user", "content": llm_dimension_prompt}
                ],
                stream=False
            )
            print("✅ LLM 返回内容：", llm_score_response.choices[0].message.content)
        except Exception as e:
            print("❌ LLM 请求失败：", e)
            llm_score_response = None

        try:
            llm_content = llm_score_response.choices[0].message.content if llm_score_response else ""
            print("📦 LLM 原始 JSON 响应：", repr(llm_content))
            llm_content = re.sub(r"```json|```", "", llm_content).strip()
            scores_json = json.loads(llm_content) if llm_content else {}
        except Exception:
            scores_json = {}

        radar_data = [
            {"维度": key, "得分": value}
            for key, value in scores_json.items()
            if isinstance(value, (int, float))
        ]
        if radar_data:
            avg_score = sum([d["得分"] for d in radar_data]) / len(radar_data)
            normalized_score = int(avg_score * 10)  
        else:
            normalized_score = 0

        chart_payload = {
            "score": normalized_score,
            "radar_data": radar_data
        }
        return chart_payload
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    identifier = data.get("identifier")
    password = data.get("password")

    users = get_user_db()["users"]
    user = next(
        (u for u in users if (
            u.get("username") == identifier or
            u.get("email") == identifier or
            u.get("phone") == identifier
        ) and u.get("password") == password),
        None
    )
    print(f"✅ 正在尝试登录：{identifier} / {password}")
    print(f"📦 当前用户列表：{[u.get('username') for u in users]}")

    if user:
        print(f"✅ 登录成功：{user['username']}（角色：{user['role']}）")
        response = JSONResponse({
            "message": "登录成功",
            "user": {
                "username": user["username"],
                "role": user["role"],
                "email": user["email"]
            }
        })
        response.set_cookie(
            key="current_user",
            value=user["username"],
            httponly=True,
            samesite="lax",
            secure=False,
            path="/"  
        )
        return response
    else:
        print("❌ 登录失败：未找到匹配用户或密码错误", identifier, password)
    raise FastAPIHTTPException(status_code=401, detail="用户名或密码错误")

@app.post("/api/verify-code")
async def verify_code(data: dict):
    phone = data.get("phone")
    code = data.get("code")
    new_password = data.get("new_password")
    print("📦 验证码比对：", phone, code, "缓存中的验证码为：", sms_code_cache.get(phone))
    if sms_code_cache.get(phone) != str(code):
        raise FastAPIHTTPException(status_code=400, detail="验证码错误或已过期")

    users_data = get_user_db()
    users = users_data.get("users", [])
    matched_user = next((u for u in users if u.get("phone") == phone), None)
    if not matched_user:
        raise FastAPIHTTPException(status_code=404, detail="用户未注册")

    matched_user["password"] = new_password
    save_user_db({"users": users})
    return {"message": "验证成功，密码已更新", "success": True}

from pydantic import BaseModel

class PhoneNumber(BaseModel):
    phone: str

@app.post("/api/send-code")
async def send_code(payload: PhoneNumber):
    result, code = send_sms_code(payload.phone)
    print(f"✅ 已发送验证码 {code} 到手机号 {payload.phone}，返回：{result}")
    if result.get("code") == 200:
        return {"message": "验证码已发送"}
    else:
        return {"message": "发送失败", "detail": result}

@app.post("/api/validate-code-only")
async def validate_code_only(data: dict):
    phone = data.get("phone")
    code = data.get("code")
    print(f"📦 验证手机号：{phone}, 用户输入验证码：{code}, 缓存中验证码：{sms_code_cache.get(phone)}")
    if sms_code_cache.get(phone) != str(code):
        raise FastAPIHTTPException(status_code=400, detail="验证码错误或已过期")
    return {"message": "验证码正确", "success": True}

@app.post("/api/register")
async def register(data: dict):
    phone = data.get("phone")
    code = data.get("code")  
    if sms_code_cache.get(phone) != str(code):
        raise FastAPIHTTPException(status_code=400, detail="验证码错误或已过期")
    username = data.get("username")
    password = data.get("password")

    if not all([phone, code, username, password]):
        raise FastAPIHTTPException(status_code=400, detail="所有字段均为必填")

    users_data = get_user_db()
    users = users_data.get("users", [])

    if any(u["username"] == username for u in users):
        raise FastAPIHTTPException(status_code=400, detail="用户名已存在")

    new_user = {
        "id": max([u["id"] for u in users], default=0) + 1,
        "username": username,
        "password": password,
        "role": "hr",
        "email": f"{username}@example.com",
        "phone": phone
    }
    users.append(new_user)
    save_user_db({"users": users})

    return {"message": "注册成功", "user": new_user}

@app.post("/api/llm/analyze-resume")
async def llm_analyze_resume(data: dict):
    resume_id = data.get("resume_id")
    if not resume_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少 resume_id")

    resume_path = f"uploads/talent_pool/{resume_id}.pdf"
    if not os.path.exists(resume_path):
        raise FastAPIHTTPException(status_code=404, detail="未找到简历 PDF 文件")

    try:
        
        with pdfplumber.open(resume_path) as pdf:
            resume_text = "\n".join([page.extract_text() or '' for page in pdf.pages])

        
        features = extract_structured_features(resume_text)
        features = ensure_all_features(features)
        X_input = pd.DataFrame([{
            "学历_x": features["学历_x"],
            "经验_x": features["经验_x"],
            "技能数_x": features["技能数_x"],
            "证书数_x": features["证书数_x"],
            "年龄_x": features["年龄_x"],
            "项目经验_x": features["项目经验_x"],
            "自我评分_x": features["自我评分_x"]
        }])
        score_raw = model.predict(X_input)[0]
        score = float(score_raw)
        if score <= 1 and model.__class__.__name__ == "RandomForestRegressor":
            score = score * 100
        elif score <= 5:
            score = score / 5 * 100
        score = round(score, 2)

        
        analysis = generate_gpt_report(resume_text, score)
        recommended = extract_recommended_position(analysis)
        analysis = re.sub(r"[<>]+", "", analysis)

        db = get_json_db("batch_resume_details.json")
        item = next((i for i in db if i["resume_id"] == resume_id), None)
        if not item:
            raise FastAPIHTTPException(status_code=404, detail="未找到简历记录")
        item["score"] = score
        item["recommended_position"] = recommended
        item["analysis"] = analysis
        save_json_db("batch_resume_details.json", db)

        
        return {
            "resume_id": resume_id,
            "score": item["score"],
            "recommended_position": item["recommended_position"],
            "analysis": item["analysis"]
        }
    except Exception as e:
        print("❌ LLM 分析失败：", e)
        raise FastAPIHTTPException(status_code=500, detail="LLM 分析失败")

@app.post("/api/save-analysis")
async def save_analysis(payload: dict):
    resume_id = payload.get("resume_id")
    score = payload.get("score")
    recommended_position = payload.get("recommended_position")
    analysis = payload.get("analysis")

    if not resume_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少 resume_id")

    
    db = get_json_db("batch_resume_details.json")
    
    record = next((item for item in db if item.get("resume_id") == resume_id), None)
    if record:
        
        record["score"] = score
        record["recommended_position"] = recommended_position
        record["analysis"] = analysis
    else:
        
        new_record = {
            "resume_id": resume_id,
            "score": score,
            "recommended_position": recommended_position,
            "analysis": analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.append(new_record)
    
    save_json_db("batch_resume_details.json", db)
    return {"message": "分析结果已保存", "resume_id": resume_id}

@app.post("/api/verify-code-login")
async def verify_code_login(data: dict):
    phone = data.get("phone")
    code = data.get("code")
    print("📦 验证码登录尝试：", phone, code)

    
    if not phone or not code:
        raise FastAPIHTTPException(status_code=400, detail="手机号和验证码不能为空")

    
    cached_code = sms_code_cache.get(phone)
    if not cached_code:
        raise FastAPIHTTPException(status_code=400, detail="未发送验证码或已过期")
    if str(cached_code) != str(code):
        raise FastAPIHTTPException(status_code=401, detail="验证码错误")

    
    users = get_user_db()["users"]
    matched_user = next((u for u in users if u.get("phone") == phone), None)

    if not matched_user:
        raise FastAPIHTTPException(status_code=404, detail="用户未注册，请先注册")

    response = JSONResponse({
        "message": "登录成功",
        "user": {
            "username": matched_user.get("username"),
            "role": matched_user.get("role"),
            "email": matched_user.get("email")
        }
    })
    response.set_cookie(
        key="current_user",
        value=matched_user.get("username"),
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"  
    )
    return response

@app.post("/api/llm/promotion")
async def llm_promotion(data: dict):
    employee_id = str(data.get("id"))
    db = get_employee_db()
    emp = next((e for e in db if str(e.get("id") or e.get("工号")) == employee_id), None)
    if not emp:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应员工")

    prompt = f"""
请根据以下员工基本信息和任务评价，撰写升职建议，不超过150字。

员工信息：
姓名：{emp.get("name", "未知")}
工号：{emp.get("id", "未知")}
职位：{emp.get("position", "未知")}
任务得分：{emp.get("score", "无评分")}
主管评语：{emp.get("comment", "暂无")}

请综合评估该员工是否建议升职，并给出理由。
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是经验丰富的HR主管"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        suggestion = response.choices[0].message.content.strip()
        return {"suggestion": suggestion}
    except Exception as e:
        print("❌ 获取升职建议失败：", e)
        raise FastAPIHTTPException(status_code=500, detail="生成升职建议失败，请稍后重试")

@app.post("/api/llm/dismissal")
async def llm_dismissal(data: dict):
    employee_id = data.get("id")
    db = get_employee_db()
    emp = next((e for e in db if e.get("id") == employee_id), None)
    if not emp:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应员工")

    prompt = f"""
请根据以下员工信息与当前表现撰写离职建议，包括赔偿预估与原因。

员工信息：
姓名：{emp.get("name", "未知")}
工号：{emp.get("id", "未知")}
职位：{emp.get("position", "未知")}
任务完成度：{emp.get("score", "无评分")}
主管意见：{emp.get("comment", "暂无")}

请判断是否建议开除，并简要说明原因与赔偿金额。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是经验丰富的HR主管"},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    content = response.choices[0].message.content.strip()

    import re
    cost_match = re.search(r"[：:]\s*([0-9]+)元", content)
    reason_match = re.search(r"2[.、:]?\s*(.+)", content)

    cost = int(cost_match.group(1)) if cost_match else 0
    reason = reason_match.group(1).strip() if reason_match else "暂无分析"

    return {
        "cost": cost,
        "reason": reason,
        "raw": content
    }

@app.post("/api/llm/interactive-eval")
async def llm_interactive_eval(payload: dict):
    print("📥 收到交互请求 payload：", payload)  
    resume_id = payload.get("resume_id")
    user_prompt = payload.get("prompt")
    if not resume_id:
        print("⚠️ 缺少 resume_id")
    if not user_prompt:
        print("⚠️ 缺少 prompt")
    if not resume_id or not user_prompt:
        raise FastAPIHTTPException(status_code=400, detail="缺少 resume_id 或 prompt")

    details = get_json_db("batch_resume_details.json")
    record = next((item for item in details if item.get("resume_id") == resume_id), None)
    print(f"📎 查询 resume_id 为 {resume_id} 的分析记录，找到：{record is not None}")
    if not record:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应分析报告")
    analysis = record.get("analysis", "")
    if not analysis or analysis.strip() == "待生成":
        raise FastAPIHTTPException(status_code=400, detail="当前简历未完成分析，无法使用面试助手")

    prompt_text = f"""
    请根据以下分析报告内容，结合用户问题，给予简洁专业的回复。
    
    原始分析报告：
    {analysis}
    
    用户提问：
    {user_prompt}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  
            messages=[
                {"role": "system", "content": "你是一位经验丰富的企业 HR 面试助手，请根据提示内容给出简洁、专业的建议"},
        {"role": "user", "content": prompt_text}
            ],
            stream=False
        )
        content = response.choices[0].message.content.strip()
        return {"response": content}
    except Exception as e:
        import traceback
        print("❌ 交互式分析失败：", traceback.format_exc())
        raise FastAPIHTTPException(status_code=500, detail="LLM 分析失败")

@app.post("/api/talent")
async def add_talent(entry: dict):
    pool = get_json_db("talent_pool.json")
    pool.append(entry)
    save_json_db("talent_pool.json", pool)
    return {"message": "已保存", "count": len(pool)}

@app.get("/api/talent")
async def get_talent_pool():
    return get_json_db("talent_pool.json")

@app.get("/api/talent-pool")
async def get_talent_pool_data():
    return get_json_db("talent_pool.json")

@app.post("/api/talent-pool")
async def add_talent_pool_entry(entry: dict):
    db = get_json_db("talent_pool.json")
    db.append(entry)
    save_json_db("talent_pool.json", db)
    return {"message": "添加成功", "count": len(db)}

@app.delete("/api/employees/{employee_id}")
async def delete_employee(employee_id: str):
    db = get_employee_db()
    updated_db = [emp for emp in db if str(emp.get("id") or emp.get("工号")) != str(employee_id)]
    if len(updated_db) == len(db):
        raise FastAPIHTTPException(status_code=404, detail="未找到对应员工")
    save_employee_db(updated_db)
    return {"message": "员工已删除", "id": employee_id}

@app.post("/api/promotion/submit-to-hr")
async def submit_promotion_to_hr(payload: dict):
    suggestion_record = {
        "id": generate_id(),
        "employee_id": payload.get("employee_id"),
        "employee_name": payload.get("employee_name"),
        "modified_suggestion": payload.get("modified_suggestion"),
        "from": payload.get("from"),
        "to": payload.get("to"),
        "status": "待处理",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db = get_json_db("promotion_suggestions.json")
    db.append(suggestion_record)
    save_json_db("promotion_suggestions.json", db)
    return {"message": "升职建议已提交给 HR", "data": suggestion_record}

@app.post("/api/dismissal/submit-to-hr")
async def submit_dismissal_to_hr(payload: dict):
    suggestion_record = {
        "id": generate_id(),
        "employee_id": payload.get("employee_id"),
        "employee_name": payload.get("employee_name"),
        "original_suggestion": payload.get("original_suggestion", ""),
        "modified_suggestion": payload.get("modified_suggestion", payload.get("suggestion")),
        "from": payload.get("from", "admin"),
        "to": payload.get("to", "hr"),
        "status": "待处理",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db = get_json_db("dismissal_suggestions.json")
    db.append(suggestion_record)
    save_json_db("dismissal_suggestions.json", db)
    return {"message": "开除建议已提交给 HR", "data": suggestion_record}

@app.get("/api/current-user")
async def get_current_user(request: Request):
    print("🧪 Cookie 全部内容：", request.cookies)  
    username = request.cookies.get("current_user")
    if not username:
         raise FastAPIHTTPException(status_code=401, detail="未登录")
    users = get_user_db()["users"]
    user = next((u for u in users if u["username"] == username), None)
    if not user:
         raise FastAPIHTTPException(status_code=404, detail="用户不存在")
    return {
         "username": user["username"],
         "role": user["role"],
         "email": user.get("email", ""),
         "phone": user.get("phone", ""),
         "realname": user.get("realname", ""),
         "id": user.get("id", "")
    }

from fastapi import Depends

@app.post("/api/logout")
async def logout():
    response = JSONResponse({"message": "已退出登录"})
    response.delete_cookie("current_user")
    return response

def get_current_user_role(request: Request) -> str:
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    users = get_user_db()["users"]
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise FastAPIHTTPException(status_code=404, detail="用户不存在")
    return user["role"]

@app.get("/api/promotion/pending")
async def get_pending_promotions():
    db = get_json_db("promotion_suggestions.json")
    return {"data": [item for item in db if item.get("status") == "待处理"]}

@app.get("/api/dismissal/pending")
async def get_pending_dismissals():
    db = get_json_db("dismissal_suggestions.json")
    return {"data": [item for item in db if item.get("status") == "待处理"]}

@app.get("/api/tracking/pending")
async def get_tracking_tasks():
    promotions = get_json_db("promotion_suggestions.json")
    dismissals = get_json_db("dismissal_suggestions.json")

    tracking_promotions = [p for p in promotions if p.get("status") == "处理中"]
    tracking_dismissals = [d for d in dismissals if d.get("status") == "处理中"]

    return {
        "promotion": tracking_promotions,
        "dismissal": tracking_dismissals
    }

@app.post("/api/promotion/mark-done")
async def mark_promotion_done(data: dict):
    employee_id = str(data.get("employee_id"))
    db = get_json_db("promotion_suggestions.json")
    for item in db:
        if str(item.get("employee_id")) == employee_id and item.get("status") == "待处理":
            item["status"] = "已处理"
    save_json_db("promotion_suggestions.json", db)
    return {"message": "升职建议已处理"}

@app.post("/api/dismissal/mark-done")
async def mark_dismissal_done(data: dict):
    employee_id = str(data.get("employee_id"))
    db = get_json_db("dismissal_suggestions.json")
    for item in db:
        if str(item.get("employee_id")) == employee_id and item.get("status") == "待处理":
            item["status"] = "已处理"
    save_json_db("dismissal_suggestions.json", db)
    return {"message": "开除建议已处理"}

@app.delete("/api/talent/{talent_id}")
async def delete_talent(talent_id: str):
    db = get_json_db("talent_pool.json")
    updated_db = [entry for entry in db if str(entry.get("id")) != str(talent_id)]
    if len(updated_db) == len(db):
        raise FastAPIHTTPException(status_code=404, detail="未找到对应记录")
    save_json_db("talent_pool.json", updated_db)
    return {"message": "人才库记录已删除", "id": talent_id}

@app.post("/api/batch-analyze-resumes-model2")
async def batch_analyze_resumes_model2(files: list[UploadFile] = File(...)):
    if len(files) > 20:
        raise FastAPIHTTPException(status_code=400, detail="上传文件数量不能超过 20 个")
    summary = []
    detailed_data = []
    features_list = []

    today = datetime.now().strftime("%Y%m%d")
    existing_ids = []
    for db_file in ["recommend.json", "recommend_history.json", "batch_resume_summary.json", "batch_resume_features.json"]:
        if os.path.exists(db_file):
            with open(db_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for d in data:
                        rid = d.get("resume_id", "")
                        if isinstance(rid, str) and rid.startswith(today):
                            parts = rid.split("-")
                            if len(parts) >= 2 and parts[1].isdigit():
                                existing_ids.append(int(parts[1]))
                except:
                    continue
    starting_index = max(existing_ids, default=0) + 1

    for i, file in enumerate(files):
        if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
            print(f"⚠️ 跳过不支持的文件类型：{file.filename}")
            continue
        try:
            resume_text = extract_text(file)
            features = extract_structured_features(resume_text)
            features = ensure_all_features(features)

            X_input = pd.DataFrame([{
                "学历_x": features["学历_x"],
                "证书数_x": features["证书数_x"]
            }])

            score_raw = model2.predict(X_input)[0]
            score = float(score_raw)
            if score <= 1 and model2.__class__.__name__ == "RandomForestRegressor":
                score = score * 100
            elif score <= 5:
                score = score / 5 * 100
            score = round(score, 2)

            age = "无年龄"
            birth_match = re.search(r"(19\d{2}|20[01]\d)年\s*(出生|生|生人)?", resume_text)
            if birth_match:
                birth_year = int(birth_match.group(1))
                current_year = datetime.now().year
                if 1900 < birth_year <= current_year:
                    age = current_year - birth_year

            resume_id = f"{today}-{starting_index + i:02d}-0"
            original_filename = file.filename.replace(".pdf", "").replace(".docx", "")
            resume_name = original_filename
            features["技能关键词"] = "未知"

            features_list.append({
                "resume_id": resume_id,
                "学历_x": features["学历_x"],
                "证书数_x": features["证书数_x"],
                "年龄": age
            })

            summary.append({
                "resume_id": resume_id,
                "name": resume_name,
                "score": score,
                "recommended_position": "待生成",
                "学历_x": features["学历_x"],
                "证书数_x": features["证书数_x"],
                "年龄": age
            })

            detailed_data.append({
                "resume_id": resume_id,
                "name": resume_name,
                "score": score,
                "analysis": "待生成",
                "score_breakdown": {**features, "技能关键词": features.get("技能关键词", "无")},
                "年龄": age,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            print("❌ 简历处理失败：", file.filename, str(e))

    save_json_db("batch_resume_summary.json", summary)
    save_json_db("batch_resume_details.json", detailed_data)
    save_json_db("batch_resume_features.json", features_list)

    return {"message": "批量简历分析完成", "count": len(summary), "summary": summary}

@app.get("/api/batch-resume/{resume_id}")
async def get_resume_analysis(resume_id: str):
    db = get_json_db("batch_resume_details.json")
    item = next((i for i in db if str(i.get("resume_id")) == str(resume_id)), None)
    if not item:
        raise FastAPIHTTPException(status_code=404, detail="未找到简历分析记录")
    return {"data": item}

@app.get("/api/resume-report/{resume_id}")
async def get_resume_report(resume_id: str):
    db = get_json_db("batch_resume_details.json")
    item = next((i for i in db if str(i.get("resume_id")) == resume_id), None)
    
    needs_analysis = not item or item.get("analysis") == "待生成" or not item.get("recommended_position")
    if needs_analysis:
        
        await llm_analyze_resume({"resume_id": resume_id})
        
        db = get_json_db("batch_resume_details.json")
        item = next((i for i in db if str(i.get("resume_id")) == str(resume_id)), None)
        if not item:
            raise FastAPIHTTPException(status_code=404, detail="未找到简历分析记录")
    
    return {
        "resume_id": item.get("resume_id"),
        "score": item.get("score"),
        "recommended_position": item.get("recommended_position"),
        "analysis": item.get("analysis")
    }

@app.post("/api/batch-resume/{resume_id}/analyze")
async def analyze_resume_by_id(resume_id: str):
    db = get_json_db("batch_resume_details.json")
    item = next((i for i in db if str(i.get("resume_id")) == str(resume_id)), None)
    if not item:
        raise FastAPIHTTPException(status_code=404, detail="未找到简历记录")

    resume_path = f"uploads/talent_pool/{resume_id}.pdf"
    if not os.path.exists(resume_path):
        raise FastAPIHTTPException(status_code=404, detail="未找到简历 PDF 文件")

    try:
        with pdfplumber.open(resume_path) as pdf:
            resume_text = "\n".join([page.extract_text() or '' for page in pdf.pages])

        features = extract_structured_features(resume_text)
        features = ensure_all_features(features)
        X_input = pd.DataFrame([{
            "学历_x": features["学历_x"],
            "经验_x": features["经验_x"],
            "技能数_x": features["技能数_x"],
            "证书数_x": features["证书数_x"],
            "年龄_x": features["年龄_x"],
            "项目经验_x": features["项目经验_x"],
            "自我评分_x": features["自我评分_x"]
        }])
        score_raw = model.predict(X_input)[0]
        score = float(score_raw)
        if score <= 1 and model.__class__.__name__ == "RandomForestRegressor":
            score = score * 100
        elif score <= 5:
            score = score / 5 * 100
        score = round(score, 2)

        analysis = generate_gpt_report(resume_text, score)
        recommended = extract_recommended_position(analysis)
        analysis = re.sub(r"[<>]+", "", analysis)

        item["score"] = score
        item["recommended_position"] = recommended
        item["analysis"] = analysis
        save_json_db("batch_resume_details.json", db)

        return {"message": "分析完成", "resume_id": resume_id, "analysis": analysis}
    except Exception as e:
        print("❌ 分析失败：", e)
        raise FastAPIHTTPException(status_code=500, detail="分析失败")

@app.post("/api/recommend-to-admin")
async def recommend_to_admin(data: dict):
    resume_id = data.get("resume_id")
    reason = data.get("reason")
    analysis = data.get("analysis", "无")

    if not resume_id or not reason:
        raise FastAPIHTTPException(status_code=400, detail="缺少 resume_id 或推荐理由")

    record = {
        "id": generate_id(),
        "resume_id": resume_id,
        "reason": reason,
        "analysis": analysis,
        "recommended_position": data.get("recommended_position", "未知岗位"),
        "score": data.get("score", 0),
        "name": data.get("name", "未知"),
        "status": "待审批",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    db = get_json_db("admin_recommendations.json")
    db.append(record)
    save_json_db("admin_recommendations.json", db)

    return {"message": "推荐已提交至管理员审批", "data": record}

@app.get("/api/admin/recommendations")
async def get_admin_recommendations():
    print("✅ 管理员获取推荐数据")
    raw = get_json_db("admin_recommendations.json")
    formatted = [
        {
            "id": item.get("id"),
            "resume_id": item.get("resume_id"),
            "recommended_position": item.get("recommended_position", "未知岗位"),
            "score": item.get("score", 0),
            "reason": item.get("reason", ""),
            "analysis": item.get("analysis", "无"),
            "status": item.get("status", "待审批"),
            "timestamp": item.get("timestamp", "")
        }
        for item in raw
    ]
    return {"data": formatted}

@app.patch("/api/admin/recommendations/{recommend_id}")
async def update_admin_recommendation(recommend_id: str, update: dict):
    db = get_json_db("admin_recommendations.json")
    item = next((r for r in db if r["id"] == recommend_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="推荐记录不存在")

    item["status"] = update.get("status", item["status"])
    save_json_db("admin_recommendations.json", db)
    return {"message": "更新成功", "updated": item}

@app.delete("/api/admin/recommendations/{recommend_id}")
async def delete_admin_recommendation(recommend_id: str):
    db = get_json_db("admin_recommendations.json")
    updated_db = [item for item in db if item.get("id") != recommend_id]
    if len(updated_db) == len(db):
        raise HTTPException(status_code=404, detail="推荐记录未找到")
    save_json_db("admin_recommendations.json", updated_db)
    return {"message": "推荐记录已删除", "id": recommend_id}

@app.post("/api/update-realname")
async def update_realname(request: Request, payload: dict = Body(...)):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    realname = payload.get("realname", "").strip()
    if not realname:
        raise FastAPIHTTPException(status_code=400, detail="姓名不能为空")

    users = get_user_db()["users"]
    for u in users:
        if u["username"] == username:
            u["realname"] = realname
            break
    save_user_db({"users": users})
    return {"message": "姓名已更新", "realname": realname}

@app.post("/api/update-employee-id")
async def update_employee_id(request: Request, payload: dict = Body(...)):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    employee_id = payload.get("employee_id", "").strip()
    if not employee_id:
        raise FastAPIHTTPException(status_code=400, detail="工号不能为空")

    users = get_user_db()["users"]
    for u in users:
        if u["username"] == username:
            u["id"] = employee_id
            
            employees = get_employee_db()
            matched = next((e for e in employees if str(e.get("id") or e.get("工号")) == employee_id), None)
            if matched:
                realname = matched.get("name") or matched.get("姓名")
                if realname:
                    u["realname"] = realname
            break
    save_user_db({"users": users})
    return {"message": "工号已更新", "id": employee_id}

@app.get("/api/employee/match-by-id/{employee_id}")
async def match_employee_by_id(employee_id: str):
    db = get_employee_db()
    employee = next((e for e in db if str(e.get("id") or e.get("工号")) == str(employee_id)), None)
    if not employee:
        raise FastAPIHTTPException(status_code=404, detail="未找到匹配的员工")
    return {"message": "匹配成功", "data": employee}

@app.post("/api/employee/analyze-and-link")
async def analyze_and_link_employee(data: dict):
    employee_id = data.get("employee_id")
    if not employee_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少 employee_id")

    employees = get_employee_db()
    employee = next((e for e in employees if str(e.get("id") or e.get("工号")) == str(employee_id)), None)
    if not employee:
        raise FastAPIHTTPException(status_code=404, detail="员工不存在")

    employee_name = employee.get("name") or employee.get("姓名")
    if not employee_name:
        raise FastAPIHTTPException(status_code=400, detail="员工姓名不存在")

    details = get_json_db("batch_resume_details.json")
    matched = next((d for d in reversed(details) if employee_name in d.get("name", "")), None)
    if not matched:
        raise FastAPIHTTPException(status_code=404, detail="未找到匹配简历")

    resume_id = matched.get("resume_id")
    try:
        result = await analyze_resume_by_id(resume_id)
    except Exception as e:
        raise FastAPIHTTPException(status_code=500, detail=f"分析失败：{str(e)}")

    
    for e in employees:
        if str(e.get("id") or e.get("工号")) == str(employee_id):
            e["resume_id"] = resume_id
            break
    save_employee_db(employees)

    return {"message": "分析完成并已绑定", "resume_id": resume_id, "analysis": result}

@app.post("/api/task/submit")
async def submit_task(request: Request, payload: dict = Body(...)):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    task_text = payload.get("task", "").strip()
    leader_id = payload.get("leader_id", "").strip()
    if not task_text or not leader_id:
        raise FastAPIHTTPException(status_code=400, detail="任务内容或 leader 工号不能为空")

    users = get_user_db()["users"]
    leader = next((u for u in users if str(u.get("id")) == leader_id), None)
    if not leader:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应 leader")

    user = next((u for u in users if u.get("username") == username), None)
    task_entry = {
        "id": generate_id(),
        "employee_id": user.get("id"),  
        "from": username,
        "from_realname": user.get("realname", "匿名"),
        "to": leader.get("username"),
        "to_realname": leader.get("realname", "未知"),
        "task": task_text,
        "status": "待审批",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    db = get_json_db("submitted_tasks.json")
    db.append(task_entry)
    save_json_db("submitted_tasks.json", db)
    return {"message": "任务已提交", "data": task_entry}

@app.get("/api/submitted_tasks")
async def get_submitted_tasks():
    return get_json_db("submitted_tasks.json")

@app.post("/api/score-task")
async def score_task(payload: dict):
    task_id = payload.get("task_id")
    score = payload.get("score")
    comment = payload.get("comment", "")

    if not task_id or score is None:
        raise FastAPIHTTPException(status_code=400, detail="缺少评分信息")

    print(f"🟨 接收到评分任务：task_id={task_id}, score={score}")

    tasks = get_json_db("submitted_tasks.json")
    task = next((t for t in tasks if t.get("id") == task_id), None)
    if not task:
        print("⚠️ 未找到任务，自动创建")
        task = {
            "id": task_id,
            "from": "未知",
            "from_realname": "匿名",
            "task": "未知任务",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks.append(task)

    task["score"] = score
    task["comment"] = comment
    task["status"] = "已评分"
    save_json_db("submitted_tasks.json", tasks)
    print("✅ 任务评分已保存")

    promotion_db = get_json_db("promotion_suggestions.json")
    suggestion = {
        "id": generate_id(),
        "employee_id": str(task.get("employee_id") or task.get("from")),
        "employee_name": task.get("from_realname", "匿名"),
        "score": score,
        "comment": comment,
        "task": task.get("task", ""),
        "status": "处理中",
        "timestamp": task.get("timestamp", "")
    }
    promotion_db.append(suggestion)
    save_json_db("promotion_suggestions.json", promotion_db)
    print("✅ 添加到动态追踪")

    
    employee_name = task.get("from_realname") or task.get("from")
    print(f"🔍 查找员工姓名：{employee_name}")
    employees = get_employee_db()
    
    employee = next(
        (e for e in employees if (e.get("name") or e.get("姓名")) == employee_name),
        None
    )
    
    employee_id = str(employee.get("id") or employee.get("工号")) if employee else None
    print(f"🔍 匹配到员工工号：{employee_id}")
    resume_id = employee.get("resume_id") if employee else None

    if resume_id:
        try:
            analysis_result = await analyze_resume_by_id(resume_id)
            print(f"✅ 分析成功：{resume_id}")
            if analysis_result and isinstance(analysis_result, dict):
                prev_score = 0
                prev_completion = 0
                if os.path.exists("resume_analysis_results.json"):
                    with open("resume_analysis_results.json", "r", encoding="utf-8") as f:
                        existing = json.load(f)
                        if resume_id in existing:
                            prev_score = existing[resume_id].get("score", 0)
                            prev_completion = existing[resume_id].get("completion_rate", 0)
                else:
                    existing = {}
                existing[resume_id] = {
    "summary": analysis_result.get("analysis", "暂无分析"),
    "previous_score": float(prev_score),
    "score": float(analysis_result.get("score", 0)),
    "previous_completion_rate": float(prev_completion),
    "completion_rate": float(score),
    "roc": {
        "fpr": [0.0, 0.2, 0.5, 1.0],
        "tpr": [0.0, 0.4, 0.85, 1.0]
    },
    "pr": {
        "recall": [0.0, 0.3, 0.7, 1.0],
        "precision": [1.0, 0.9, 0.6, 0.5]
    },
    "radar": {
        "labels": ["学历", "经验", "技能", "证书", "项目经验", "自我驱动", "岗位适配"],
        "values": [
            float(employee.get("学历_x", 0)),
            float(employee.get("经验_x", 0)),
            float(employee.get("技能数_x", 0)),
            float(employee.get("证书数_x", 0)),
            float(employee.get("项目经验_x", 0)),
            8.0,
            7.0
        ]
    }
}
                with open("resume_analysis_results.json", "w", encoding="utf-8") as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 分析失败：{e}")
    else:
        
        try:
            summary = f"任务内容：{task.get('task', '')}\n主管评分：{score}\n主管评价：{comment}"
            prompt = f"""
该员工无完整简历记录，以下是其任务表现汇总：

任务内容：{task.get('task', '')}
主管评分：{score}
主管评价：{comment}

请根据上述信息，撰写该员工的简要总结（200字内），可用于评估岗位适配度。
"""
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位经验丰富的 HR 助手"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            content = response.choices[0].message.content.strip()
            fallback_resume_id = f"{employee_id}-fallback"
            fallback_result = {
                fallback_resume_id: {
                    "summary": content,
                    "score": float(score),
                    "previous_score": float(score),
                    "completion_rate": float(score),
                    "previous_completion_rate": float(score),
                    "roc": {
                        "fpr": [0.0, 0.3, 0.6, 1.0],
                        "tpr": [0.0, 0.5, 0.75, 1.0]
                    },
                    "pr": {
                        "recall": [0.0, 0.4, 0.7, 1.0],
                        "precision": [1.0, 0.85, 0.65, 0.4]
                    },
                    "radar": {
                        "labels": ["学历", "经验", "技能", "证书", "项目经验", "自我驱动", "岗位适配"],
                        "values": [0, 0, 0, 0, 0, 7, 7]
                    }
                }
            }
            if os.path.exists("resume_analysis_results.json"):
                with open("resume_analysis_results.json", "r", encoding="utf-8") as f:
                    existing = json.load(f)
            else:
                existing = {}
            existing.update(fallback_result)
            with open("resume_analysis_results.json", "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            print("✅ 无简历也写入分析 fallback 数据：", fallback_resume_id)
        except Exception as e:
            print("❌ 无简历分析生成失败：", e)

    return {"message": "评分成功并已加入动态追踪"}
@app.get("/api/tracking/summary")
async def tracking_summary():
    
    suggestions = get_json_db("promotion_suggestions.json")

    
    analysis_results = {}
    if os.path.exists("resume_analysis_results.json"):
        with open("resume_analysis_results.json", "r", encoding="utf-8") as f:
            analysis_results = json.load(f)

    
    results = []
    for item in suggestions:
        rid = item.get("resume_id") or ""
        llm_data = analysis_results.get(rid) or analysis_results.get(f"{rid}-fallback", {})
        llm_summary = llm_data.get("summary") if isinstance(llm_data, dict) else None

        results.append({
            "employee_name": item.get("employee_name"),
            "task": item.get("task"),
            "score": item.get("score"),
            "comment": item.get("comment"),
            "llm_summary": llm_summary,
            "previous_completion_rate": llm_data.get("previous_completion_rate", 0),
            "completion_rate": llm_data.get("completion_rate", 0),
            "llm_advice": llm_data.get("llm_advice", "")
        })

    return results
@app.get("/api/analysis-results")
async def get_analysis_results():
    log_path = "analysis_results.log"
    try:
        if os.path.exists("resume_analysis_results.json"):
            with open("resume_analysis_results.json", "r", encoding="utf-8") as f:
                raw = json.load(f)

            filtered = raw

            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"[{datetime.now()}] 提取分析记录 {len(filtered)} 条：\n")
                for k in filtered:
                    log_file.write(f"  - {k}\n")

            return filtered
    except Exception as e:
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{datetime.now()}] ❌ 获取分析结果失败：{str(e)}\n")
    return {}

@app.get("/api/profile")
async def get_profile(request: Request):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    users = get_user_db()["users"]
    user = next((u for u in users if u.get("username") == username), None)
    if not user:
        raise FastAPIHTTPException(status_code=404, detail="用户不存在")

    return {
        "username": user["username"],
        "role": user["role"],
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "realname": user.get("realname", ""),
        "id": user.get("id", "")
    }

@app.get("/api/my-promotions")
async def get_my_promotions(request: Request):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    users = get_user_db()["users"]
    user = next((u for u in users if u.get("username") == username), None)
    if not user:
        raise FastAPIHTTPException(status_code=404, detail="用户不存在")

    promotion_db = get_json_db("promotion_suggestions.json")
    return {
        "data": [
            item for item in promotion_db
            if str(item.get("employee_id")) == str(user.get("id"))
        ]
    }