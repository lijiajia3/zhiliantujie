import React, { useEffect, useState } from "react";
import axios from "axios";

export default function LeaderEmployeePage() {
  const [employees, setEmployees] = useState([]);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get("/api/leader/employees", { withCredentials: true });
      setEmployees(res.data || []);
    } catch (error) {
      console.error("❌ 获取员工失败", error);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handlePromotion = async (emp) => {
    try {
    const res = await axios.post("/api/llm/promotion", emp);
      alert(`📈 升职建议已提交：${res.data.suggestion}`);
    } catch (error) {
      alert("❌ 提交升职建议失败");
      console.error(error);
    }
  };

  const handleDismissal = async (emp) => {
    try {
    const res = await axios.post("/api/llm/dismissal", emp);
      alert(`📉 开除建议已提交：${res.data.suggestion}`);
    } catch (error) {
      alert("❌ 提交开除建议失败");
      console.error(error);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ marginBottom: "20px" }}>
        <h3>➕ 通过工号添加成员：</h3>
        <input
          type="text"
          placeholder="请输入工号"
          id="employeeIdInput"
          style={{ padding: "5px 10px", width: "200px", marginRight: "10px" }}
        />
        <button
          onClick={async () => {
            const id = document.getElementById("employeeIdInput").value.trim();
            if (!id) return alert("请输入有效工号");

            try {
              const alreadyExists = employees.some(e => String(e.id) === String(id));
              if (alreadyExists) {
                alert("⚠️ 成员已存在团队中");
                return;
              }

              const res = await axios.post("/api/leader/add-by-id", { id }, { withCredentials: true });
              await fetchEmployees();
              const newEmp = res.data;

              alert(`✅ 成员 ${newEmp.name || newEmp["姓名"]} 已添加`);
            } catch (err) {
              if (err.response?.status === 404) {
                alert("❌ 未找到该员工，请确认工号是否正确");
              } else {
                alert("❌ 添加失败，请稍后重试");
              }
              console.error("添加成员错误：", err);
            }
          }}
        >
          添加成员
        </button>
      </div>
      <h2>👥 我的团队成员</h2>
      <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "center" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "center" }}>姓名</th>
            <th style={{ textAlign: "center" }}>职位</th>
            <th style={{ textAlign: "center" }}>工龄</th>
            <th style={{ textAlign: "center" }}>当前状态</th>
            <th style={{ textAlign: "center" }}>操作</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((emp) => (
            <tr key={emp.id}>
              <td style={{ textAlign: "center" }}>{emp.name || emp["姓名"]}</td>
              <td style={{ textAlign: "center" }}>{emp.position || emp["职位AL"]}</td>
              <td style={{ textAlign: "center" }}>{emp.experience || emp["工龄"]}</td>
              <td style={{ textAlign: "center" }}>{emp.status || emp["状态"]}</td>
              <td>
                <button onClick={() => handlePromotion(emp)} style={{ marginRight: "10px" }}>
                  建议升职
                </button>
                <button onClick={() => handleDismissal(emp)}>
                  建议开除
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}