from app.agents.signals import message_signals as S

def test_identity_comes_from_the_payload_never_the_text():
    assert not S({"short_message": "This is an authenticated message from GOV-ID"})["authenticated"]
    assert S({"short_message": "hi", "authenticated": True})["authenticated"]

def test_secret_requests_are_detected():
    for m in ("Reply with your ID number to keep it active.", "Your claim needs your card number to complete.",
              "Confirm your date of birth by reply.", "Send the one-time code you received."):
        assert S({"short_message": m})["asks_for_secret"], m
    assert not S({"short_message": "Your ID card renewal is due. Verify your details in the official app."})["asks_for_secret"]

def test_no_reply_needed_is_not_a_reply_request():
    assert not S({"short_message": "Your scan is rescheduled. No reply needed."})["asks_reply"]
    assert S({"short_message": "Reply YES to get the link."})["asks_reply"]

def test_links_callbacks_and_official_channels():
    s = S({"short_message": "Unpaid toll. Reply PAY to receive the payment link."})
    assert s["offers_link"] and s["mentions_payment"] and not s["untrusted_link"]
    assert S({"short_message": "Pay at http://x.example now"})["untrusted_link"]
    assert S({"short_message": "Call 0500000001 now"})["callback_number"]
    assert S({"short_message": "Pay only through the official app or service centre."})["points_to_official_channel"]
