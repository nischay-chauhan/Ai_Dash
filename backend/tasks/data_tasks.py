import pandas as pd
import os
from celery import shared_task
from backend.database import SessionLocal
from backend.models.upload import Upload
from backend.models.summary import Summary
from backend.ai_utils import generate_ai_response

@shared_task(bind=True)
def process_file_task(self, upload_id):
    db = SessionLocal()
    try:
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            return {"error": "Upload not found"}

        df = pd.read_csv(upload.filepath)

        summary = {
            "filename": upload.filename,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
        }

        prompt = f"Analyze this dataset summary and give 3 key insights:\n{summary}"
        insights = generate_ai_response(prompt)

        new_summary = Summary(
            upload_id=upload.id,
            summary_json=summary,
            insights=insights
        )
        db.add(new_summary)
        db.commit()

        return {"status": "completed", "insights": insights}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
