const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 4000;

app.use(cors());
app.use(express.json());

const employees = [
  {
    id: 1,
    name: "张三",
    gender: "男",
    education: "本科",
    experience: 3,
    skills: ["Excel", "沟通", "设备维护"],
    certificates: ["中级技工"],
    performance: 87,
    satisfaction: 80
  },
  {
    id: 2,
    name: "李四",
    gender: "女",
    education: "专科",
    experience: 5,
    skills: ["维修", "管理"],
    certificates: ["高级维修工"],
    performance: 92,
    satisfaction: 85
  }
];

app.get("/api/employees", (req, res) => {
    console.log("📥 收到一个 /api/employees 请求！");
    res.json(employees);
  });

app.listen(PORT, () => {
  console.log(`✅ Server is running on http://localhost:${PORT}`);
});