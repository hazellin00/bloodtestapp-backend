import React, { useState } from 'react';
import axios from 'axios';

const DadInputPortal = ({ userId }) => {
  // 7-2-2 狀態管理
  const [step, setStep] = useState(1); // 1: 第一遍, 2: 第二遍, 3: 完成
  const [m1, setM1] = useState({ sys: '', dia: '', hr: '' });
  const [m2, setM2] = useState({ sys: '', dia: '', hr: '' });
  const [loading, setLoading] = useState(false);

  // 計算平均值
  const calculateAvg = () => {
    return {
      sys: Math.round((Number(m1.sys) + Number(m2.sys)) / 2),
      dia: Math.round((Number(m1.dia) + Number(m2.dia)) / 2),
      hr: Math.round((Number(m1.hr) + Number(m2.hr)) / 2)
    };
  };

  // 提交數據至 FastAPI
  const handleSubmit = async () => {
    setLoading(true);
    const avg = calculateAvg();
    const period = new Date().getHours() < 12 ? 'morning' : 'evening';

    try {
      await axios.post('http://localhost:8000/logs', {
        user_id: userId,
        systolic: avg.sys,
        diastolic: avg.dia,
        heart_rate: avg.hr,
        period: period
      });
      setStep(3);
    } catch (error) {
      alert("儲存失敗，請檢查網路！");
    } finally {
      setLoading(false);
    }
  };

  // 紅綠燈狀態判定
  const getStatusColor = (sys, dia) => {
    if (sys >= 140 || dia >= 90) return '#ff4d4d'; // 紅色
    if (sys >= 120 || dia >= 80) return '#ffcc00'; // 黃色
    return '#4CAF50'; // 綠色
  };

  return (
    <div style={{ padding: '30px', fontSize: '24px', maxWidth: '500px', margin: '0 auto', textAlign: 'center' }}>
      <h1 style={{ fontSize: '36px', marginBottom: '20px' }}>🩸 爸爸量血壓</h1>

      {step < 3 && (
        <div style={{ backgroundColor: '#f0f4f8', padding: '20px', borderRadius: '20px', marginBottom: '20px' }}>
          <h2 style={{ color: '#007bff' }}>第 {step} 遍測量</h2>
          <p style={{ fontSize: '20px', color: '#666' }}>請坐好休息 5 分鐘再開始喔</p>
          
          <div style={{ margin: '20px 0' }}>
            <label>高壓 (收縮壓):</label>
            <input 
              type="number" 
              style={inputStyle} 
              value={step === 1 ? m1.sys : m2.sys}
              onChange={(e) => step === 1 ? setM1({...m1, sys: e.target.value}) : setM2({...m2, sys: e.target.value})}
            />
          </div>

          <div style={{ margin: '20px 0' }}>
            <label>低壓 (舒張壓):</label>
            <input 
              type="number" 
              style={inputStyle} 
              value={step === 1 ? m1.dia : m2.dia}
              onChange={(e) => step === 1 ? setM1({...m1, dia: e.target.value}) : setM2({...m2, dia: e.target.value})}
            />
          </div>

          <button 
            style={buttonStyle} 
            onClick={() => step === 1 ? setStep(2) : handleSubmit()}
            disabled={loading}
          >
            {step === 1 ? "下一步：量第二遍" : "確認並儲存"}
          </button>
        </div>
      )}

      {step === 3 && (
        <div style={{ padding: '40px', borderRadius: '20px', backgroundColor: getStatusColor(calculateAvg().sys, calculateAvg().dia), color: 'white' }}>
          <h2 style={{ fontSize: '40px' }}>量完囉！👍</h2>
          <p>平均血壓：{calculateAvg().sys} / {calculateAvg().dia}</p>
          <p>心率：{calculateAvg().hr}</p>
          <button style={{ ...buttonStyle, backgroundColor: 'white', color: 'black' }} onClick={() => window.location.reload()}>
            回主畫面
          </button>
        </div>
      )}

      <footer style={{ marginTop: '30px', fontSize: '16px', color: '#999' }}>
        僅供參考；調整藥物前請務必諮詢醫師。
      </footer>
    </div>
  );
};

// 大字體 UI 樣式
const inputStyle = {
  fontSize: '32px', width: '100%', padding: '10px', borderRadius: '10px', border: '2px solid #ddd', textAlign: 'center'
};
const buttonStyle = {
  fontSize: '28px', width: '100%', height: '80px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '15px', cursor: 'pointer', marginTop: '10px'
};

export default DadInputPortal;