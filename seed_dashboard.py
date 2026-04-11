import sys
import os
import hashlib
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.database import SessionLocal, engine
from src.core.database import Base
from src.endpoints.samples.model import Sample, SampleFile, SampleResult
from src.endpoints.users.model import User

Base.metadata.create_all(bind=engine)

# Imagem existente em /uploads/
EXISTING_IMAGE = "8c1dd242-acaf-4aee-a61d-29c1a1752fc3.jpg"
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

def file_checksum(path: str) -> str:
    h = hashlib.md5()
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                h.update(f.read())
            return h.hexdigest()
        return "unknown"
    except Exception:
        return "unknown"

def seed():
    db = SessionLocal()
    
    user = db.query(User).first()
    if not user:
        print("No users found. Creating a default user.")
        user = User(
            name="Admin",
            email="admin@eon.com",
            hashed_password="hashed_password",
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    user_id = user.id

    samples_to_create = [
        {"code": "SMP-8902", "tier_label": "Exame de Sangue",    "status": "concluido",   "conf": 0.98, "pred": "Normal"},
        {"code": "SMP-8903", "tier_label": "Biópsia de Tecido",  "status": "rejeitado",   "conf": 0.92, "pred": "Alta Probabilidade de Malignidade"},
        {"code": "SMP-8904", "tier_label": "Exame de RM",        "status": "processando", "conf": 0.45, "pred": "Processando..."},
        {"code": "SMP-8905", "tier_label": "Exame de Sangue",    "status": "concluido",   "conf": 0.85, "pred": "Leves Indicadores de Anemia"},
        {"code": "SMP-8906", "tier_label": "Exame de Sangue",    "status": "concluido",   "conf": 0.91, "pred": "Normal"},
        {"code": "SMP-8907", "tier_label": "Análise de Urina",   "status": "rejeitado",   "conf": 0.30, "pred": "Volume Insuficiente"},
        {"code": "SMP-8908", "tier_label": "Exame de Sangue",    "status": "pendente",    "conf": 0.00, "pred": "Aguardando"},
        {"code": "SMP-8909", "tier_label": "Biópsia de Tecido",  "status": "concluido",   "conf": 0.77, "pred": "Benigno"},
    ]

    img_path = os.path.join(UPLOADS_DIR, EXISTING_IMAGE)
    img_size = os.path.getsize(img_path) if os.path.exists(img_path) else 0
    img_checksum = file_checksum(img_path)

    for s_data in samples_to_create:
        existing = db.query(Sample).filter(Sample.code == s_data["code"]).first()
        if not existing:
            sample = Sample(
                code=s_data["code"],
                created_by=user_id,
                tier_label=s_data["tier_label"],
                status=s_data["status"],
                collected_at=datetime.now(timezone.utc)
            )
            db.add(sample)
            db.commit()
            db.refresh(sample)
            
            # Só insere resultado se não for pendente
            if s_data["conf"] > 0:
                result = SampleResult(
                    sample_id=sample.id,
                    confidence_score=s_data["conf"],
                    ml_raw_output={"predicted_class": s_data["pred"]},
                    model_version="v1.0"
                )
                db.add(result)
                db.commit()

            # Vincula a imagem existente ao sample
            sf = SampleFile(
                sample_id=sample.id,
                file_name=EXISTING_IMAGE,
                file_type="image/jpeg",
                storage_path=EXISTING_IMAGE,
                file_size=img_size,
                checksum=img_checksum,
            )
            db.add(sf)
            db.commit()

            print(f"[OK] Amostra {s_data['code']} + imagem inseridas.")
        else:
            # Garante que amostras existentes também tenham SampleFile
            sf_exists = db.query(SampleFile).filter(SampleFile.sample_id == existing.id).first()
            if not sf_exists:
                sf = SampleFile(
                    sample_id=existing.id,
                    file_name=EXISTING_IMAGE,
                    file_type="image/jpeg",
                    storage_path=EXISTING_IMAGE,
                    file_size=img_size,
                    checksum=img_checksum,
                )
                db.add(sf)
                db.commit()
                print(f"[OK] Imagem vinculada à amostra existente {s_data['code']}.")
            else:
                print(f"[--] Amostra {s_data['code']} já existe com imagem, pulando.")

    db.close()
    print("\nSeed concluído!")

if __name__ == "__main__":
    seed()
