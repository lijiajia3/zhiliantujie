import React, { useState, useEffect } from "react";
import axios from "axios";

export default function HRManageEmployeePage() {
  const [employees, setEmployees] = useState([]);
  const [formData, setFormData] = useState({
    id: "",
    name: "",
    position: "",
    experience: "",
    status: "在职",
    note: ""
  });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get("/api/employees");
      console.log("✅ 返回数据：", res.data);
      const employeesData = Array.isArray(res.data?.data)
        ? res.data.data
        : Array.isArray(res.data)
          ? res.data
          : [];
      if (employeesData.length === 0) {
        console.warn("⚠️ 未识别的员工数据结构：", res.data);
      }
      setEmployees(employeesData);
    } catch (err) {
      console.error("❌ 获取员工失败：", err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("/api/employees/add", formData);
      setFormData({ id: "", name: "", position: "", experience: "", status: "在职", note: "" });
      fetchEmployees();
    } catch (err) {
      console.error("❌ 添加失败：", err);
    }
  };

  if (!Array.isArray(employees)) {
    console.error("⚠️ 员工数据格式错误：", employees);
    return <div style={{ padding: 40 }}>⚠️ 员工数据格式错误，请检查后端返回格式</div>;
  }

  return (
    <div style={{ padding: "40px" }}>
      <h1>员工管理页面（HR）</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: 40 }}>
        <div><input type="text" name="id" value={formData.id} onChange={handleChange} placeholder="工号" required /></div>
        <div><input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="姓名" required /></div>
        <div><input type="text" name="position" value={formData.position} onChange={handleChange} placeholder="职位" required /></div>
        <div><input type="text" name="experience" value={formData.experience} onChange={handleChange} placeholder="工龄" required /></div>
        <div><textarea name="note" value={formData.note} onChange={handleChange} placeholder="备注" /></div>
        <button type="submit">添加员工</button>
      </form>

      <table border="1" cellPadding={10} style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>工号</th>
            <th>姓名</th>
            <th>职位</th>
            <th>工龄</th>
            <th>状态</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(employees) && employees.length > 0 ? (
            employees.map((emp, idx) => (
              <tr key={idx}>
                <td>{emp.id}</td>
                <td>{emp.name}</td>
                <td>{emp.position}</td>
                <td>{emp.experience}</td>
                <td>{emp.status}</td>
                <td>{emp.note}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6" style={{ textAlign: "center", color: "#999" }}>暂无员工信息</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}