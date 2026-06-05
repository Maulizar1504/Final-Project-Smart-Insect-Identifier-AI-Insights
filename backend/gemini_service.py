# backend/gemini_service.py
import asyncio
import io
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Integrasi Google Gemini-3.5 Flash untuk AI insights serangga."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model   = None
        self._init()

    def _init(self):
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY tidak ditemukan di .env")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name = "gemini-3.5-flash",
                generation_config = genai.GenerationConfig(
                    temperature       = 0.7,
                    top_p             = 0.85,
                    top_k             = 40,
                    max_output_tokens = 8192,
                ),
                system_instruction = (
                    "Kamu adalah ahli entomologi senior yang sangat berpengalaman. "
                    "Tugasmu adalah memberikan informasi LENGKAP, DETAIL, dan AKURAT "
                    "tentang serangga dalam Bahasa Indonesia yang mudah dipahami. "
                    "Selalu jawab SEMUA bagian yang diminta tanpa terkecuali. "
                    "Jangan pernah mempersingkat atau melewati bagian apapun. "
                    "Format respons selalu dalam Markdown yang rapi dan terstruktur."
                ),
            )
            print("Gemini model berhasil diinisialisasi")
        except ImportError:
            print("WARNING: google-generativeai tidak terinstall")
        except Exception as exc:
            print(f"WARNING: Gagal init Gemini — {exc}")

    def _build_prompt(self, name: str) -> str:
        return f"""Kamu adalah ahli entomologi senior. Berikan informasi LENGKAP dan DETAIL tentang serangga berikut dalam Bahasa Indonesia.

Serangga: {name}

Tulis dengan format PERSIS seperti ini (jangan skip satu bagian pun, isi setiap bagian dengan lengkap):

## Identifikasi Ilmiah
**Nama Ilmiah:** [nama ilmiah lengkap dalam huruf miring]
**Nama Umum:** [nama umum dalam bahasa Indonesia]
**Kingdom:** Animalia | **Phylum:** Arthropoda | **Class:** Insecta
**Ordo:** [ordo] | **Famili:** [famili] | **Genus:** [genus]

## Distribusi & Habitat
[Tulis 3-4 kalimat LENGKAP tentang di mana serangga ini ditemukan di dunia, negara atau benua mana saja, jenis habitat yang disukai seperti hutan, ladang, kebun, rumah, atau area lainnya, serta kondisi iklim yang cocok untuk hidupnya]

## Morfologi & Ciri Khas
[Tulis 3-4 kalimat LENGKAP tentang ukuran tubuh dalam milimeter atau sentimeter, warna dan pola tubuh yang khas, bentuk sayap jika ada, antena, kaki, dan ciri fisik unik yang membedakannya dari spesies lain yang mirip]

## Perilaku & Ekologi
[Tulis 3-4 kalimat LENGKAP tentang pola makan dan makanan favoritnya, siklus hidup dari telur hingga dewasa, perilaku sosial apakah soliter atau berkelompok, musim aktif, dan interaksi dengan makhluk hidup lain di sekitarnya]

## Dampak & Kepentingan
[Tulis 3-4 kalimat LENGKAP tentang manfaat positif atau kerugian yang ditimbulkan bagi manusia, perannya dalam pertanian baik sebagai hama maupun pembantu, kontribusinya pada ekosistem seperti penyerbukan atau dekomposisi, dan nilai ekonomisnya jika ada]

## Fun Facts 🦋
- [Fakta unik dan mengejutkan tentang serangga ini yang jarang diketahui orang]
- [Fakta menarik kedua tentang kemampuan atau perilaku khususnya]
- [Fakta ketiga yang berhubungan dengan rekor atau keunikan biologisnya]
- [Fakta keempat tentang hubungannya dengan manusia atau budaya]

---
*Informasi disediakan oleh LensArthropoda AI*

PENTING: Isi SEMUA bagian di atas secara lengkap dan detail. Jangan disingkat. Total minimal 400 kata."""

    async def get_insights(
        self,
        name        : str,
        image_bytes : bytes = None,
    ) -> dict:
        """
        Dapatkan AI insights tentang serangga dari Gemini.

        Raises:
            Exception: Jika API gagal (caller harus tangani dengan fallback)
        """
        if not self.model:
            raise Exception("Gemini tidak terinisialisasi — periksa GEMINI_API_KEY")

        import google.generativeai as genai

        prompt = self._build_prompt(name)
        loop   = asyncio.get_event_loop()

        if image_bytes:
            try:
                img  = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                resp = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content([prompt, img]),
                )
            except Exception:
                # Fallback ke text-only jika gambar bermasalah
                resp = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt),
                )
        else:
            resp = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt),
            )

        return {
            "available"  : True,
            "content"    : resp.text,
            "insect_name": name,
        }