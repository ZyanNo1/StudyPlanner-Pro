// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 1. 导航栏滚动效果
    const nav = document.querySelector('nav');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 10) {
            nav.classList.add('shadow-lg');
            nav.classList.add('py-2');
            nav.classList.remove('py-3');
        } else {
            nav.classList.remove('shadow-lg');
            nav.classList.add('py-3');
            nav.classList.remove('py-2');
        }
    });

    // 2. 初始化所有进度条（移到全局，页面加载即执行！）
    // 课程进度条
    document.querySelectorAll('[data-progress]').forEach(el => {
        const progress = el.getAttribute('data-progress');
        el.style.width = progress + '%';
    });
    // 完成率进度条
    document.querySelectorAll('[data-rate]').forEach(el => {
        const rate = el.getAttribute('data-rate');
        el.style.width = rate + '%';
    });
    // 学习时间进度条（新增）
    document.querySelectorAll('[data-time]').forEach(el => {
        const time = parseFloat(el.getAttribute('data-time'));
        const total = parseFloat(el.getAttribute('data-total'));
        const widthPercent = (time / total) * 100;
        el.style.width = widthPercent + '%';
    });

    // 3. 任务完成按钮交互（取消前端模拟，保留后端提交逻辑）
    const completeForms = document.querySelectorAll('form[action*="complete_task"]');
    completeForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const timeInput = this.querySelector('input[name="actual_time"]');
            if (!timeInput.value || isNaN(timeInput.value)) {
                e.preventDefault();
                showToast('请输入有效的实际耗时（数字）！');
                timeInput.classList.add('border-danger');
                setTimeout(() => timeInput.classList.remove('border-danger'), 3000);
            }
        });
    });

    // 4. 全局提示框函数
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-secondary text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-500';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-4');
            setTimeout(() => document.body.removeChild(toast), 500);
        }, 3000);
    }

    // 5. 全局表单验证（所有表单通用）
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-danger');
                    const errorMsg = document.createElement('p');
                    errorMsg.className = 'text-danger text-xs mt-1';
                    errorMsg.textContent = '此字段不能为空';
                    field.parentNode.appendChild(errorMsg);
                    setTimeout(() => {
                        field.classList.remove('border-danger');
                        if (errorMsg.parentNode) errorMsg.parentNode.removeChild(errorMsg);
                    }, 3000);
                }
            });
            if (!isValid) {
                e.preventDefault();
                showToast('请填写所有必填字段！');
            }
        });
    });
});