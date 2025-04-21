from motor.motor_asyncio import AsyncIOMotorClient
import os

# —— 1. 连接 MongoDB —— 
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client    = AsyncIOMotorClient(MONGO_URL)
db        = client["zhiliantujie"]

# —— 2. 各集合（Collection）句柄 —— 
users_col                     = db["users"]
employees_col                 = db["employees"]
recommend_col                 = db["recommend"]
recommend_history_col         = db["recommend_history"]
talent_pool_col               = db["talent_pool"]
resume_details_col            = db["batch_resume_details"]
promotion_suggestions_col     = db["promotion_suggestions"]
dismissal_suggestions_col     = db["dismissal_suggestions"]
admin_recommendations_col     = db["admin_recommendations"]
submitted_tasks_col           = db["submitted_tasks"]
resume_analysis_results_col   = db["resume_analysis_results"]

# —— 3. 示例 CRUD 辅助函数 —— 
async def get_all_employees():
    cursor = employees_col.find({})
    docs = await cursor.to_list(length=None)
    for d in docs:
        d["id"] = str(d.get("_id") or d.get("id"))
    return docs

async def add_employees(employees: list[dict]):
    result = await employees_col.insert_many(employees)
    return [str(_id) for _id in result.inserted_ids]

async def delete_employee_by_id(employee_id: str):
    result = await employees_col.delete_one({
        "$or": [
            {"_id": employee_id},
            {"id": employee_id},
            {"工号": employee_id}
        ]
    })
    return result.deleted_count

async def get_all_users():
    cursor = users_col.find({})
    return await cursor.to_list(length=None)

async def find_user_by(filter_dict):
    return await users_col.find_one(filter_dict)

async def insert_user(user_data: dict):
    return await users_col.insert_one(user_data)

async def update_user(filter_dict, update_dict):
    return await users_col.update_one(filter_dict, {"$set": update_dict})