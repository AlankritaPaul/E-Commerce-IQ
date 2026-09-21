"""
Customer Review Sentiment Analysis and Topic Extraction Engine.

Analyzes raw textual feedback to identify:
- Polarity score (-1.0 to +1.0) and categorical sentiment (Positive, Neutral, Negative)
- Primary feedback topic (Quality, Sizing, Delivery, Packaging, Value, Battery/Hardware)
- Specific complaints, defect patterns, and praised features
- Fully explainable rationale with matched cues, negations, and intensifiers
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple


class SentimentAnalyzer:
    """
    Evaluates customer review sentiments and topic classifications using an
    explainable, transparent, rule-and-lexicon based NLP model.
    """

    # Lexicon with base valence weights (-1.0 to 1.0)
    POSITIVE_LEXICON: Dict[str, float] = {
        "exceptional": 0.95,
        "superb": 0.9,
        "excellent": 0.85,
        "stellar": 0.85,
        "flawless": 0.9,
        "amazing": 0.8,
        "fantastic": 0.8,
        "love": 0.8,
        "loved": 0.8,
        "perfect": 0.85,
        "perfectly": 0.8,
        "great": 0.7,
        "good": 0.5,
        "solid": 0.6,
        "sturdy": 0.65,
        "sleek": 0.6,
        "premium": 0.7,
        "durable": 0.7,
        "comfortable": 0.7,
        "delighted": 0.75,
        "pleased": 0.65,
        "satisfied": 0.6,
        "worth": 0.65,
        "recommend": 0.7,
        "recommended": 0.7,
        "exceeded": 0.8,
        "fast": 0.5,
        "responsive": 0.6,
        "impressive": 0.75,
        "helpful": 0.55,
        "beautiful": 0.7,
        "happy": 0.65,
        "best": 0.85,
        "smooth": 0.55,
        "reliable": 0.7,
        "crisp": 0.6,
        "bargain": 0.65,
        "superior": 0.8,
    }

    NEGATIVE_LEXICON: Dict[str, float] = {
        "terrible": -0.9,
        "horrible": -0.9,
        "awful": -0.85,
        "worst": -0.95,
        "defective": -0.9,
        "defect": -0.85,
        "broken": -0.85,
        "broke": -0.8,
        "failed": -0.8,
        "fails": -0.75,
        "useless": -0.85,
        "garbage": -0.9,
        "trash": -0.85,
        "waste": -0.8,
        "disappointed": -0.75,
        "disappointing": -0.75,
        "poor": -0.7,
        "poorly": -0.7,
        "cheap": -0.65,
        "flimsy": -0.7,
        "bad": -0.6,
        "hate": -0.8,
        "hated": -0.8,
        "unusable": -0.85,
        "regret": -0.75,
        "tight": -0.5,
        "small": -0.45,
        "scratch": -0.5,
        "scratched": -0.55,
        "damaged": -0.75,
        "overpriced": -0.65,
        "slow": -0.45,
        "late": -0.5,
        "noisy": -0.5,
        "overheating": -0.7,
        "overheats": -0.7,
        "misleading": -0.7,
        "inaccurate": -0.6,
        "annoying": -0.6,
        "lacking": -0.5,
    }

    NEGATION_TOKENS: Set[str] = {
        "not", "never", "no", "hardly", "barely", "scarcely", "cannot", "cant",
        "can't", "wont", "won't", "don't", "dont", "doesnt", "doesn't", "didnt",
        "didn't", "without", "rarely", "neither"
    }

    INTENSIFIERS: Dict[str, float] = {
        "very": 1.3,
        "extremely": 1.5,
        "highly": 1.4,
        "absolutely": 1.5,
        "really": 1.3,
        "super": 1.35,
        "incredibly": 1.45,
        "totally": 1.3,
        "completely": 1.35,
        "exceptionally": 1.5,
        "deeply": 1.3,
    }

    TOPIC_KEYWORD_MAP: Dict[str, List[str]] = {
        "Battery/Hardware": [
            "battery", "charge", "charging", "dies", "dying", "hardware",
            "power", "cuts out", "cut out", "shuts off", "overheat", "overheating"
        ],
        "Sizing/Fit": [
            "size", "sizing", "fit", "fitting", "tight", "loose", "narrow",
            "wide", "runs small", "runs large", "shoulders", "waist", "inches"
        ],
        "Shipping/Delivery": [
            "shipping", "delivery", "arrived", "courier", "package", "transit",
            "carrier", "box", "late", "delay", "damaged in transit"
        ],
        "Pricing/Value": [
            "price", "pricing", "cost", "value", "worth", "money", "penny",
            "expensive", "cheap", "overpriced", "bargain", "deal"
        ],
        "Item Not as Pictured": [
            "picture", "photo", "misleading", "different", "color", "appearance",
            "pictured", "description", "not as shown"
        ],
        "Quality": [
            "quality", "material", "durability", "durable", "sturdy", "build",
            "craftsmanship", "finish", "flimsy", "fabric", "construction"
        ],
    }

    def _tokenize(self, text: str) -> List[str]:
        """Clean and split text into normalized words while preserving punctuation cues."""
        cleaned = re.sub(r"[^\w\s\'-]", " ", text.lower())
        return [t.strip("'") for t in cleaned.split() if t.strip("'")]

    def analyze_text(
        self,
        text: str,
        rating: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract sentiment polarity score, label, primary topic, and explainable
        evidence from raw review text.
        """
        if not text or not text.strip():
            return {
                "sentiment_label": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.5,
                "primary_topic": "General",
                "detected_issue": None,
                "matched_positive_cues": [],
                "matched_negative_cues": [],
                "negations_detected": [],
                "intensifiers_detected": [],
                "explanation": "No text provided; classified as neutral.",
            }

        tokens = self._tokenize(text)
        lowered_text = text.lower()

        matched_positive: List[str] = []
        matched_negative: List[str] = []
        negations_found: List[str] = []
        intensifiers_found: List[str] = []

        raw_scores: List[float] = []

        n_tokens = len(tokens)
        for i, token in enumerate(tokens):
            # Check for intensifier in previous 2 tokens
            multiplier = 1.0
            for back_idx in range(max(0, i - 2), i):
                prev_token = tokens[back_idx]
                if prev_token in self.INTENSIFIERS:
                    multiplier = max(multiplier, self.INTENSIFIERS[prev_token])
                    intensifiers_found.append(f"{prev_token} -> {token}")

            # Check for negation in previous 3 tokens
            is_negated = False
            for back_idx in range(max(0, i - 3), i):
                prev_token = tokens[back_idx]
                if prev_token in self.NEGATION_TOKENS:
                    is_negated = True
                    negations_found.append(f"{prev_token} {token}")
                    break

            # Positive match
            if token in self.POSITIVE_LEXICON:
                val = self.POSITIVE_LEXICON[token] * multiplier
                if is_negated:
                    # Negated positive -> becomes negative ("not good" = -0.6)
                    inverted_val = -abs(val) * 0.9
                    raw_scores.append(inverted_val)
                    matched_negative.append(f"not {token}")
                else:
                    raw_scores.append(val)
                    matched_positive.append(token)

            # Negative match
            elif token in self.NEGATIVE_LEXICON:
                val = self.NEGATIVE_LEXICON[token] * multiplier
                if is_negated:
                    # Negated negative -> becomes mildly positive or neutral ("not bad" = +0.3)
                    inverted_val = abs(val) * 0.5
                    raw_scores.append(inverted_val)
                    matched_positive.append(f"not {token}")
                else:
                    raw_scores.append(val)
                    matched_negative.append(token)

        # Composite polarity calculation
        if raw_scores:
            base_polarity = sum(raw_scores) / len(raw_scores)
            # Clip between -1.0 and 1.0
            polarity = max(-1.0, min(1.0, base_polarity))
        else:
            polarity = 0.0

        # Calibrate with star rating if provided
        if rating is not None:
            rating_norm = (rating - 3) / 2.0  # 1->-1.0, 2->-0.5, 3->0.0, 4->0.5, 5->1.0
            if raw_scores:
                # 65% text weight, 35% rating weight
                polarity = round(0.65 * polarity + 0.35 * rating_norm, 4)
            else:
                polarity = round(rating_norm, 4)
        else:
            polarity = round(polarity, 4)

        # Assign sentiment categorical label
        if polarity >= 0.15:
            sentiment_label = "positive"
        elif polarity <= -0.15:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        # Topic detection
        detected_topic = "General"
        max_topic_matches = 0
        for topic, keywords in self.TOPIC_KEYWORD_MAP.items():
            matches = sum(1 for kw in keywords if kw in lowered_text)
            if matches > max_topic_matches:
                max_topic_matches = matches
                detected_topic = topic

        # Issue detection for negative feedback
        detected_issue = None
        if sentiment_label == "negative":
            if "battery" in lowered_text or "charge" in lowered_text or "dies" in lowered_text:
                detected_issue = "Battery failure / cuts out"
            elif "tight" in lowered_text or "small" in lowered_text or "fit" in lowered_text:
                detected_issue = "Incorrect size / runs small"
            elif "delivery" in lowered_text or "late" in lowered_text or "shipping" in lowered_text:
                detected_issue = "Shipping delay / damaged package"
            elif "picture" in lowered_text or "misleading" in lowered_text:
                detected_issue = "Item not as pictured"
            elif "cheap" in lowered_text or "flimsy" in lowered_text or "broken" in lowered_text or "defective" in lowered_text:
                detected_issue = "Material defect / poor craftsmanship"
            else:
                detected_issue = "Unsatisfied with product performance"

        # Confidence calculation
        evidence_count = len(matched_positive) + len(matched_negative)
        confidence = min(0.98, max(0.55, 0.50 + (evidence_count * 0.10)))

        # Explainability text
        reasons: List[str] = []
        if matched_positive:
            reasons.append(f"positive cues: [{', '.join(matched_positive[:4])}]")
        if matched_negative:
            reasons.append(f"negative cues: [{', '.join(matched_negative[:4])}]")
        if negations_found:
            reasons.append(f"negations: [{', '.join(negations_found[:3])}]")
        if rating is not None:
            reasons.append(f"grounded by {rating}-star rating")

        explanation_str = (
            f"Classified as {sentiment_label.upper()} (score: {polarity:+.2f}). "
            + ("; ".join(reasons) if reasons else "Based on neutral or balanced vocabulary.")
        )

        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": polarity,
            "confidence": round(confidence, 2),
            "primary_topic": detected_topic,
            "detected_issue": detected_issue,
            "matched_positive_cues": matched_positive,
            "matched_negative_cues": matched_negative,
            "negations_detected": negations_found,
            "intensifiers_detected": intensifiers_found,
            "explanation": explanation_str,
        }

    def batch_process_reviews(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process batches of customer reviews and produce structured insight records.
        """
        results: List[Dict[str, Any]] = []
        for r in reviews:
            text = f"{r.get('title', '')} {r.get('comment', '')}".strip()
            rating = r.get("rating")
            analysis = self.analyze_text(text, rating=rating)
            results.append({
                "review_id": r.get("review_id"),
                **analysis
            })
        return results
