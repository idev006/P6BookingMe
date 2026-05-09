<script setup lang="ts">
import { onMounted } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import { useApprovalStore } from '../../stores/approval';
import { 
  ClipboardCheck, 
  Clock, 
  History, 
  CalendarDays,
  CheckCircle2,
  XCircle,
  ArrowRight,
  LayoutDashboard
} from 'lucide-vue-next';
import { formatDateTime } from '../../utils/format';

const approvalStore = useApprovalStore();

onMounted(async () => {
  await approvalStore.fetchSummary();
});
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in space-y-10">
      <header class="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 class="text-4xl font-black text-base-content tracking-tight mb-2 flex items-center gap-4">
            <LayoutDashboard class="text-primary" :size="40" />
            Approver Insights
          </h1>
          <p class="text-base-content/60 text-lg font-medium italic">"แผงควบคุมการตัดสินใจและการพิจารณาการจองห้องประชุม"</p>
        </div>
      </header>

      <!-- Stats Cards -->
      <div v-if="approvalStore.summary" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link to="/admin/approvals" class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden group hover:border-warning/40 transition-all">
          <div class="card-body p-8 flex-row items-center gap-6">
            <div class="w-16 h-16 rounded-2xl bg-warning/10 flex items-center justify-center text-warning group-hover:bg-warning group-hover:text-white transition-all">
              <Clock :size="28" />
            </div>
            <div>
              <div class="text-4xl font-black text-warning">{{ approvalStore.summary.pending_count }}</div>
              <div class="text-sm uppercase font-black tracking-widest opacity-40">รายการรอพิจารณา</div>
            </div>
          </div>
        </router-link>

        <router-link to="/admin/approvals/history" class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden group hover:border-success/40 transition-all">
          <div class="card-body p-8 flex-row items-center gap-6">
            <div class="w-16 h-16 rounded-2xl bg-success/10 flex items-center justify-center text-success group-hover:bg-success group-hover:text-white transition-all">
              <ClipboardCheck :size="28" />
            </div>
            <div>
              <div class="text-4xl font-black text-success">{{ approvalStore.summary.my_actions_total }}</div>
              <div class="text-sm uppercase font-black tracking-widest opacity-40">รายการที่คุณตัดสินใจแล้ว</div>
            </div>
          </div>
        </router-link>

        <router-link to="/calendar" class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden group hover:border-primary/40 transition-all">
          <div class="card-body p-8 flex-row items-center gap-6">
            <div class="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-all">
              <CalendarDays :size="28" />
            </div>
            <div>
              <div class="text-sm uppercase font-black tracking-widest opacity-40 mb-1">Context View</div>
              <div class="text-lg font-black">ตรวจสอบปฏิทินรวม</div>
            </div>
          </div>
        </router-link>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-10">
        <!-- Recent Actions -->
        <div class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden">
          <div class="card-body p-0">
            <div class="p-8 border-b border-base-content/5 flex justify-between items-center bg-base-200/20">
              <h3 class="text-xl font-black flex items-center gap-3">
                <History class="text-primary" />
                ประวัติการพิจารณาล่าสุดของคุณ
              </h3>
              <router-link to="/admin/approvals/history" class="btn btn-ghost btn-sm gap-2 font-black opacity-50 hover:opacity-100">
                ดูทั้งหมด <ArrowRight :size="16" />
              </router-link>
            </div>
            
            <div v-if="approvalStore.summary?.recent_actions?.length > 0" class="divide-y divide-base-content/5">
              <div v-for="action in approvalStore.summary.recent_actions" :key="action.id" class="p-6 flex items-center justify-between hover:bg-base-200/30 transition-colors">
                <div class="flex items-center gap-4">
                  <div :class="['w-10 h-10 rounded-xl flex items-center justify-center', 
                    action.action === 'approve' ? 'bg-success/10 text-success' : 'bg-error/10 text-error']">
                    <CheckCircle2 v-if="action.action === 'approve'" :size="18" />
                    <XCircle v-else :size="18" />
                  </div>
                  <div>
                    <div class="font-bold text-base-content/80">{{ action.booking_title }}</div>
                    <div class="text-[10px] uppercase font-black opacity-30">{{ formatDateTime(action.actioned_at) }}</div>
                  </div>
                </div>
                <div :class="['badge badge-sm font-black uppercase tracking-widest', 
                  action.action === 'approve' ? 'badge-success' : 'badge-error']">
                  {{ action.action === 'approve' ? 'APPROVED' : 'REJECTED' }}
                </div>
              </div>
            </div>
            <div v-else class="py-20 text-center opacity-30 italic font-medium">
              ยังไม่มีประวัติการพิจารณา
            </div>
          </div>
        </div>

        <!-- System Message / Quick Links -->
        <div class="space-y-6">
          <div class="card bg-gradient-to-br from-primary to-secondary text-white shadow-2xl p-8 border-0 relative overflow-hidden">
            <div class="relative z-10">
              <h3 class="text-3xl font-black mb-4 tracking-tight">พร้อมตัดสินใจแล้วหรือยัง?</h3>
              <p class="mb-8 opacity-90 text-lg font-medium leading-relaxed">มีเพื่อนร่วมงานกำลังรอการอนุมัติห้องประชุมจากคุณอยู่ ตรวจสอบรายการและช่วยให้การทำงานลื่นไหลกันเถอะ!</p>
              <router-link to="/admin/approvals" class="btn bg-white border-0 text-primary font-black px-8 rounded-2xl shadow-xl hover:scale-105 transition-transform uppercase tracking-widest">
                เข้าสู่หน้าพิจารณาเดี๋ยวนี้
              </router-link>
            </div>
            <ClipboardCheck class="absolute -bottom-10 -right-10 opacity-10" :size="200" />
          </div>

          <div class="card bg-base-100 shadow-xl border border-base-content/5 p-8">
            <h4 class="text-xs font-black uppercase tracking-widest opacity-40 mb-6">Pro Tips for Approvers</h4>
            <ul class="space-y-4">
              <li class="flex items-start gap-4">
                <div class="w-2 h-2 bg-primary rounded-full mt-2 shrink-0"></div>
                <p class="text-sm font-medium opacity-70 italic">"ควรตรวจสอบปฏิทินกลางทุกครั้งก่อนอนุมัติ เพื่อหลีกเลี่ยงความขัดแย้งเชิงนโยบายการใช้ห้อง"</p>
              </li>
              <li class="flex items-start gap-4">
                <div class="w-2 h-2 bg-secondary rounded-full mt-2 shrink-0"></div>
                <p class="text-sm font-medium opacity-70 italic">"การระบุเหตุผลในการปฏิเสธที่ชัดเจน ช่วยให้เพื่อนร่วมงานปรับปรุงการจองในครั้งถัดไปได้ดีขึ้น"</p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
