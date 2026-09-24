import json


def analyze_trivy_report(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    vulnerability_count = 0
    secret_count = 0
    misconfiguration_count = 0

    for result in data.get("Results", []):

        # Vulnerabilities
        for vulnerability in result.get("Vulnerabilities", []) or []:
            severity = vulnerability.get("Severity", "").lower()

            if severity in severity_counts:
                severity_counts[severity] += 1

            vulnerability_count += 1

        # Secrets
        for secret in result.get("Secrets", []) or []:
            severity = secret.get("Severity", "").lower()

            if severity in severity_counts:
                severity_counts[severity] += 1

            secret_count += 1

        # Misconfigurations
        for misconfiguration in result.get("Misconfigurations", []) or []:
            severity = misconfiguration.get("Severity", "").lower()

            if severity in severity_counts:
                severity_counts[severity] += 1

            misconfiguration_count += 1

    # Our own project scoring formula
    penalty = (
        severity_counts["critical"] * 25
        + severity_counts["high"] * 10
        + severity_counts["medium"] * 4
        + severity_counts["low"] * 1
    )

    security_score = max(0, 100 - penalty)

    if severity_counts["critical"] > 0:
        risk_level = "Critical"

    elif severity_counts["high"] > 0:
        risk_level = "High"

    elif severity_counts["medium"] > 0:
        risk_level = "Medium"

    elif severity_counts["low"] > 0:
        risk_level = "Low"

    else:
        risk_level = "Safe"

    recommendations = []

    if severity_counts["critical"] > 0:
        recommendations.append(
            "Fix critical vulnerabilities immediately."
        )

    if severity_counts["high"] > 0:
        recommendations.append(
            "Upgrade or patch packages with high-severity vulnerabilities."
        )

    if secret_count > 0:
        recommendations.append(
            "Remove exposed secrets and rotate affected credentials."
        )

    if misconfiguration_count > 0:
        recommendations.append(
            "Review and fix detected security misconfigurations."
        )

    if not recommendations:
        recommendations.append(
            "No major security issues detected."
        )

    return {
        "critical": severity_counts["critical"],
        "high": severity_counts["high"],
        "medium": severity_counts["medium"],
        "low": severity_counts["low"],

        "vulnerabilities": vulnerability_count,
        "secrets": secret_count,
        "misconfigurations": misconfiguration_count,

        "security_score": security_score,
        "risk_level": risk_level,

        "recommendations": recommendations
    }