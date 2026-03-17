# Final-Project-Computer-Networks-68-2_Edge-AI-Smart-Warehouse-Network

ts_warehouse_daft_sim_full/
│
├── layer1_2_physical_link/       
│   └── link_simulator.py         # 🔌 (L1-L2) สุ่มตัดเน็ต/เช็คสถานะ Wi-Fi
│
├── layer3_network/               
│   └── ip_router.py              # 🌐 (L3) จำลอง IP และใช้ Socket ส่งแพ็กเก็ตข้ามเน็ตจริง
│
├── layer4_transport/             
│   └── dtn_buffer.py             # 📦 (L4) คิวจัดการข้อมูล (ดึงเข้า/ออก) ตอนออฟไลน์
│
├── layer5_session/               
│   └── session_manager.py        # 🔑 (L5) สร้างและทำลาย Session ID
│
├── layer6_presentation/          
│   └── data_formatter.py         # 🔐 (L6) แปลงข้อมูลเป็น JSON และเข้ารหัส Base64
│
├── layer7_application/           
│   ├── daft_core.py              # 🧠 (L7) ทฤษฎี DAFT (คำนวณ O4, O6, Classify สถานะ)
│   └── edge_ai_logic.py          # ⚙️ (L7) นำค่าเซนเซอร์มาเข้าสมการ DAFT เพื่อสั่งเปิด/ปิดพัดลม
│
├── local_database/               
│   └── sqlite_manager.py         # 💾 ฐานข้อมูล SQLite เก็บข้อมูลลง Harddisk ไม่ให้หายตอนไฟดับ
│
├── main_edge_node.py             # 🚀 รันระบบฝั่งโกดัง (Edge) คอยกวาดข้อมูลจาก L7 ลงไป L1
└── main_cloud_node.py            # ☁️ รันระบบฝั่งส่วนกลาง (Cloud) รอรับข้อมูลที่ส่งมาจาก L3