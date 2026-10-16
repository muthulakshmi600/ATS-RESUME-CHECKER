/**
 * FileUploader Component: Drag and drop PDF/DOCX file uploader with validation
 * ResumeAI ATS SaaS Theme
 */

window.FileUploader = ({ file, onFileSelect, onFileRemove, error }) => {
  const { Upload, FileText, X, AlertCircle, CheckCircle } = window.Icons;
  const [isDragging, setIsDragging] = React.useState(false);
  const inputRef = React.useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSet(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSet(e.target.files[0]);
    }
  };

  const validateAndSet = (selectedFile) => {
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx'].includes(ext)) {
      onFileSelect(null, 'Only PDF and DOCX files are supported.');
      return;
    }
    if (selectedFile.size > 5 * 1024 * 1024) {
      onFileSelect(null, `File size exceeds 5 MB. Selected file is ${(selectedFile.size / (1024*1024)).toFixed(2)} MB.`);
      return;
    }
    onFileSelect(selectedFile, null);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  return (
    <div className="w-full">
      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current && inputRef.current.click()}
          className={`relative border-2 border-dashed rounded-2xl p-8 sm:p-10 text-center cursor-pointer transition-all duration-200 ${
            isDragging
              ? 'border-[#2563EB] bg-blue-50/60 scale-[1.01]'
              : 'border-[#CBD5E1] bg-[#F8FAFC] hover:border-[#2563EB] hover:bg-slate-50'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleChange}
            className="hidden"
          />

          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] transition-transform">
            <Upload className="w-8 h-8" />
          </div>

          <h4 className="text-base font-bold text-[#14213D] mb-1">
            Drag & Drop your resume here
          </h4>
          <p className="text-sm text-[#64748B] mb-4">
            or <span className="text-[#2563EB] font-bold hover:underline">Browse Files</span> from your computer
          </p>

          <div className="inline-flex items-center gap-3 px-3.5 py-1.5 rounded-lg bg-white border border-[#CBD5E1] text-xs text-[#64748B] shadow-sm">
            <span className="font-bold text-[#2563EB]">Formats: PDF, DOCX</span>
            <span className="text-slate-300">•</span>
            <span>Max file size: 5 MB</span>
          </div>
        </div>
      ) : (
        <div className="bg-white border border-[#CBD5E1] rounded-2xl p-5 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB] flex-shrink-0">
              <FileText className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-bold text-[#14213D] truncate max-w-xs sm:max-w-md">
                  {file.name}
                </p>
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-50 text-[#16A34A] border border-emerald-200">
                  Ready
                </span>
              </div>
              <p className="text-xs text-[#64748B] mt-0.5">
                {formatSize(file.size)} • {file.name.split('.').pop().toUpperCase()} Document
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onFileRemove();
            }}
            className="p-2 text-[#64748B] hover:text-rose-600 hover:bg-rose-50 rounded-xl transition flex-shrink-0"
            title="Remove resume"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-center gap-2 text-xs text-rose-600 bg-rose-50 border border-rose-200 px-3.5 py-2.5 rounded-xl font-medium">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
