from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from ml_service import MLService
from gemini_service import GeminiService

ml_svc     = MLService()
gemini_svc = GeminiService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading ML model ...")
    ml_svc.load_model()
    print(f"Model loaded — {ml_svc.num_classes} classes")
    yield


app = FastAPI(
    title       = "Smart Insect Identifier API",
    description = "Identifikasi serangga dari gambar menggunakan AI",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


@app.get("/")
async def root():
    return {"message": "Smart Insect Identifier API", "status": "running"}


@app.get("/health")
async def health():
    return {
        "status"      : "healthy",
        "model_loaded": ml_svc.is_loaded(),
        "num_classes" : ml_svc.num_classes,
    }


@app.get("/classes")
async def get_classes():
    if not ml_svc.is_loaded():
        raise HTTPException(503, "Model belum dimuat")
    return {"classes": ml_svc.classes, "total": len(ml_svc.classes)}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Endpoint utama: upload gambar → prediksi kelas + AI insights."""

    allowed = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"}

    if file.content_type and file.content_type not in allowed:
        raise HTTPException(400, f"Harus berupa gambar, bukan {file.content_type}")

    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "Maksimal ukuran file 10 MB")

    # ── ML Prediction ─────────────────────────────────────────────────────────
    try:
        prediction = ml_svc.predict(data, top_k=5)
    except Exception as exc:
        raise HTTPException(500, f"Prediksi gagal: {exc}")

    # ── Gemini Insights ───────────────────────────────────────────────────────
    try:
        print(f"🔍 Memanggil Gemini untuk: {prediction['class_name']}")
        insights = await gemini_svc.get_insights(prediction["class_name"], data)
        print(f"✅ Gemini berhasil — panjang respons: {len(insights.get('content', ''))} karakter")
    except Exception as exc:
        print(f"❌ GEMINI ERROR: {type(exc).__name__}: {exc}")
        name = prediction["class_name"]
        conf = prediction["confidence"]
        insights = {
            "available": False,
            "error"    : str(exc),
            "content"  : (
                f"## Hasil Identifikasi\n\n"
                f"**Serangga:** {name}\n\n"
                f"**Confidence:** {conf:.1%}\n\n"
                "> Informasi detail AI sementara tidak tersedia. "
                "Silakan coba lagi nanti."
            ),
        }

    return JSONResponse({
        "status"    : "success",
        "prediction": prediction,
        "insights"  : insights,
        "filename"  : file.filename,
    })


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)