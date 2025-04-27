from fastapi import HTTPException
from fastapi import FastAPI, UploadFile, File, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from openai import OpenAI
from fastapi import HTTPException as FastAPIHTTPException
import os
import joblib
from datetime import datetime
import hashlib
from passlib.context import CryptContext
import time
import random
import json
import inspect
from fastapi import APIRouter
from bson import ObjectId
router = APIRouter()
app = FastAPI()
import json, os
from mongodbapi import find_user_by
import re
from datetime import datetime
from fastapi import Depends
import joblib  
import tempfile
import requests
import docx2txt
import anyio
from fastapi.responses import JSONResponse
import pdfplumber
import pandas as pd

from mongodbapi import employees_col
app.include_router(router)
router = APIRouter()
from mongodbapi import (
    users_col,
    employees_col,
    recommend_col,
    recommend_history_col,
    talent_pool_col,
    resume_details_col,
    promotion_suggestions_col,
    dismissal_suggestions_col,
    admin_recommendations_col,
    submitted_tasks_col,
    resume_analysis_results_col
)
sms_code_cache = {}
class PhoneNumber(BaseModel):
    phone: str
MODEL_PATH = "model.pkl"
model = joblib.load(MODEL_PATH)
MODEL2_PATH = "model2.pkl"
model2 = joblib.load(MODEL2_PATH)
client = OpenAI(
    api_key="sk-65f94c51220b4bb38bfb694b73c96279",
    base_url="https://api.deepseek.com",
)
class LoginRequest(BaseModel):
    identifier: str
    password: str

async def get_recommend_db():
    return await recommend_col.find().to_list(length=None)

async def save_recommend_db(data):
    await recommend_col.delete_many({})
    if data:
        await recommend_col.insert_many(data)


async def generate_resume_id():
    now = datetime.now()
    prefix = now.strftime("%Y%m")
    db = await talent_pool_col.find().to_list(length=None)
    count = sum(1 for item in db if item.get("resume_id", "").startswith(prefix))
    return f"{prefix}-{count + 1:02d}"
def generate_id():
    import uuid
    return str(uuid.uuid4())


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
async def create_test_users():
    existing = await users_col.find({"username": {"$in": ["employee", "leader", "hr", "admin"]}}).to_list(length=None)
    if len(existing) < 4:
        await users_col.delete_many({"username": {"$in": ["employee", "leader", "hr", "admin"]}})
        hashed = pwd_context.hash("123456")
        await users_col.insert_many([
            {"username": "employee", "password": hashed, "role": "employee", "phone": "", "email": "", "realname": "测试员工", "id": ""},
            {"username": "leader", "password": hashed, "role": "leader", "phone": "", "email": "", "realname": "测试主管", "id": ""},
            {"username": "hr",      "password": hashed, "role": "hr",      "phone": "", "email": "", "realname": "测试HR", "id": ""},
            {"username": "admin",   "password": hashed, "role": "admin",   "phone": "", "email": "", "realname": "超级管理员", "id": ""}
        ])
def send_sms_code(phone):
    
    code = str(random.randint(100000, 999999))
    sms_code_cache[phone] = code


    m = 3

  
    url = "http://v.juhe.cn/sms/send"
    payload = {
        "mobile": phone,
        "tpl_id": "270119",  
        "tpl_value": f"#code#={code}&#m#={m}",
        "key": "7a5b82404fd9b83327bfb81629b86a51"  
    }

    print("📤 正在发送验证码，payload 为：", payload)
    response = requests.post(url, data=payload)

    return response.json(), code, m
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://113.46.143.235",       
        "http://localhost:3000",       
        "http://127.0.0.1:3000"       
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

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
def clean_mongo_id(doc):
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

@app.get("/talent-pool")
async def get_talent_pool_data():
    raw_data = await talent_pool_col.find().to_list(length=None)
    return [clean_mongo_id(doc) for doc in raw_data]

@app.post("/talent-pool")
async def add_talent_pool_entry(entry: dict):
    await talent_pool_col.insert_one(entry)
    count = await talent_pool_col.count_documents({})
    return {"message": "添加成功", "count": count}
