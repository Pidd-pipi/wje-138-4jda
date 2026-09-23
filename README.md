# 车队调度与维护管理平台

## Docker 快速启动

```bash
cp .env.example .env
docker compose up -d
```

前端：http://localhost:18708  
后端：http://localhost:19208/api/health/

## 项目介绍

面向物流公司和车队管理者的全栈 Web 应用，覆盖车辆档案、司机管理、调度派单、油耗统计和维保记录。

## 主要功能

- 调度中心：创建调度单、指派车辆和司机、查看运输时间线；**保养到期车辆被占用，选用时展示具体原因（里程超 10,000 km / 距上次保养满 90 天 / 维修中），调度单不保存**。
- 车辆管理：车辆卡片、维保历史、油耗趋势入口；被占用车辆展示“为什么不能排班”。
- 司机管理：状态筛选、调度历史、驾驶时长统计。
- 维保管理：保养到期自动生成待处理预约，可筛选「到期占用 / 待处理预约 / 已完成」；维修人员提交里程、费用和完成时间后解除占用，并按新里程重算下次预约（+10,000 km / +90 天）。
- 油耗分析：油耗趋势、月度总油耗、异常油耗预警。

## 保养到期占用规则

- 规则阈值：距上次保养**超过 10,000 公里**，或距上次保养日期**满 90 天**（任一满足即到期）。
- 到期后系统自动生成 `Scheduled` 的系统预约（幂等），车辆禁止调度；维修人员开工后转为 `InProgress`，完工提交里程/费用/完成时间后：
  - 车辆占用解除、累计里程同步、状态恢复可用；
  - 按新里程重算下次保养（里程阈值 +10,000、日期阈值 +90 天）。
- 相关代码：
  - 规则：`backend/fleet_app/services/maintenance_policy.py`
  - 业务：`backend/fleet_app/services/maintenance_service.py`
  - 调度拦截：`backend/fleet_app/services/dispatch_service.py`（`VehicleMaintenanceBlocked`，HTTP 409，调度单不保存）
  - 页面：`frontend/src/pages/MaintenanceManage.tsx`、`frontend/src/pages/DispatchCenter.tsx`

## 本地开发

后端默认监听 3000，前端开发服务器会把 `/api` 请求代理到后端。后端本地启动需要可连接的 PostgreSQL；如果没有本机 PostgreSQL，请优先使用 Docker Compose 启动完整环境。

```bash
cd backend
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:3000
```

```bash
cd frontend
npm install
npm run dev
```

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | React 18 + TypeScript + Vite |
| UI | Ant Design 5 |
| 图表 | ECharts |
| 状态 | Zustand |
| 后端 | Django + Django REST Framework |
| 数据库 | PostgreSQL 15 |
| 认证 | SimpleJWT |

## 目录结构

```
frontend/src/
├── api/ stores/ types/ components/common/ hooks/ pages/ router/ utils/ constants/
backend/
├── fleet_app/views/ serializers/ services/ middleware/ models.py urls.py permissions.py admin.py
└── config/settings.py urls.py
```

## 环境变量

| 变量 | 说明 |
| --- | --- |
| COMPOSE_PROJECT_NAME | Docker Compose 项目名 |
| DB_NAME / DB_USER / DB_PASSWORD / DB_ROOT_PASSWORD | PostgreSQL 配置 |
| JWT_SECRET | JWT 密钥 |
| FRONTEND_PORT / BACKEND_PORT | 宿主机端口 |

## 枚举位置

- VehicleStatus：frontend/src/types/enums.ts；frontend/src/types/vehicle.ts；frontend/src/components/common/VehicleCard.tsx；backend/fleet_app/models.py；backend/fleet_app/services/vehicle_service.py
- DispatchStatus：frontend/src/types/enums.ts；frontend/src/types/dispatch.ts；frontend/src/hooks/useDispatch.ts；backend/fleet_app/models.py；backend/fleet_app/services/dispatch_service.py
- MaintenanceType：frontend/src/types/enums.ts；frontend/src/types/maintenance.ts；frontend/src/pages/MaintenanceManage.tsx；backend/fleet_app/models.py；backend/fleet_app/services/maintenance_service.py
- DriverStatus：frontend/src/types/enums.ts；frontend/src/types/driver.ts；backend/fleet_app/models.py；backend/fleet_app/services/driver_service.py

## License

MIT
