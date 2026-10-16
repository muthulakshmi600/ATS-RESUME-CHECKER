/**
 * Toast Notification Component
 * ResumeAI ATS SaaS Theme
 */

window.Toast = ({ message, type = "success", onClose }) => {
  const { CheckCircle, AlertCircle, X, Info } = window.Icons;

  if (!message) return null;

  const bgColors = {
    success: "bg-[#16A34A] text-white shadow-md shadow-green-600/20",
    error: "bg-rose-600 text-white shadow-md shadow-rose-600/20",
    info: "bg-[#2563EB] text-white shadow-md shadow-blue-600/20"
  };

  const IconComp = type === 'success' ? CheckCircle : type === 'error' ? AlertCircle : (Info || CheckCircle);

  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-xl transition-all transform animate-bounce-short ${bgColors[type] || bgColors.info}`}>
      {IconComp && <IconComp className="w-5 h-5 flex-shrink-0" />}
      <span className="text-sm font-semibold">{message}</span>
      <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-lg transition ml-2" aria-label="Close notification">
        {X ? <X className="w-4 h-4" /> : '✕'}
      </button>
    </div>
  );
};
