import { useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Sparkles,
  RefreshCw,
  ImageIcon,
  ChevronRight,
  Loader2,
  Leaf,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const inputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const stage = useMemo(() => {
    if (loading) return "loading";
    if (result) return "result";
    if (file && previewUrl) return "preview";
    return "upload";
  }, [file, previewUrl, result, loading]);

  const openPicker = () => {
    inputRef.current?.click();
  };

  const resetAll = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);

    setFile(null);
    setPreviewUrl(null);
    setLoading(false);
    setError("");
    setResult(null);

    if (inputRef.current) inputRef.current.value = "";
  };

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (!selected.type.startsWith("image/")) {
      setError("Please upload a valid image file.");
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);

    setError("");
    setResult(null);
    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
  };

  const handleClassify = async () => {
    if (!file) return;

    try {
      setLoading(true);
      setError("");
      setResult(null);

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || "Prediction failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const primaryPrediction =
    result?.final_prediction || result?.predicted_label || "-";

  return (
    <div className="app-shell">
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        className="hidden-input"
        onChange={handleFileChange}
      />

      <div className="bg-orb orb-1" />
      <div className="bg-orb orb-2" />
      <div className="bg-orb orb-3" />
      <div className="dot-grid" />

      <div className="floating-icon icon-1">
        <Leaf size={58} />
      </div>
      <div className="floating-icon icon-2">
        <Sparkles size={48} />
      </div>
      <div className="floating-icon icon-3">
        <Leaf size={42} />
      </div>

      <main className="container">
        <motion.header
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="hero"
        >
          <h1>Mushroom Variety Classifier</h1>
          <p>
            Classify your mushroom image variety with top 3 confidence scores.
          </p>
        </motion.header>

        <AnimatePresence mode="wait">

{/* UPLOAD STAGE */}

{stage === "upload" && (
<motion.section
key="upload"
initial={{ opacity: 0, y: 16 }}
animate={{ opacity: 1, y: 0 }}
exit={{ opacity: 0, y: -12 }}
className="panel-wrap"
>

<div className="card upload-card">

<button type="button" onClick={openPicker} className="upload-zone">

<div className="upload-icon-box">
<Upload size={40} />
</div>

<h2>Upload your mushroom image</h2>

<p className="upload-subtext">Click to select Image</p>

<p className="upload-fileinfo">
PNG, JPG, JPEG, WEBP
</p>

<button
type="button"
className="gradient-btn hero-btn"
onClick={(e) => {
e.stopPropagation();
openPicker();
}}
>

Start Classifying
<ChevronRight size={18} />

</button>

</button>

</div>

</motion.section>
)}

{/* PREVIEW */}

{stage === "preview" && previewUrl && (

<motion.section key="preview" className="preview-layout">

<div className="card image-card">
<div className="image-frame">
<img src={previewUrl} alt="Selected preview" />
</div>
</div>

<div className="side-column">

<div className="card info-card">

<div className="badge-icon success-icon">
<ImageIcon size={28} />
</div>

<h2>Preview ready</h2>

<div className="button-stack">

<button className="gradient-btn classify-btn" onClick={handleClassify}>
<Sparkles size={18} />
Classify Image
</button>

<button className="gradient-btn retry-btn" onClick={resetAll}>
<RefreshCw size={18} />
Upload Again
</button>

</div>

</div>

{error && <div className="error-box">{error}</div>}

</div>

</motion.section>
)}

{/* LOADING */}

{stage === "loading" && previewUrl && (

<motion.section key="loading" className="panel-wrap">

<div className="card loading-card">

<div className="loading-image-frame">
<img src={previewUrl} alt="Preview" />
</div>

<div className="loader-badge">
<Loader2 size={34} className="spin" />
</div>

<h2>Analyzing your image...</h2>

</div>

</motion.section>
)}

{/* RESULT */}

{stage === "result" && result && previewUrl && (

<motion.section key="result" className="result-layout">

<div className="card image-card">
<div className="image-frame">
<img src={previewUrl} alt="Prediction input" />
</div>
</div>

<div className="side-column">

<div className="card result-card">

<p className="section-label">
Top Prediction
</p>

<h2 className="prediction-title">
{primaryPrediction}
</h2>

<div className="confidence-chip">
Confidence: {(result.confidence * 100).toFixed(1)}%
</div>

</div>

<div className="card result-card">

<p className="section-label alt">
Top 3 matches
</p>

<div className="top-list">

{result.top3_predictions?.map((item, index) => (

<div key={index} className="top-item">

<p className="top-label">{item.label}</p>

<div className="score-pill">
{(item.confidence * 100).toFixed(1)}%
</div>

</div>

))}

</div>

<button
className="gradient-btn hero-btn"
onClick={resetAll}
>

Try Another Image

</button>

</div>

</div>

</motion.section>

)}

</AnimatePresence>

</main>

</div>
);
}

export default App;