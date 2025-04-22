import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ProfilePage() {
    const [profile, setProfile] = useState({
        username: '',
        realname: '',
        email: '',
        phone: '',
        role: '',
        id: ''
    });
    const [newEmployeeId, setNewEmployeeId] = useState("");
    const [savedEmployeeId, setSavedEmployeeId] = useState(false);

    useEffect(() => {
        axios.get("/profile", { withCredentials: true })
        .then(res => setProfile(res.data))
        .catch(err => {
            console.error("❌ 获取用户信息失败", err);
        });
    }, []);

    const handleSaveEmployeeId = async () => {
        try {
            await axios.post("/update-id", {
                employee_id: newEmployeeId
            }, { withCredentials: true });
            alert("✅ 工号已更新");
            
            const refreshed = await axios.get("/profile", { withCredentials: true });
            setProfile(refreshed.data);
            setNewEmployeeId("");
            setSavedEmployeeId(true);
            setTimeout(() => setSavedEmployeeId(false), 2000);
        } catch (err) {
            alert("❌ 工号更新失败，请稍后再试");
            console.error(err);
        }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-blue-100 flex items-center justify-center p-6">
        <div className="bg-white shadow-xl rounded-xl p-10 max-w-xl w-full">
          <h1 className="text-5xl font-extrabold mb-8 text-center text-blue-800">我的信息</h1>
          <div className="space-y-5 text-xl text-gray-800 tracking-wide leading-relaxed">
            <p className="border-b pb-2"><span className="font-semibold">用户名：</span>{profile.username || '—'}</p>
            <p className="border-b pb-2"><span className="font-semibold">姓名：</span>{profile.realname || '—'}</p>
            <p className="border-b pb-2"><span className="font-semibold">邮箱：</span>{profile.email || '—'}</p>
            <p className="border-b pb-2"><span className="font-semibold">手机号：</span>{profile.phone || '—'}</p>
            <p className="border-b pb-2"><span className="font-semibold">工号：</span>{profile.id || '—'}</p>
            <p className="pb-2"><span className="font-semibold">权限：</span>{profile.role || '—'}</p>
          </div>
          <hr className="my-8 border-t-2 border-dashed border-gray-300" />
          <h2 className="text-lg font-semibold text-blue-500 mt-8 mb-2">🆔 填写工号</h2>
          <div className="flex items-center gap-2 bg-gray-50 p-3 rounded-lg border border-blue-200 shadow-sm transition-all duration-700 ease-out animate-fade-in">
            <input
              type="text"
              placeholder="请输入工号..."
              value={newEmployeeId}
              onChange={(e) => setNewEmployeeId(e.target.value)}
              className="flex-1 border border-gray-300 px-3 py-1.5 rounded-full text-sm focus:outline-none focus:ring-1 focus:ring-blue-300"
            />
            <button
              onClick={handleSaveEmployeeId}
              className="bg-blue-500 text-white px-3 py-1.5 text-sm rounded-full hover:bg-blue-600 transition"
            >
              保存
            </button>
          </div>
          {savedEmployeeId && <span className="text-green-600 text-sm ml-2">✓ 已保存</span>}
        </div>
      </div>
    );
}