from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.protocol import Envelope


def test_envelope_accepts_current_protocol() -> None:
    message = Envelope(
        type="observation",
        timestamp=datetime.now(UTC),
        protocol_version="1",
        payload={},
    )

    assert message.protocol_version == "1"


def test_envelope_rejects_version_mismatch() -> None:
    with pytest.raises(ValidationError):
        Envelope(type="observation", protocol_version="999", payload={})