@app.post("/interview-assist")
async def interview_assist(request: Request):
    data = await request.json()
    resume_id = data.get("resume_id")
    prompt = data.get("prompt")

    if not resume_id or not prompt:
        raise HTTPException(status_code=400, detail="resume_id 和 prompt 是必需的")

    print("📩 面試助手收到：", resume_id, prompt)

    
    record = await resume_details_col.find_one({"resume_id": resume_id})
    if not record:
        raise HTTPException(status_code=404, detail="未找到該簡歷分析內容")

    analysis = record.get("analysis", "暫無分析結果")

    prompt_text = f"""
請根據以下簡歷分析內容與提問問題，幫我設計幾個延伸提問，評估候選人是否適合該崗位。

簡歷分析內容：
{analysis}

面試問題：
{prompt}
"""

    try:
        response = await anyio.to_thread.run_sync(
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "根據這些幫助HR面試，並且最後用簡體中文回答"},
                    {"role": "user", "content": prompt_text}
                ],
                stream=False
            )
        )
        content = response.choices[0].message.content.strip()
        return {"response": content}
    except Exception as e:
        print("❌ GPT 面試助手調用失敗：", e)
        raise HTTPException(status_code=500, detail="面試助手服務失敗")

@app.post("/batch-analyze-resumes-model2")
async def batch_analyze_resumes_model(files: list[UploadFile] = File(...)):
    print("▶️ 收到上传文件数量：", len(files))
    for f in files:
        print(" ‑‑", f.filename)
    ...
def generate_resume_id(source_flag="0"):
    now = datetime.now()
    prefix = now.strftime("%Y%m%d")
    
    max_index = 0
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


def ensure_all_features(features: dict) -> dict:
    all_fields = ['学历_x', '经验_x', '技能数_x', '证书数_x', '年龄_x', '项目经验_x', '自我评分_x']
    for field in all_fields:
        if field not in features:
            features[field] = 0
    return features



async def generate_gpt_report(resume_text: str, score: int) -> str:
    prompt = f"""
请根据以下简历内容和模型评分撰写简要的分析报告，内容包括：优点、缺点、改进建议。

评分：{score}
简历内容如下：
{resume_text}
"""
    try:
        response = await anyio.to_thread.run_sync(
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "请根据以下简历内容和模型评分撰写分析报告，输出纯文本，不啊哟markdown。"},
                    {"role": "user",   "content": prompt}
                ],
                stream=False
            )
        )
    except Exception as e:
        raise HTTPException(502, f"AI 服务调用失败：{e}")

    return response.choices[0].message.content

def extract_recommended_position(text: str) -> str:
    pattern = r"(?:适合的?岗位(?:类型)?|岗位类型)[：:\s]*([^\n。；]*)"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return "暂无明确岗位推荐"

