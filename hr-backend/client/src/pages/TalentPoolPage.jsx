import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function TalentPoolPage() {
  const role = localStorage.getItem('role');
  const navigate = useNavigate();

  const [talentPool, setTalentPool] = useState([]);
  
  useEffect(() => {
    axios.get("/api/talent-pool")
      .then(res => {
        if (Array.isArray(res.data)) {
          setTalentPool(res.data);
        }
      }).catch(err => {
        console.error("获取人才库失败", err);
      });
  }, []);
  
  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/talent-pool/${id}`)
      setTalentPool(talentPool.filter((item) => item.id !== id));
    } catch (error) {
      console.error("❌ 删除失败", error);
    }
  };

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', skills: '' });

  const handleAdd = () => {
    const now = new Date();
    const id = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}-${String(talentPool.length + 1).padStart(3, '0')}`;
    const newEntry = {
      id,
      name: formData.name,
      skills: formData.skills,
      recommender: localStorage.getItem('username') || 'HR用户',
      addedAt: now.toISOString().slice(0, 10)
    };
    axios.post("/api/talent-pool", newEntry)
      .catch(err => {
        console.error("保存失败", err);
      });
    setTalentPool([...talentPool, newEntry]);
    setFormData({ name: '', skills: '' });
    setShowForm(false);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-extrabold text-gray-800 mb-2">🎯 人才储备库</h1>
      <p className="text-gray-600 mb-6">展示未录用但具潜力的候选人信息，方便后续评估与追踪。</p>

      {(role === 'admin' || role === 'hr') && (
        <>
          <button
            className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold px-5 py-2 rounded shadow mb-4 transition-all duration-300"
            onClick={() => setShowForm(!showForm)}
          >
            ➕ 加入人才储备库
          </button>

          {showForm && (
            <div className="mb-4 space-y-2">
              <input
                type="text"
                placeholder="姓名"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="border border-gray-300 rounded px-3 py-2 mr-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <input
                type="text"
                placeholder="技能"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                className="border border-gray-300 rounded px-3 py-2 mr-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <button
                onClick={handleAdd}
                className="bg-green-600 text-white px-3 py-1 rounded"
              >
                提交
              </button>
            </div>
          )}
        </>
      )}

      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "20px" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: "12px" }}>编号</th>
            <th style={{ textAlign: "left", padding: "12px" }}>姓名</th>
            <th style={{ textAlign: "left", padding: "12px" }}>技能</th>
            <th style={{ textAlign: "left", padding: "12px" }}>推荐人</th>
            <th style={{ textAlign: "left", padding: "12px" }}>加入时间</th>
            <th style={{ textAlign: "left", padding: "12px" }}>操作</th>
          </tr>
        </thead>
        <tbody>
          {talentPool.map((item) => (
            <tr
              key={item.id}
              style={{
                borderTop: "1px solid #ccc",
                transition: "background-color 0.3s ease",
                cursor: "pointer"
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f0f4f8")}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
            >
              <td style={{ padding: "12px", textAlign: "left" }}>{item.id}</td>
              <td style={{ padding: "12px", textAlign: "left" }}>{item.name}</td>
              <td style={{ padding: "12px", textAlign: "left" }}>{item.skills}</td>
              <td style={{ padding: "12px", textAlign: "left" }}>{item.recommender}</td>
              <td style={{ padding: "12px", textAlign: "left" }}>{item.addedAt}</td>
              <td style={{ padding: "12px", textAlign: "left" }}>
                <details>
                  <summary style={{ cursor: "pointer", color: "#3b82f6" }}>更多操作</summary>
                  <div style={{ marginTop: "6px" }}>
                    <button
                      onClick={() => navigate(`/analyze/${item.id}`)}
                      className="text-blue-600 hover:text-blue-800 block mb-1"
                    >
                      📊 查看分析报告
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="text-red-600 hover:text-red-800 block"
                    >
                      🗑️ 删除
                    </button>
                  </div>
                </details>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}