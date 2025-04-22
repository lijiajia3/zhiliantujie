import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Modal from 'react-modal';


Modal.setAppElement('#root');

function AdminEmployeePage() {
  const [employees, setEmployees] = useState([]);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [updatedRecommendation, setUpdatedRecommendation] = useState('');
  const [updatedNote, setUpdatedNote] = useState('');
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [newEmployee, setNewEmployee] = useState({
    resume_id: '',
    position: '',
    experience: '',
    score: '',
    recommended_position: '',
    note: ''
  });

  console.log("🛰 AdminEmployeePage render - modalIsOpen:", modalIsOpen, "selectedEmployee:", selectedEmployee);

  useEffect(() => {
    axios.get("/employees").then(res => {
      console.log("✅ 员工数据响应：", res.data);
      const fetched = res.data.data;
      if (Array.isArray(fetched)) {
        setEmployees(fetched);
      } else {
        console.warn("⚠️ 返回的员工数据不是数组，设置为空数组");
        setEmployees([]);
      }
    }).catch(err => {
      console.error("❌ 获取员工数据失败", err);
      setEmployees([]);
    });
  }, []);

  const handleAdjust = (emp) => {
    console.log("🛰 handleAdjust emp:", emp);
    setSelectedEmployee(emp);
    setUpdatedRecommendation(emp.recommended_position || '');
    setUpdatedNote(emp.note || '');
    setModalIsOpen(true);
  };

  return (
    <div style={{ padding: 40 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>👥 员工管理</h2>
        <button onClick={() => setAddModalOpen(true)}>➕ 添加员工</button>
      </div>
      {employees.length ? (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>ID</th>
              <th>简历编号</th>
              <th>来源</th>
              <th>录用时间</th>
              <th>职位</th>
              <th>工龄</th>
              <th>评分</th>
              <th>岗位建议</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {employees.map(emp => (
              <tr key={emp.id}>
                <td>{emp.id}</td>
                <td>{emp.resume_id}</td>
                <td>{emp.source}</td>
                <td>{emp.created_at}</td>
                <td>{emp.position || "未填写"}</td>
                <td>{emp.experience || "无"}</td>
                <td>{emp.score || "无"}</td>
                <td>{emp.recommended_position || "暂无建议"}</td>
                <td>{emp.note || "—"}</td>
                <td>
                  <button onClick={() => handleAdjust(emp)}>岗位调整</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>暂无员工数据</p>
      )}
      {modalIsOpen && (
        <Modal
          isOpen
          onRequestClose={() => setModalIsOpen(false)}
          contentLabel="岗位调整对话框"
          style={{ content: { maxWidth: 500, margin: 'auto' } }}
        >
      <div className="modal-content">
        <h3>岗位调整 - {selectedEmployee?.resume_id}</h3>
        <label>岗位建议：</label>
        <input
          type="text"
          value={updatedRecommendation}
          onChange={(e) => setUpdatedRecommendation(e.target.value)}
          style={{ width: '100%', marginBottom: 10 }}
        />
        <label>备注：</label>
        <textarea
          value={updatedNote}
          onChange={(e) => setUpdatedNote(e.target.value)}
          style={{ width: '100%', height: 100 }}
        />
        <div style={{ marginTop: 20 }}>
          <button onClick={() => {
            axios.post("/employees/update", {
              id: selectedEmployee?.id,
              recommended_position: updatedRecommendation,
              note: updatedNote,
            }).then(res => {
              console.log("✅ 修改成功：", res.data);
              setModalIsOpen(false);
            }).catch(err => {
              console.error("❌ 修改失败：", err);
            });
          }}>提交</button>
          <button onClick={() => setModalIsOpen(false)} style={{ marginLeft: 10 }}>取消</button>
        </div>
        </div>
        </Modal>
      )}
      {addModalOpen && (
        <Modal
          isOpen
          onRequestClose={() => setAddModalOpen(false)}
          contentLabel="添加新员工对话框"
          style={{ content: { maxWidth: 500, margin: 'auto' } }}
        >
      <div className="modal-content">
        <h3>添加新员工</h3>
        <label>简历编号：</label>
        <input
          type="text"
          value={newEmployee.resume_id}
          onChange={(e) => setNewEmployee({ ...newEmployee, resume_id: e.target.value })}
          style={{ width: '100%', marginBottom: 10 }}
        />
        <label>职位：</label>
        <input
          type="text"
          value={newEmployee.position}
          onChange={(e) => setNewEmployee({ ...newEmployee, position: e.target.value })}
          style={{ width: '100%', marginBottom: 10 }}
        />
        <label>工龄：</label>
        <input
          type="text"
          value={newEmployee.experience}
          onChange={(e) => setNewEmployee({ ...newEmployee, experience: e.target.value })}
          style={{ width: '100%', marginBottom: 10 }}
        />
        <label>评分：</label>
        <input
          type="text"
          value={newEmployee.score}
          onChange={(e) => setNewEmployee({ ...newEmployee, score: e.target.value })}
          style={{ width: '100%', marginBottom: 10 }}
        />
        <label>岗位建议：</label>
        <input
          type="text"
          value={newEmployee.recommended_position}
          onChange={(e) => setNewEmployee({ ...newEmployee, recommended_position: e.target.value })}
          style={{ width: '100%', marginBottom: 10 }}
        />
        <label>备注：</label>
        <textarea
          value={newEmployee.note}
          onChange={(e) => setNewEmployee({ ...newEmployee, note: e.target.value })}
          style={{ width: '100%', height: 100 }}
        />
        <div style={{ marginTop: 20 }}>
          <button onClick={() => {
            axios.post("/employees/add", newEmployee)
              .then(res => {
                console.log("✅ 添加成功：", res.data);
                setAddModalOpen(false);
              }).catch(err => {
                console.error("❌ 添加失败：", err);
              });
          }}>提交</button>
          <button onClick={() => setAddModalOpen(false)} style={{ marginLeft: 10 }}>取消</button>
        </div>
        </div>
        </Modal>
      )}
    </div>
  );
}

export default AdminEmployeePage;