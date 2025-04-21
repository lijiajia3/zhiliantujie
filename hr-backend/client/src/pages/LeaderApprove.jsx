import React, { useEffect, useState } from "react";
import axios from "axios";

export default function LeaderApprove() {
  const [pendingList, setPendingList] = useState([]);

  const fetchData = async () => {
    try {
      const res = await axios.get("/api/recommend?status=待审批");
      setPendingList(res.data || []);
    } catch (err) {
      console.error("获取推荐列表失败：", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAction = async (id, action) => {
    try {
      await axios.post("/api/recommend/approve", {
        id,
        decision: action, 
      });
      alert(`已${action}`);
      fetchData();
    } catch (err) {
      console.error(`${action}失败：`, err);
      alert(`${action}失败`);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">主管审批列表</h1>
      {pendingList.length === 0 ? (
        <p>暂无待审批推荐。</p>
      ) : (
        pendingList.map((item) => (
          <div
            key={item.id}
            className="border rounded p-4 mb-4 shadow bg-white"
          >
            <p className="font-semibold mb-2">简历编：{item.resume_id}</p>
            <p className="text-gray-700 mb-2">推荐理由：{item.recommend_reason || "（无）"}</p>
            <div className="flex gap-4">
              <button
                className="bg-green-600 text-white px-4 py-1 rounded"
                onClick={() => handleAction(item.id, "通过")}
              >
                通过
              </button>
              <button
                className="bg-red-600 text-white px-4 py-1 rounded"
                onClick={() => handleAction(item.id, "拒绝")}
              >
                拒绝
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}