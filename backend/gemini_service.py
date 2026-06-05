# backend/gemini_service.py
import asyncio
import io
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Integrasi Google Gemini 2.0 Flash Lite untuk AI insights serangga."""

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
                model_name        = "gemini-2.0-flash-lite",
                generation_config = genai.GenerationConfig(
                    temperature       = 0.7,
                    top_p             = 0.85,
                    top_k             = 40,
                    max_output_tokens = 1200,
                ),
                system_instruction = (
                    "Anda adalah ahli entomologi (ilmuwan serangga) berpengalaman. "
                    "Berikan informasi akurat, menarik, dan mudah dipahami "
                    "tentang serangga dalam Bahasa Indonesia. "
                    "Format respons selalu dalam Markdown yang rapi."
                ),
            )
            print("Gemini model berhasil diinisialisasi")
        except ImportError:
            print("WARNING: google-generativeai tidak terinstall")
        except Exception as exc:
            print(f"WARNING: Gagal init Gemini — {exc}")

    def _build_prompt(self, name: str) -> str:
        lines = [
            f"Berikan informasi lengkap dan menarik tentang serangga berikut:",
            "",
            f"**Serangga:** {name}",
            "",
            "Gunakan format berikut PERSIS (termasuk emoji dan heading Markdown):",
            "",
            "## Identifikasi Ilmiah",
            "**Nama Ilmiah:** [nama ilmiah]  ",
            "**Kingdom:** Animalia | **Phylum:** Arthropoda | **Class:** Insecta  ",
            "**Ordo:** [ordo] | **Famili:** [famili] | **Genus:** [genus]",
            "",
            "## Distribusi & Habitat",
            "[Deskripsi 2-3 kalimat tentang sebaran geografis dan habitat alami]",
            "",
            "## Morfologi & Ciri Khas",
            "[Deskripsi 2-3 kalimat tentang penampilan fisik yang membedakan]",
            "",
            "## Perilaku & Ekologi",
            "[Deskripsi 2-3 kalimat tentang perilaku, makanan, dan peran ekologis]",
            "",
            "## Dampak & Kepentingan",
            "[Dampak terhadap manusia/pertanian/ekosistem — positif maupun negatif]",
            "",
            "## Fun Facts",
            "- [Fakta menarik 1]",
            "- [Fakta menarik 2]",
            "- [Fakta menarik 3]",
            "",
            "---",
            "*Informasi disediakan oleh Smart Insect Identifier AI*",
        ]
        return "\n".join(lines)

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
