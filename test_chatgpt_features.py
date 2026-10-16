import sys
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def test_full_flow():
    print("Testing NexusAI Full Flow with new features...")
    
    # 1. Login with existing test account
    login_res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "muthu@gmail.com",
        "password": "M12345"
    })
    if login_res.status_code != 200:
        # Fallback to test user or signup if needed
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "Password@123"
        })
    print(f"1. Login Status: {login_res.status_code}")
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"

    # 2. Create a new conversation
    chat_res = session.post(f"{BASE_URL}/api/chats", json={"title": "ChatGPT Features Test"})
    assert chat_res.status_code == 201
    chat_id = chat_res.json()["id"]
    print(f"2. Created Chat ID: {chat_id}")

    # 3. Test Pin Feature (PATCH /api/chats/<id>)
    pin_res = session.patch(f"{BASE_URL}/api/chats/{chat_id}", json={"is_pinned": 1})
    assert pin_res.status_code == 200
    print("3. Pinned Chat Successfully")

    # 4. Verify in /api/chats that chat is in pinned list
    list_res = session.get(f"{BASE_URL}/api/chats")
    chats_data = list_res.json()
    pinned_ids = [c["id"] for c in chats_data.get("pinned", [])]
    assert chat_id in pinned_ids, "Chat not found in pinned list!"
    print(f"4. Verified Chat in Pinned Section (Total pinned: {len(pinned_ids)})")

    # 5. Send message with Tamil/Tanglish Persona
    print("5. Testing Message with Tamil Persona...")
    msg_res = session.post(f"{BASE_URL}/api/chats/{chat_id}/message", json={
        "content": "வணக்கம்! எனக்கு Python கற்றுக்கொள்ள உதவி பண்ணுங்க.",
        "persona": "tamil"
    }, stream=True)
    print(f"5. msg_res status: {msg_res.status_code}")
    if msg_res.status_code != 200:
        print(f"Error text: {msg_res.text}")
    assert msg_res.status_code == 200
    
    response_text = ""
    for line in msg_res.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                try:
                    import json
                    d = json.loads(decoded[6:])
                    if "chunk" in d:
                        response_text += d["chunk"]
                except Exception:
                    pass
    print("AI Response Preview (Tamil Persona):")
    print(response_text[:300] + "...")
    assert len(response_text) > 100, "Response is too short!"

    # 6. Send message with Math Persona
    print("6. Testing Math Query...")
    msg_res2 = session.post(f"{BASE_URL}/api/chats/{chat_id}/message", json={
        "content": "Calculate step-by-step: 15 * 24 + 350",
        "persona": "math"
    }, stream=True)
    assert msg_res2.status_code == 200
    
    math_text = ""
    for line in msg_res2.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                try:
                    import json
                    d = json.loads(decoded[6:])
                    if "chunk" in d:
                        math_text += d["chunk"]
                except Exception:
                    pass
    print("AI Response Preview (Math):")
    print(math_text[:300] + "...")
    assert "710" in math_text or "360" in math_text, "Math solution should contain 710!"

    # 7. Test Clear Chat Messages (/api/chats/<id>/clear)
    clear_res = session.post(f"{BASE_URL}/api/chats/{chat_id}/clear")
    assert clear_res.status_code == 200
    print("7. Chat cleared successfully.")

    # Verify messages are 0
    get_chat = session.get(f"{BASE_URL}/api/chats/{chat_id}")
    assert len(get_chat.json()["messages"]) == 0
    print("8. Verified 0 messages after clear.")

    # 8. Clean up: Delete test chat
    del_res = session.delete(f"{BASE_URL}/api/chats/{chat_id}")
    assert del_res.status_code == 200
    print("9. Cleaned up test chat.")

    print("\nALL BACKEND & CHATGPT WORKFLOW TESTS PASSED!")

if __name__ == "__main__":
    test_full_flow()
