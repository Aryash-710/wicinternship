from typing import List, Dict, Any, Optional
from app.services.location_service import LocationService
from app.services.worker_service import WorkerService
from app.services.job_service import JobService

RELATED_TRADES: Dict[str, List[str]] = {
    "electrician": ["ac technician", "appliance tech", "inverter repair", "helper"],
    "plumber": ["tile mason", "sanitary worker", "helper"],
    "mason": ["tile mason", "plasterer", "concrete worker", "helper"],
    "carpenter": ["wood polish", "furniture fitter", "helper"],
    "painter": ["waterproofing", "putty worker", "helper"],
    "welder": ["fabricator", "blacksmith", "helper"],
    "tile_mason": ["mason", "flooring", "helper"],
    "helper": ["loader", "gardener", "construction worker"]
}


class MatchingService:
    @classmethod
    def calculate_skill_score(cls, worker_trade: str, worker_skills: str, job_trade: str) -> float:
        w_t = (worker_trade or "").strip().lower()
        j_t = (job_trade or "").strip().lower()
        w_skills = (worker_skills or "").strip().lower()

        if w_t == j_t:
            return 1.0

        # Check secondary skills
        if j_t in w_skills:
            return 0.85

        # Check related trades
        related = RELATED_TRADES.get(w_t, [])
        if any(r in j_t for r in related):
            return 0.70

        if w_t == "helper" or j_t == "helper":
            return 0.50

        return 0.15

    @classmethod
    def calculate_distance_score(cls, dist_km: float, max_radius: float = 50.0) -> float:
        if dist_km <= 5.0:
            return 1.0
        elif dist_km <= 15.0:
            return 0.85
        elif dist_km <= 30.0:
            return 0.65
        elif dist_km <= max_radius:
            return 0.40
        else:
            return 0.10

    @classmethod
    def calculate_wage_score(cls, worker_rate: float, job_offer: float) -> float:
        if worker_rate <= 0:
            return 1.0
        ratio = job_offer / worker_rate
        if ratio >= 1.0:
            return 1.0  # Employer pays equal or higher than worker's expectations
        elif ratio >= 0.85:
            return 0.80  # Within 15% negotiation range
        elif ratio >= 0.70:
            return 0.50
        else:
            return 0.20

    @classmethod
    def score_match(
        cls,
        worker: Dict[str, Any],
        job: Dict[str, Any],
        max_radius_km: float = 50.0
    ) -> Dict[str, Any]:
        """
        Compute multi-factor match score between a worker and a job.
        """
        dist_km = LocationService.haversine_distance(
            worker["latitude"], worker["longitude"],
            job["latitude"], job["longitude"]
        )

        skill_score = cls.calculate_skill_score(
            worker["trade"], worker.get("secondary_skills", ""), job["trade"]
        )
        distance_score = cls.calculate_distance_score(dist_km, max_radius_km)
        wage_score = cls.calculate_wage_score(worker["daily_rate"], job["wage_offered"])

        # Experience & Reliability
        rating = worker.get("rating", 4.5)
        rating_score = min(rating / 5.0, 1.0)

        availability = worker.get("availability", "available")
        avail_score = 1.0 if availability == "available" else (0.7 if availability == "on_call" else 0.3)

        reliability_score = (rating_score * 0.6) + (avail_score * 0.4)

        # Weighted composite score (0 - 100%)
        # Weights: Skill 40%, Distance 30%, Wage 20%, Reliability 10%
        composite = (
            (skill_score * 0.40) +
            (distance_score * 0.30) +
            (wage_score * 0.20) +
            (reliability_score * 0.10)
        ) * 100.0

        total_score = round(composite, 1)

        # Human explainability string
        expl_parts = []
        if skill_score >= 0.85:
            expl_parts.append(f"Strong skill match ({job['trade']})")
        else:
            expl_parts.append(f"Related trade ({worker['trade']} -> {job['trade']})")

        expl_parts.append(f"{dist_km} km away ({job.get('area') or job.get('city')})")

        if wage_score >= 1.0:
            expl_parts.append(f"Fair pay (₹{job['wage_offered']:.0f} >= ₹{worker['daily_rate']:.0f} requested)")
        else:
            expl_parts.append(f"Offer ₹{job['wage_offered']:.0f} vs requested ₹{worker['daily_rate']:.0f}")

        explanation = "; ".join(expl_parts)

        return {
            "skill_score": round(skill_score * 100, 1),
            "distance_score": round(distance_score * 100, 1),
            "wage_score": round(wage_score * 100, 1),
            "experience_score": round(reliability_score * 100, 1),
            "availability_score": round(avail_score * 100, 1),
            "total_score": total_score,
            "distance_km": dist_km,
            "explanation": explanation
        }

    @classmethod
    def match_jobs_for_worker(
        cls,
        worker_id: int,
        max_radius_km: float = 60.0,
        min_score: float = 40.0,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        worker = WorkerService.get_worker(worker_id)
        if not worker:
            return []

        all_open_jobs = JobService.list_jobs(status="open", limit=200)
        matched = []

        for job in all_open_jobs:
            score_data = cls.score_match(worker, job, max_radius_km)
            if score_data["distance_km"] <= max_radius_km and score_data["total_score"] >= min_score:
                matched.append({
                    "job": job,
                    "match_score": score_data["total_score"],
                    "breakdown": score_data
                })

        # Sort descending by match score
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        return matched[:limit]

    @classmethod
    def match_workers_for_job(
        cls,
        job_id: int,
        max_radius_km: float = 60.0,
        min_score: float = 40.0,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        job = JobService.get_job(job_id)
        if not job:
            return []

        all_workers = WorkerService.list_workers(limit=200)
        matched = []

        for worker in all_workers:
            score_data = cls.score_match(worker, job, max_radius_km)
            if score_data["distance_km"] <= max_radius_km and score_data["total_score"] >= min_score:
                matched.append({
                    "worker": worker,
                    "match_score": score_data["total_score"],
                    "breakdown": score_data
                })

        # Sort descending by match score
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        return matched[:limit]
