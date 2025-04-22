import React, { useEffect, useState } from "react";
import axios from "axios";

export default function LeaderApprovePage() {
  const [recommendations, setRecommendations] = useState([]);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [currentApproveId, setCurrentApproveId] = useState(null);
  const [employeePosition, setEmployeePosition] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [employeeName, setEmployeeName] = useState("");

  const fetchRecommendations = () => {
    axios.get("/admin/recommendations")
      .then(res => {
        console.log("✅ 获取推荐数据：", res.data);
        setRecommendations(res.data?.data || []);
      })
      .catch(err => {
        console.error("❌ 获取推荐失败", err);
      });
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleApproval = async (id, newStatus) => {
    if (newStatus === "已录用") {
      setCurrentApproveId(id);
      setModalIsOpen(true);
    } else if (newStatus === "不通过") {
      try {
        await axios.delete(`/admin/recommendations/${id}`);
        fetchRecommendations();
      } catch (err) {
        console.error("❌ 删除失败：", err);
      }
    }
  };

  const submitEmployee = async () => {
    try {
      const item = recommendations.find(r => r.id === currentApproveId);
      const nameToUse = employeeName || item.name || "未命名员工";

      if (!employeeId || !employeePosition || !nameToUse) {
        alert("❌ 请填写完整的姓名、职位和工号信息");
        return;
      }

      const payload = [{
        name: String(nameToUse || "").trim(),
        id: String(employeeId || "").trim(),
        position: String(employeePosition || "").trim()
      }];

      console.log("📤 提交数据：", payload);
      await axios.post("/employees", payload);
      
      await axios.delete(`/admin/recommendations/${currentApproveId}`);
      setModalIsOpen(false);
      setEmployeeName("");
      setEmployeeId("");
      setEmployeePosition("");
      fetchRecommendations();
    } catch (err) {
      console.error("❌ 员工录入失败：", err);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">推荐审批</h1>
      {recommendations.length === 0 ? (
        <p className="text-gray-500">暂无推荐数据。</p>
      ) : (
        <div className="space-y-4">
          {recommendations.map((item, index) => (
            <div key={index} className="p-4 border rounded shadow">
              <p><strong>简历编号：</strong>{item.resume_id}</p>
              <p><strong>姓名：</strong>{item.name}</p>
              <p><strong>推荐理由：</strong>{item.reason}</p>
              <div>
                <strong>LLM 报告：</strong>
                <pre className="whitespace-pre-wrap text-sm text-gray-800">{item.analysis}</pre>
              </div>
              <p><strong>当前状态：</strong>{item.status}</p>
              <div className="mt-2 space-x-2">
                <button
                  className="bg-green-500 text-white px-3 py-1 rounded"
                  onClick={() => handleApproval(item.id, "已录用")}
                  disabled={item.status !== "待审批"}
                >
                  同意
                </button>
                <button
                  className="bg-red-500 text-white px-3 py-1 rounded"
                  onClick={() => handleApproval(item.id, "不通过")}
                  disabled={item.status !== "待审批"}
                >
                  拒绝
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      {modalIsOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">录用信息填写</h2>
            <input
              type="text"
              placeholder="姓名"
              value={employeeName}
              onChange={(e) => setEmployeeName(e.target.value)}
              className="border p-2 mb-4 w-full"
            />
            <p className="text-sm text-gray-500 mb-2">默认将使用简历中的姓名，如需修改可在此输入</p>
            <input
              type="text"
              placeholder="职位"
              value={employeePosition}
              onChange={(e) => setEmployeePosition(e.target.value)}
              className="border p-2 mb-4 w-full"
            />
            <input
              type="text"
              placeholder="工号"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="border p-2 mb-4 w-full"
            />
            <div className="flex justify-end space-x-2">
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={submitEmployee}
              >
                提交
              </button>
              <button
                className="bg-gray-400 text-white px-4 py-2 rounded"
                onClick={() => {
                  setModalIsOpen(false);
                  setEmployeeName("");
                }}
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}