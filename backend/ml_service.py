# backend/ml_service.py
import io
import json
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image
from pathlib import Path


class MLService:
    """Load model TorchScript/checkpoint dan jalankan inference serangga."""

    def __init__(
        self,
        model_path    = "artifacts/insect_model.pt",
        metadata_path = "artifacts/model_metadata.json",
    ):
        self.model_path    = model_path
        self.metadata_path = metadata_path
        self.model         = None
        self.classes       = None
        self.transform     = None
        self.device        = torch.device("cpu")  # CPU untuk deployment lokal
        self.num_classes   = 0
        self.img_size      = 224

    def load_model(self):
        """Muat model dan metadata dari disk."""
        # Load metadata
        with open(self.metadata_path) as f:
            meta = json.load(f)

        self.classes     = meta["classes"]
        self.num_classes = len(self.classes)
        self.img_size    = meta["img_size"]
        mean = meta["normalization"]["mean"]
        std  = meta["normalization"]["std"]

        pth = Path(self.model_path)
        if pth.suffix == ".pt":
            # TorchScript model (format direkomendasikan)
            self.model = torch.jit.load(str(pth), map_location=self.device)
        else:
            # Regular checkpoint → perlu reconstruct arsitektur
            import timm
            import torch.nn as nn

            backbone = timm.create_model(
                meta.get("model_name", "efficientnet_b4"),
                pretrained  = False,
                num_classes = 0,
                global_pool = "avg",
            )
            with torch.no_grad():
                feat = backbone(
                    torch.zeros(1, 3, self.img_size, self.img_size)
                ).shape[1]

            head = nn.Sequential(
                nn.Dropout(0.4),
                nn.Linear(feat, 512),
                nn.BatchNorm1d(512),
                nn.GELU(),
                nn.Dropout(0.2),
                nn.Linear(512, self.num_classes),
            )

            class InsectModel(nn.Module):
                def __init__(self, b, h):
                    super().__init__()
                    self.backbone = b
                    self.head     = h
                def forward(self, x):
                    return self.head(self.backbone(x))

            self.model = InsectModel(backbone, head)
            ckpt = torch.load(str(pth), map_location=self.device)
            self.model.load_state_dict(ckpt.get("state_dict", ckpt))

        self.model.eval()

        # Preprocessing transform (harus sama dengan saat training)
        self.transform = T.Compose([
            T.Resize(
                (self.img_size, self.img_size),
                interpolation=T.InterpolationMode.BICUBIC,
            ),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ])
        print(f"Model loaded: {self.num_classes} classes, img_size={self.img_size}")

    def is_loaded(self) -> bool:
        return self.model is not None

    def predict(self, image_bytes: bytes, top_k: int = 5) -> dict:
        """
        Prediksi kelas serangga dari bytes gambar.

        Returns:
            dict dengan class_name, confidence, dan top_k predictions
        """
        if not self.is_loaded():
            raise RuntimeError("Model belum dimuat. Panggil load_model() terlebih dahulu.")

        img    = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            out   = self.model(tensor)
            probs = F.softmax(out, dim=1)
            k     = min(top_k, self.num_classes)
            tp, ti = torch.topk(probs, k=k, dim=1)
            tp = tp[0].tolist()
            ti = ti[0].tolist()

        top_list = [
            {
                "rank"      : i + 1,
                "class_name": self.classes[idx],
                "class_idx" : idx,
                "confidence": round(p, 6),
            }
            for i, (idx, p) in enumerate(zip(ti, tp))
        ]

        return {
            "class_name": self.classes[ti[0]],
            "class_idx" : ti[0],
            "confidence": round(tp[0], 6),
            "top_k"     : top_list,
        }
