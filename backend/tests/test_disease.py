from app.disease import DiseaseClassifier, treatment_for

def test_classifier_reports_missing_model_explicitly(tmp_path):
    classifier = DiseaseClassifier(tmp_path / "missing.tflite", tmp_path / "labels.txt")
    assert classifier.ready is False
    result = classifier.predict(b"not-an-image")
    assert result["status"] == "model_not_configured"

def test_healthy_treatment_is_conservative():
    assert "routine monitoring" in treatment_for("Tomato___healthy")
