import csv
import json
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID
from zipfile import ZipFile

from src.application.export.dtos import AdvertiserExportSchema


class UUIDEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return str(o)
        if str(o).startswith("TargetingGender."):
            return str(o).replace("TargetingGender.", "")
        return super().default(o)


class ExportServiceProtocol(Protocol):
    def create_export_archive(self, data: AdvertiserExportSchema) -> bytes: ...


class ExportService:
    def create_export_archive(self, data: AdvertiserExportSchema) -> bytes:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            json_path = temp_path / "export.json"
            with open(json_path, "w") as f:
                json.dump(data.model_dump(), f, indent=2, cls=UUIDEncoder)

            csv_path = temp_path / "export.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                writer.writerow(
                    [
                        "advertiser_id",
                        "advertiser_name",
                        "campaign_id",
                        "image_url",
                        "impressions_limit",
                        "clicks_limit",
                        "cost_per_impression",
                        "cost_per_click",
                        "ad_title",
                        "ad_text",
                        "start_date",
                        "end_date",
                        "gender",
                        "age_from",
                        "age_to",
                        "location",
                        "impressions_count",
                        "clicks_count",
                        "conversion",
                        "spent_impressions",
                        "spent_clicks",
                        "spent_total",
                        "unique_events_count",
                        "average_rating",
                        "ml_score",
                    ]
                )

                for campaign in data.campaigns:
                    stats = campaign.statistics[0] if campaign.statistics else None

                    ratings = [
                        event.rating
                        for event in campaign.unique_events
                        if event.rating is not None
                    ]
                    avg_rating = sum(ratings) / len(ratings) if ratings else 0

                    campaign_client_ids = {
                        event.client_id for event in campaign.unique_events
                    }
                    campaign_ml_scores = [
                        score.score
                        for score in data.ml_scores
                        if score.client_id in campaign_client_ids
                    ]
                    avg_ml_score = (
                        sum(campaign_ml_scores) / len(campaign_ml_scores)
                        if campaign_ml_scores
                        else 0
                    )

                    gender = (
                        str(campaign.gender).replace("TargetingGender.", "")
                        if campaign.gender
                        else None
                    )

                    writer.writerow(
                        [
                            str(data.advertiser_id),
                            data.name,
                            str(campaign.campaign_id),
                            campaign.image_url or "",
                            campaign.impressions_limit,
                            campaign.clicks_limit,
                            campaign.cost_per_impression,
                            campaign.cost_per_click,
                            campaign.ad_title,
                            campaign.ad_text,
                            campaign.start_date,
                            campaign.end_date,
                            gender,
                            campaign.age_from,
                            campaign.age_to,
                            campaign.location,
                            stats.impressions_count if stats else 0,
                            stats.clicks_count if stats else 0,
                            stats.conversion if stats else 0,
                            stats.spent_impressions if stats else 0,
                            stats.spent_clicks if stats else 0,
                            stats.spent_total if stats else 0,
                            len(campaign.unique_events),
                            round(avg_rating, 2),
                            round(avg_ml_score, 2),
                        ]
                    )

            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                zip_file.write(json_path, "export.json")
                zip_file.write(csv_path, "export.csv")

            return zip_buffer.getvalue()