@app.post("/save-resume")
async def save_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        record = {
            "filename": file.filename,
            "content": content,
            "uploaded_at": datetime.utcnow()
        }
        result = await resume_details_col.insert_one(record)
        return JSONResponse({"status": "success", "id": str(result.inserted_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败：{e}")
@app.post("/save-analysis")
async def save_analysis(payload: dict):
    resume_id = payload.get("resume_id")
    score = payload.get("score")
    recommended_position = payload.get("recommended_position")
    analysis = payload.get("analysis")

    if not resume_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少 resume_id")

    existing = await resume_details_col.find_one({"resume_id": resume_id})
    if existing:
        await resume_details_col.update_one(
            {"resume_id": resume_id},
            {"$set": {
                "score": score,
                "recommended_position": recommended_position,
                "analysis": analysis
            }}
        )
    else:
        await resume_details_col.insert_one({
            "resume_id": resume_id,
            "score": score,
            "recommended_position": recommended_position,
            "analysis": analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return {"message": "分析结果已保存", "resume_id": resume_id}
from bson import ObjectId

@app.post("/recommend")
async def hr_recommend(data: dict):
    print("🟡 接收到推荐数据：", data)
    db = await recommend_col.find().to_list(length=None)
    resume_id = data.get("resume_id") or generate_resume_id()

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

    target = await resume_details_col.find_one({"resume_id": resume_id})
    if target:
        await resume_details_col.update_one(
            {"resume_id": resume_id},
            {"$set": {"analysis": "待生成"}}
        )
        record["name"] = target.get("name", "未知")
        record["score"] = target.get("score", 0)

    record["analysis"] = "待生成"
    insert_result = await talent_pool_col.insert_one(record)
    await save_recommend_db(db)
    print("✅ 已保存推荐记录：", record)

    return {
        "message": "推荐成功",
        "data": {**record, "_id": str(insert_result.inserted_id)}
    }
@app.patch("/recommend/{recommend_id}")
async def update_recommend_status(recommend_id: str, payload: dict):
    item = await recommend_col.find_one({"id": recommend_id})
    if not item:
        raise HTTPException(status_code=404, detail="推荐记录未找到")

    new_status = payload.get("status", item["status"])
    await recommend_col.update_one({"id": recommend_id}, {"$set": {"status": new_status}})

    await recommend_history_col.insert_one({**item, "status": new_status, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    if new_status == "已录用":
        await employees_col.insert_one(item)
    elif new_status == "不通过":
        await talent_pool_col.insert_one(item)

    return {"message": "状态已更新", "status": new_status}
@app.get("/recommend")
async def get_recommend_list(status: str = "全部"):
    db = await recommend_col.find().to_list(length=None)
    if status == "全部":
        return {"data": db}
    return {"data": [item for item in db if item.get("status") == status]}
@app.post("/recommend/approve")
async def leader_approve(data: dict):
    await recommend_col.update_one({"id": data["id"]}, {"$set": {"status": data["decision"]}})
    return {"message": "已处理"}

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    try:
       
        resume_text = extract_text(file)
        print("✅ 简历内容片段：", resume_text[:200])


        features = extract_structured_features(resume_text)
        print("✅ 提取的特征：", features)
        features = ensure_all_features(features)
        print("✅ 补全后的特征：", features)


        X_input = pd.DataFrame([{
            "学历_x":    features["学历_x"],
            "经验_x":    features["经验_x"],
            "技能数_x":  features["技能数_x"],
            "证书数_x":  features["证书数_x"],
            "年龄_x":    features["年龄_x"],
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

 
        analysis = await generate_gpt_report(resume_text, score)
        print("✅ LLM 分析报告：", analysis)


        recommended = extract_recommended_position(analysis)
        analysis = re.sub(r"[\[\]]+", "", str(analysis))


        resume_id = generate_resume_id()
        result = {
            "score": int(score),
            "recommended_position": recommended,
            "analysis": analysis,
            "score_breakdown": {
                "学历_x":    features["学历_x"],
                "经验_x":    features["经验_x"],
                "技能数_x":  features["技能数_x"],
                "证书数_x":  features["证书数_x"],
                "年龄_x":    features["年龄_x"],
                "项目经验_x": features["项目经验_x"],
                "自我评分_x": features["自我评分_x"]
            },
            "resume_id": resume_id,
            "name": file.filename.replace(".pdf", "").replace(".docx", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        
        insert_result = await resume_details_col.insert_one(result)

        inserted_id = insert_result.inserted_id

        response_data = {
           "id": str(inserted_id),
            "score": result["score"],
            "recommended_position": result["recommended_position"],
           "analysis": result["analysis"],
            "score_breakdown": result["score_breakdown"],
            "resume_id": result["resume_id"],
            "name": result["name"],
            "timestamp": result["timestamp"],
        }
        return JSONResponse(content=response_data)

    except Exception as e:
        print("❌ 出错了：", e)

        raise HTTPException(status_code=500, detail=str(e))
@app.get("/employees")
async def get_employees():
    raw = await employees_col.find().to_list(length=None)
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
    print("✅ 收到员工列表请求")
    return {"data": formatted}

@app.get("/leader/employees")
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

@app.post("/leader/add-by-id")
async def add_employee_by_id(data: dict, request: Request):
    employee_id = data.get("id")
    if not employee_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少工号")
    
    username = request.cookies.get("current_user")
    if not username:
         raise FastAPIHTTPException(status_code=401, detail="未登录")

    db = await employees_col.find().to_list(length=None)
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

@app.post("/employees")
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
                details = await resume_details_col.find().to_list(length=None)
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
    db = await employees_col.find().to_list(length=None)
    db.extend(employees)
    print("✅ 已保存员工数据，共计：", len(employees))
    return {"message": "员工数据已保存", "count": len(employees)}
@app.post("/employees/save")
async def save_employees(data: list[dict]):
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="格式錯誤")
    await employees_col.delete_many({})
    await employees_col.insert_many(data)
    return {"message": "保存成功", "count": len(data)}
@app.post("/chart-data")
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
            llm_score_response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "以企业HR的角度分析"},
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

from mongodbapi import find_user_by

from pydantic import BaseModel

class LoginRequest(BaseModel):
    identifier: str
    password: str


# 初始化加密器（未来要用）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 是否启用加密模式（目前为 False，未来可改成 True）
ENCRYPTED_MODE = True

@app.post("/login")
async def login(data: LoginRequest):
    identifier = data.identifier
    password = data.password
    

    # Step 1: 查用户（不带密码）
    user = await find_user_by({
        "$or": [
            {"username": identifier},
            {"email": identifier},
            {"phone": identifier}
        ]
    })

    print(f"✅ 正在尝试登录：{identifier} / {password}")

    # Step 2: 校验密码
    if user:
        db_password = user.get("password", "")
        if ENCRYPTED_MODE:
            if not pwd_context.verify(password, db_password):
                print("❌ 密码加密校验失败")
                raise HTTPException(status_code=401, detail="用户名或密码错误")
        else:
            if password != db_password:
                print("❌ 明文密码不匹配")
                raise HTTPException(status_code=401, detail="用户名或密码错误")
        print("🚀 当前加密模式：", ENCRYPTED_MODE)

        print(f"✅ 登录成功：{user['username']}（角色：{user['role']}）")
        response = JSONResponse({
            "message": "登录成功",
            "user": {
                "username": user["username"],
                "role": user["role"],
                "email": user["email"]
            },
            "token": "dummy-token"
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

    print("❌ 登录失败：用户不存在")
    raise HTTPException(status_code=401, detail="用户名或密码错误")
@app.post("/verify-code")
async def verify_code(data: dict):
    from mongodbapi import find_user_by, update_user
    
    phone = data.get("phone")
    code = data.get("code")
    new_password = data.get("new_password")
    print("📦 验证码比对：", phone, code, "缓存中的验证码为：", sms_code_cache.get(phone))
    
    if sms_code_cache.get(phone) != str(code):
        raise FastAPIHTTPException(status_code=400, detail="验证码错误或已过期")
    
    matched_user = await find_user_by({"phone": phone})
    if not matched_user:
        raise FastAPIHTTPException(status_code=404, detail="用户未注册")
    
    hashed_new_password = pwd_context.hash(new_password)
    await update_user({"phone": phone}, {"password": hashed_new_password})  # ✅ 加密后更新
    return {"message": "验证成功，密码已更新", "success": True}


class PhoneNumber(BaseModel):
    phone: str

@app.post("/send-code")
async def send_code(payload: PhoneNumber):
    result, code, m = send_sms_code(payload.phone)
    print(f"✅ 已发送验证码 {code}（有效期 {m} 分钟）到手机号 {payload.phone}，返回：{result}")

    if result.get("error_code") == 0:
        return {"message": "验证码已发送"}
    else:
        return {"message": "发送失败", "detail": result}

@app.post("/validate-code-only")
async def validate_code_only(data: dict):
    phone = data.get("phone")
    code = data.get("code")
    print(f"📦 验证手机号：{phone}, 用户输入验证码：{code}, 缓存中验证码：{sms_code_cache.get(phone)}")
    if sms_code_cache.get(phone) != str(code):
        raise FastAPIHTTPException(status_code=400, detail="验证码错误或已过期")
    return {"message": "验证码正确", "success": True}

from mongodbapi import insert_user, find_user_by

@app.post("/register")
async def register(data: dict):
    phone = data.get("phone")
    code = data.get("code")
    if sms_code_cache.get(phone) != str(code):
        raise FastAPIHTTPException(status_code=400, detail="验证码错误或已过期")

    username = data.get("username")
    password = data.get("password")

    if not all([phone, code, username, password]):
        raise FastAPIHTTPException(status_code=400, detail="所有字段均为必填")

    existing_user = await find_user_by({"username": username})
    if existing_user:
        raise FastAPIHTTPException(status_code=400, detail="用户名已存在")
    hashed_password = pwd_context.hash(password)

    new_user = {
        
        "username": username,
        "password": hashed_password,
        "role": "hr",
        "email": f"{username}@example.com",
        "phone": phone
    }
    await insert_user(new_user)

    return {"message": "注册成功", "user": new_user}
@app.post("/llm/analyze-resume")
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

        
        result = await resume_details_col.update_one(
            {"resume_id": resume_id},
            {"$set": {
                "score": score,
                "recommended_position": recommended,
                "analysis": analysis
            }}
        )
        if result.matched_count == 0:
            raise FastAPIHTTPException(status_code=404, detail="未找到简历记录")

        
        return {
            "resume_id": resume_id,
            "score": score,
            "recommended_position": recommended,
            "analysis": analysis
        }
    except Exception as e:
        print("❌ LLM 分析失败：", e)
        raise FastAPIHTTPException(status_code=500, detail="LLM 分析失败")

@app.post("/save-analysis")
async def save_analysis(payload: dict):
    resume_id = payload.get("resume_id")
    score = payload.get("score")
    recommended_position = payload.get("recommended_position")
    analysis = payload.get("analysis")

    if not resume_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少 resume_id")

    existing = await resume_details_col.find_one({"resume_id": resume_id})
    if existing:
        await resume_details_col.update_one(
            {"resume_id": resume_id},
            {"$set": {
                "score": score,
                "recommended_position": recommended_position,
                "analysis": analysis
            }}
        )
    else:
        await resume_details_col.insert_one({
            "resume_id": resume_id,
            "score": score,
            "recommended_position": recommended_position,
            "analysis": analysis,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return {"message": "分析结果已保存", "resume_id": resume_id}
@app.post("/verify-code-login")
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

    
    matched_user = await find_user_by({"phone": phone})

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

@app.post("/llm/promotion")
async def llm_promotion(data: dict):
    employee_id = str(data.get("id"))
    db = await employees_col.find().to_list(length=None)
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

@app.post("/llm/dismissal")
async def llm_dismissal(data: dict):
    employee_id = data.get("id")
    db = await employees_col.find().to_list(length=None)
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

@app.post("/llm/interactive-eval")
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

    record = await resume_details_col.find_one({"resume_id": resume_id})
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
                {"role": "system", "content": "请根据提示内容给出简洁、专业的建议"},
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

@app.post("/talent")
async def add_talent(entry: dict):
    await talent_pool_col.insert_one(entry)
    count = await talent_pool_col.count_documents({})
    return {"message": "已保存", "count": count}

@app.get("/talent")
async def get_talent_pool():
    return await talent_pool_col.find().to_list(length=None)


def clean_mongo_id(doc):
    """把 _id 转换成字符串，避免 FastAPI 500 错误"""
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

@app.get("/talent-pool")
async def get_talent_pool_data():
    raw_data = await talent_pool_col.find().to_list(length=None)
    return [clean_mongo_id(doc) for doc in raw_data]

@app.post("/talent-pool")
async def add_talent_pool_entry(entry: dict):
    await talent_pool_col.insert_one(entry)
    count = await talent_pool_col.count_documents({})
    return {"message": "添加成功", "count": count}

@app.delete("/employees/{employee_id}")
async def delete_employee_by_id(employee_id: str):

    filter_criteria = {"$or": []}
    try:
        filter_criteria["$or"].append({"_id": ObjectId(employee_id)})
    except Exception:
        pass

    filter_criteria["$or"].extend([
        {"id": employee_id},
        {"工号": employee_id}
    ])
    result = await employees_col.delete_one(filter_criteria)
    return result.deleted_count

@app.post("/promotion/submit-to-hr")
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
    insert_result = await promotion_suggestions_col.insert_one(suggestion_record)
    suggestion_record["_id"] = str(insert_result.inserted_id)  # 👈 转成 str
    print("📤 收到升职建议：", suggestion_record)
    return {"message": "升职建议已提交给 HR", "data": suggestion_record}

@app.post("/dismissal/submit-to-hr")
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
    await dismissal_suggestions_col.insert_one(suggestion_record)
    return {"message": "开除建议已提交给 HR", "data": suggestion_record}

@app.get("/current-user")
async def get_current_user(request: Request):
    print("🧪 Cookie 全部内容：", request.cookies)
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    user = await find_user_by({"username": username})
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



@app.post("/logout")
async def logout():
    response = JSONResponse({"message": "已退出登录"})
    response.delete_cookie("current_user")
    return response

def get_current_user_role(request: Request) -> str:
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    import asyncio
    user = asyncio.run(find_user_by({"username": username}))
    if not user:
        raise FastAPIHTTPException(status_code=404, detail="用户不存在")
    return user["role"]
def clean_mongo_id(doc):
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

@app.get("/promotion/pending")
async def get_pending_promotions():
    data = await promotion_suggestions_col.find({
        "status": "待处理",
        "to": "hr"
    }).to_list(length=None)
    print("📦 当前数据库中 promotion_suggestions_col 内容：", data)
    data = [clean_mongo_id(item) for item in data]
    print("✅ 返回升职建议（已清洗）：", data)
    return {"data": data}

@app.get("/tracking/pending")
async def get_tracking_tasks():
    promotions = await promotion_suggestions_col.find({"status": "处理中"}).to_list(length=None)
    dismissals = await dismissal_suggestions_col.find({"status": "处理中"}).to_list(length=None)
    return {
        "promotion": [clean_mongo_id(d) for d in promotions],
        "dismissal": [clean_mongo_id(d) for d in dismissals]
    }
@app.post("/promotion/mark-done")
async def mark_promotion_done(data: dict):
    employee_id = str(data.get("employee_id"))
    db = await promotion_suggestions_col.find().to_list(length=None)
    for item in db:
        if str(item.get("employee_id")) == employee_id and item.get("status") == "待处理":
            item["status"] = "已处理"
    await promotion_suggestions_col.replace_one({"id": item["id"]}, item)
    return {"message": "升职建议已处理"}

@app.post("/dismissal/mark-done")
async def mark_dismissal_done(data: dict):
    employee_id = str(data.get("employee_id"))
    record = await dismissal_suggestions_col.find_one({"employee_id": employee_id, "status": "待处理"})
    if record:
        await dismissal_suggestions_col.update_one(
            {"_id": record["_id"]},
            {"$set": {"status": "已处理"}}
        )
    return {"message": "开除建议已处理"}

@app.delete("/talent/{talent_id}")
async def delete_talent(talent_id: str):
    result = await talent_pool_col.delete_one({"id": talent_id})
    if result.deleted_count == 0:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应记录")
    return {"message": "人才库记录已删除", "id": talent_id}




@app.post("/batch-analyze-resumes-brief")
async def batch_analyze_resumes_model2(files: list[UploadFile] = File(...)):
    print("🚀 /batch-analyze-resumes-brief进入，共上传文件数：", len(files))

    if len(files) > 20:
        raise FastAPIHTTPException(status_code=400, detail="上传文件数量不能超过 20 个")

    summary = []
    detailed_data = []

    today = datetime.now().strftime("%Y%m%d")
    existing_ids = []
    for db_file in ["recommend.json", "recommend_history.json",
                    "batch_resume_summary.json", "batch_resume_features.json"]:
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
                except Exception:
                    continue
    starting_index = max(existing_ids, default=0) + 1

    for i, file in enumerate(files):
        print(f"📄 处理第 {i+1} 个文件：{file.filename}")
        if file.filename.startswith(".") or not file.filename.lower().endswith((".pdf", ".docx")):
            print(f"⚠️ 跳过无效文件：{file.filename}")
            continue
        try:
            resume_text = extract_text(file)
            features = ensure_all_features(extract_structured_features(resume_text))

            score_raw = model2.predict(pd.DataFrame([{
                "学历_x": features["学历_x"],
                "证书数_x": features["证书数_x"]
            }]))[0]
            score = round(float(score_raw) * 100 if score_raw <= 1 else score_raw, 2)

            resume_id  = f"{today}-{starting_index + i:02d}-0"
            resume_name = file.filename.rsplit(".", 1)[0]

            summary.append({
                "resume_id": resume_id,
                "name": resume_name,
                "score": score,
                "recommended_position": "待生成",
                "学历_x": features["学历_x"],
                "证书数_x": features["证书数_x"],
                "年龄": 0
            })

            detailed_data.append({
                "resume_id": resume_id,
                "name": resume_name,
                "score": score,
                "analysis": "待生成",
                "score_breakdown": features,
                "年龄": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            print("❌ 处理失败：", file.filename, str(e))
            traceback.print_exc()

    if detailed_data:
        try:
            await resume_details_col.insert_many(detailed_data)
        except Exception as e:
            print("❌ insert_many 失败：", str(e))
            traceback.print_exc()

    print("✅ 最终 summary 返回条数：", len(summary))
    return JSONResponse(content=summary if summary else [])
@app.get("/batch-resume/{resume_id}")
async def get_resume_analysis(resume_id: str):
    item = await resume_details_col.find_one({"resume_id": resume_id})
    if not item:
        raise FastAPIHTTPException(status_code=404, detail="未找到简历分析记录")
    return {"data": item}

@app.get("/resume-report/{resume_id}")
async def get_resume_report(resume_id: str):
    item = await resume_details_col.find_one({"resume_id": resume_id})
    
    needs_analysis = not item or item.get("analysis") == "待生成" or not item.get("recommended_position")
    if needs_analysis:
        
        await llm_analyze_resume({"resume_id": resume_id})
        item = await resume_details_col.find_one({"resume_id": resume_id})
        if not item:
            raise FastAPIHTTPException(status_code=404, detail="未找到简历分析记录")
    
    return {
        "resume_id": item.get("resume_id"),
        "score": item.get("score"),
        "recommended_position": item.get("recommended_position"),
        "analysis": item.get("analysis")
    }
@app.get("/resume/{resume_id}")
async def get_resume_meta(resume_id: str):
    """查詢簡歷元資料 & 分析結果（不含檔案本體）"""
    doc = await resume_details_col.find_one({"resume_id": resume_id})
    if not doc:
        raise HTTPException(status_code=404, detail="未找到該簡歷")
    # 把 _id、gridfs_id 轉成字串，方便前端顯示
    doc["_id"] = str(doc["_id"])
    doc["gridfs_id"] = str(doc["gridfs_id"])
    return doc


@app.get("/resume/{resume_id}/download")
async def download_resume_file(resume_id: str):
    """下載原始 PDF/DOCX"""
    doc = await resume_details_col.find_one({"resume_id": resume_id})
    if not doc:
        raise HTTPException(status_code=404, detail="未找到該簡歷")

    gridfs_id = doc.get("gridfs_id")
    try:
        grid_file = fs.get(ObjectId(gridfs_id))
        return Response(grid_file.read(),
                        media_type="application/octet-stream",
                        headers={"Content-Disposition": f'attachment; filename="{doc["filename"]}"'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下載失敗：{e}")
@app.post("/batch-resume/{resume_id}/analyze")
async def analyze_resume_by_id(resume_id: str):
    item = await resume_details_col.find_one({"resume_id": resume_id})
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

        await resume_details_col.update_one(
            {"resume_id": resume_id},
            {"$set": {
                "score": score,
                "recommended_position": recommended,
                "analysis": analysis
            }}
        )

        return {"message": "分析完成", "resume_id": resume_id, "analysis": analysis}
    except Exception as e:
        print("❌ 分析失败：", e)
        raise FastAPIHTTPException(status_code=500, detail="分析失败")

@app.post("/recommend-to-admin")
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

    await admin_recommendations_col.insert_one(record)

    return {"message": "推荐已提交至管理员审批", "data": record}

@app.get("/admin/recommendations")
async def get_admin_recommendations():
    print("✅ 管理员获取推荐数据")
    raw = await admin_recommendations_col.find().to_list(length=None)
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

@app.patch("/admin/recommendations/{recommend_id}")
async def update_admin_recommendation(recommend_id: str, update: dict):
    result = await admin_recommendations_col.update_one(
        {"id": recommend_id},
        {"$set": {"status": update.get("status")}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="推荐记录不存在")
    return {"message": "更新成功", "updated_id": recommend_id}

@app.delete("/admin/recommendations/{recommend_id}")
async def delete_admin_recommendation(recommend_id: str):
    result = await admin_recommendations_col.delete_one({"id": recommend_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="推荐记录未找到")
    return {"message": "推荐记录已删除", "id": recommend_id}

@app.post("/update-realname")
async def update_realname(request: Request, payload: dict = Body(...)):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    realname = payload.get("realname", "").strip()
    if not realname:
        raise FastAPIHTTPException(status_code=400, detail="姓名不能为空")

    from mongodbapi import update_user

    await update_user({"username": username}, {"realname": realname})
    return {"message": "姓名已更新", "realname": realname}

@app.post("/update-employee-id")
async def update_employee_id(request: Request, payload: dict = Body(...)):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")
    employee_id = payload.get("employee_id", "").strip()
    if not employee_id:
        raise FastAPIHTTPException(status_code=400, detail="工号不能为空")

    from mongodbapi import update_user
    
    employees = await employees_col.find().to_list(length=None)
    matched = next((e for e in employees if str(e.get("id") or e.get("工号")) == employee_id), None)
    realname = matched.get("name") or matched.get("姓名") if matched else None
    
    update_fields = {"id": employee_id}
    if realname:
        update_fields["realname"] = realname
    
    await update_user({"username": username}, update_fields)
    
    return {"message": "工号已更新", "id": employee_id}
@app.get("/employee/match-by-id/{employee_id}")
async def match_employee_by_id(employee_id: str):
    db = await employees_col.find().to_list(length=None)
    employee = next((e for e in db if str(e.get("id") or e.get("工号")) == str(employee_id)), None)
    if not employee:
        raise FastAPIHTTPException(status_code=404, detail="未找到匹配的员工")
    return {"message": "匹配成功", "data": employee}

@app.post("/employee/analyze-and-link")
async def analyze_and_link_employee(data: dict):
    employee_id = data.get("employee_id")
    if not employee_id:
        raise FastAPIHTTPException(status_code=400, detail="缺少 employee_id")

    matched = await employees_col.find_one({
    "$or": [{"id": employee_id}, {"工号": employee_id}]
})
    if not matched:
        raise FastAPIHTTPException(status_code=404, detail="员工不存在")

    employee_name = matched.get("name") or matched.get("姓名")
    if not employee_name:
        raise FastAPIHTTPException(status_code=400, detail="员工姓名不存在")

    matched = await resume_details_col.find_one(
        {"name": {"$regex": employee_name}}
    )
    if not matched:
        raise FastAPIHTTPException(status_code=404, detail="未找到匹配简历")

    resume_id = matched.get("resume_id")
    try:
        result = await analyze_resume_by_id(resume_id)
    except Exception as e:
        raise FastAPIHTTPException(status_code=500, detail=f"分析失败：{str(e)}")

    
    await employees_col.update_one(
        {"$or": [{"id": employee_id}, {"工号": employee_id}]},
        {"$set": {"resume_id": resume_id}}
    )

    return {"message": "分析完成并已绑定", "resume_id": resume_id, "analysis": result}
@app.get("/tasks")
async def get_tasks():
    return await submitted_tasks_col.find().to_list(length=None)
@app.post("/task/submit")
async def submit_task(request: Request, payload: dict = Body(...)):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    task_text = payload.get("task", "").strip()
    leader_id = payload.get("leader_id", "").strip()
    if not task_text or not leader_id:
        raise FastAPIHTTPException(status_code=400, detail="任务内容或 leader 工号不能为空")
    
    leader = await find_user_by({"id": leader_id})
    if not leader:
        raise FastAPIHTTPException(status_code=404, detail="未找到对应 leader")
    
    user = await find_user_by({"username": username})
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

    await submitted_tasks_col.insert_one(task_entry)
    return {"message": "任务已提交", "data": task_entry}

@app.get("/submitted_tasks")
async def get_submitted_tasks():
    return await submitted_tasks_col.find().to_list(length=None)

@app.post("/score-task")
async def score_task(payload: dict):
    task_id = payload.get("task_id")
    score = payload.get("score")
    comment = payload.get("comment", "")

    if not task_id or score is None:
        raise FastAPIHTTPException(status_code=400, detail="缺少评分信息")

    print(f"🟨 接收到评分任务：task_id={task_id}, score={score}")

    tasks = await submitted_tasks_col.find().to_list(length=None)
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
    await submitted_tasks_col.delete_many({})
    if tasks:
        await submitted_tasks_col.insert_many(tasks)
    print("✅ 任务评分已保存")

    promotion_db = await promotion_suggestions_col.find().to_list(length=None)
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
    await promotion_suggestions_col.insert_one(suggestion)
    print("✅ 添加到动态追踪")

    
    employee_name = task.get("from_realname") or task.get("from")
    print(f"🔍 查找员工姓名：{employee_name}")
    employees = await employees_col.find().to_list(length=None)
    
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
                existing_doc = await resume_analysis_results_col.find_one({"resume_id": resume_id})
                prev_score = existing_doc.get("score", 0) if existing_doc else 0
                prev_completion = existing_doc.get("completion_rate", 0) if existing_doc else 0

                new_doc = {
                    "resume_id": resume_id,
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
                await resume_analysis_results_col.replace_one(
                    {"resume_id": resume_id},
                    new_doc,
                    upsert=True
                )
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
@app.get("/tracking/summary")
async def tracking_summary():
    
    suggestions = await promotion_suggestions_col.find().to_list(length=None)

    
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
@app.get("/analysis-results")
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

@app.get("/profile")
async def get_profile(request: Request):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    from mongodbapi import find_user_by
    
    user = await find_user_by({"username": username})
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

@app.get("/my-promotions")
async def get_my_promotions(request: Request):
    username = request.cookies.get("current_user")
    if not username:
        raise FastAPIHTTPException(status_code=401, detail="未登录")

    from mongodbapi import find_user_by
    
    user = await find_user_by({"username": username})
    if not user:
        raise FastAPIHTTPException(status_code=404, detail="用户不存在")
    
    promotion_db = await promotion_suggestions_col.find().to_list(length=None)
    return {
        "data": [
            item for item in promotion_db
            if str(item.get("employee_id")) == str(user.get("id"))
        ]
    }