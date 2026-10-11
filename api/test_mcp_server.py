import asyncio
import json

from mcp_server import clinic_catalog, find_available_clinics, search_clinics, server


def test_server_registers_two_tools_and_one_resource():
    tools = asyncio.run(server.list_tools())
    resources = asyncio.run(server.list_resources())
    assert {tool.name for tool in tools} >= {"search_clinics", "find_available_clinics"}
    assert any(str(resource.uri) == "clinics://catalog" for resource in resources)


def test_search_tool_returns_matching_clinic():
    result = search_clinics("Nairobi", "KE")
    assert result["ok"] is True
    assert result["clinics"][0]["clinic_id"] == "KE-NBO-001"


def test_invalid_tool_call_returns_instructive_error_data(caplog):
    result = search_clinics("x", "Kenya")
    assert result == {
        "ok": False,
        "error": {
            "code": "INVALID_QUERY",
            "message": "query must contain 2 to 80 characters",
            "hint": "Provide a clinic, city, service, or ID search term.",
        },
    }
    assert sum('"event":"mcp_call"' in record.message for record in caplog.records) == 1


def test_available_clinics_and_resource_are_real_catalog_data():
    result = find_available_clinics(5, "KE")
    resource = json.loads(clinic_catalog())
    assert result["count"] == 1
    assert resource["ok"] is True
    assert len(resource["clinics"]) == 3