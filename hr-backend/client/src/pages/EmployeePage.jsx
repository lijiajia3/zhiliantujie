import React, { useEffect, useState } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';


const EmployeePage = () => {
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    axios.get('/api/employees')
      .then(res => {
        setEmployees(res.data);
      })
      .catch(err => {
        console.error('获取失败:', err);
      });
  }, []);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const data = new Uint8Array(evt.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(sheet);
      setEmployees(jsonData);
    };
    reader.readAsArrayBuffer(file);
  };

  const handleDefaultImport = () => {
    
    fetch('/employees.xlsx')
      .then(res => res.arrayBuffer())
      .then(buffer => {
        const data = new Uint8Array(buffer);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(sheet);
        setEmployees(jsonData);
      })
      .catch(err => console.error('导入失败:', err));
  };

  return (
    <div style={{ padding: 50 }}>
      <div style={{ marginBottom: 20 }}>
        <input type="file" accept=".xlsx" onChange={handleFileUpload} />
        <button onClick={handleDefaultImport} style={{ marginLeft: 10 }}>
          导入默认Excel
        </button>
      </div>
      <h1>员工信息表</h1>
      <table border="1">
        <thead>
          <tr>
            <th>姓名</th>
            <th>性别</th>
            <th>学历</th>
            <th>经验</th>
            <th>技能</th>
            <th>证书</th>
            <th>绩效</th>
            <th>满意度</th>
          </tr>
        </thead>
        <tbody>
          {employees.map(emp => (
            <tr key={emp.id}>
              <td>{emp.name}</td>
              <td>{emp.gender}</td>
              <td>{emp.education}</td>
              <td>{emp.experience}</td>
              <td>{emp.skills.join(', ')}</td>
              <td>{emp.certificates.join(', ')}</td>
              <td>{emp.performance}</td>
              <td>{emp.satisfaction}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EmployeePage;