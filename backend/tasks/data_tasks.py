import pandas as pd
import os
import json
from celery import shared_task
from backend.database import SessionLocal
from backend.models.upload import Upload
from backend.models.summary import Summary
from backend.ai import call_groq_insights

from backend.celery_app import celery_app

@celery_app.task(bind=True, name="backend.tasks.data_tasks.process_file_task")
def process_file_task(self, upload_id):
    db = SessionLocal()
    try:
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Starting processing...'})
        
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            return {"error": "Upload not found"}

        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Loading CSV...'})
        df = pd.read_csv(upload.filepath)

        self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': 'Calculating statistics...'})
        summary = {
            "filename": upload.filename,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "stats": df.describe(include='all').fillna("").to_dict(),
            "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
            "categorical_columns": df.select_dtypes(exclude="number").columns.tolist(),
        }

        if len(summary["numeric_columns"]) >= 2:
            corr = df[summary["numeric_columns"]].corr().round(3).to_dict()
            summary["correlation"] = corr

        summary["sample_data"] = df.head(5).to_dict(orient="records")
        summary_json = json.dumps(summary)

        self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Generating AI insights...'})
        prompt = f"Analyze this dataset summary and give 3 key insights:\n{summary_json}"
        insights = call_groq_insights(prompt)

        self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Saving results...'})
        new_summary = Summary(
            upload_id=upload.id,
            user_id=upload.user_id,
            summary_json=summary_json
        )
        db.add(new_summary)
        db.commit()

        self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed'})
        return {"status": "completed", "upload_id": upload.id, "summary_id": new_summary.id}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()
