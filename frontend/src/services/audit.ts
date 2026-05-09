import api from './api';

const auditService = {
  getLogs: (params: any) => 
    api.get('/admin/audit-logs', { params }),
};

export default auditService;
