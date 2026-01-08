"""
Telemetry processing utilities for token-efficient device data formatting.
"""
from typing import Optional
from src.models.schemas import DeviceTelemetry, RequestCategory


# Mapping of request categories to relevant telemetry fields
CATEGORY_TELEMETRY_MAPPING = {
    RequestCategory.HARDWARE_FAILURE: [
        "cpu_pct", "mem_pct", "disk_critical", "uptime_hours", "recent_errors"
    ],
    RequestCategory.NETWORK_CONNECTIVITY: [
        "online", "vpn_connected", "ip_assigned", "dns_resolved"
    ],
    RequestCategory.SOFTWARE_INSTALLATION: [
        "os", "disk_critical", "failed_services"
    ],
    RequestCategory.PASSWORD_RESET: [],  # No telemetry needed
    RequestCategory.EMAIL_CONFIGURATION: [
        "online", "vpn_connected"
    ],
    RequestCategory.SECURITY_INCIDENT: [
        "online", "vpn_connected", "recent_errors"
    ],
    RequestCategory.POLICY_QUESTION: [],  # No telemetry needed
    RequestCategory.UNKNOWN: [],  # No filtering for unknown categories
}


def format_telemetry(telemetry: Optional[DeviceTelemetry], category: RequestCategory) -> str:
    """
    Format telemetry data in a token-efficient way based on request category.
    
    Only includes fields relevant to the specific category to minimize token usage.
    Uses compact formatting: [Device: cpu=85; mem=95; disk_critical=true]
    
    Args:
        telemetry: Optional device telemetry data
        category: Request category to determine relevant fields
        
    Returns:
        Formatted telemetry string or empty string if no relevant data
    """
    if not telemetry or category not in CATEGORY_TELEMETRY_MAPPING:
        return ""
    
    relevant_fields = CATEGORY_TELEMETRY_MAPPING[category]
    if not relevant_fields:
        return ""
    
    parts = []
    for field in relevant_fields:
        value = getattr(telemetry, field, None)
        if value is not None:
            # Format booleans as lowercase true/false for brevity
            if isinstance(value, bool):
                parts.append(f"{field}={str(value).lower()}")
            # Format lists as comma-separated values
            elif isinstance(value, list):
                if value:  # Only include non-empty lists
                    parts.append(f"{field}={','.join(str(v) for v in value)}")
            else:
                parts.append(f"{field}={value}")
    
    return f"[Device: {'; '.join(parts)}]" if parts else ""


def should_escalate_on_telemetry(telemetry: Optional[DeviceTelemetry]) -> bool:
    """
    Check if telemetry indicates a critical issue requiring escalation.
    
    Args:
        telemetry: Optional device telemetry data
        
    Returns:
        True if telemetry indicates critical hardware issues
    """
    if not telemetry:
        return False
    
    # Auto-escalate on critical hardware conditions
    return (
        telemetry.disk_critical or
        (telemetry.cpu_pct is not None and telemetry.cpu_pct > 95) or
        (telemetry.mem_pct is not None and telemetry.mem_pct > 95) or
        (telemetry.failed_services is not None and len(telemetry.failed_services) > 2)
    )
