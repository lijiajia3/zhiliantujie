import React, { useEffect, useState } from "react";
import axios from "axios";

export default function MyTaskPage() {
  const [promotionData, setPromotionData] = useState([]);
  const [currentTask, setCurrentTask] = useState("");
  const [leaderId, setLeaderId] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmitTask = async () => {
    if (!currentTask.trim()) {
      alert("请填写任务内容");
      return;
    }
    try {
      await axios.post("/task/submit", {
        task: currentTask,
        leader_id: leaderId
      });
      alert("✅ 任务已提交等待审批");
      setCurrentTask("");
    } catch (err) {
      console.error("❌ 提交任务失败", err);
      alert("提交失败，请稍后重试");
    }
  };

  useEffect(() => {
    axios.get("/my-promotions")
      .then(res => {
        setPromotionData(res.data.promotion || []);
      })
      .catch(err => {
        console.error("❌ 获取我的任务失败", err);
      });
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ marginBottom: "30px" }}>
      <h2>📝 当前任务</h2>
      <input
        type="text"
        placeholder="请输入你的 Leader 工号"
        value={leaderId}
        onChange={(e) => setLeaderId(e.target.value)}
        style={{ width: "100%", padding: "8px", marginBottom: "10px", border: "1px solid #ccc", borderRadius: "4px" }}
      />
      <textarea
          style={{ width: "100%", height: "100px", marginBottom: "10px" }}
          value={currentTask}
          onChange={(e) => setCurrentTask(e.target.value)}
          placeholder="填写你目前完成的任务内容内容和报告..."
        />
      <button onClick={handleSubmitTask}>提交任务</button>
      </div>
      <h2>📈 我的升职建议追踪</h2>
      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "30px" }}>
        <thead>
          <tr>
            <th>建议来源</th>
            <th>建议内容</th>
            <th>当前状态</th>
          </tr>
        </thead>
        <tbody>
          {promotionData.map((item, idx) => (
            <tr key={idx}>
              <td>{item.leader}</td>
              <td>{item.reason}</td>
              <td>{item.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}