import React, { useEffect, useState, useRef } from "react";
import Modal from "react-modal";
import * as XLSX from "xlsx";
import axios from "axios";
axios.defaults.withCredentials = true;

export default function EmployeeManagePage() {
  const [employees, setEmployees] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [promotionPendingList, setPromotionPendingList] = useState([]);
  const [dismissalPendingList, setDismissalPendingList] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [suggestionText, setSuggestionText] = useState("");
  const [originalSuggestion, setOriginalSuggestion] = useState("");
  const [loadingModal, setLoadingModal] = useState(false);
  const [dismissalText, setDismissalText] = useState("");
  const [originalDismissal, setOriginalDismissal] = useState("");
  const [showDismissalModal, setShowDismissalModal] = useState(false);

  const handlePromotion = async (emp) => {
    console.log("📤 正在请求升职建议，传入对象：", emp);
    setLoadingModal(true);
    try {
      const res = await axios.post("/api/llm/promotion", emp, { withCredentials: true });
      setOriginalSuggestion(res.data.suggestion);
      setSuggestionText(res.data.suggestion);
      setSelectedEmployee(emp);
      setShowModal(true);
    } catch (error) {
      alert("❌ 获取升职建议失败：" + (error?.response?.data?.detail || "未知错误"));
      console.error(error);
    } finally {
      setLoadingModal(false);
    }
  };

  const handleSubmitToHR = async () => {
    try {
    await axios.post("/api/promotion/submit", {
      employee_id: selectedEmployee.id,
      employee_name: selectedEmployee.name,
      modified_suggestion: suggestionText,
      from: "admin",
      to: "hr"
    });
      const updated = employees.map(emp =>
        emp.id === selectedEmployee.id ? { ...emp, promotionStatus: "待处理" } : emp
      );
      setEmployees(updated);
      alert("✅ 升职建议已提交给 HR");
      setShowModal(false);
    } catch (error) {
      alert("❌ 提交给 HR 失败");
      console.error(error);
    }
  };

  const handleDelete = async (empId) => {
    try {
      await axios.delete(`/api/employees/${empId}`);
      const updatedEmployees = employees.filter((e) => e.id !== empId);
      setEmployees(updatedEmployees);
      alert("🗑️ 员工已删除！");
    } catch (err) {
      alert("❌ 删除失败，请检查后端接口");
      console.error(err);
    }
  };

  const handleDismissal = (emp) => {
    setSelectedEmployee(emp);
    setDismissalText("");
    setOriginalDismissal("");
    setShowDismissalModal(true);
  };

  const handleSubmitDismissalToHR = async () => {
    try {
      await axios.post("/api/dismissal/submit", {
        employee_id: selectedEmployee.id,
        employee_name: selectedEmployee.name,
        original_suggestion: originalDismissal,
        modified_suggestion: dismissalText,
        from: "admin",
        to: "hr"
      });
      const updated = employees.map(emp =>
        emp.id === selectedEmployee.id ? { ...emp, dismissalStatus: "待处理" } : emp
      );
      setEmployees(updated);
      alert("✅ 开除建议已提交给 HR");
      setShowDismissalModal(false);
    } catch (error) {
      alert("❌ 提交给 HR 失败");
      console.error(error);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = (evt) => {
      const data = new Uint8Array(evt.target.result);
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const rawData = XLSX.utils.sheet_to_json(worksheet);
      const translatedData = rawData.map((item) => ({
        id: item["工号"],
        name: item["姓名"],
        position: item["职位AL"],
        experience: item["工龄"],
        gender: item["性别"],
        age: item["年龄J"],
        degree: item["学历L"],
        note: item["个人简历"] || item["个人简历O"] || ""
      }));
      setEmployees(translatedData);
    };

    if (file) {
      reader.readAsArrayBuffer(file);
    }
  };

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const res = await axios.get("/api/employees");
        console.log("🧩 后端返回的数据：", res.data);
        const data = Array.isArray(res.data.data) ? res.data.data : [];
        setEmployees(data);
      } catch (err) {
        console.error("❌ 获取员工数据失败：", err);
      }
    };

    fetchEmployees();
  }, []);
  
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const res = await axios.get("/api/current-user");
        setCurrentUser(res.data);
      } catch (error) {
        console.error("❌ 获取当前用户信息失败：", error);
      }
    };
    fetchCurrentUser();
  }, []);

  useEffect(() => {
    if (currentUser?.role === 'hr') {
      axios.get("/api/promotion/pending")
        .then(res => setPromotionPendingList(res.data.data || []))
        .catch(err => console.error("升职待处理加载失败", err));

      axios.get("/api/dismissal/pending")
        .then(res => setDismissalPendingList(res.data.data || []))
        .catch(err => console.error("开除待处理加载失败", err));
    }
  }, [currentUser]);

  if (!currentUser) {
    return <div style={{ padding: "40px" }}>⏳ 正在加载用户信息...</div>;
  }

  if (!Array.isArray(employees)) {
    return (
      <div style={{ padding: "40px" }}>
        <h1>员工管理页面（管理员）</h1>
        <p style={{ color: "red" }}>⚠️ 无效的员工数据格式，请检查后端返回值。</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "40px" }}>
      <div style={{ marginBottom: "20px" }}>
        <label htmlFor="fileUpload">📥 导入员工 Excel 文件：</label>
        <input
          id="fileUpload"
          type="file"
          accept=".xlsx, .xls"
          onChange={handleFileUpload}
          style={{ marginLeft: "10px" }}
        />
      </div>
      <div style={{ marginBottom: "20px" }}>
        <h3>📝 手动添加员工信息：</h3>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const newEmployee = {
              name: e.target.name.value,
              id: e.target.id.value,
              position: e.target.position.value,
              experience: e.target.experience.value,
              status: e.target.status.value,
            };
            setEmployees([...employees, newEmployee]);
            e.target.reset();
          }}
        >
          <input name="name" placeholder="姓名" required style={{ marginRight: "10px" }} />
          <input name="id" placeholder="工号" required style={{ marginRight: "10px" }} />
          <input name="position" placeholder="职位" style={{ marginRight: "10px" }} />
          <input name="experience" placeholder="工龄" style={{ marginRight: "10px" }} />
          <input name="status" placeholder="当前状态" style={{ marginRight: "10px" }} />
          <button type="submit">添加</button>
        </form>
        <div style={{ marginTop: "10px", color: "green" }}>
          <small>👆 添加后数据暂存在前端，需点击“提交”或后端处理才会永久保存</small>
        </div>
      </div>
      <h1>员工管理页面（管理员）</h1>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "20px", textAlign: "center" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "center" }}>姓名</th>
            <th style={{ textAlign: "center" }}>工号</th>
            <th style={{ textAlign: "center" }}>职位</th>
            <th style={{ textAlign: "center" }}>工龄</th>
            <th style={{ textAlign: "center" }}>当前状态</th>
            <th style={{ textAlign: "center" }}>操作：建议升职</th>
            <th style={{ textAlign: "center" }}>操作：建议开除</th>
            <th style={{ textAlign: "center" }}>操作：删除</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((emp, idx) => (
            <tr
              key={idx}
              style={{
                borderTop: "1px solid #ccc",
                transition: "background-color 0.3s ease",
                cursor: "pointer"
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f0f4f8")}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
            >
              <td style={{ padding: "14px 12px", textAlign: "center" }}>{emp.name}</td>
              <td style={{ padding: "14px 12px", textAlign: "center" }}>{emp.id}</td>
              <td style={{ padding: "14px 12px", textAlign: "center" }}>{emp.position}</td>
              <td style={{ padding: "14px 12px", textAlign: "center" }}>{emp.experience}</td>
              <td style={{ padding: "14px 12px", textAlign: "center" }}>{emp.status}</td>
              <td style={{ textAlign: "center" }}>
                {currentUser.role === "hr" ? (
                promotionPendingList.some(p => p.employee_id === emp.id) ? (
                    <button onClick={async () => {
                      await axios.post("/api/promotion/mark-done", { employee_id: emp.id });
                      setPromotionPendingList(promotionPendingList.filter(p => p.employee_id !== emp.id));
                    }}>✅ 已处理</button>
                  ) : "—"
                ) : (
                  <button onClick={() => handlePromotion(emp)}>建议升职</button>
                )}
              </td>
              <td style={{ textAlign: "center" }}>
                {currentUser.role === "hr" ? (
                dismissalPendingList.some(p => p.employee_id === emp.id) ? (
                    <button onClick={async () => {
                      await axios.post("/api/dismissal/mark-done", { employee_id: emp.id });
                      setDismissalPendingList(dismissalPendingList.filter(p => p.employee_id !== emp.id));
                    }}>✅ 已处理</button>
                  ) : "—"
                ) : (
                  <button onClick={() => handleDismissal(emp)}>建议开除</button>
                )}
              </td>
              <td style={{ padding: "14px 12px", textAlign: "center" }}>
                <button onClick={() => handleDelete(emp.id)}>删除</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: "20px" }}>
        <button
          onClick={async () => {
            try {
              const res = await axios.post("/api/employees/save", employees);
              alert("✅ 员工信息已保存到后端！");
            } catch (error) {
              alert("❌ 保存失败，请检查后端接口是否正常");
              console.error("保存失败", error);
            }
          }}
        >
          💾 提交全部员工数据到后端
        </button>
      </div>
      {showModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, width: "100%", height: "100%",
          backgroundColor: "rgba(0,0,0,0.5)", display: "flex",
          justifyContent: "center", alignItems: "center", zIndex: 1000
        }}>
          <div style={{ background: "white", padding: "20px", width: "500px", borderRadius: "8px" }}>
            <h3>📈 升职建议（可修改后提交）</h3>
            <textarea
              rows={6}
              value={suggestionText}
              onChange={(e) => setSuggestionText(e.target.value)}
              style={{ width: "100%", marginBottom: "10px" }}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button onClick={() => setShowModal(false)}>取消</button>
              <button onClick={handleSubmitToHR}>提交给 HR</button>
            </div>
          </div>
        </div>
      )}
      {showDismissalModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, width: "100%", height: "100%",
          backgroundColor: "rgba(0,0,0,0.5)", display: "flex",
          justifyContent: "center", alignItems: "center", zIndex: 1000
        }}>
          <div style={{ background: "white", padding: "20px", width: "500px", borderRadius: "8px" }}>
            <h3>📉 开除建议（可修改后提交）</h3>
            <textarea
              rows={6}
              value={dismissalText}
              onChange={(e) => setDismissalText(e.target.value)}
              style={{ width: "100%", marginBottom: "10px" }}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button onClick={() => setShowDismissalModal(false)}>取消</button>
              <button onClick={handleSubmitDismissalToHR}>提交给 HR</button>
            </div>
          </div>
        </div>
      )}
      {loadingModal && (
        <div style={{
          position: "fixed", top: 0, left: 0, width: "100%", height: "100%",
          backgroundColor: "rgba(0,0,0,0.4)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 2000
        }}>
          <div style={{ background: "white", padding: "20px 40px", borderRadius: "8px", fontSize: "18px" }}>
            ⏳ 正在加载，请稍候...
          </div>
        </div>
      )}
    </div>
  );
}